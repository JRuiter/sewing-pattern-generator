"""Step diagrams for the illustrated sewing instructions.

Every :class:`steps.Step` is drawn from the real pattern geometry, so the pictures are
right for every size and option:

* ``seam``      the two pieces right sides together (bottom piece right side up, shaded;
                top piece wrong side up, white), aligned on the seam, with pins across the
                seam, the stitch line on the seam line, the notches and the sewing direction.
                Seams that join several edges (sleeve into armhole, waistband to top edge)
                are drawn as "this edge goes to that edge": pieces side by side, matching
                edges in the same colour, arrows from one to the other.
* ``ring``      a band folded crosswise right sides together, the short ends sewn
* ``fold``      a band folded lengthwise wrong sides together
* ``quarter``   band and opening divided into quarters with pins
* ``attach``    the band ring pulled over the opening, stretched while sewing
* ``hem`` / ``press`` / ``topstitch`` / ``edge``   a piece with the worked edge, the fold
                and the stitch line at the given distance, plus a cross-section detail
* ``gather``    two gathering rows along an edge, threads pulled
* ``place``     a pocket placed on its placement mark and stitched on
* ``icon``      a pictogram (wash, cut, snip notches, turn, thread elastic, done …)

Pieces carry their part letter (A, B, C …) from the parts overview. All drawing functions
draw into a matplotlib ``Axes``; the booklet (``booklet.py``) puts them into its panels,
``render_steps`` writes one PNG per step for the Markdown instructions.
"""
from __future__ import annotations

import math
import os

import numpy as np

import geometry as G
import steps as S
from i18n import t as T

RIGHT_SIDE = "#f1d39b"          # right side of the fabric
RIGHT_EDGE = "#8a6d3b"
WRONG_SIDE = "#ffffff"          # wrong side
HATCH = "#c9c9c9"
INK = "#222222"
STITCH = "#c62828"              # stitch line
ACCENT = ["#c62828", "#1565c0", "#2e7d32", "#6a1b9a"]
PIN = "#607d8b"
PIN_HEAD = "#1565c0"


# --------------------------------------------------------------------------- helpers

def letters(pattern) -> dict[str, str]:
    """Part letters A, B, C … in the order of the pattern pieces."""
    out = {}
    for i, pc in enumerate(pattern.pieces):
        out[pc.key] = chr(ord("A") + i) if i < 26 else f"A{chr(ord('A') + i - 26)}"
    return out


def _resample(pts, n=48):
    pts = np.asarray(pts, float)
    L = G.length(pts)
    return np.array([G.point_at(pts, s) for s in np.linspace(0, L, n)])


def _outline(pc, cut=True) -> np.ndarray:
    """The outline to draw: the cutting line when the pattern has allowances."""
    if cut and any(e.sa > 0 for e in pc.edges):
        try:
            r = np.asarray(pc.cut_ring(), float)
            if len(r) > 3:
                return r
        except Exception:  # pragma: no cover - fall back to the seam line
            pass
    return np.asarray(pc.seam_ring(), float)


def _unfolded(pc, ring: np.ndarray) -> np.ndarray:
    """A piece cut on the fold, opened out (both halves)."""
    folds = [e for e in pc.edges if e.fold]
    if not folds:
        return ring
    try:
        from shapely.geometry import Polygon
        e = folds[0]
        a, b = e.pts[0], e.pts[-1]
        poly = Polygon(ring).buffer(0)
        mir = Polygon(G.mirror_line(ring, a, b)).buffer(0)
        u = poly.union(mir.buffer(0.01)).buffer(-0.005)
        if u.geom_type == "MultiPolygon":
            u = max(u.geoms, key=lambda g: g.area)
        return np.asarray(u.exterior.coords, float)
    except Exception:  # pragma: no cover
        return ring


def _apply(T, pts):
    R, t, flip = T
    p = np.atleast_2d(np.asarray(pts, float)).copy()
    if flip:
        p[:, 0] = -p[:, 0]
    return p @ R.T + t


ID = (np.eye(2), np.zeros(2), False)


def _fit(src, dst):
    """Rotation + translation that maps src onto dst (corresponding points, Kabsch)."""
    cs, cd = src.mean(0), dst.mean(0)
    H = (src - cs).T @ (dst - cd)
    U, _s, Vt = np.linalg.svd(H)
    d = np.sign(np.linalg.det(Vt.T @ U.T)) or 1.0
    R = Vt.T @ np.diag([1.0, d]) @ U.T
    t = cd - cs @ R.T
    rms = float(np.sqrt(((src @ R.T + t - dst) ** 2).sum(1).mean()))
    return R, t, rms


def _inward(edge):
    """Unit normals pointing into a CCW piece (left of the direction of travel)."""
    return -G.normals_right(edge)


def _coincide(a, b) -> bool:
    from shapely.geometry import Polygon
    pa, pb = Polygon(a).buffer(0), Polygon(b).buffer(0)
    return pa.symmetric_difference(pb).area < 0.15 * max(pa.area, 1e-9)


def _piece_label(ax, pattern, pc, ring, T=ID, text=None, size=8.0, avoid=None):
    from shapely.geometry import Polygon
    pts = _apply(T, ring)
    try:
        poly = Polygon(pts).buffer(0)
        if avoid is not None:
            rest = poly.difference(Polygon(avoid).buffer(0))
            if rest.area > 0.04 * poly.area:
                if rest.geom_type == "MultiPolygon":
                    rest = max(rest.geoms, key=lambda g: g.area)
                poly = rest
        c = np.asarray(poly.representative_point().coords[0])
    except Exception:  # pragma: no cover
        c = pts.mean(0)
    let = letters(pattern).get(pc.key, "")
    ax.text(c[0], c[1], let, ha="center", va="center", fontsize=size, fontweight="bold", color=INK,
            zorder=9, bbox=dict(boxstyle="circle,pad=0.25", fc="white", ec=INK, lw=0.9))
    if text:
        ax.annotate(text, (c[0], c[1]), xytext=(0, -size * 1.6), textcoords="offset points",
                    ha="center", va="top", fontsize=size * 0.72, color="#555", zorder=9)


# Colour language (legend in the booklet): the fabric decides the colour, right and wrong side differ.
# (right side, wrong side, texture of the right side)
PALETTES = {
    "main": (RIGHT_SIDE, WRONG_SIDE, ""),
    "corduroy": ("#9c7656", "#efe3cf", "wale"),
    "velvet": ("#7e5a86", "#efe6f0", "pile"),
    "lining": ("#90caf9", "#e3f2fd", ""),
    "rib": ("#a5d6a7", "#eef7ee", "rib"),
}
HAND_STITCH = (0, (0.6, 1.8))       # red dotted: by hand
DONE_STITCH = "#9e9e9e"             # grey dashed: already sewn
FOLD_LINE = (0, (6, 2, 1, 2))       # blue dash-dot: fold / press line
_CTX: dict = {"pattern": None, "hand": False}


def palette_key(pc=None, pattern=None) -> str:
    """Which colour a piece gets: rib, lining (pocket bag fabric) or the main fabric."""
    pattern = pattern if pattern is not None else _CTX["pattern"]
    fab = (getattr(pc, "fabric_key", None) or getattr(pc, "fabric", "") or "").lower() if pc is not None else ""
    if "rib" in fab:
        return "rib"
    if fab.startswith("lining"):
        return "lining"
    main = (pattern.options.get("fabric", "") if pattern is not None and isinstance(pattern.options, dict)
            else "")
    return main if main in PALETTES else "main"


def palette(pc=None, pattern=None) -> tuple[str, str, str]:
    return PALETTES[palette_key(pc, pattern)]


def _fill(ax, pts, wrong=False, z=1, alpha=1.0, lw=1.1, pc=None):
    right, back, texture = palette(pc)
    if wrong:
        ax.fill(pts[:, 0], pts[:, 1], fc=back, ec=INK, lw=lw, zorder=z, alpha=alpha,
                hatch="////", **_hatch_kw())
        ax.fill(pts[:, 0], pts[:, 1], fc="none", ec=INK, lw=lw, zorder=z + 0.1)
    else:
        ax.fill(pts[:, 0], pts[:, 1], fc=right, ec=INK, lw=lw, zorder=z, alpha=alpha)
        if texture:                  # wales / pile / rib ribs along the grain
            ax.fill(pts[:, 0], pts[:, 1], fc="none", ec="none", zorder=z + 0.05,
                    hatch={"wale": "||", "pile": "...", "rib": "||"}[texture], **_hatch_kw())


def _hatch_kw():
    import matplotlib
    matplotlib.rcParams["hatch.color"] = HATCH
    matplotlib.rcParams["hatch.linewidth"] = 0.5
    return {}


