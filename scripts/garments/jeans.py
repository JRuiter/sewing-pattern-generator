"""Jeans (five-pocket, woven/denim): the pants block with little ease, a real zip fly (fly
extension cut on the front leg, fly shield), scoop front pockets with pocket bags, a back yoke,
two back patch pockets, a coin pocket, a straight interfaced waistband with button and belt loops.
Leg shape: straight, tapered (slim), bootcut or flare."""
from __future__ import annotations

import numpy as np

import geometry as G
from pattern import Edge, Mark, Notch, Pattern, rect_piece

from . import _parts as PT
from . import pants_basic as PB
from ._common import clamp, is_adult

DEFAULTS = dict(fit="normal", fabric="woven", stretch=None, leg_shape="straight", length="long", sa=10.0,
                hem_sa=30.0, coin_pocket=True, belt_loops=True, back_pockets=2)
FINISHED_LABELS = dict(PB.FINISHED_LABELS)
FIT_CHECK = "does the waistband close without gaping at the back, can you sit and squat, and does the fly lie flat?"
ZIPS = [10, 12, 14, 16, 18, 20]


def draft(measures: dict, options: dict | None = None) -> Pattern:
    o = dict(DEFAULTS)
    o.update({k: v for k, v in (options or {}).items() if v is not None})
    m = measures
    sa = o["sa"]
    adult = is_adult(m)
    ease = {"slim": 0.04, "normal": 0.07, "wide": 0.12}.get(o["fit"], 0.07)
    popts: dict = {k: v for k, v in o.items() if k not in ("coin_pocket", "belt_loops")}
    popts.update(style="trousers", fit="normal", cuffs=False, waistband="casing", pockets=["side"],
                 hip_total=o.get("hip_total") or m["hip"] * (1 + ease), pocket_bag_fabric="cotton")
    pat = PB.draft(m, popts)
    pat.garment = "jeans"
    f, b = pat.piece("front"), pat.piece("back")
    R = pat.options.get("_R", 0.25 * m["hip"])
    for _ in range(5):
        if not _shape_top(pat, m, R):
            break
    # ---- fly extension on the front leg
    fw = 35.0 if adult else 28.0
    cr = f.edge("crotch").pts
    top = cr[0]
    zl = [z * 10 for z in ZIPS if z * 10 <= 0.62 * R]
    zl = zl[-1] if zl else ZIPS[0] * 10
    Lf = zl + 15.0
    cl = G.cumlen(cr)
    d = G.unit(G.point_at(cr, min(Lf * 0.5, cl[-1] * 0.3)) - top)
    n = np.array([d[1], -d[0]])
    if n[0] > 0:
        n = -n
    B = G.point_at(cr, Lf)
    C = G.point_at(cr, Lf + fw * 0.9)
    A = top + n * fw
    fly = G.join(G.line(A, B + n * fw), G.quad(B + n * fw, B + n * fw + d * fw * 0.6, C))
    i = int(np.searchsorted(cl, Lf + fw * 0.9))
    rest = np.vstack([C, cr[i:]])
    ci = f.edge_index("crotch")
    f.edges[ci:ci + 1] = [Edge("fly_ext", fly, sa, label="Fly extension"), Edge("crotch", rest, sa, label="Crotch seam")]
    wb = f.edge("waistband")
    wb.pts = np.vstack([wb.pts, A])
    for c in pat.corners:
        if c.get("piece") == "front" and c.get("b") == "crotch" and c.get("a") == "waistband":
            c["b"] = "fly_ext"
    f.marks.append(Mark(G.join(G.line(top + n * -30.0, top + n * -30.0 + d * (Lf - 25)),
                               G.quad(top + n * -30.0 + d * (Lf - 25), top + n * -30.0 + d * Lf, B)), "mark",
                        "Fly topstitching (left front leg only)", template=True))
    f.notches.append(Notch("crotch", 0.0, 1))
    shield = rect_piece("fly_shield", "Fly shield", 2 * (fw + 5), Lf + 20, sa=sa, cut_count=1,
                        labels=("Bottom end", "Raw edges (zip seam)", "Waist end", "Raw edges"))
    shield.marks.append(Mark(G.line(G.P(fw + 5, 0), G.P(fw + 5, Lf + 20)), "fold", "Fold line"))
    pat.pieces.append(shield)
    pat.seams.append(dict(name="Fly: left ↔ right extension", a=[("front", "fly_ext", 1)],
                          b=[("front", "fly_ext", 1)], type="equal"))
    # ---- back yoke
    bw = b.seam_ring()
    xmax = float(bw[:, 0].max())
    bcr = b.edge("crotch").pts
    x_cb = float(bcr[np.argmax(bcr[:, 1]), 0])
    y_top = float(b.edge("waistband").pts[:, 1].min())
    hy_cb, hy_side = clamp(0.035 * m["height"], 45, 75), clamp(0.02 * m["height"], 28, 45)
    cut = G.line(G.P(x_cb - 60, y_top - hy_cb - 3), G.P(xmax + 60, y_top - hy_side - 3 - 0.0))
    parts = PT.split_piece(b, cut, ("back_yoke", "back"), ("Back yoke", "Back leg"), label="Yoke seam")
    yoke = next(p for p in parts if "waistband" in [e.name for e in p.edges])
    lower = next(p for p in parts if p is not yoke)
    yoke.key, yoke.name, lower.key, lower.name = "back_yoke", "Back yoke", "back", "Back leg"
    yoke.part_of = "back"
    yoke.marks = []
    PT.replace_piece(pat, "back", [lower, yoke])
    pat.seams.append(dict(name="Yoke seam (back leg ↔ yoke)", a=[("back", "split", 1)], b=[("back_yoke", "split", 1)],
                          type="equal"))
    # ---- waistband: straight, interfaced, with button overlap
    top_parts = None
    for s in pat.seams:
        if s["name"].startswith("Waistband"):
            top_parts = s["a"]
            pat.seams.remove(s)
            break
    pat.pieces = [p for p in pat.pieces if p.key != "waistband"]
    top_len = sum(pat.piece(k).edge(e).length * n for k, e, n in top_parts)
    wbh = 40.0 if adult else 30.0
    L = top_len + fw
    band = rect_piece("waistband", "Waistband", L, 2 * wbh, sa=sa, cut_count=1, grain_vertical=False,
                      labels=("Seam edge", "End (button)", "Seam edge (turned in)", "End (buttonhole)"))
    band.marks.append(Mark(G.line(G.P(0, wbh), G.P(L, wbh)), "fold", "Fold line"))
    band.marks.append(Mark(G.line(G.P(12, wbh / 2), G.P(12 + PT.button_size(m) + 4, wbh / 2)), "mark", "Buttonhole"))
    band.info.append("interface it completely")
    pat.pieces.append(band)
    pat.seams.append(dict(name="Waistband ↔ jeans top edge", a=top_parts, b=[("waistband", "bottom", 1)],
                          type="ease", lo=fw - 3, hi=fw + 3, note="plus the button overlap"))
    pat.checks = [c for c in pat.checks if "over the hip" not in c["name"]]
    mid = 0.5 * (m["waist"] + m["hip"])
    pat.checks.append(dict(name="Waistband fits the mid-rise waistline", kind="range", value=top_len - 2 * fw, lo=mid * 0.98,
                           hi=mid * 1.08, note="mid rise: between waist and hip; the waistband closes with a button"))
    pat.checks.append(dict(name="Hip passes the opened fly", kind="min", value=top_len + 2 * Lf, target=m["hip"] * 1.03,
                           note="waist + the opened fly ≥ hip"))
    pat.notes = [nt for nt in pat.notes if "lastic" not in nt]
    if o["coin_pocket"]:
        cw = clamp(0.06 * m["hip"], 50, 85)
        coin = rect_piece("coin_pocket", "Coin pocket", cw, cw * 1.1, sa=sa, cut_count=1,
                          labels=("Pocket edge", "Pocket edge", "Pocket opening (hem)", "Pocket edge"),
                          sas=(sa, sa, 20.0, sa))
        coin.edges[2].turned = True
        pat.pieces.append(coin)
        if pat.has("side_panel"):
            sp = pat.piece("side_panel")
            r = sp.seam_ring()
            x0, y0 = float(r[:, 0].min()) + 15, -cw * 1.1 - 25
            sp.marks.append(Mark(np.array([[x0, y0], [x0 + cw, y0], [x0 + cw, y0 + cw * 1.1], [x0, y0 + cw * 1.1]]),
                                 "placement", "Coin pocket (right side panel only)"))
    if o["belt_loops"]:
        loops = rect_piece("belt_loop", "Belt loop strip", 30.0, 5 * (wbh + 25), sa=0.0, cut_count=1,
                           labels=("End", "Edge", "End", "Edge"))
        for e in loops.edges:
            e.raw = True
        loops.info.append("fold both edges to the middle, topstitch, cut 5 loops")
        pat.pieces.append(loops)
    pat.notes.append(f"Jeans zip {zl / 10:.0f} cm, 1 jeans button {17 if adult else 14} mm"
                     + (", 6 rivets (optional)" if adult else "") + "; interfacing for the waistband; "
                     "topstitching thread")
    pat.options.update(_zip_len=zl, coin_pocket=o["coin_pocket"], belt_loops=o["belt_loops"])
    pat.title = "Jeans"
    return pat


