"""The finished garment from the front and the back, drawn from the real pattern pieces.

Used on the booklet's title page and on the "Done!" page. Every view is a list of layers
(outline, piece for the colour, z order) plus seam lines, marks and gather strokes:

* pants: both legs (the drafted half and its mirror image), crotch seams, the waistband on
  top and leg cuffs at the hem; a gathered edge (elastic waist, cuffs) narrows to the band;
* tops and dresses: the body opened out, both sleeves set into the armholes at the angle
  their width gives, cuffs, hem band, neckband or hood, a kangaroo pocket on the front; a
  dress skirt is gathered onto the bodice;
* skirts: opened out with the waistband.
"""
from __future__ import annotations

import numpy as np
from shapely.geometry import LineString, Polygon, box

import diagrams as DG

BIG = 1e5


def _pc(pattern, key):
    return pattern.piece(key) if pattern.has(key) else None


def _poly(pts) -> Polygon:
    return Polygon(np.asarray(pts, float)).buffer(0)


def _ring(poly) -> np.ndarray:
    if poly.geom_type == "MultiPolygon":
        poly = max(poly.geoms, key=lambda g: g.area)
    return np.asarray(poly.exterior.coords, float)


def _segments(poly, y) -> list[tuple[float, float]]:
    cut = poly.intersection(LineString([(-BIG, y), (BIG, y)]))
    parts = getattr(cut, "geoms", [cut])
    segs = []
    for g in parts:
        if g.is_empty or g.geom_type != "LineString":
            continue
        xs = [c[0] for c in g.coords]
        segs.append((min(xs), max(xs)))
    return sorted(segs)


def _taper(poly, y_cut, y_edge, width=None):
    """Replace everything beyond y_cut (towards y_edge) by straight trapezoids that end at y_edge,
    one per piece of the outline the cut line crosses, each `width` wide (None: as wide as the cut).
    Returns (new polygon, [(x0, x1) at y_edge])."""
    keep = poly.intersection(box(-BIG, y_cut, BIG, BIG) if y_edge < y_cut else box(-BIG, -BIG, BIG, y_cut))
    ends = []
    for x0, x1 in _segments(poly, y_cut):
        c = (x0 + x1) / 2
        w = (x1 - x0) if width is None else min(width, x1 - x0)
        e0, e1 = c - w / 2, c + w / 2
        keep = keep.union(Polygon([(x0, y_cut), (x1, y_cut), (e1, y_edge), (e0, y_edge)]).buffer(0.01))
        ends.append((e0, e1))
    return keep.buffer(0), ends


def _gathers(x0, x1, y, length, n=None):
    """Short strokes along a gathered edge."""
    n = n or max(4, int((x1 - x0) / 25))
    return [np.array([[x, y], [x, y + length]]) for x in np.linspace(x0, x1, n + 2)[1:-1]]


def _band_rect(x0, x1, y, h):
    return np.array([[x0, y], [x1, y], [x1, y + h], [x0, y + h]], float)


def _clip_marks(marks, poly):
    """Marks cut to the visible outline (a taper may have moved the edge inwards)."""
    out = []
    area = poly.buffer(0.5)
    for style, pts in marks:
        pts = np.asarray(pts, float)
        if style == "placement" and len(pts) >= 3:
            g = _poly(pts).intersection(area)
            if not g.is_empty and g.area > 1:
                out.append((style, _ring(g)))
            continue
        if len(pts) < 2:
            continue
        g = LineString(pts).intersection(area)
        for part in getattr(g, "geoms", [g]):
            if part.geom_type == "LineString" and part.length > 1:
                out.append((style, np.asarray(part.coords, float)))
    return out


# --------------------------------------------------------------------------- pants