def _stitch(ax, pts, z=6, lw=1.6, color=STITCH, hand=None):
    """Stitch line: red solid = sew now on a machine, red dotted = by hand."""
    pts = np.asarray(pts, float)
    hand = _CTX["hand"] if hand is None else hand
    ax.plot(pts[:, 0], pts[:, 1], color=color, lw=lw * (1.25 if hand else 1.0), ls=HAND_STITCH if hand else "-",
            zorder=z, solid_capstyle="butt", dash_capstyle="round")


def _arrow(ax, p0, p1, z=8, color=INK, lw=1.4, head=None, rad=0.0):
    from matplotlib.patches import FancyArrowPatch
    head = head or 9
    ax.add_patch(FancyArrowPatch(tuple(p0), tuple(p1), arrowstyle=f"-|>,head_length={head / 18:.2f},"
                                 f"head_width={head / 30:.2f}", mutation_scale=12, color=color, lw=lw,
                                 zorder=z, connectionstyle=f"arc3,rad={rad}", shrinkA=0, shrinkB=0))


def _pins(ax, edge_pts, size, count=None, inward=True, z=7):
    """Pins across a seam: shaft from inside the piece to beyond the raw edge, head outside."""
    e = np.asarray(edge_pts, float)
    L = G.length(e)
    n = count or int(np.clip(round(L / (size * 0.16)), 2, 6))
    nrm = _inward(e)
    for s in np.linspace(L / (n + 1), L * n / (n + 1), n):
        i = int(np.argmin(np.abs(G.cumlen(e) - s)))
        p = G.point_at(e, s)
        nv = nrm[i] * (1 if inward else -1)
        a = p + nv * size * 0.045
        b = p - nv * size * 0.03
        ax.plot([a[0], b[0]], [a[1], b[1]], color=PIN, lw=1.1, zorder=z, solid_capstyle="round")
        ax.plot([b[0]], [b[1]], "o", ms=3.6, color=PIN_HEAD, zorder=z + 0.1)


def _notches(ax, pc, edge_name, T, size, z=7):
    e = pc.edge(edge_name)
    L = e.length
    for n in pc.notches:
        if n.edge != edge_name:
            continue
        s = n.s if n.s >= 0 else L + n.s
        if not 0 <= s <= L:
            continue
        p = G.point_at(e.pts, s)
        t = G.tangent_at(e.pts, s)
        nv = np.array([t[1], -t[0]])                     # outward (right of travel)
        for k in range(n.count):
            dd = t * size * 0.014 * (k - (n.count - 1) / 2)
            seg = np.array([p + dd - nv * size * 0.012, p + dd + nv * (e.sa + size * 0.02)])
            q = _apply(T, seg)
            ax.plot(q[:, 0], q[:, 1], color=INK, lw=1.3, zorder=z)


def _direction(ax, edge_pts, size, offset, z=8):
    """Sewing direction: an arrow beside the seam, outside the piece."""
    e = np.asarray(edge_pts, float)
    L = G.length(e)
    s0, s1 = L * 0.3, L * 0.7
    nrm = -_inward(e)
    i0 = int(np.argmin(np.abs(G.cumlen(e) - s0)))
    i1 = int(np.argmin(np.abs(G.cumlen(e) - s1)))
    p0 = G.point_at(e, s0) + nrm[i0] * offset
    p1 = G.point_at(e, s1) + nrm[i1] * offset
    _arrow(ax, p0, p1, z=z, color=STITCH, lw=1.6)


def _finish_axes(ax, pts_list, pad=0.08):
    allp = np.vstack([np.atleast_2d(p) for p in pts_list if len(np.atleast_2d(p))])
    x0, y0 = allp.min(0)
    x1, y1 = allp.max(0)
    w, h = max(x1 - x0, 1), max(y1 - y0, 1)
    p = pad * max(w, h)
    ax.set_xlim(x0 - p, x1 + p)
    ax.set_ylim(y0 - p, y1 + p)
    ax.set_aspect("equal")
    ax.axis("off")


def _dim(ax, a, b, text, size, z=9, side=1.0):
    """Dimension arrow a↔b with a label."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    from matplotlib.patches import FancyArrowPatch
    ax.add_patch(FancyArrowPatch(tuple(a), tuple(b), arrowstyle="<|-|>,head_length=0.35,head_width=0.18",
                                 mutation_scale=10, color=INK, lw=0.9, zorder=z, shrinkA=0, shrinkB=0))
    m = (a + b) / 2
    d = G.unit(b - a)
    nv = np.array([-d[1], d[0]]) * side
    ax.text(*(m + nv * size * 0.04), T(text), fontsize=7.5, ha="center", va="center", zorder=z,
            bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none"))


# --------------------------------------------------------------------------- seam

def _main_edges(sm):
    """The longest edge on each side of a seam: what the overlay aligns."""
    def longest(side, pattern):
        return max(side, key=lambda x: pattern.piece(x[0]).edge(x[1]).length)
    return longest


OVERLAY_MAX_RMS = 0.008     # stacked picture only when the two edges really lie on each other


def overlay_parts(pattern, sm):
    """Transforms that put piece b (wrong side up) onto piece a along the seam.

    Returns (pc_a, edge_a, pc_b, edge_b, T_b) or None when the seam is not a simple
    edge-to-edge seam (several edges, stretched/gathered)."""
    if sm.get("type") not in (None, "equal", "ease"):
        return None
    pick = _main_edges(sm)
    pa, ea, _ = pick(sm["a"], pattern)
    pb, eb, _ = pick(sm["b"], pattern)
    A, B = pattern.piece(pa), pattern.piece(pb)
    EA, EB = A.edge(ea).pts, B.edge(eb).pts
    if not 0.75 < G.length(EA) / max(G.length(EB), 1e-6) < 1.33:
        return None
    from shapely.geometry import Polygon
    dst = _resample(EA)
    poly_a = Polygon(A.seam_ring()).buffer(0)
    results = {}
    for flip in (True, False):
        src = _resample(EB) * (np.array([-1.0, 1.0]) if flip else 1.0)
        ring_b = np.asarray(B.seam_ring(), float) * (np.array([-1.0, 1.0]) if flip else 1.0)
        best = None
        for cand in (src, src[::-1]):
            R, t, rms = _fit(cand, dst)
            poly_b = Polygon(ring_b @ R.T + t).buffer(0)
            share = poly_a.intersection(poly_b).area / max(min(poly_a.area, poly_b.area), 1e-9)
            score = rms + (0 if share > 0.3 else 1e6)        # stacked pieces overlap
            if best is None or score < best[0]:
                best = (score, R, t)
        results[flip] = best
    # pieces lie right sides together: the top one is turned over (mirrored) unless it is the
    # other piece of a mirrored pair (same edge) or clearly fits only unmirrored (pocket bags)
    same = pa == pb and ea == eb
    flip = not same
    if not same and results[False][0] < 0.5 * results[True][0]:
        flip = False
    score, R, t = results[flip]
    if score > OVERLAY_MAX_RMS * G.length(EA):     # edges of different shape: they would lie skewed
        return None
    return A, ea, B, eb, (R, t, flip)


def draw_seam(ax, pattern, step, sms=None):
    """All seams of a step: overlays side by side, or a join diagram."""
    sms = sms if sms is not None else S.resolve_seams(pattern, step)
    if not sms:
        return draw_icon(ax, pattern, step)
    simple = [overlay_parts(pattern, sm) for sm in sms]
    if all(simple) and len(sms) <= 3:
        _draw_overlays(ax, pattern, step, sms, simple)
    elif (len(sms) == 1 and len(sms[0]["a"]) <= 2 and len(sms[0]["b"]) <= 2
          and not {p for p, _e, _n in sms[0]["a"]} & {p for p, _e, _n in sms[0]["b"]}):
        draw_pair(ax, pattern, step, sms[0])
    else:
        draw_join(ax, pattern, step, sms)


def _continuations(pattern, main_pc, main_edge, others):
    """Pieces already sewn to the main piece whose edge continues the seam (a side panel above
    the side seam): placed so that their edge carries on from one end of the main edge.
    Returns [(piece, ring, edge)] in the main piece's coordinates."""
    from shapely.geometry import Polygon
    hull = Polygon(_outline(main_pc)).convex_hull
    out = []
    for p, e, _n in others:
        pc = pattern.piece(p)
        src = pc.edge(e).pts
        L = G.length(src)
        ring = _outline(pc)
        best = None
        for end, nxt in ((main_edge[-1], main_edge[-2]), (main_edge[0], main_edge[1])):
            d = (end - nxt) / max(np.hypot(*(end - nxt)), 1e-9)
            dst = np.array([end, end + d * L])
            for flip in (False, True):
                sp = src * (np.array([-1.0, 1.0]) if flip else 1.0)
                rp = ring * (np.array([-1.0, 1.0]) if flip else 1.0)
                for cand in (sp, sp[::-1]):
                    R, t, _ = _fit(np.array([cand[0], cand[-1]]), dst)
                    poly = Polygon(rp @ R.T + t).buffer(0)
                    score = poly.intersection(hull).area / max(poly.area, 1e-9)
                    if best is None or score > best[0]:
                        best = (score, rp @ R.T + t, cand @ R.T + t)
        out.append((pc, best[1], best[2]))
    return out