def _shape_top(pat, m, R):
    """Mid-rise jeans: the pull-on block is as wide at the top as at the hip; take the difference to
    (waist + hip) / 2 + 3 % out above the hip line, at the side seams and at centre back (the back
    yoke and the curved centre back seam take it), never at centre front (fly)."""
    def top_len():
        return sum(pat.piece(k).edge(e).length * n for s in pat.seams if s["name"].startswith("Waistband")
                   for k, e, n in s["a"])
    target = 0.5 * (m["waist"] + m["hip"]) * 1.03
    excess = top_len() - target
    if excess <= 4:
        return False
    half = excess / 2
    ds, dcb = 0.33 * half, 0.34 * half          # each side seam, centre back
    y_h = -0.6 * R

    def t(y):
        return np.clip((y - y_h) / (0.0 - y_h), 0.0, 1.0) ** 1.4
    # the side seam leans in at the top: raise the waist towards the side so that it still meets the
    # side seam at a right angle
    tan_t = 1.4 * ds / abs(y_h)
    Lb = 70.0

    def lift(x, xs):
        s_ = np.clip(x - (xs - Lb), 0.0, None)
        return tan_t * s_ ** 2 / (2 * Lb)

    f, b = pat.piece("front"), pat.piece("back")
    fr = f.seam_ring()
    x_cf, x_fs = float(f.edge("crotch").pts[0, 0]), float(fr[:, 0].max())
    br = b.seam_ring()
    bc = b.edge("crotch").pts
    x_cb, x_bs = float(bc[np.argmax(bc[:, 1]), 0]), float(br[:, 0].max())
    if x_cb > x_bs:          # centre back to the right: mirror the formulas
        x_cb, x_bs = x_bs, x_cb
    for pc in pat.pieces:
        if pc.key in ("front", "side_panel", "pocket_bag"):
            for e in pc.edges:
                w = np.clip((e.pts[:, 0] - x_cf) / (x_fs - x_cf), 0, 1)
                e.pts = e.pts - np.c_[ds * t(e.pts[:, 1]) * w, -lift(e.pts[:, 0], x_fs) * t(e.pts[:, 1])]
        elif pc.key == "back":
            for e in pc.edges:
                w = np.clip((e.pts[:, 0] - x_cb) / (x_bs - x_cb), 0, 1)
                e.pts = e.pts + np.c_[(-ds * w + dcb * (1 - w)) * t(e.pts[:, 1]), lift(e.pts[:, 0], x_bs) *
                                      t(e.pts[:, 1])]
    pat.options["_top_target"] = target
    return True