def _pants_view(pattern, view):
    pc = pattern.piece(view)
    ring = np.asarray(pc.seam_ring(), float)
    cr = pc.edge("crotch").pts
    top = cr[0] if cr[0][1] >= cr[-1][1] else cr[-1]
    ax_x = float(top[0])
    sil = _poly(ring).union(_poly(DG._mirror_x(ring, ax_x)))
    height = np.ptp(ring[:, 1])
    layers, lines, gathers = [], [], []
    # the legs part below the crotch point (where the back legs, wider than the front, would overlap)
    hem = pc.edge("hem").pts
    hy = float(hem[:, 1].mean())
    crotch_y = float(cr[:, 1].min())
    gh = 0.05 * (crotch_y - hy) / max(height, 1.0) * height
    tip = crotch_y - 0.02 * height
    # above the crotch the pants are one closed shape: fill pocket openings and the like
    top_part = sil.intersection(box(-BIG, crotch_y, BIG, BIG)).convex_hull
    sil = sil.union(top_part.intersection(box(-BIG, crotch_y + 0.02 * height, BIG, BIG))).buffer(0)
    sil = sil.difference(Polygon([(ax_x, tip), (ax_x - gh, hy - 0.5 * height), (ax_x + gh, hy - 0.5 * height)]))
    # waist: the band on top, as wide as the waist (elastic: gathered inside the band)
    waist = pc.edge("waistband").pts
    w_lo, w_hi = float(waist[:, 1].min()), float(waist[:, 1].max())
    band = _pc(pattern, "waistband")
    y_cut = w_lo - 0.02 * height
    sil, ends = _taper(sil, y_cut, w_hi, None)
    if band is not None and ends:
        x0, x1 = ends[0][0], ends[-1][1]
        bh = DG._band_dims(band)[1] / 2
        layers.append((_band_rect(x0, x1, w_hi, bh), band, 2))
        if DG.palette_key(band, pattern) != "rib":
            gathers += _gathers(x0, x1, w_hi + bh * 0.2, bh * 0.6, n=int((x1 - x0) / 12))
    # hem: leg cuffs
    cuff = _pc(pattern, "leg_cuff")
    if cuff is not None:
        y_cut_b = hy + min(0.12 * height, 0.6 * (crotch_y - hy))
        cw = DG._band_dims(cuff)[0] / 2
        before = _segments(sil, y_cut_b)
        sil, cuff_ends = _taper(sil, y_cut_b, hy, cw)
        ch = DG._band_dims(cuff)[1] / 2
        for (x0, x1), (s0, s1) in zip(cuff_ends, before):
            layers.append((_band_rect(x0, x1, hy - ch, ch), cuff, 2))
            if x1 - x0 < 0.9 * (s1 - s0):
                gathers += _gathers(x0, x1, hy, 0.03 * height)
    layers.insert(0, (_ring(sil), pc, 1))
    lines.append(np.array([[ax_x, w_hi], [ax_x, tip]]))      # centre seam
    # marks: drafted front = left front (seen from the front: on the right); drafted back = right back
    marks = []
    for m in pc.marks:
        if m.style == "fold":
            continue
        lab = getattr(m, "key", None) or m.label
        only = DG._only_side(lab)
        pts = np.asarray(m.pts, float)
        drafted_side = "left" if view == "front" else "right"
        if only and only != drafted_side:
            pts = DG._mirror_x(pts, ax_x)
        marks.append((m.style, pts))
        if not only:
            marks.append((m.style, DG._mirror_x(pts, ax_x)))
    return dict(layers=layers, seams=[ln for ln in lines if len(ln) > 1], marks=_clip_marks(marks, sil),
                gathers=gathers)


# --------------------------------------------------------------------------- tops, dresses, skirts

def _fold_x(pc) -> float:
    e = next(e for e in pc.edges if e.fold)
    return float(np.mean(e.pts[:, 0]))