def draw_pair(ax, pattern, step, sm):
    """Two pieces side by side, right side up, the seam edges facing each other and marked red,
    with "right sides together" between them (edges of different shape: side seams, inseams,
    sleeve into armhole), as in a printed booklet."""
    pick = _main_edges(sm)
    pa, ea, _n1 = pick(sm["a"], pattern)
    pb, eb, _n2 = pick(sm["b"], pattern)
    A, B = pattern.piece(pa), pattern.piece(pb)
    ra, rb = _unfolded(A, _outline(A)), _unfolded(B, _outline(B))
    EA, EB = A.edge(ea).pts, B.edge(eb).pts
    extra_a = _continuations(pattern, A, EA, [x for x in sm["a"] if x[0] != pa])
    extra_b = _continuations(pattern, B, EB, [x for x in sm["b"] if x[0] != pb])
    size = max(np.ptp(ra, 0).max(), np.ptp(rb, 0).max())
    gap = size * 0.16
    a_right = EA[:, 0].mean() > ra[:, 0].mean()
    b_left = EB[:, 0].mean() < rb[:, 0].mean()
    flip = b_left != a_right
    Tb0 = (np.eye(2), np.zeros(2), flip)
    eb0, rb0 = _apply(Tb0, EB), _apply(Tb0, rb)
    ea_all = np.vstack([EA] + [e for _p, _r, e in extra_a])
    dy = ea_all[:, 1].max() - eb0[:, 1].max()
    dx = (EA[:, 0].max() + gap - eb0[:, 0].min()) if a_right else (EA[:, 0].min() - gap - eb0[:, 0].max())
    Tb = (np.eye(2), np.array([dx, dy]), flip)
    rb2, eb2 = rb0 + [dx, dy], eb0 + [dx, dy]
    for pc, ring, edge in extra_a:
        _fill(ax, ring, z=0.9, pc=pc)
        ax.plot(edge[:, 0], edge[:, 1], color=STITCH, lw=2.6, zorder=6, solid_capstyle="round")
    for pc, ring, edge in extra_b:
        ring, edge = _apply(Tb, ring), _apply(Tb, edge)
        _fill(ax, ring, z=0.9, pc=pc)
        ax.plot(edge[:, 0], edge[:, 1], color=STITCH, lw=2.6, zorder=6, solid_capstyle="round")
    _fill(ax, ra, z=1, pc=A)
    _fill(ax, rb2, z=1, pc=B)
    for e in (EA, eb2):
        ax.plot(e[:, 0], e[:, 1], color=STITCH, lw=2.6, zorder=6, solid_capstyle="round")
    _notches(ax, A, ea, ID, size)
    _notches(ax, B, eb, Tb, size)
    _piece_label(ax, pattern, A, ra, ID, size=8)
    _piece_label(ax, pattern, B, rb, Tb, size=8)
    ma = G.point_at(EA, G.length(EA) * 0.5)
    mb = G.point_at(eb2, G.length(eb2) * 0.5)
    _arrow(ax, mb, ma, color=INK, lw=1.3, rad=-0.5 if a_right else 0.5)
    top = max(ra[:, 1].max(), rb2[:, 1].max(), *[r[:, 1].max() for _p, r, _e in extra_a])
    ax.text((EA[:, 0].mean() + eb2[:, 0].mean()) / 2, top + size * 0.03, T("right sides together"),
            ha="center", va="bottom", fontsize=7.5, fontweight="bold", color=INK, zorder=9)
    _finish_axes(ax, [ra, rb2, np.array([[ma[0], top + size * 0.09]])] + [r for _p, r, _e in extra_a]
                 + [_apply(Tb, r) for _p, r, _e in extra_b], pad=0.05)


def _draw_overlays(ax, pattern, step, sms, parts):
    allpts = []
    xoff = 0.0
    size = max(max(np.ptp(_outline(p[0]), 0).max(), np.ptp(_outline(p[2]), 0).max()) for p in parts)
    seen = set()
    for _sm, (A, ea, B, eb, Tb) in zip(sms, parts):
        if (A.key, B.key) in seen:            # same two pieces again: one picture is enough
            continue
        seen.add((A.key, B.key))
        ring_a = _unfolded(A, _outline(A))
        ring_b = _apply(Tb, _unfolded(B, _outline(B)))
        bb = np.vstack([ring_a, ring_b])
        sh = np.array([xoff - bb[:, 0].min(), -bb[:, 1].min()])
        Ta = (np.eye(2), sh, False)
        Tb2 = (Tb[0], Tb[1] + sh, Tb[2])
        ra = ring_a + sh
        rb = ring_b + sh
        if _coincide(ra, rb):                     # identical pieces: show the lower layer
            ra = ra + np.array([size * 0.015, -size * 0.02])
        _fill(ax, ra, wrong=False, z=1, pc=A)
        _fill(ax, rb, wrong=True, z=2, alpha=0.93, pc=B)
        edge = A.edge(ea).pts + sh
        moved = _resample(_apply(Tb2, B.edge(eb).pts))
        dev = min(np.abs(moved - _resample(edge)).max(), np.abs(moved[::-1] - _resample(edge)).max())
        import booklet_qa as QA
        QA.check_overlay(step.title, dev / max(A.edge(ea).length, 1e-9), 0.06)
        _stitch(ax, edge)
        _pins(ax, edge, size)
        _notches(ax, A, ea, Ta, size)
        _notches(ax, B, eb, Tb2, size)
        _direction(ax, edge, size, offset=A.edge(ea).sa + size * 0.06)
        _piece_label(ax, pattern, B, _unfolded(B, _outline(B)), Tb2, size=8)
        _piece_label(ax, pattern, A, _unfolded(A, _outline(A)), Ta, size=8, avoid=rb)
        if len(sms) == 1:
            allpts += [_zoom_view(np.vstack([ra, rb]), [edge], size)]
        else:
            allpts += [ra, rb]
        xoff = max(ra[:, 0].max(), rb[:, 0].max()) + size * 0.25
    _finish_axes(ax, allpts)


def draw_join(ax, pattern, step, sms):
    """Pieces side by side; matching edges in one colour, arrows from b to a."""
    keys: list[str] = []
    for sm in sms:
        for p, _e, _n in sm["a"] + sm["b"]:
            if p not in keys:
                keys.append(p)
    rings = [_outline(pattern.piece(k)) for k in keys]
    size = max(max(np.ptp(r, 0)) for r in rings)
    gap = size * 0.18
    # shelf layout: target pieces in the first row, the joined piece(s) below
    b_keys = {p for sm in sms for p, _e, _n in sm["b"]}
    a_first = [k for k in keys if k not in b_keys] + [k for k in keys if k in b_keys]
    offs = {}
    x, y_row, row_h, row_w = 0.0, 0.0, 0.0, 0.0
    max_w = max(2.6 * size, sum(np.ptp(r[:, 0]) for r in rings) * 0.6)
    for k in a_first:
        r = rings[keys.index(k)]
        w, h = np.ptp(r[:, 0]), np.ptp(r[:, 1])
        if x > 0 and (x + w > max_w or (k in b_keys and not any(kk in b_keys for kk in offs))):
            x, y_row = 0.0, y_row - row_h - gap
            row_h = 0.0
        offs[k] = np.array([x - r[:, 0].min(), y_row - h - r[:, 1].min()])
        x += w + gap
        row_h = max(row_h, h)
        row_w = max(row_w, x)
    allpts = []
    for k in keys:
        pc = pattern.piece(k)
        T = (np.eye(2), offs[k], False)
        r = rings[keys.index(k)] + offs[k]
        _fill(ax, r, wrong=False, z=1, pc=pc)
        _piece_label(ax, pattern, pc, rings[keys.index(k)], T, size=8)
        allpts.append(r)
    for i, sm in enumerate(sms):
        col = ACCENT[i % len(ACCENT)]
        mids = {}
        for side in ("a", "b"):
            for p, e, _n in sm[side]:
                pc = pattern.piece(p)
                pts = pc.edge(e).pts + offs[p]
                ax.plot(pts[:, 0], pts[:, 1], color=col, lw=3.0, zorder=4, solid_capstyle="round",
                        ls="-" if side == "a" else (0, (4, 1.5)))
                _notches(ax, pc, e, (np.eye(2), offs[p], False), size)
                mids.setdefault(side, []).append(G.point_at(pts, G.length(pts) / 2))
        if "a" in mids and "b" in mids:
            for j, mb in enumerate(mids["b"]):
                ma = mids["a"][min(j, len(mids["a"]) - 1)] if len(mids["b"]) > 1 else \
                    np.mean(mids["a"], axis=0)
                _arrow(ax, mb, ma, color=col, lw=1.4, rad=0.25)
    _finish_axes(ax, allpts)


