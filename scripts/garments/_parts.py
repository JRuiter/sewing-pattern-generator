"""Shared construction components for the woven and structured garments.

- darts: `bust_dart` (side bust dart, the front gets the extra length over the bust) and
  `waist_dart` (marks a dart on the hem/waist edge); darts are inner lines, as on commercial
  patterns, and the seams they shorten are checked with their intake (`ease` seams)
- `button_stand`: turns a centre-front fold into a front opening with an overlap
- `buttonholes`: evenly spaced buttonhole marks along centre front
- `collar_pieces`: stand (mandarin), shirt collar (stand + fall), Peter Pan, polo (knit), shawl band
- `split_piece`: generic split of a piece along a polyline (yokes, princess seams, colour
  blocking, facings): each part keeps the original edges where its outline follows them
- `welt_pocket`: single welt, jetted (double welt) and flap pockets with their pocket bags
- `lining_of`: a lining copy of a piece
"""
from __future__ import annotations

import math

import numpy as np

import geometry as G
from pattern import Edge, Mark, Notch, Piece, rect_piece

from ._common import clamp, ring_of


# --------------------------------------------------------------------------- darts
def shift_above(pts, y0: float, d: float) -> np.ndarray:
    """Move every point above y0 up by d. Where the polyline crosses y0 the crossing point is
    inserted twice (unshifted and shifted), so the line stays connected."""
    pts = np.asarray(pts, float)
    out = []
    for i, p in enumerate(pts):
        if i:
            q = pts[i - 1]
            if (q[1] - y0) * (p[1] - y0) < 0:
                c = q + (p - q) * (y0 - q[1]) / (p[1] - q[1])
                out += [c, c + (0, d)] if q[1] < y0 else [c + (0, d), c]
        out.append(p + (0, d) if p[1] > y0 else p.copy())
    return np.array(out)


def bust_dart(front: Piece, y_d: float, intake: float, bp_x: float) -> dict:
    """Side bust dart: everything above the dart line moves up by the intake (the front gets the
    length it needs over the bust); the dart is marked from the side seam towards the bust point
    and ends 2 cm before it. Returns the dart data (intake, side point)."""
    if intake <= 0:
        return dict(intake=0.0)
    y_d -= 0.37                       # never exactly on a polyline vertex
    for e in front.edges:
        e.pts = shift_above(e.pts, y_d, intake)
    if front.grain is not None:
        front.grain = tuple(p + (0, intake) if p[1] > y_d else p for p in front.grain)
    for mk in front.marks:
        mk.pts = np.where(mk.pts[:, 1:2] > y_d, mk.pts + (0, intake), mk.pts)
    side = front.edge("side").pts
    xs = float(side[np.argmin(np.abs(side[:, 1] - y_d)), 0])
    apex = G.P(bp_x + 20.0, y_d + intake / 2)
    front.marks.append(Mark(np.vstack([G.P(xs, y_d + intake), apex, G.P(xs, y_d)]), "mark", "Bust dart"))
    front.info.append(f"Bust dart: {intake / 10:.1f} cm at the side seam")
    return dict(intake=intake, side=G.P(xs, y_d), apex=apex)


def waist_dart(piece: Piece, edge: str, x: float, width: float, height: float, label: str = "Waist dart") -> float:
    """Mark a dart standing on `edge` (a roughly horizontal hem/waist edge) at x. Returns the
    width it takes out of that edge."""
    pts = piece.edge(edge).pts
    y = float(np.interp(x, *(pts[np.argsort(pts[:, 0])].T)))
    up = 1.0 if piece.seam_ring()[:, 1].mean() > y else -1.0
    piece.marks.append(Mark(np.vstack([G.P(x - width / 2, y), G.P(x, y + up * height), G.P(x + width / 2, y)]),
                            "mark", label))
    return width


def dart_steps(section: str, text: str, repeat: int = 1):
    import steps as ST
    return ST.icon("Sew the darts", "dart", text, section=section, repeat=repeat,
                   hint="Do not backstitch at the point: tie the threads off by hand.")