def _unfold_marks(pc, cx):
    marks = []
    for m in pc.marks:
        if m.style == "fold":
            continue
        pts = np.asarray(m.pts, float)
        if m.style == "placement" and len(pts) >= 3:
            u = _poly(pts).union(_poly(DG._mirror_x(pts, cx)).buffer(0.01)).buffer(0)
            for g in (u.geoms if hasattr(u, "geoms") else [u]):
                marks.append((m.style, _ring(g)))
        else:
            marks += [(m.style, pts), (m.style, DG._mirror_x(pts, cx))]
    return marks


def _sleeve(pattern, body_pc, cx, side):
    """Sleeve set into the armhole: from the shoulder point, at the angle its width gives."""
    sl = _pc(pattern, "sleeve")
    if sl is None:
        return []
    names = [e.name for e in body_pc.edges]
    # set-in sleeve: from the armhole; raglan: from the raglan line (its top is at the neckline)
    arm = body_pc.edge("armhole" if "armhole" in names else "raglan").pts
    s = arm[0] if arm[0][1] > arm[-1][1] else arm[-1]          # shoulder point
    u = arm[-1] if s is arm[0] else arm[0]                      # underarm point
    ring = np.asarray(sl.seam_ring(), float)
    L = float(np.ptp(ring[:, 1]))
    bicep = float(np.ptp(ring[:, 0])) / 2
    hem_w = sl.edge("hem").length / 2
    del bicep
    raglan = "armhole" not in names
    # hanging down and a little outwards, like a garment laid flat; a raglan sleeve starts at the
    # neckline, so its top edge runs flatter (it continues the shoulder line)
    a = np.radians(58 if raglan else 38)
    d = np.array([np.sin(a), -np.cos(a)])
    if s[0] < cx:
        d[0] = -d[0]
    n = np.array([-d[1], d[0]])
    if (n[1] > 0) if raglan else (np.dot(n, u - s) < 0):
        n = -n                     # the underarm edge lies below the top edge
    out = []
    outer, inner = s + d * L, s + d * L + n * hem_w
    mid = (outer + inner) / 2
    cuff = _pc(pattern, "sleeve_cuff")
    w_end = min(hem_w, DG._band_dims(cuff)[0] / 2) if cuff is not None else hem_w
    p0, p1 = mid - n * w_end / 2, mid + n * w_end / 2
    if w_end < 0.95 * hem_w:            # gathered into the cuff: narrows over the last 15 %
        sleeve = np.array([s, s + d * L * 0.85, p0, p1, u + 0.85 * (inner - u), u])
    else:
        sleeve = np.array([s, outer, inner, u])
    # fill up to the curved armhole so there is no gap between sleeve and body
    a_pts = arm if np.allclose(arm[0], u) else arm[::-1]
    sleeve = _ring(_poly(np.vstack([sleeve, a_pts[1:-1]])).union(_poly(sleeve)))
    out.append((sleeve, sl, 1.5))
    if cuff is not None:
        ch = DG._band_dims(cuff)[1] / 2
        out.append((np.array([p0, p0 + d * ch, p1 + d * ch, p1]), cuff, 2))
    if side == "mirror":
        out = [(DG._mirror_x(r, cx), p, z) for r, p, z in out]
    return out


def _cf_mark_x(pc):
    """x of the 'Centre front' mark of a front with a button stand (None if there is none)."""
    for m in pc.marks:
        if m.label == "Centre front":
            return float(np.mean(np.asarray(m.pts, float)[:, 0]))
    return None