# --------------------------------------------------------------------------- bands

def _band_dims(pc):
    """(length, height) of a rectangular band, opened out if cut on the fold."""
    r = _unfolded(pc, np.asarray(pc.seam_ring(), float))
    w, h = np.ptp(r[:, 0]), np.ptp(r[:, 1])
    return max(w, h), min(w, h)


def draw_ring(ax, pattern, step):
    pc = pattern.piece(step.pieces[0])
    L, H = _band_dims(pc)
    half = L / 2
    sa = max(e.sa for e in pc.edges) or 7.0
    # bottom layer right side up, top layer folded over: wrong side visible
    bot = np.array([[0, 0], [half, 0], [half, H], [0, H]], float)
    top = bot + np.array([0.0, 0.0])
    _fill(ax, bot + [half * 0.03, -H * 0.06], wrong=False, z=1, pc=pc)
    _fill(ax, top, wrong=True, z=2, pc=pc)
    # fold at the left, short raw ends at the right: stitch there
    _stitch(ax, [[half - sa, -H * 0.06], [half - sa, H]])
    _pins(ax, np.array([[half, 0.0], [half, H]]), max(half, H) * 0.9, count=2, inward=True)
    ax.plot([0, 0], [0, H], color=INK, lw=2.2, zorder=5)
    ax.text(-half * 0.03, H / 2, T("fold"), rotation=90, ha="right", va="center", fontsize=7, color="#555")
    _arrow(ax, [half * 0.8, H * 1.45], [half * 0.2, H * 1.45], rad=0.35)
    pc_lab = (np.eye(2), np.zeros(2), False)
    _piece_label(ax, pattern, pc, top, pc_lab, size=8)
    _finish_axes(ax, [bot - [0, H * 0.1], top + [0, H * 1.8], [[-half * 0.12, 0]]], pad=0.06)


def draw_fold(ax, pattern, step):
    pc = pattern.piece(step.pieces[0])
    L, H = _band_dims(pc)
    w = min(L, H * 6)                       # a section of the band
    flat = np.array([[0, 0], [w, 0], [w, H], [0, H]], float)
    _fill(ax, flat, wrong=True, z=1, pc=pc)
    ax.plot([0, w], [H / 2, H / 2], color=ACCENT[1], lw=1.2, ls=FOLD_LINE, zorder=3)
    ax.text(w * 1.02, H / 2, T("fold line"), fontsize=7, va="center", color="#555")
    _arrow(ax, [w * 0.5, H * 0.95], [w * 0.5, H * 0.05], rad=-0.5)
    # result: folded band, right side outside
    res = np.array([[0, 0], [w, 0], [w, H / 2], [0, H / 2]], float) + [0, -H * 1.1]
    _fill(ax, res, wrong=False, z=1, pc=pc)
    ax.plot([0, w], [res[2, 1], res[2, 1]], color=INK, lw=2.0, zorder=3)
    ax.text(w * 1.02, res[2, 1], T("fold"), fontsize=7, va="center", color="#555")
    ax.text(w * 1.02, res[0, 1], T("raw edges"), fontsize=7, va="center", color="#555")
    _piece_label(ax, pattern, pc, flat, ID, size=8)
    _finish_axes(ax, [flat, res, [[w * 1.35, 0]]], pad=0.06)


def _cylinder(ax, y0, y1, rx, ry, fc=RIGHT_SIDE, z=1.0, open_top=True, lw=1.2):
    """A fabric tube seen slightly from above: body from y0 to y1, open at the top."""
    from matplotlib.patches import Arc, Ellipse
    from matplotlib.patches import Polygon as Poly
    th = np.linspace(np.pi, 2 * np.pi, 40)
    front_bot = np.c_[rx * np.cos(th), y0 + ry * np.sin(th)]
    front_top = np.c_[rx * np.cos(th), y1 + ry * np.sin(th)][::-1]
    ax.add_patch(Poly(np.vstack([front_bot, front_top]), closed=True, fc=fc, ec="none", zorder=z))
    ax.plot(front_bot[:, 0], front_bot[:, 1], color=INK, lw=lw, zorder=z + 0.05)
    ax.plot([-rx, -rx], [y0, y1], color=INK, lw=lw, zorder=z + 0.05)
    ax.plot([rx, rx], [y0, y1], color=INK, lw=lw, zorder=z + 0.05)
    if open_top:
        ax.add_patch(Ellipse((0, y1), 2 * rx, 2 * ry, fc="#fbf3e4", ec=INK, lw=lw, zorder=z + 0.1))
        ax.add_patch(Arc((0, y1), 2 * rx, 2 * ry, theta1=180, theta2=360, color=INK, lw=lw, zorder=z + 0.2))


def _quarter_pins(ax, cy, rx, ry, z, labels=("", "", "", ""), label_dy=0.0):
    for k, ang in enumerate((-90, 0, 90, 180)):
        a = math.radians(ang)
        x, y = rx * math.cos(a), cy + ry * math.sin(a)
        if ang == 90:
            z_ = z - 0.5
        else:
            z_ = z + 1
        ax.plot([x, x], [y - 0.1, y + 0.06], color=PIN, lw=1.3, zorder=z_)
        ax.plot([x], [y + 0.08], "o", ms=4.2, color=PIN_HEAD, zorder=z_ + 0.1)
        if labels[k]:
            dx = {0: 0.0, 1: 0.2, 2: 0.0, 3: -0.2}[k]
            dy = {0: -0.2, 1: 0.0, 2: 0.2, 3: 0.0}[k]
            ax.text(x + dx, y + dy + label_dy, T(labels[k]), fontsize=6.5, ha="center", va="center",
                    color="#444", zorder=z + 2)


QUARTER_LABELS = {
    "waist": ("CF", "side", "CB", "side"), "neck": ("CF", "shoulder", "CB", "shoulder"),
    "hem": ("CF", "side", "CB", "side"),
}


def draw_quarter(ax, pattern, step):
    band = pattern.piece(step.pieces[0])
    target = step.data.get("target", "opening")
    labs = QUARTER_LABELS.get(step.data.get("quarters", ""), ("", "", "", ""))
    _cylinder(ax, 1.15, 1.45, 0.7, 0.2, z=4)                       # folded band ring
    _cylinder(ax, -0.9, 0.0, 1.0, 0.3, z=1)                        # garment opening
    _quarter_pins(ax, 1.45, 0.7, 0.2, 5)
    _quarter_pins(ax, 0.0, 1.0, 0.3, 2, labs)
    ax.text(0.85, 1.35, letters(pattern)[band.key], fontsize=8, fontweight="bold", ha="center",
            va="center", zorder=9, bbox=dict(boxstyle="circle,pad=0.25", fc="white", ec=INK, lw=0.9))
    ax.text(0.0, -0.75, T(target), fontsize=7, ha="center", va="center", zorder=9,
            bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.85))
    ax.text(1.05, 1.35, T(band.name), fontsize=7, ha="left", va="center")
    ax.set_xlim(-1.5, 2.2)
    ax.set_ylim(-1.3, 1.8)
    ax.set_aspect("equal")
    ax.axis("off")


def draw_attach(ax, pattern, step):
    band = pattern.piece(step.pieces[0])
    target = step.data.get("target", "opening")
    # garment tube right side out, the folded band on its raw edge, raw edges together
    _cylinder(ax, -0.9, 0.0, 1.0, 0.3, z=1, open_top=False)
    _cylinder(ax, 0.0, 0.45, 1.0, 0.3, fc="#e8c27e", z=2)
    th = np.linspace(np.pi, 2 * np.pi, 50)
    ax.plot(np.cos(th), 0.0 + 0.3 * np.sin(th) + 0.06, color=STITCH, lw=1.8, ls=(0, (3, 1.5)), zorder=6)
    _arrow(ax, [0.55, -0.58], [-0.25, -0.58], color=STITCH, lw=1.6, rad=-0.12)
    ax.text(0.0, 0.12, letters(pattern)[band.key], fontsize=8, fontweight="bold", ha="center",
            va="center", zorder=9, bbox=dict(boxstyle="circle,pad=0.25", fc="white", ec=INK, lw=0.9))
    ax.text(0.0, -0.85, T(target), fontsize=7, ha="center", va="bottom", zorder=9,
            bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.85))
    ax.text(1.12, 0.3, T("band folded,\nraw edges down"), fontsize=6.5, ha="left", va="center", color="#444")
    if step.stretch:
        _arrow(ax, [-1.1, -0.15], [-1.55, -0.15], lw=1.6)
        _arrow(ax, [1.1, -0.15], [1.55, -0.15], lw=1.6)
        ax.text(1.35, -0.32, T("stretch"), fontsize=7, ha="center", va="top")
    ax.set_xlim(-1.8, 2.3)
    ax.set_ylim(-1.3, 0.9)
    ax.set_aspect("equal")
    ax.axis("off")