def finished_measures(pat):
    return pat.finished


def assembly(pat):
    import steps as ST
    o = pat.options
    sa = ST.cm(pat.piece("front").edge("side").sa)
    base = PB.assembly(pat)
    out = []
    if pat.has("coin_pocket"):
        out += [ST.hem("Hem the coin pocket", [("coin_pocket", "top")], 20.0,
                       "Fold the top edge twice and topstitch it with topstitching thread.", section="Pockets"),
                ST.place("Stitch the coin pocket on", "coin_pocket", "side_panel", "Coin pocket",
                         "Press the other edges under and topstitch the pocket onto the right side panel.",
                         section="Pockets")]
    out += [ST.seam("Sew the back yokes on", ["Yoke seam"],
                    f"Sew each yoke onto its back leg with {sa} seam allowance. Finish, press up and topstitch twice.",
                    section="Back", repeat=2)]
    skip = ("Waistband", "Elastic", "Thread the elastic", "Close the waistband", "Fold the waistband",
            "Sew the waistband", "Mark quarters", "Close the elastic", "Close the opening")
    fly_done = False
    for st in base:
        if st.section in ("Waistband",) or st.title.startswith(skip):
            continue
        if st.section == "Crotch" and not fly_done:
            out += [ST.icon("Sew the fly", "zip",
                            f"Finish the fly extensions. Sew the {o.get('_zip_len', 160) / 10:.0f} cm zip onto the "
                            "right fly extension, with the folded fly shield underneath. Sew the front crotch seam "
                            "from the inseam up to the notch. Lay the left front over the zip, centre fronts "
                            "matching, and sew the zip onto the left extension from the inside; topstitch the J "
                            "line from the right side and bar-tack its lower end.", section="Fly",
                            hint="Use a jeans needle (90–100) and topstitching thread for the visible seams.")]
            fly_done = True
        out.append(st)
    done = out.pop() if out and out[-1].title == "Final pressing" else ST.done()
    if pat.has("belt_loop"):
        out.append(ST.icon("Make the belt loops", "needle",
                           "Fold both long edges of the strip to the middle, fold again and topstitch both edges. "
                           "Cut 5 loops.", section="Waistband"))
    out += [ST.icon("Interface the waistband", "interfacing", "Iron interfacing onto the waistband.", section="Waistband"),
            ST.seam("Sew the waistband on", ["Waistband ↔ jeans"],
                    "Sew the waistband right sides together onto the top edge, the ends extending past the fly "
                    f"by the seam allowance, with {sa} seam allowance. Fold the ends right sides together and "
                    "sew across them; turn. Turn the inner edge under over the allowance and topstitch all round "
                    "the waistband" + (", catching the belt loops (centre back, back yokes, front)."
                                       if pat.has("belt_loop") else "."), section="Waistband"),
            ST.icon("Buttonhole and button", "button",
                    "Sew the buttonhole in the left end of the waistband and set the jeans button on the right "
                    "end.", section="Finish", data={"single": True}),
            done]
    return out


def sewing_steps(pat):
    import steps as ST
    return ST.as_texts(assembly(pat), pat.options)