def _top_view(pattern, view):
    pc = pattern.piece(view)
    ring = np.asarray(pc.seam_ring(), float)
    names = [e.name for e in pc.edges]
    parts = [p for p in pattern.pieces if p.part_of == view]
    cfx = _cf_mark_x(pc)
    # half a body: on the fold, a centre seam/opening, or a button stand with a centre-front mark
    halved = pc.on_fold or "center" in names or cfx is not None
    if pc.on_fold:
        cx = _fold_x(pc)
        body = _poly(DG._unfolded(pc, ring))
    elif "center" in names:
        cx = float(np.mean(pc.edge("center").pts[:, 0]))
        body = _poly(ring).union(_poly(DG._mirror_x(ring, cx)).buffer(0.01)).buffer(0)
    elif cfx is not None:
        cx = cfx
        body = _poly(ring).union(_poly(DG._mirror_x(ring, cx)).buffer(0.01)).buffer(0)
    else:
        cx = float(np.mean(ring[:, 0]))
        body = _poly(ring)
    part_seams = []
    for p in parts:                       # yoke, side panels, colour blocks: drawn with the main piece
        pr = np.asarray(p.seam_ring(), float)
        pp = _poly(DG._unfolded(p, pr)) if p.on_fold else _poly(pr)
        if halved and not p.on_fold:
            pp = pp.union(_poly(DG._mirror_x(pr, cx)).buffer(0.01)).buffer(0)
        body = body.union(pp.buffer(0.3)).buffer(-0.3)
        for e in p.edges:
            if e.name.startswith("split"):
                part_seams += [np.asarray(e.pts, float), DG._mirror_x(np.asarray(e.pts, float), cx)]
    if body.geom_type != "Polygon":
        body = max(body.geoms, key=lambda g: g.area)
    allnames = names + [e.name for p in parts for e in p.edges]
    arm_pc = next((p for p in [pc] + parts if any(e.name in ("armhole", "raglan") for e in p.edges)), pc)
    neck_pc = next((p for p in [pc] + parts if any(e.name == "neckline" for e in p.edges)), pc)
    height = np.ptp(ring[:, 1])
    layers, gathers, seams = [], [], []
    marks = _unfold_marks(pc, cx) if halved else [(m.style, np.asarray(m.pts, float)) for m in pc.marks
                                                  if m.style != "fold"]
    if halved and not pc.on_fold and "center" in names:
        seams.append(np.array(pc.edge("center").pts, float))
    elif "front_edge" in names:
        seams.append(np.array(pc.edge("front_edge").pts, float))
    seams += part_seams
    for p in parts:
        marks += _unfold_marks(p, cx) if halved else [(m.style, np.asarray(m.pts, float)) for m in p.marks
                                                      if m.style != "fold"]
    # dress: the skirt hangs from the bodice and is gathered onto it
    skirt = _pc(pattern, "skirt_" + view)
    if skirt is not None and "hem" in names:
        hem_y = float(pc.edge("hem").pts[:, 1].mean())
        sr = np.asarray(skirt.seam_ring(), float)
        if skirt.on_fold:
            sp, scx = _poly(DG._unfolded(skirt, sr)), _fold_x(skirt)
        elif "center" in [e.name for e in skirt.edges]:
            scx = float(np.mean(skirt.edge("center").pts[:, 0]))
            sp = _poly(sr).union(_poly(DG._mirror_x(sr, scx)).buffer(0.01)).buffer(0)
        else:
            sp, scx = _poly(sr), float(np.mean(sr[:, 0]))
        from shapely.affinity import translate
        sp = translate(sp, cx - scx, hem_y - sp.bounds[3])
        bodice_w = _segments(body, hem_y + 1)
        bw = (bodice_w[-1][1] - bodice_w[0][0]) if bodice_w else None
        sp, ends = _taper(sp, hem_y - 0.3 * np.ptp(sr[:, 1]), hem_y, bw)
        layers.append((_ring(sp), skirt, 0.8))
        if ends:
            gathers += _gathers(ends[0][0], ends[-1][1], hem_y, -0.05 * np.ptp(sr[:, 1]))
            seams.append(np.array([[ends[0][0], hem_y], [ends[-1][1], hem_y]]))
    band = _pc(pattern, "hem_band") or (_pc(pattern, "waistband") if "waistband" in names else None)
    if band is not None:
        L, H = DG._band_dims(band)
        if "waistband" in names:            # skirt: band on top
            wy = float(pc.edge("waistband").pts[:, 1].max())
            lo = float(pc.edge("waistband").pts[:, 1].min())
            full = _segments(body, lo - 0.25 * height)
            body, ends = _taper(body, lo - 0.25 * height, wy, L / 2)
            if ends:
                layers.append((_band_rect(ends[0][0], ends[-1][1], wy, H / 2), band, 2))
                if full and ends[-1][1] - ends[0][0] < 0.9 * (full[-1][1] - full[0][0]):
                    gathers += _gathers(ends[0][0], ends[-1][1], wy, -0.03 * height)
        else:                                # top: hem band below
            hy = float(pc.edge("hem").pts[:, 1].mean())
            full = _segments(body, hy + 0.06 * height)
            body, ends = _taper(body, hy + 0.06 * height, hy, L / 2)
            if ends:
                layers.append((_band_rect(ends[0][0], ends[-1][1], hy - H / 2, H / 2), band, 2))
                if full and ends[-1][1] - ends[0][0] < 0.9 * (full[-1][1] - full[0][0]):
                    gathers += _gathers(ends[0][0], ends[-1][1], hy, 0.03 * height)
    layers.insert(0, (_ring(body), pc, 1))
    if "armhole" in allnames or "raglan" in allnames:
        layers += _sleeve(pattern, arm_pc, cx, "drafted") + _sleeve(pattern, arm_pc, cx, "mirror")
    if "neckline" in allnames:
        neck = neck_pc.edge("neckline").pts
        both = np.vstack([neck, DG._mirror_x(neck, cx)[::-1]]) if halved else neck
        both = both[np.argsort(both[:, 0])]
        hood = _pc(pattern, "hood")
        nb = _pc(pattern, "neckband")
        if hood is not None:
            layers.append((_hood(hood, both, view, cx), hood, 0.5 if view == "front" else 3))
        elif nb is not None:
            g = LineString(both).buffer(DG._band_dims(nb)[1] / 4, cap_style=2)
            layers.append((_ring(g), nb, 2.5))
        bb = _pc(pattern, "button_band")
        if bb is not None and "center" in names and view == "front":   # cardigan: band from hem to hem
            ce = np.asarray(pc.edge("center").pts, float)
            ce = ce[np.argsort(ce[:, 1])]                                 # bottom → top
            fn = np.asarray(pc.edge("neckline").pts, float)[::-1]           # CF → neck point
            half = np.vstack([ce, fn])
            path = np.vstack([half, DG._mirror_x(half, cx)[::-1]])
            g = LineString(path).buffer(DG._band_dims(bb)[1] / 4, cap_style=2, join_style=2)
            layers.append((_ring(g), bb, 2.5))
        col = _pc(pattern, "collar") or _pc(pattern, "collar_stand")
        if col is not None and hood is None:
            cr = np.asarray(col.seam_ring(), float)
            ch = float(min(np.ptp(cr[:, 0]), np.ptp(cr[:, 1])))
            if any(m.style == "fold" for m in col.marks):
                ch /= 2                                   # folded lengthwise
            if col.name == "Peter Pan collar":           # lies flat on the body round the neck
                g = LineString(both).buffer(ch, cap_style=2).intersection(body.buffer(-0.5))
                if not g.is_empty:
                    g = max(g.geoms, key=lambda q: q.area) if hasattr(g, "geoms") else g
                    layers.append((_ring(g), col, 2.5))
            else:                                         # stands up from the neckline
                up = both + np.array([0.0, ch * 0.8])
                layers.append((np.vstack([both, up[::-1]]), col, 2.5))
                fall = _pc(pattern, "collar") if col.key == "collar_stand" else None
                if fall is not None and view == "front":  # shirt collar: the points fold down over the stand
                    for sgn in (-1, 1):
                        x0 = cx + sgn * 0.08 * np.ptp(both[:, 0])
                        y0 = float(both[:, 1].min())
                        tip = np.array([cx + sgn * 0.42 * np.ptp(both[:, 0]), y0 - ch * 0.9])
                        top = np.array([cx + sgn * 0.55 * np.ptp(both[:, 0]), float(both[:, 1].max()) + ch * 0.8])
                        layers.append((np.array([[x0, y0 + ch * 0.3], tip, top,
                                                 [cx + sgn * 0.2 * np.ptp(both[:, 0]), top[1]]]), fall, 2.7))
    return dict(layers=layers, seams=seams, marks=_clip_marks(marks, body), gathers=gathers)