# --------------------------------------------------------------------------- edges

def _edge_piece(pattern, step):
    p, e = step.edges[0]
    return pattern.piece(p), e


def _xsection(ax, origin, scale, kind, amount_txt=""):
    """Cross-section detail (bottom right): fabric as a thick line, stitch as a dot."""
    ox, oy = origin
    s = scale
    if kind in ("hem", "press", "topstitch_fold"):
        ax.plot([ox, ox + 3 * s], [oy + 0.35 * s, oy + 0.35 * s], color=RIGHT_EDGE, lw=2.4, zorder=10)
        from matplotlib.patches import Arc
        ax.add_patch(Arc((ox + 3 * s, oy + 0.2 * s), 0.3 * s, 0.3 * s, theta1=-90, theta2=90,
                         color=RIGHT_EDGE, lw=2.4, zorder=10))
        ax.plot([ox + 1.9 * s, ox + 3 * s], [oy + 0.05 * s, oy + 0.05 * s], color=RIGHT_EDGE, lw=2.4, zorder=10)
        if kind != "press":
            ax.plot([ox + 2.15 * s] * 2, [oy - 0.15 * s, oy + 0.55 * s], color=STITCH, lw=1.6, zorder=11)
        if amount_txt:
            ax.text(ox + 2.45 * s, oy - 0.35 * s, T(amount_txt), fontsize=6.5, ha="center", va="top", zorder=11)
    elif kind == "edge":
        ax.plot([ox, ox + 3 * s], [oy, oy], color=RIGHT_EDGE, lw=2.4, zorder=10)
        xs = np.linspace(ox + 2.3 * s, ox + 3 * s, 7)
        ax.plot(xs, oy + np.where(np.arange(7) % 2, 0.18, -0.18) * s, color=STITCH, lw=1.2, zorder=11)


def _zoom_view(full, edges, size):
    """The part of the drawing to show: the whole piece, or a close-up of short edges."""
    e = np.vstack(edges) if edges else full
    ext = np.ptp(e, 0).max()
    if ext >= 0.4 * size:
        return full
    c = (e.min(0) + e.max(0)) / 2
    half = max(ext * 0.9, size * 0.18)
    return np.array([c - half, c + half])


def _detail(ax, kind, amount_txt):
    """Cross-section in a round detail frame at the lower right of the axes."""
    from matplotlib.patches import Circle
    iax = ax.inset_axes((0.66, 0.0, 0.34, 0.5))
    iax.set_xlim(-0.1, 3.6)
    iax.set_ylim(-1.5, 1.6)
    iax.set_aspect("equal")
    iax.axis("off")
    iax.add_patch(Circle((1.75, 0.05), 1.5, fc="white", ec="#9e9e9e", lw=1.4, zorder=1))
    _xsection(iax, (0.35, -0.15), 0.85, kind, amount_txt)
    caption = {"edge": "Cross-section of the edge", "press": "Cross-section: pressed edge"}.get(
        kind, "Cross-section of the hem")
    iax.text(1.75, 1.62, T(caption), ha="center", va="bottom", fontsize=5.8, color="#555", zorder=12,
             clip_on=False)
    # magnifier handle
    iax.plot([0.7, 0.05], [-1.0, -1.45], color="#9e9e9e", lw=3.0, solid_capstyle="round", zorder=0.5)