# --------------------------------------------------------------------------- front opening
def button_stand(front: Piece, ext: float, facing: float | None = None, label: str = "Front edge (button stand)"):
    """Turn the centre-front fold of a front into a front opening with an overlap of `ext` mm
    beyond centre front. The edge allowance is `facing` (default 2 × ext: folded twice, a
    self-faced button stand). The front is then cut twice (mirrored)."""
    i = front.edge_index("center")
    ce = front.edge("center")
    top, bot = ce.pts[0], ce.pts[-1]
    hem = front.edges[(i + 1) % len(front.edges)]
    neck = front.edges[i - 1]
    hem.pts = np.vstack([G.P(-ext, bot[1]), hem.pts])
    neck.pts = np.vstack([neck.pts, G.P(-ext, top[1])])
    fe = Edge("front_edge", G.line(G.P(-ext, top[1]), G.P(-ext, bot[1])), facing if facing is not None else 2 * ext,
              False, label, turned=facing is None)
    front.edges[i] = fe
    front.cut_count, front.mirror = 2, True
    front.marks.append(Mark(G.line(top, bot), "mark", "Centre front"))
    if facing is None:
        front.marks.append(Mark(G.line(G.P(-ext, top[1]) + (2 * ext, 0), G.P(-ext, bot[1]) + (2 * ext, 0)),
                                "fold", "Fold line (stand)"))
    return fe


def buttonholes(piece: Piece, y_top: float, y_bot: float, n: int, size: float, x: float = 0.0,
                vertical: bool = False, label: str = "Buttonhole") -> list[float]:
    """Evenly spaced buttonhole marks on centre front (x) from y_top down to y_bot. A horizontal
    buttonhole starts 3 mm beyond centre front, so the button sits on centre front."""
    ys = list(np.linspace(y_top, y_bot, n))
    for y in ys:
        if vertical:
            pts = G.line(G.P(x, y + size / 2), G.P(x, y - size / 2))
        else:
            pts = G.line(G.P(x - 3, y), G.P(x - 3 + size, y))
        piece.marks.append(Mark(pts, "mark", label))
    return ys


def button_size(m: dict) -> float:
    return 15.0 if m["height"] < 1400 else (18.0 if m["height"] < 1650 else 20.0)