def _hood(hood, neck, view, cx):
    """Hood behind the neck (front view) or lying on the back (back view)."""
    hr = np.asarray(hood.seam_ring(), float)
    hh = float(np.ptp(hr[:, 1]))
    nw = float(np.ptp(neck[:, 0]))
    ny = float(neck[:, 1].max())
    t = np.linspace(0, 2 * np.pi, 80)
    if view == "front":            # rises behind the shoulders
        rx, ry, c = nw * 0.62, hh * 0.14, (cx, ny - hh * 0.06)
        pts = np.c_[c[0] + rx * np.sign(np.cos(t)) * np.abs(np.cos(t)) ** 0.7,
                    c[1] + ry * np.sign(np.sin(t)) * np.abs(np.sin(t)) ** 0.9]
    else:                          # hangs down the back from the neckline
        rx, ry, c = nw * 0.62, hh * 0.62, (cx, ny)
        lower = t[(t >= np.pi) & (t <= 2 * np.pi)]
        pts = np.c_[c[0] + rx * np.cos(lower), c[1] + ry * np.sin(lower)]
        pts = np.vstack([[[cx - rx, ny + hh * 0.04]], pts, [[cx + rx, ny + hh * 0.04]]])
    return pts


def garment_views(pattern) -> dict:
    """{'front': view, 'back': view} for garments with a front and a back piece, else {}."""
    keys = {pc.key for pc in pattern.pieces}
    views: dict = {}
    for view in ("front", "back"):
        if view not in keys:
            continue
        pc = pattern.piece(view)
        names = {e.name for e in pc.edges}
        try:
            if pattern.garment.startswith("pants") and "crotch" in names and not pc.on_fold:
                views[view] = _pants_view(pattern, view)
            else:
                views[view] = _top_view(pattern, view)
        except (KeyError, ValueError, IndexError, StopIteration):   # pragma: no cover - defensive
            ring = DG._unfolded(pc, np.asarray(pc.seam_ring(), float))
            views[view] = dict(layers=[(ring, pc, 1)], seams=[], marks=[], gathers=[])
    return views


def draw_view(ax, pattern, view: dict, back: bool = False):
    """One garment view (see garment_views)."""
    allp = []
    for ring, pc, z in sorted(view["layers"], key=lambda r: r[2]):
        DG._fill(ax, np.asarray(ring, float), z=z, pc=pc)
        allp.append(np.asarray(ring, float))
    for sm in view["seams"]:
        ax.plot(sm[:, 0], sm[:, 1], color=DG.INK, lw=0.9, zorder=4)
    for g in view.get("gathers", []):
        ax.plot(g[:, 0], g[:, 1], color=DG.INK, lw=0.6, zorder=4)
    for style, pts in view["marks"]:
        if style == "placement" and len(pts) >= 3:
            ax.fill(pts[:, 0], pts[:, 1], fc=DG.palette(None, pattern)[0], ec=DG.INK, lw=0.9, zorder=3.5)
            DG._fill(ax, pts, z=3.5)
        ax.plot(pts[:, 0], pts[:, 1], color="#5d4037", lw=0.8, ls=(0, (2, 1.2)), zorder=4)
    DG._finish_axes(ax, allp, pad=0.03)
