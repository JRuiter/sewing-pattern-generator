"""Nesting engine for cutting layouts on fabric (strip packing with fixed width).

Canvas coordinates as in layout.py: mm, x across the fabric (0 = fold or left selvage),
y along the fabric, **down**. A piece is placed by an orientation (angle, mirrored) and an
offset: canvas = oriented(ring) + (dx, dy).

How it works:
- Every piece outline is rasterised once per allowed orientation, grown by half the gap
  plus a safety margin of 0.75 pixel, so two masks that do not overlap guarantee a real
  distance of at least `gap` between the cutting lines (checked exactly afterwards in the
  tests with shapely).
- Placement is greedy: for each piece the free positions come from an FFT correlation of
  its mask with the occupied area; the best position by the strategy's score wins.
- The order of the pieces decides a lot, so many orders are tried: fixed heuristics (area,
  length, width), seeded random perturbations and a local search (moving and swapping
  pieces). Deterministic: the same input always gives the same layout.

Constraints handled here:
- grainline: only the orientations the caller allows (grain parallel to the selvage,
  with nap / one-way prints only "top towards the top end");
- fold pieces (`pinned`): the leftmost point lies exactly on the fold (x = 0);
- clearance from the fold for all other pieces, from the selvages and from the cut end;
- stripes / plaids (`match_y`, `match_x`): a reference point of the piece (hem at the side
  seam, underarm point, centre line) must lie on the same phase of the print repeat, so
  stripes continue across seams.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass

import numpy as np
from PIL import Image, ImageDraw
from scipy import fft as sfft
from shapely.geometry import Polygon

import geometry as G

RES = 2.5               # raster resolution in mm
SEARCH_EVALS = 40       # greedy runs per layout on the coarse raster (orders × strategies + local search)
FINE_CANDIDATES = 5     # best coarse solutions re-run on the fine raster
FINE_LOCAL = 8          # extra local-search runs on the fine raster


@dataclass
class Item:
    ring: np.ndarray                    # cutting outline in piece coordinates
    orients: list                       # allowed (angle, mirrored)
    pinned: bool = False                # leftmost point exactly at x = 0 (fabric fold)
    match_y: tuple | None = None        # (point in piece coords, phase mm): canvas y ≡ phase (mod repeat)
    match_x: tuple | None = None        # the same across the fabric (plaid)


@dataclass
class Spot:
    item: int
    angle: float
    mirrored: bool
    dx: float
    dy: float


def oriented(pts, angle, mirrored=False):
    p = G.as_pts(pts)
    if mirrored:
        p = G.mirror_x(p, 0.0)
    r = G.rotate(p, angle)
    return np.stack([r[:, 0], -r[:, 1]], axis=1)


def _residual(v, phase, rep):
    """Signed distance of v to the nearest value ≡ phase (mod rep)."""
    d = (v - phase) % rep
    return d - rep if d > rep / 2 else d


class _Shape:
    """One item in one orientation: outline, raster mask and its anchor."""

    def __init__(self, item: Item, angle, mirrored, pad, res, cx, cy, extra):
        self.angle, self.mirrored = float(angle), bool(mirrored)
        self.pts = oriented(item.ring, angle, mirrored)
        self.minx, self.miny = self.pts.min(axis=0)
        self.maxx, self.maxy = self.pts.max(axis=0)
        p = pad + extra
        poly = Polygon(self.pts).buffer(p, quad_segs=4)
        bx0, by0, bx1, by1 = poly.bounds
        self.ref = None
        if item.match_y is not None or item.match_x is not None:
            src = item.match_y[0] if item.match_y is not None else item.match_x[0]
            self.ref = oriented(np.array([src]), angle, mirrored)[0]
            if item.match_x is not None and item.match_y is not None:
                self.ref = np.array([oriented(np.array([item.match_x[0]]), angle, mirrored)[0][0],
                                     oriented(np.array([item.match_y[0]]), angle, mirrored)[0][1]])
        # mask origin: for fold pieces chosen so that column 0 puts the leftmost point on x = 0
        ox = self.minx + cx if item.pinned else bx0 - res
        oy = by0 - res
        self.ox, self.oy = ox, oy
        w = int(math.ceil((bx1 - ox) / res)) + 2
        h = int(math.ceil((by1 - oy) / res)) + 2
        img = Image.new("1", (w, h), 0)
        ext = [((x - ox) / res - 0.5, (y - oy) / res - 0.5) for x, y in poly.exterior.coords]
        ImageDraw.Draw(img).polygon(ext, fill=1)
        m = np.array(img, dtype=np.float32)
        rows = np.flatnonzero(m.any(axis=1))
        cols = np.flatnonzero(m.any(axis=0))
        self.mask = m[: rows[-1] + 1, : cols[-1] + 1]
        self.kern = self.mask[::-1, ::-1].copy()


class Nester:
    def __init__(self, items: list[Item], width: float, gap: float = 5.0, left: float = 10.0,
                 right: float = 10.0, top: float = 10.0, res: float = RES,
                 repeat: tuple | None = None):
        """width: fabric width (or folded width) in mm. left: clearance of normal pieces
        from x = 0 (fold or selvage), right: from x = width, top: from y = 0.
        repeat: (across, along) print repeat in mm for match_x / match_y."""
        self.items, self.width, self.gap = items, float(width), float(gap)
        self.left, self.right, self.top, self.res = left, right, top, res
        self.repeat = repeat
        pad = gap / 2.0 + 0.75 * res
        self.cx = -(pad + 3 * res)               # canvas origin (x of column 0)
        self.cy = 0.0
        self.cols = int(math.ceil((self.width - self.cx) / res)) + 2
        self.shapes = []
        for it in items:
            extra = 0.5 * res if (it.match_x is not None or it.match_y is not None) else 0.0
            self.shapes.append([_Shape(it, a, m, pad, res, self.cx, self.cy, extra) for a, m in it.orients])
        est = sum(max(s.maxx - s.minx, s.maxy - s.miny) + gap for s in (sh[0] for sh in self.shapes))
        rep_y = repeat[1] if repeat else 0.0
        self.rows = int((est + top + rep_y * (len(items) + 1)) / res) + 40
        self.max_mh = max(s.mask.shape[0] for sh in self.shapes for s in sh) if self.shapes else 1
        self.max_mw = max(s.mask.shape[1] for sh in self.shapes for s in sh) if self.shapes else 1
        self._kcache: dict = {}

    # ------------------------------------------------------------------ greedy
    def _overlap(self, s: _Shape, sid, spec, nrows):
        """Overlap count of the shape's mask at every position of the band (valid region)."""
        fshape, B = spec
        key = (sid, fshape)
        K = self._kcache.get(key)
        if K is None:
            K = sfft.rfft2(s.kern, fshape)
            self._kcache[key] = K
        full = sfft.irfft2(B * K, fshape)
        mh, mw = s.mask.shape
        return full[mh - 1:nrows, mw - 1:self.cols]

    def _band_spec(self, occ, band_end):
        nrows = band_end
        fshape = (sfft.next_fast_len(nrows + self.max_mh - 1, real=True),
                  sfft.next_fast_len(self.cols + self.max_mw - 1, real=True))
        return (fshape, sfft.rfft2(occ[:nrows], fshape)), nrows

    def _feasible(self, i, k, s: _Shape, spec, nrows):
        res = self.res
        mh, mw = s.mask.shape
        if mw > self.cols or mh > nrows:
            return None
        ov = self._overlap(s, (i, k), spec, nrows)
        feas = ov < 0.5
        nr, nc = feas.shape
        it = self.items[i]
        # column limits: true outline between left/right clearance (fold pieces: column 0 only)
        x_of_col = self.cx + np.arange(nc) * res - s.ox
        if it.pinned:
            feas[:, 1:] = False
        else:
            feas[:, x_of_col + s.minx < self.left - 1e-6] = False
        feas[:, x_of_col + s.maxx > self.width - self.right + 1e-6] = False
        y_of_row = self.cy + np.arange(nr) * res - s.oy
        feas[y_of_row + s.miny < self.top - 1e-6, :] = False
        if it.match_y is not None and self.repeat:
            rep = self.repeat[1]
            ry = y_of_row + s.ref[1]
            d = (ry - it.match_y[1]) % rep
            d = np.where(d > rep / 2, d - rep, d)
            feas[np.abs(d) > res / 2 + 1e-9, :] = False
        if it.match_x is not None and self.repeat and not it.pinned:
            rep = self.repeat[0]
            rx = x_of_col + s.ref[0]
            d = (rx - it.match_x[1]) % rep
            d = np.where(d > rep / 2, d - rep, d)
            feas[:, np.abs(d) > res / 2 + 1e-9] = False
        return feas, x_of_col, y_of_row

    def greedy(self, order, mode="bottom", force=None):
        """Place the items in `order`. force: per item the index of the orientation to use
        (or -1 = free choice by the score)."""
        res = self.res
        occ = np.zeros((self.rows, self.cols), dtype=np.float32)
        spots, unplaced = [], []
        top_row = 0
        extra = int(self.top / res) + 4 + (int(self.repeat[1] / res) + 2 if self.repeat else 0)
        for i in order:
            best = None
            mh_i = max(s.mask.shape[0] for s in self.shapes[i])
            band_end = min(self.rows, -(-(top_row + mh_i + extra) // 32) * 32)
            spec, nrows = self._band_spec(occ, band_end)
            fk = force[i] if force is not None else -1
            for k, s in enumerate(self.shapes[i]):
                if fk >= 0 and k != fk:
                    continue
                f = self._feasible(i, k, s, spec, nrows)
                if f is None:
                    continue
                feas, xs, ys = f
                if not feas.any():
                    continue
                mh = s.mask.shape[0]
                rr = int(np.argmax(feas.any(axis=1)))        # topmost free row
                cc = int(np.argmax(feas[rr]))                # leftmost free column in it
                if mode == "blf":
                    score = (round(ys[rr] + s.miny, 3), xs[cc] + s.minx)
                else:                                        # lowest bottom edge, then leftmost
                    score = (round(ys[rr] + s.maxy, 3), xs[cc] + s.minx)
                if best is None or score < best[0]:
                    best = (score, k, rr, cc, xs[cc], ys[rr], mh)
            if best is None:
                unplaced.append(i)
                continue
            _, k, rr, cc, dx, dy, mh = best
            s = self.shapes[i][k]
            mh, mw = s.mask.shape
            occ[rr:rr + mh, cc:cc + mw] = np.maximum(occ[rr:rr + mh, cc:cc + mw], s.mask)
            top_row = max(top_row, rr + mh)
            it = self.items[i]
            # exact phase for stripes / plaids (the mask has half a pixel of extra margin)
            if it.match_y is not None and self.repeat:
                dy -= _residual(dy + s.ref[1], it.match_y[1], self.repeat[1])
            if it.match_x is not None and self.repeat and not it.pinned:
                dx -= _residual(dx + s.ref[0], it.match_x[1], self.repeat[0])
            spots.append(Spot(i, s.angle, s.mirrored, float(dx), float(dy)))
        return spots, unplaced, self.used(spots)

    def used(self, spots) -> float:
        u = 0.0
        for sp in spots:
            s = next(x for x in self.shapes[sp.item] if x.angle == sp.angle and x.mirrored == sp.mirrored)
            u = max(u, s.maxy + sp.dy)
        return u

    # ------------------------------------------------------------------ exact compaction
    def compact(self, spots, passes: int = 2):
        """The raster keeps up to ~1.5 pixels more than `gap` between pieces. Slide every
        piece up, then left, with exact geometry until it is exactly `gap` away from its
        neighbours (or a fabric edge / its print phase stops it)."""
        if len(spots) < 1:
            return spots
        polys = {}
        for sp in spots:
            s = next(x for x in self.shapes[sp.item] if x.angle == sp.angle and x.mirrored == sp.mirrored)
            polys[id(sp)] = (s, Polygon(s.pts))
        span = self.gap + 2.0 * self.res

        def ok(sp, dx, dy):
            s, P = polys[id(sp)]
            if s.miny + dy < self.top - 1e-6:
                return False
            it = self.items[sp.item]
            if not it.pinned and s.minx + dx < self.left - 1e-6:
                return False
            moved = None
            for o in spots:
                if o is sp:
                    continue
                so, Po = polys[id(o)]
                # cheap bounding-box test first
                if (s.minx + dx > so.maxx + o.dx + self.gap or so.minx + o.dx > s.maxx + dx + self.gap or
                        s.miny + dy > so.maxy + o.dy + self.gap or so.miny + o.dy > s.maxy + dy + self.gap):
                    continue
                if moved is None:
                    moved = _translate(P, dx, dy)
                if moved.distance(_translate(Po, o.dx, o.dy)) < self.gap - 1e-6:
                    return False
            return True

        for _ in range(passes):
            for sp in sorted(spots, key=lambda q: q.dy):
                it = self.items[sp.item]
                axes = []
                if it.match_y is None or not self.repeat:
                    axes.append((0.0, -1.0))
                if not it.pinned and (it.match_x is None or not self.repeat):
                    axes.append((-1.0, 0.0))
                for ax, ay in axes:
                    lo, hi = 0.0, span
                    if ok(sp, sp.dx + ax * hi, sp.dy + ay * hi):
                        lo = hi
                    else:
                        for _k in range(7):
                            mid = (lo + hi) / 2
                            if ok(sp, sp.dx + ax * mid, sp.dy + ay * mid):
                                lo = mid
                            else:
                                hi = mid
                    sp.dx += ax * lo
                    sp.dy += ay * lo
        return spots

    # ------------------------------------------------------------------ search
    def _score(self, result):
        spots, unplaced, used = result
        # second criterion: pieces packed high up leave a usable remnant at the end
        tail = sum(sp.dy for sp in spots) / max(len(spots), 1)
        return (len(unplaced), round(used / self.res), tail)

    def solve(self, evals: int = SEARCH_EVALS, seed: int = 7, seeds=(), local_only=False):
        """Search over (order of the pieces, orientation of each piece, strategy).

        Fixed heuristic orders first, then seeded random restarts, then a local search on
        the best solution (move a piece forward, swap neighbours, turn a piece round)."""
        n = len(self.items)
        if n == 0:
            return [], [], 0.0
        area = [Polygon(it.ring).area for it in self.items]
        h0 = [s[0].maxy - s[0].miny for s in self.shapes]
        w0 = [min(x.maxx - x.minx for x in s) for s in self.shapes]
        pin = [not it.pinned for it in self.items]
        free = tuple([-1] * n)
        no = [len(sh) for sh in self.shapes]
        orders = [
            sorted(range(n), key=lambda i: (pin[i], -area[i])),
            sorted(range(n), key=lambda i: (pin[i], -h0[i])),
            sorted(range(n), key=lambda i: (pin[i], -w0[i])),
            sorted(range(n), key=lambda i: -area[i]),
        ]
        cache: dict = {}
        budget = max(evals, 8)

        def run(order, mode, force):
            key = (tuple(order), mode, tuple(force))
            if key not in cache:
                cache[key] = self.greedy(order, mode, force)
            return cache[key]

        def chosen(r):
            """Orientation index each item got (to continue from a free run)."""
            f = [-1] * n
            for sp in r[0]:
                f[sp.item] = next(k for k, x in enumerate(self.shapes[sp.item])
                                  if x.angle == sp.angle and x.mirrored == sp.mirrored)
            return tuple(f)

        best = None

        def consider(order, mode, force):
            nonlocal best
            r = run(order, mode, force)
            sc = self._score(r)
            if best is None or sc < best[0]:
                best = (sc, list(order), mode, chosen(r), r)
                return True
            return False

        for order, mode, force in seeds:
            consider(list(order), mode, force)
        rng = random.Random(seed)
        if not local_only:
            for order in orders:
                for mode in ("bottom", "blf"):
                    consider(order, mode, free)
        n_random = max(0, (budget - len(cache)) // 3) if n > 1 and not local_only else 0
        for _ in range(n_random):
            order = sorted(range(n), key=lambda i: (pin[i] if rng.random() < 0.5 else 0,
                                                    -area[i] * rng.uniform(0.6, 1.4)))
            force = tuple(rng.randrange(no[i]) if no[i] > 1 and rng.random() < 0.5 else -1 for i in range(n))
            consider(order, best[2], force)
        # local search on the best solution
        improved = True
        while improved and len(cache) < budget:
            improved = False
            o, mode, f = best[1], best[2], best[3]
            cand = []
            for i in range(n):
                for k in range(no[i]):
                    if k != f[i]:
                        g = list(f)
                        g[i] = k
                        cand.append((o, tuple(g)))
            for a in range(n):
                for b in range(a):
                    cand.append((o[:b] + [o[a]] + o[b:a] + o[a + 1:], f))
            for a in range(n - 1):
                m = list(o)
                m[a], m[a + 1] = m[a + 1], m[a]
                cand.append((m, f))
            rng.shuffle(cand)
            for m, g in cand:
                if len(cache) >= budget:
                    break
                if (tuple(m), mode, tuple(g)) in cache:
                    continue
                if consider(m, mode, g):
                    improved = True
                    break
        ranked = sorted(cache.items(), key=lambda kv: self._score(kv[1]))
        self.ranking = [(list(k[0]), k[1], chosen(v)) for k, v in ranked]
        return best[4]


def nest(items: list[Item], width: float, evals: int = SEARCH_EVALS, **kw):
    """Coarse-to-fine search: explore orders/orientations on a 5 mm raster (fast), then
    re-run the best candidates and a short local search on the fine raster."""
    coarse = Nester(items, width, res=5.0, **kw)
    coarse.solve(evals=evals)
    fine = Nester(items, width, res=RES, **kw)
    top = coarse.ranking[:FINE_CANDIDATES]
    spots, unplaced, _ = fine.solve(evals=len(top) + FINE_LOCAL, seeds=top, local_only=True)
    spots = fine.compact(spots)
    return spots, unplaced, fine.used(spots)


def _translate(poly, dx, dy):
    from shapely import affinity
    return affinity.translate(poly, dx, dy)


def min_distance(rings_placed) -> float:
    """Smallest distance between any two placed outlines (canvas coordinates)."""
    polys = [Polygon(r) for r in rings_placed]
    d = math.inf
    for i in range(len(polys)):
        for j in range(i + 1, len(polys)):
            d = min(d, polys[i].distance(polys[j]))
    return d