# --------------------------------------------------------------------------- collars
def collar_pieces(kind: str, neck_half: float, m: dict, sa: float, ext: float = 0.0, front_neck: float = 0.0,
                  back_neck: float = 0.0, front_pts=None, back_pts=None, fabric: str = "Main fabric"):
    """Collar pieces for a neckline of half length `neck_half` (CB to CF). ext: the button stand
    overlap the stand runs onto. Returns (pieces, info) with info['seam'] = (key, edge) sewn to
    the neckline and info['height'].

    kinds: stand (mandarin), shirt (stand + fall collar), peter_pan (flat, needs the front and
    back neckline points), polo (knit collar), shawl (wide folded band, see cardigan/jacket)."""
    adult = m["height"] > 1650
    if kind in ("stand", "shirt"):
        h = 32.0 if adult else 25.0
        rise = 12.0 if adult else 9.0
        target = neck_half + ext

        def neck_of(L):
            # neck edge: straight from CB for half its length, then rising towards the front
            return G.join(G.line(G.P(0, 0), G.P(L * 0.45, 0)), G.cubic(G.P(L * 0.45, 0), G.P(L * 0.75, 0),
                                                                         G.P(L * 0.92, rise * 0.4), G.P(L, rise)))
        L = target
        for _ in range(4):
            L *= target / G.length(neck_of(L))
        neck = neck_of(L)
        d = G.unit(G.end_dir(neck))
        nrm = np.array([-d[1], d[0]])
        top_end = G.P(L * 0.93, rise + h * 0.95)
        front = G.join(G.tangent_curve(neck[-1], nrm, top_end, (-1, 0.15), 0.6, 0.5))
        top = G.join(G.cubic(top_end, G.P(L * 0.75, rise + h * 1.0), G.P(L * 0.45, h), G.P(0, h)))
        edges = [Edge("neck", neck, sa, label="Neckline seam"), Edge("front", front, sa, label="Front end"),
                 Edge("top", top, sa, label="Top edge" if kind == "stand" else "Collar seam"),
                 Edge("center", G.line(G.P(0, h), G.P(0, 0)), 0.0, True, "Centre back (fold)")]
        stand = Piece("collar_stand", "Collar stand" if kind == "shirt" else "Stand collar", edges, cut_count=2,
                      mirror=False, fabric=fabric, grain=(G.P(L * 0.2, h * 0.2), G.P(L * 0.2, h * 0.8)))
        stand.info.append("outer and inner piece; interface the outer one")
        stand.notches.append(Notch("neck", back_neck if back_neck else neck_half * 0.4, 1))
        out = [stand]
        info = dict(seam=("collar_stand", "neck"), height=h)
        if kind == "shirt":
            Lc = G.length(top)
            hc = h + (15.0 if adult else 10.0)
            spread = 18.0 if adult else 12.0
            base = G.join(G.cubic(G.P(0, 0), G.P(Lc * 0.5, 0), G.P(Lc * 0.85, -3), G.P(Lc, -8)))
            point = G.line(base[-1], G.P(Lc + spread, hc - 4))
            outer = G.join(G.cubic(G.P(Lc + spread, hc - 4), G.P(Lc * 0.75, hc + 2), G.P(Lc * 0.35, hc), G.P(0, hc)))
            cedges = [Edge("bottom", base, sa, label="Collar seam"), Edge("point", point, sa, label="Collar point"),
                      Edge("outer", outer, sa, label="Collar edge"),
                      Edge("center", G.line(G.P(0, hc), G.P(0, 0)), 0.0, True, "Centre back (fold)")]
            col = Piece("collar", "Collar", cedges, cut_count=2, mirror=False, fabric=fabric,
                        grain=(G.P(Lc * 0.2, hc * 0.2), G.P(Lc * 0.2, hc * 0.8)))
            col.info.append("upper and under collar; interface the upper one")
            out.append(col)
            info["fall"] = hc
        return out, info
    if kind == "polo":
        h = 75.0 if adult else 60.0
        L = 2 * neck_half * 0.95
        c = rect_piece("collar", "Polo collar", L / 2, 2 * h, sa=sa, cut_count=1, fold_left=True, fabric=fabric,
                       labels=("Neckline seam", "Front end", "Neckline seam (fold)", "Centre back"))
        c.marks.append(Mark(G.line(G.P(0, h), G.P(L / 2, h)), "fold", "Fold line"))
        c.edges[2].label = "Raw edge (folded inside)"
        return [c], dict(seam=("collar", "bottom"), height=h, ratio=0.95)
    if kind == "peter_pan":
        w = clamp(0.06 * m["chest"], 45, 75)
        # back neckline reflected over the shoulder line so that front and back meet at the shoulder,
        # overlapping 1 cm there (the collar rolls slightly)
        S = back_pts["S"]
        N = back_pts["N"]
        bneck = G.mirror_line(back_pts["neck"], N, S)[::-1]       # CB → neck point
        fneck = np.asarray(front_pts["neck"], float)
        fneck = fneck - fneck[0] + N                                # neck point → CF
        inner = G.resample(G.join(bneck, fneck), 2.0)
        Ln = G.length(inner)
        nrm = G.normals_right(inner)
        k = len(inner) // 2
        if np.dot(S - inner[k], nrm[k]) < 0:                        # outer side: towards the shoulder
            nrm = -nrm
        s = G.cumlen(inner)
        f = np.ones_like(s)
        end = s > Ln - w
        f[end] = np.sqrt(np.clip(1 - ((s[end] - (Ln - w)) / w) ** 2, 0, 1))
        outer = (inner + nrm * (w * f)[:, None])[::-1]              # CF → CB
        cb = G.line(outer[-1], inner[0])
        if G.signed_area(np.vstack([inner, outer[1:]])) > 0:
            edges = [Edge("neck", inner, sa, label="Neckline seam"), Edge("outer", outer, sa, label="Collar edge"),
                     Edge("center", cb, 0.0, True, "Centre back (fold)")]
        else:
            edges = [Edge("center", cb[::-1].copy(), 0.0, True, "Centre back (fold)"),
                     Edge("outer", outer[::-1].copy(), sa, label="Collar edge"),
                     Edge("neck", inner[::-1].copy(), sa, label="Neckline seam")]
        d = G.unit(outer[-1] - inner[0])
        g0 = inner[0] + d * w * 0.5 + nrm[0] * 0 + G.unit(inner[min(15, len(inner) - 1)] - inner[0]) * 25
        col = Piece("collar", "Peter Pan collar", edges, cut_count=2, mirror=False, fabric=fabric,
                    grain=(g0 - d * w * 0.3, g0 + d * w * 0.3))
        col.info.append("upper and under collar; interface the upper one")
        return [col], dict(seam=("collar", "neck"), height=w, length=Ln)
    raise ValueError(f"unknown collar kind '{kind}'")