def draw_edge(ax, pattern, step, kind="edge"):
    pc, ename = _edge_piece(pattern, step)
    ring = _outline(pc)
    full = _unfolded(pc, ring)
    size = max(np.ptp(full, 0))
    _fill(ax, full, wrong=(kind in ("hem", "press")), z=1, pc=pc)
    for k, (p, e) in enumerate(step.edges):
        if p != pc.key:
            continue
        first = k == 0
        edge = pc.edge(e)
        pts = edge.pts
        cut = G.offset_polyline(pts, edge.sa) if edge.sa > 0 else pts
        ax.plot(cut[:, 0], cut[:, 1], color=ACCENT[1], lw=3.0, zorder=4, solid_capstyle="round")
        if kind in ("hem", "press") and step.amount > 0:
            # the turned-up allowance: band between the raw edge and the fold
            fold = pts if edge.sa > 0 else G.offset_polyline(pts, -step.amount)
            raw_in = G.offset_polyline(fold, -step.amount * (0.5 if kind == "press" else 1.0))
            band = np.vstack([fold, raw_in[::-1]])
            ax.fill(band[:, 0], band[:, 1], fc=RIGHT_SIDE, ec=INK, lw=0.8, zorder=3)
            if kind == "hem":
                _stitch(ax, G.offset_polyline(fold, -max(step.amount - 5.0, step.amount * 0.6)))
            m = G.length(fold) * 0.82
            a = G.point_at(fold, m)
            nv = _inward(fold)[int(np.argmin(np.abs(G.cumlen(fold) - m)))]
            if first:
                _dim(ax, a, a + nv * step.amount, S.cm(step.amount), size)
            _arrow(ax, G.point_at(cut, G.length(cut) * 0.4) - _inward(cut)[len(cut) // 3] * size * 0.06,
                   G.point_at(fold, G.length(fold) * 0.4) + _inward(fold)[len(fold) // 3] * step.amount * 1.4,
                   rad=-0.45)
        elif kind == "topstitch" and step.amount > 0:
            _stitch(ax, G.offset_polyline(pts, -step.amount))
            m = G.length(pts) * 0.8
            a = G.point_at(pts, m)
            nv = _inward(pts)[int(np.argmin(np.abs(G.cumlen(pts) - m)))]
            if first:
                _dim(ax, a, a + nv * max(step.amount, size * 0.03), S.cm(step.amount), size)
        elif kind == "edge":
            xs = cut
            ax.plot(xs[:, 0], xs[:, 1], color=STITCH, lw=1.2, zorder=5, ls=(0, (1, 1)))
    _piece_label(ax, pattern, pc, full, size=8)
    xs_kind = {"hem": "hem", "press": "press", "topstitch": "topstitch_fold", "edge": "edge"}[kind]
    view = _zoom_view(full, [pc.edge(e).pts for p, e in step.edges if p == pc.key], size)
    x0, y0 = view.min(0)
    x1, y1 = view.max(0)
    w = x1 - x0
    _finish_axes(ax, [view, [[x1 + 0.55 * w, y0]]], pad=0.04)
    _detail(ax, xs_kind, S.cm(step.amount) if step.amount else "")


def draw_gather(ax, pattern, step):
    pc, ename = _edge_piece(pattern, step)
    full = _unfolded(pc, _outline(pc))
    size = max(np.ptp(full, 0))
    _fill(ax, full, z=1, pc=pc)
    pts = pc.edge(ename).pts
    for d in (5.0, 12.0):
        ax.plot(*G.offset_polyline(pts, -d).T, color=STITCH, lw=1.1, ls=(0, (4, 2)), zorder=5)
    a, b = pts[0], pts[-1]
    t = G.unit(b - a)
    for p, sgn in ((a, -1), (b, 1)):
        _arrow(ax, p + t * sgn * size * 0.02, p + t * sgn * size * 0.16, color=STITCH, lw=1.4)
    ax.text(*(b + t * size * 0.1 + np.array([0, size * 0.04])), T("pull"), fontsize=7, ha="center")
    _piece_label(ax, pattern, pc, full, size=8)
    _finish_axes(ax, [full, a - t * size * 0.2, b + t * size * 0.2])


def draw_place(ax, pattern, step):
    pocket = pattern.piece(step.pieces[0])
    base = pattern.piece(step.pieces[1])
    full = _unfolded(base, _outline(base))
    _fill(ax, full, z=1, pc=base)
    mark = next((m for m in base.marks if step.data.get("mark", "") in (getattr(m, "key", None) or m.label)), None)
    _piece_label(ax, pattern, base, full, size=8)
    if mark is not None and len(mark.pts) >= 3:
        mp = np.asarray(mark.pts, float)
        folds = [e for e in base.edges if e.fold]
        if folds:                                           # base cut on the fold: the whole pocket
            from shapely.geometry import Polygon
            fa, fb = folds[0].pts[0], folds[0].pts[-1]
            u = Polygon(mp).buffer(0).union(Polygon(G.mirror_line(mp, fa, fb)).buffer(0.01)).buffer(-0.005)
            if u.geom_type == "Polygon":
                mp = np.asarray(u.exterior.coords, float)[:-1]
                mp = mp[[i for i in range(len(mp)) if np.hypot(*(mp[i] - mp[i - 1])) > 1.0]]
        _fill(ax, mp, z=3, pc=pocket)
        top_y, bot_y = mp[:, 1].max(), mp[:, 1].min()
        hem_y = full[:, 1].min()
        slanted_open = any(e.name == "opening" for e in pocket.edges)
        sides = [(mp[i], mp[(i + 1) % len(mp)]) for i in range(len(mp))]
        for a, b in sides:
            d0 = G.unit(b - a)
            horiz_top = abs(a[1] - top_y) < 1 and abs(b[1] - top_y) < 1
            at_hem = abs(a[1] - bot_y) < 1 and abs(b[1] - bot_y) < 1 and bot_y - hem_y < 20
            slanted = 0.2 < abs(d0[0]) < 0.98
            if at_hem or (slanted if slanted_open else horiz_top):
                continue                                    # openings stay open; the hem band catches the bottom
            d = G.unit(b - a)
            n = np.array([-d[1], d[0]]) * 3.0
            _stitch(ax, [a + n, b + n], lw=1.3)
        c = mp.mean(0)
        ax.text(c[0], c[1], letters(pattern)[pocket.key], ha="center", va="center", fontsize=8,
                fontweight="bold", zorder=9, bbox=dict(boxstyle="circle,pad=0.25", fc="white", ec=INK, lw=0.9))
    _finish_axes(ax, [full])


# --------------------------------------------------------------------------- icons

def _pic_scissors(ax, x, y, s, rot=0.0):
    import matplotlib.transforms as mtrans
    from matplotlib.patches import Circle
    tr = mtrans.Affine2D().rotate_deg_around(x, y, rot) + ax.transData
    for dy in (0.18, -0.18):
        ax.add_patch(Circle((x - 0.55 * s, y + dy * s * 1.6), 0.2 * s, fc="white", ec=INK, lw=1.4, transform=tr,
                            zorder=6))
    ax.plot([x - 0.4 * s, x + 0.7 * s], [y + 0.18 * s, y - 0.05 * s], color=INK, lw=2.2, transform=tr, zorder=6)
    ax.plot([x - 0.4 * s, x + 0.7 * s], [y - 0.18 * s, y + 0.05 * s], color=INK, lw=2.2, transform=tr, zorder=6)


def _pic_fabric(ax, x0, y0, w, h, wrong=False):
    pts = np.array([[x0, y0], [x0 + w, y0], [x0 + w, y0 + h], [x0, y0 + h]])
    _fill(ax, pts, wrong=wrong)


def _pic_safety_pin(ax, x, y, s):
    from matplotlib.patches import Arc
    ax.plot([x - s, x + 0.6 * s], [y + 0.12 * s, y + 0.12 * s], color=INK, lw=1.4, zorder=6)
    ax.plot([x - s, x + 0.6 * s], [y - 0.12 * s, y - 0.12 * s], color=INK, lw=1.4, zorder=6)
    ax.add_patch(Arc((x - s, y), 0.24 * s, 0.24 * s, theta1=90, theta2=270, color=INK, lw=1.4, zorder=6))
    ax.add_patch(plt_rect(x + 0.5 * s, y - 0.2 * s, 0.3 * s, 0.4 * s))


def plt_rect(x, y, w, h, fc=INK, ec=INK, lw=1.0, z=6):
    from matplotlib.patches import Rectangle
    return Rectangle((x, y), w, h, fc=fc, ec=ec, lw=lw, zorder=z)


def _legs_inside(ax, pattern):
    """Leg 1 stays inside out, leg 2 is turned right side out; then leg 2 is pushed into leg 1
    from the top until the top edges are even (the part inside dotted)."""
    pc = pattern.piece("front")
    r = _outline(pc)
    r = (r - r.min(0)) / np.ptp(r[:, 1]) * 1.6           # 1.6 units high
    w = np.ptp(r[:, 0])
    g = 0.45 * w
    leg1 = r
    leg2 = r + [w + g, 0]
    _fill(ax, leg1, wrong=True, z=1, pc=pc)
    _fill(ax, leg2, z=1, pc=pc)
    _arrow(ax, [w + g + 0.1 * w, 1.85], [w + g + 0.9 * w, 1.85], lw=1.3, rad=-0.6)
    ax.text(w + g + w / 2, 2.05, T("turn"), fontsize=6.5, ha="center", va="bottom")
    ax.text(w / 2, -0.08, T("leg 1: stays inside out").replace(": ", ":\n"), fontsize=6.5, ha="center",
            va="top")
    ax.text(w + g + w / 2, -0.08, T("leg 2: turn right side out").replace(": ", ":\n"), fontsize=6.5,
            ha="center", va="top")
    # result, larger: leg 2 half way in, coming down from above
    k = 1.45
    x3 = 2 * w + 2.4 * g
    _arrow(ax, [2 * w + 1.25 * g, 0.8], [x3 - 0.35 * g, 0.8], lw=1.6)
    big = r * k + [x3, -0.05]
    up = 0.55 * np.ptp(big[:, 1])
    leg2b = big + [0, up]
    _fill(ax, leg2b, z=1, pc=pc)
    _fill(ax, big, wrong=True, z=2, pc=pc)
    from shapely.geometry import LineString, Polygon
    hidden = LineString(leg2b).intersection(Polygon(big).buffer(0))
    for part in getattr(hidden, "geoms", [hidden]):
        if part.geom_type == "LineString" and part.length > 0.01:
            c = np.asarray(part.coords)
            ax.plot(c[:, 0], c[:, 1], color=INK, lw=0.9, ls=(0, (1.5, 1.5)), zorder=3)
    top = big[:, 1].max()
    ax.text(x3 + np.ptp(big[:, 0]) * 0.35, top + up * 0.55, T("leg 2"), fontsize=6.5, ha="center", va="center",
            zorder=4)
    ax.text(x3 + np.ptp(big[:, 0]) * 0.35, big[:, 1].min() + up * 0.6, T("leg 1"), fontsize=6.5, ha="center",
            va="center", color="#555", zorder=4)
    xa = x3 + np.ptp(big[:, 0]) + 0.9 * g
    _arrow(ax, [xa, top + up * 0.8], [xa, top - up * 0.4], lw=2.0)
    ax.text(xa, top - up * 0.5, T("push in, up to the top").replace(", ", ",\n"), fontsize=6.5,
            fontweight="bold", ha="center", va="top")
    ax.set_xlim(-0.25 * w, xa + 1.1 * g)
    ax.set_ylim(-0.4, top + up + 0.1)
    ax.set_aspect("equal")


def draw_icon(ax, pattern, step):
    pic = step.data.get("picture", "")
    ax.set_xlim(0, 4)
    ax.set_ylim(0, 2.6)
    ax.set_aspect("equal")
    ax.axis("off")
    from matplotlib.patches import Circle, FancyBboxPatch, Rectangle
    if pic == "wash":
        ax.add_patch(FancyBboxPatch((1.2, 0.3), 1.6, 1.9, boxstyle="round,pad=0.05", fc="white", ec=INK, lw=1.5))
        ax.add_patch(Circle((2.0, 1.1), 0.55, fc="#e3f2fd", ec=INK, lw=1.5))
        ax.add_patch(Circle((2.0, 1.1), 0.38, fc=RIGHT_SIDE, ec=INK, lw=0.8))
        ax.plot([1.3, 2.7], [1.85, 1.85], color=INK, lw=1)
        ax.add_patch(Circle((2.5, 2.0), 0.06, fc=INK))
        ax.text(3.1, 1.1, T("30–40°"), fontsize=8, va="center")
    elif pic == "cut":
        _pic_fabric(ax, 0.4, 0.4, 3.2, 1.8)
        outline = np.array([[0.9, 0.7], [2.2, 0.7], [2.5, 1.9], [1.0, 1.9]])
        ax.plot(*np.vstack([outline, outline[:1]]).T, color=INK, lw=1.2, ls=(0, (4, 2)), zorder=4)
        _arrow(ax, [0.6, 1.6], [0.6, 0.6], lw=1.0)
        ax.text(0.5, 1.1, T("grain"), rotation=90, fontsize=6.5, ha="right", va="center")
        _pic_scissors(ax, 2.95, 1.3, 0.45, rot=-75)
    elif pic == "notch":
        _pic_fabric(ax, 0.6, 0.5, 2.8, 1.2)
        ax.plot([2.0, 2.0], [1.7, 1.35], color=INK, lw=2.0, zorder=5)
        ax.plot([0.6, 3.4], [1.45, 1.45], color=STITCH, lw=1.0, ls=(0, (3, 2)), zorder=4)
        _dim(ax, [2.25, 1.7], [2.25, 1.35], "3–4 mm", 2.5, side=-1.0)
        _pic_scissors(ax, 1.85, 2.05, 0.35, rot=-90)
    elif pic == "needle":
        ax.plot([2.0, 2.0], [0.4, 2.2], color=INK, lw=2.4)
        ax.add_patch(Rectangle((1.85, 1.6), 0.3, 0.7, fc="#ddd", ec=INK, lw=1.2))
        ax.plot([2.0, 2.0], [0.35, 0.25], color=INK, lw=1.2)
        ax.add_patch(Circle((2.0, 0.75), 0.05, fc="white", ec=INK, lw=0.8, zorder=5))
        ax.plot([2.0, 3.0, 3.3], [0.75, 1.2, 0.9], color=STITCH, lw=1.0)
        _pic_fabric(ax, 0.6, 0.0, 2.8, 0.25)
    elif pic == "turn" and pattern.garment.startswith("pants") and pattern.has("front"):
        _legs_inside(ax, pattern)
    elif pic == "turn":
        ax.add_patch(Rectangle((0.6, 0.6), 1.2, 1.4, fc=WRONG_SIDE, ec=INK, lw=1.3, hatch="////"))
        ax.add_patch(Rectangle((2.4, 0.6), 1.2, 1.4, fc=RIGHT_SIDE, ec=INK, lw=1.3))
        _arrow(ax, [1.9, 1.3], [2.3, 1.3], lw=1.6)
        _arrow(ax, [1.2, 2.2], [1.2, 2.5], lw=1.2, rad=0.0)
        ax.text(1.2, 0.35, T("inside out"), fontsize=7, ha="center")
        ax.text(3.0, 0.35, T("right side out"), fontsize=7, ha="center")
    elif pic == "elastic":
        ax.add_patch(Rectangle((0.3, 1.0), 3.4, 0.6, fc=RIGHT_SIDE, ec=INK, lw=1.3))
        ax.plot([0.3, 3.7], [1.3, 1.3], color="#eeeeee", lw=6, zorder=3, alpha=0.0)
        ax.plot([0.9, 2.6], [1.3, 1.3], color=INK, lw=3.5, zorder=4, alpha=0.35)
        _pic_safety_pin(ax, 2.95, 1.3, 0.4)
        _arrow(ax, [2.9, 1.9], [3.6, 1.9], lw=1.4)
        ax.text(1.75, 0.65, T("elastic, with a safety pin"), fontsize=7, ha="center")
    elif pic == "velcro":
        _pic_fabric(ax, 0.6, 0.4, 1.4, 1.8)
        _pic_fabric(ax, 2.0, 0.4, 1.4, 1.8, wrong=True)
        ax.add_patch(Rectangle((1.75, 0.6), 0.2, 1.4, fc="#90a4ae", ec=INK, lw=1, zorder=4))
        ax.add_patch(Rectangle((2.05, 0.6), 0.2, 1.4, fc="#cfd8dc", ec=INK, lw=1, zorder=4, hatch="xx"))
        _arrow(ax, [2.6, 1.3], [2.3, 1.3], lw=1.2)
    elif pic == "hand":
        _pic_fabric(ax, 0.4, 1.35, 3.2, 0.6)
        _pic_fabric(ax, 0.4, 0.55, 3.2, 0.6)
        xs = np.linspace(0.8, 3.0, 6)
        for i, x in enumerate(xs[:-1]):
            y0, y1 = (1.35, 1.15) if i % 2 == 0 else (1.15, 1.35)
            ax.plot([x, xs[i + 1]], [y0, y1], color=STITCH, lw=1.1)
        ax.text(2.0, 0.25, T("ladder stitch: the stitches disappear"), fontsize=7, ha="center")
    elif pic == "level":
        ax.plot([1.0, 3.0], [2.3, 2.3], color=INK, lw=2.0)
        skirt = np.array([[1.6, 2.25], [2.4, 2.25], [3.0, 0.5], [1.0, 0.5]])
        _fill(ax, skirt)
        ax.add_patch(Circle((3.5, 1.6), 0.35, fc="white", ec=INK, lw=1.3))
        ax.plot([3.5, 3.5, 3.7], [1.85, 1.6, 1.5], color=INK, lw=1.2)
        ax.text(3.5, 1.05, "24 h", fontsize=8, ha="center")
    elif pic == "done":                       # final pressing: the iron on the garment
        _pic_fabric(ax, 0.5, 0.35, 3.0, 0.9)
        iax = ax.inset_axes((0.28, 0.42, 0.44, 0.5), transform=ax.transAxes)
        draw_machine(iax, "iron")
    elif pic == "zip":
        _pic_fabric(ax, 0.4, 0.3, 1.5, 2.0)
        _pic_fabric(ax, 2.1, 0.3, 1.5, 2.0)
        for y in np.linspace(0.4, 2.2, 14):
            ax.add_patch(Rectangle((1.9 if int(y * 10) % 2 else 1.95, y), 0.15, 0.08, fc="#888", ec="none",
                                   zorder=5))
    else:
        _pic_fabric(ax, 0.8, 0.5, 2.4, 1.6)


# --------------------------------------------------------------------------- machines

def draw_machine(ax, key: str) -> None:
    """Small pictogram of a machine or tool (sewing, overlocker, coverstitch, iron, hand, pins …)."""
    from matplotlib.patches import Circle, FancyBboxPatch, Rectangle
    from matplotlib.patches import Polygon as Poly
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect("equal")
    ax.axis("off")
    lw = 1.3
    if key in ("sewing", "coverstitch"):
        ax.add_patch(FancyBboxPatch((0.08, 0.12), 0.84, 0.12, boxstyle="round,pad=0.02", fc="white", ec=INK, lw=lw))
        ax.add_patch(Rectangle((0.12, 0.24), 0.16, 0.5, fc="white", ec=INK, lw=lw))
        ax.add_patch(FancyBboxPatch((0.12, 0.66), 0.72, 0.16, boxstyle="round,pad=0.02", fc="white", ec=INK,
                                    lw=lw))
        ax.add_patch(Rectangle((0.72, 0.44), 0.1, 0.22, fc="white", ec=INK, lw=lw))
        ax.plot([0.77, 0.77], [0.44, 0.3], color=INK, lw=lw)
        ax.add_patch(Circle((0.5, 0.88), 0.05, fc="white", ec=INK, lw=lw))
        if key == "coverstitch":
            ax.plot([0.8, 0.8], [0.44, 0.3], color=INK, lw=lw)
            ax.add_patch(Circle((0.35, 0.88), 0.05, fc="white", ec=INK, lw=lw))
    elif key == "overlocker":
        ax.add_patch(FancyBboxPatch((0.1, 0.12), 0.8, 0.5, boxstyle="round,pad=0.03", fc="white", ec=INK, lw=lw))
        ax.add_patch(Rectangle((0.55, 0.62), 0.3, 0.12, fc="white", ec=INK, lw=lw))
        for x in (0.2, 0.33, 0.46, 0.59):
            ax.add_patch(Poly([[x - 0.04, 0.66], [x + 0.04, 0.66], [x + 0.02, 0.92], [x - 0.02, 0.92]],
                              closed=True, fc=RIGHT_SIDE, ec=INK, lw=0.9))
        ax.plot([0.62, 0.62], [0.62, 0.48], color=INK, lw=lw)
    elif key == "iron":
        ax.add_patch(Poly([[0.1, 0.25], [0.85, 0.25], [0.85, 0.45], [0.55, 0.62], [0.25, 0.55]], closed=True,
                          fc="white", ec=INK, lw=lw))
        ax.plot([0.4, 0.45, 0.8, 0.8], [0.56, 0.78, 0.78, 0.45], color=INK, lw=lw)
        for x in (0.35, 0.5, 0.65):
            ax.add_patch(Circle((x, 0.33), 0.02, fc=INK))
    elif key == "hand":
        ax.plot([0.15, 0.85], [0.15, 0.85], color=INK, lw=1.6)
        ax.add_patch(Circle((0.8, 0.8), 0.04, fc="white", ec=INK, lw=1.0))
        ax.plot([0.8, 0.6, 0.4, 0.25], [0.8, 0.95, 0.7, 0.85], color=STITCH, lw=1.0)
    elif key == "pins":
        for i, x in enumerate((0.25, 0.5, 0.75)):
            ax.plot([x - 0.1, x + 0.1], [0.15, 0.75], color=PIN, lw=1.3)
            ax.add_patch(Circle((x + 0.11, 0.78), 0.06, fc=ACCENT[i], ec="none"))
    elif key == "scissors":
        _pic_scissors(ax, 0.5, 0.5, 0.38)
    elif key == "safety_pin":
        _pic_safety_pin(ax, 0.55, 0.5, 0.38)
    elif key == "tape":
        ax.add_patch(Circle((0.35, 0.5), 0.25, fc="#fff59d", ec=INK, lw=lw))
        ax.add_patch(Rectangle((0.35, 0.25), 0.55, 0.12, fc="#fff59d", ec=INK, lw=lw))
        for x in np.linspace(0.45, 0.85, 6):
            ax.plot([x, x], [0.37, 0.31], color=INK, lw=0.7)
    elif key == "clips":
        for i, x in enumerate((0.3, 0.62)):
            ax.add_patch(Poly([[x - 0.12, 0.2], [x + 0.12, 0.2], [x + 0.12, 0.8], [x - 0.12, 0.8], [x - 0.12, 0.62],
                               [x + 0.04, 0.62], [x + 0.04, 0.38], [x - 0.12, 0.38]], closed=True,
                              fc=ACCENT[i], ec=INK, lw=0.9))
    elif key == "towel":
        ax.add_patch(Rectangle((0.1, 0.25), 0.8, 0.5, fc="#e1f5fe", ec=INK, lw=lw))
        for x in np.linspace(0.18, 0.82, 9):
            ax.plot([x, x], [0.25, 0.75], color="#90caf9", lw=0.8, ls=(0, (1, 1.5)))
    elif key == "chalk":
        ax.add_patch(Poly([[0.2, 0.35], [0.7, 0.35], [0.8, 0.55], [0.3, 0.55]], closed=True, fc="#e1f5fe",
                          ec=INK, lw=lw))
        ax.plot([0.2, 0.75], [0.2, 0.2], color="#90caf9", lw=2)


# --------------------------------------------------------------------------- dispatch

# --------------------------------------------------------------------------- labels and views

def _tag(ax, xy, text, size=8.0, z=11):
    """Piece label as a strip of masking tape (FL/FR/BL/BR …)."""
    ax.text(xy[0], xy[1], text, ha="center", va="center", fontsize=size, fontweight="bold", color=INK,
            rotation=-6, zorder=z,
            bbox=dict(boxstyle="square,pad=0.35", fc="#fff6c9", ec="#c9b46a", lw=0.8))


def _chalk(ax, pts, z=6):
    """Marking line (chalk): white dashed on a dark outline."""
    pts = np.asarray(pts, float)
    ax.plot(pts[:, 0], pts[:, 1], color="#555555", lw=2.6, zorder=z, solid_capstyle="round")
    ax.plot(pts[:, 0], pts[:, 1], color="white", lw=1.4, ls=(0, (3, 2)), zorder=z + 0.1)


def _mirror_x(pts, axis_x):
    p = np.asarray(pts, float).copy()
    p[:, 0] = 2 * axis_x - p[:, 0]
    return p


def _only_side(label: str) -> str:
    """'left'/'right' for marks that belong on one leg only ('… (right back leg only)')."""
    low = (label or "").lower()
    if "only" in low:
        return "left" if "(left" in low else "right" if "(right" in low else ""
    return ""


LEG_TAGS = {("front", False): "FL", ("front", True): "FR", ("back", False): "BR", ("back", True): "BL"}


def draw_label(ax, pattern, step):
    """The four leg pieces right side up, as worn: FL, FR, BL, BR as tape tags; one-leg marks only
    on their leg (the drafted front is the left front leg, the drafted back the right back leg)."""
    allp = []
    x = 0.0
    size = max(max(np.ptp(_outline(pattern.piece(k)), 0)) for k in ("front", "back"))
    for key, mirrored in (("front", True), ("front", False), ("back", True), ("back", False)):
        pc = pattern.piece(key)
        ring = _outline(pc)
        if mirrored:
            ring = _mirror_x(ring, 0.0)
        sh = np.array([x - ring[:, 0].min(), -ring[:, 1].min()])
        r = ring + sh
        _fill(ax, r, z=1, pc=pc)
        side_here = {("front", False): "left", ("front", True): "right",
                     ("back", False): "right", ("back", True): "left"}[(key, mirrored)]
        for m in pc.marks:
            lab = getattr(m, "key", None) or m.label
            only = _only_side(lab)
            if only and only != side_here:
                continue
            if not only and m.style == "fold":
                continue
            pts = np.asarray(m.pts, float)
            if mirrored:
                pts = _mirror_x(pts, 0.0)
            pts = pts + sh
            if m.style == "placement" and len(pts) >= 3:
                ax.fill(pts[:, 0], pts[:, 1], fc="none", ec="none", zorder=3)
            _chalk(ax, pts, z=5)
        c = np.array([(r[:, 0].min() + r[:, 0].max()) / 2, r[:, 1].min() + np.ptp(r[:, 1]) * 0.55])
        _tag(ax, c, T(LEG_TAGS[(key, mirrored)]), size=10)
        ax.text(c[0], r[:, 1].max() + size * 0.05, T("waist ↑"), ha="center", va="bottom", fontsize=6.5,
                color="#555")
        allp.append(r)
        allp.append([[c[0], r[:, 1].max() + size * 0.12]])
        x = r[:, 0].max() + size * 0.12
    _finish_axes(ax, allp, pad=0.04)


DIAGRAMS = {
    "seam": draw_seam,
    "ring": draw_ring,
    "fold": draw_fold,
    "quarter": draw_quarter,
    "attach": draw_attach,
    "hem": lambda ax, p, s: draw_edge(ax, p, s, "hem"),
    "press": lambda ax, p, s: draw_edge(ax, p, s, "press") if s.edges else draw_icon(ax, p, s),
    "topstitch": lambda ax, p, s: draw_edge(ax, p, s, "topstitch"),
    "edge": lambda ax, p, s: draw_edge(ax, p, s, "edge"),
    "gather": draw_gather,
    "place": draw_place,
    "icon": draw_icon,
    "label": draw_label,
}


STRICT = False          # tests: raise instead of drawing the fallback pictogram


def draw(ax, pattern, step) -> None:
    """Draw one step into ax (falls back to the pictogram if the data is incomplete)."""
    fn = DIAGRAMS.get(step.diagram, draw_icon)
    tool = S.tool_for(pattern.options, step.stitch, step.data.get("knit")) if step.stitch else {}
    _CTX.update(pattern=pattern, hand=tool.get("machine") == "hand")
    try:
        fn(ax, pattern, step)
        for t in ax.texts:                      # close-ups: labels outside the view are cut
            t.set_clip_on(True)
    except (KeyError, ValueError, IndexError) as exc:            # pragma: no cover - defensive
        if STRICT:
            raise
        import booklet_qa as QA
        QA.fallback(step.title, exc)
        ax.cla()
        draw_icon(ax, pattern, S.Step(step.title, data={"picture": ""}))
        ax.set_title(f"({type(exc).__name__})", fontsize=5, color="#aaa")


def render_step(pattern, step, path: str, number: int | None = None, dpi: int = 130) -> str:
    """One step as a PNG (for the Markdown instructions)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(4.6, 2.9), dpi=dpi)
    ax = fig.add_axes((0.02, 0.02, 0.96, 0.96))
    draw(ax, pattern, step)
    if number is not None:
        fig.text(0.02, 0.97, str(number), fontsize=16, fontweight="bold", va="top", ha="left")
    fig.savefig(path, dpi=dpi)
    plt.close(fig)
    _shrink_png(path)
    return path


def _shrink_png(path):
    try:
        from PIL import Image
        im = Image.open(path).convert("RGB").quantize(colors=64)
        im.save(path, optimize=True)
    except Exception:  # pragma: no cover
        pass


def render_steps(pattern, steps: list, out_dir: str, sub: str | None = None) -> dict[int, str]:
    """One PNG per step with a diagram; returns {step number (1-based): relative path}."""
    import i18n
    sub = sub or i18n.fname("steps")
    os.makedirs(os.path.join(out_dir, sub), exist_ok=True)
    res = {}
    for i, st in enumerate(steps, 1):
        if not isinstance(st, S.Step) or st.diagram == "icon":
            continue
        rel = f"{sub}/{i18n.fname('step_')}{i:02d}.png"
        render_step(pattern, st, os.path.join(out_dir, rel), number=i)
        res[i] = rel
    return res