# --------------------------------------------------------------------------- split lines
def _classify(ring, lines):
    """For each segment of a closed ring, the index of the nearest polyline in `lines`."""
    from shapely.geometry import LineString, Point
    geo = [LineString(L) for L in lines]
    mids = (ring + np.roll(ring, -1, axis=0)) / 2
    out = []
    for p in mids:
        P_ = Point(p)
        out.append(int(np.argmin([g.distance(P_) for g in geo])))
    return np.array(out)


def split_piece(piece: Piece, cut, keys: tuple[str, str], names: tuple[str, str], label: str = "Style seam",
                sa: float | None = None, fold: bool = False) -> list[Piece]:
    """Split a piece along the polyline `cut` (it has to cross the outline twice). Returns the
    parts (largest first if the caller doesn't care, else ordered by keys: the first part is the
    one on the left of the cut direction). Each part keeps the original edges (name, allowance,
    label, fold, turned) where its outline follows them; the cut becomes an edge named `split`
    with allowance `sa` (default: the piece's side seam allowance)."""
    from shapely.geometry import LineString, Polygon
    from shapely.ops import split as sp_split
    cut = np.asarray(cut, float)
    d0, d1 = G.unit(cut[1] - cut[0]), G.unit(cut[-1] - cut[-2])
    ext = np.vstack([cut[0] - d0 * 50, cut, cut[-1] + d1 * 50])
    poly = Polygon(piece.seam_ring())
    parts = list(sp_split(poly, LineString(ext)).geoms)
    if len(parts) != 2:
        raise ValueError(f"{piece.name}: split line must cross the outline twice ({len(parts)} parts)")
    # order: the part on the left of the cut direction first
    mid = cut[len(cut) // 2]
    left_dir = np.array([-d0[1], d0[0]]) if len(cut) < 3 else np.array([-(cut[-1] - cut[0])[1], (cut[-1] - cut[0])[0]])

    def side(pg):
        c = np.array(pg.representative_point().coords[0])
        return float(np.dot(c - mid, left_dir))
    parts.sort(key=side, reverse=True)
    if sa is None:
        sa = max((e.sa for e in piece.edges if not e.fold and not e.turned), default=10.0)
    lines = [e.pts for e in piece.edges] + [cut]
    out = []
    for key, name, pg in zip(keys, names, parts):
        ring = ring_of(pg, 1.0)
        cls = _classify(ring, lines)
        # start at a class change
        ch = np.nonzero(cls != np.roll(cls, 1))[0]
        r0 = int(ch[0]) if len(ch) else 0
        ring, cls = np.roll(ring, -r0, axis=0), np.roll(cls, -r0)
        edges = []
        n = len(ring)
        start = 0
        used: dict[str, int] = {}
        for i in range(1, n + 1):
            if i == n or cls[i] != cls[start]:
                pts = np.vstack([ring[start:i + 1]]) if i < n else np.vstack([ring[start:], ring[:1]])
                k = int(cls[start])
                if k == len(piece.edges):
                    e = Edge("split", pts, 0.0 if fold else sa, fold, label)
                else:
                    o = piece.edges[k]
                    e = Edge(o.name, pts, o.sa, o.fold, o.label, o.turned, o.sa_hint, o.pointed, o.raw)
                used[e.name] = used.get(e.name, 0) + 1
                if used[e.name] > 1:
                    e.name = f"{e.name}_{used[e.name]}"
                if len(pts) >= 2 and G.length(pts) > 0.5:
                    edges.append(e)
                start = i
        pc = Piece(key, name, edges, cut_count=piece.cut_count, mirror=piece.mirror, fabric=piece.fabric,
                   grain=None, info=list(piece.info), stretch_dir=piece.stretch_dir)
        # grain: keep it if it lies inside, else a parallel arrow through the part
        from shapely.geometry import Point
        if piece.grain is not None:
            g0, g1 = np.asarray(piece.grain[0], float), np.asarray(piece.grain[1], float)
            if pg.contains(Point((g0 + g1) / 2)) and pg.contains(Point(g0)) and pg.contains(Point(g1)):
                pc.grain = (g0, g1)
            else:
                c = np.array(pg.representative_point().coords[0])
                d = G.unit(g1 - g0)
                half = min(G.length(np.vstack([g0, g1])) / 2, 0.3 * math.sqrt(pg.area))
                pc.grain = (c - d * half, c + d * half)
        for mk in piece.marks:
            c = mk.pts.mean(axis=0)
            if pg.buffer(0.5).contains(Point(c)):
                pc.marks.append(mk)
        orig = {e.name: e for e in piece.edges}
        for nt in piece.notches:
            if nt.edge in orig and any(e.name == nt.edge for e in edges) and \
                    abs(pc.edge(nt.edge).length - orig[nt.edge].length) < 1.0:
                pc.notches.append(nt)
        out.append(pc)
    return out


def remap_seams(pat, old: str, parts: list[Piece]) -> None:
    """After a split: seams that used an edge of the old piece now use that edge on the part(s)
    that kept it (an edge cut in two is listed on both parts)."""
    for s in pat.seams:
        for side in ("a", "b"):
            new = []
            for k, e, n in s[side]:
                if k != old:
                    new.append((k, e, n))
                    continue
                for pc in parts:
                    for ed in pc.edges:
                        if ed.name == e or ed.name.startswith(e + "_") and ed.name[len(e) + 1:].isdigit():
                            new.append((pc.key, ed.name, n))
            s[side] = new
    keep = []
    for c in pat.corners:
        if c.get("piece") == old:
            for pc in parts:
                names = [e.name for e in pc.edges]
                if c["a"] in names and c["b"] in names:
                    keep.append(dict(c, piece=pc.key))
                    break
        elif "sum" in c and any(p == old for p, _, _ in c["sum"]):
            new = []
            for p, a, b in c["sum"]:
                if p == old:
                    hit = next((pc.key for pc in parts if {a, b} <= {e.name for e in pc.edges}), None)
                    if hit is None:
                        break
                    p = hit
                new.append((p, a, b))
            else:
                keep.append(dict(c, sum=new))
        else:
            keep.append(c)
    pat.corners = keep


def replace_piece(pat, old: str, parts: list[Piece]) -> None:
    i = [p.key for p in pat.pieces].index(old)
    pat.pieces[i:i + 1] = parts
    remap_seams(pat, old, parts)


# --------------------------------------------------------------------------- pockets
def welt_pocket(on: Piece, kind: str, center, width: float, sa: float, angle: float = 0.0,
                fabric_bag: str = "Pocket lining", key: str = "pocket") -> tuple[list[Piece], list[dict]]:
    """Welt (single), jetted (double welt) or flap pocket on `on` at `center` (opening width).
    Adds the opening mark to `on`; returns the extra pieces and their seams."""
    c = np.asarray(center, float)
    d = np.array([math.cos(math.radians(angle)), math.sin(math.radians(angle))])
    a, b = c - d * width / 2, c + d * width / 2
    label = {"welt": "Welt pocket opening", "jetted": "Jetted pocket opening", "flap": "Flap pocket opening"}[kind]
    on.marks.append(Mark(np.vstack([a, b]), "placement", label))
    depth = clamp(width * 1.15, 120, 200)
    pieces: list[Piece] = []
    seams: list[dict] = []
    if kind == "welt":
        wh = 25.0
        welt = rect_piece(key + "_welt", "Pocket welt", width, 2 * wh, sa=sa, cut_count=2, fabric="Main fabric",
                          labels=("Welt seam", "Welt end", "Welt seam (fold)", "Welt end"), grain_vertical=False)
        welt.marks.append(Mark(G.line(G.P(0, wh), G.P(width, wh)), "fold", "Fold line"))
        welt.info.append("interface one half")
        pieces.append(welt)
    elif kind == "jetted":
        lip = 10.0
        jet = rect_piece(key + "_jet", "Pocket lips", width + 40, 4 * lip + 2 * sa, sa=0.0, cut_count=2,
                         fabric="Main fabric", labels=("Lip edge", "Lip end", "Lip edge", "Lip end"),
                         grain_vertical=False)
        for e in jet.edges:
            e.raw = True
        jet.info.append("one strip per pocket (both lips); interface it")
        pieces.append(jet)
    else:
        fh = clamp(width * 0.35, 40, 65)
        pts_b = G.line(G.P(0, 0), G.P(width, 0))
        flap_edges = [Edge("top", G.line(G.P(width, fh), G.P(0, fh)), sa, label="Flap seam"),
                      Edge("outline", G.join(G.line(G.P(0, fh), G.P(0, 12)), G.quad(G.P(0, 12), G.P(0, 0), G.P(12, 0)),
                                             G.line(G.P(12, 0), G.P(width - 12, 0)),
                                             G.quad(G.P(width - 12, 0), G.P(width, 0), G.P(width, 12)),
                                             G.line(G.P(width, 12), G.P(width, fh))), sa, label="Flap edge")]
        del pts_b
        flap = Piece(key + "_flap", "Pocket flap", flap_edges, cut_count=4, mirror=False, fabric="Main fabric",
                     grain=(G.P(width * 0.5, fh * 0.2), G.P(width * 0.5, fh * 0.8)))
        flap.info.append("2 per pocket (outer flap + facing); interface the outer one")
        pieces.append(flap)
        seams.append(dict(name="Pocket flap round", a=[(key + "_flap", "outline", 1)],
                          b=[(key + "_flap", "outline", 1)], type="equal"))
        jet = rect_piece(key + "_jet", "Pocket lips", width + 40, 40 + 2 * sa, sa=0.0, cut_count=2,
                         fabric="Main fabric", labels=("Lip edge", "Lip end", "Lip edge", "Lip end"),
                         grain_vertical=False)
        for e in jet.edges:
            e.raw = True
        pieces.append(jet)
    bw = width + 40
    bag = rect_piece(key + "_bag", "Pocket bag", bw, depth, sa=sa, cut_count=4, fabric=fabric_bag,
                     labels=("Bag bottom", "Bag side", "Opening edge", "Bag side"))
    bag.info.append("2 per pocket")
    pieces.append(bag)
    seams.append(dict(name="Pocket bag round", a=[(key + "_bag", "left", 1), (key + "_bag", "bottom", 1),
                                                   (key + "_bag", "right", 1)],
                      b=[(key + "_bag", "left", 1), (key + "_bag", "bottom", 1), (key + "_bag", "right", 1)],
                      type="equal"))
    return pieces, seams


def welt_steps(kind: str, on_name: str, section: str = "Pockets", repeat: int = 2) -> list:
    import steps as ST
    sa_t = "the marked opening"
    out = [ST.icon("Interface the pocket opening", "interfacing",
                   f"Iron a strip of interfacing (4 cm wide) onto the wrong side of the {on_name} behind {sa_t}.",
                   section=section)]
    if kind == "flap":
        out.append(ST.seam("Sew the pocket flaps", ["Pocket flap round"],
                           "Lay each flap right sides together onto its facing and sew round the outline; the top "
                           "stays open. Trim, turn and press; topstitch 5 mm from the edge if you like.",
                           section=section, repeat=repeat))
    lip = {"welt": "Fold the welt lengthwise, wrong sides together, and lay it below the marked line, raw "
                   "edges on the line, the fold pointing down.",
           "jetted": "Fold both long edges of the lip strip to the middle and press. Lay it centred on the "
                     "marked line, right side down.",
           "flap": "Lay the flap above the marked line, raw edges on the line, pointing up, and the lip strip "
                   "below it."}[kind]
    out += [
        ST.icon("Sew the welt on", "needle", lip + " Lay a pocket bag piece on top, right sides together, and sew "
                "two parallel lines 5 mm above and below the marked line, exactly as long as the opening.",
                section=section, repeat=repeat),
        ST.icon("Cut the opening", "cut", "Cut along the middle between the two lines, through the garment only, "
                "and into the corners in a Y, up to the last stitch.", section=section, repeat=repeat),
        ST.icon("Turn the welt through", "turn", "Push the bag and the allowances through the opening to the "
                "inside. Press the welt (lips) into place and secure the little triangles at the ends with a "
                "few stitches across.", section=section, repeat=repeat),
        ST.seam("Close the pocket bags", ["Pocket bag round"],
                "Sew the second bag piece onto the upper allowance and sew both bag pieces together round the "
                "sides and the bottom. Finish the edges.", section=section, repeat=repeat),
    ]
    return out


# --------------------------------------------------------------------------- lining
def lining_of(pc: Piece, key: str | None = None, name: str | None = None, sa: float | None = None,
              hem_shorter: float = 0.0) -> Piece:
    """A lining copy of a piece (fabric 'Lining'); hems become plain seams `hem_shorter` mm
    shorter (the lining hangs 2 cm above the hem)."""
    edges = []
    for e in pc.edges:
        ne = Edge(e.name, e.pts.copy(), e.sa if sa is None or e.fold else sa, e.fold, e.label, False, e.sa_hint,
                  e.pointed, e.raw)
        if e.turned:
            ne.sa = sa if sa is not None else min(e.sa, 10.0)
            ne.label = (e.label + " (lining)").strip()
        edges.append(ne)
    lp = Piece(key or pc.key + "_lining", name or pc.name + " lining", edges, cut_count=pc.cut_count,
               mirror=pc.mirror, fabric="Lining", grain=pc.grain, notches=list(pc.notches))
    del hem_shorter
    return lp


def rename_edge_refs(pat, piece: str, old: str, new: str) -> None:
    """Corners and seams that referenced edge `old` of `piece` now use `new`."""
    for c in pat.corners:
        if c.get("piece") == piece:
            for k in ("a", "b"):
                if c[k] == old:
                    c[k] = new
        if "sum" in c:
            c["sum"] = [(p, new if p == piece and a == old else a, new if p == piece and b == old else b)
                        for p, a, b in c["sum"]]
    for s in pat.seams:
        for side in ("a", "b"):
            s[side] = [(k, new if k == piece and e == old else e, n) for k, e, n in s[side]]
