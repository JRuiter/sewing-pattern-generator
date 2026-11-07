"""Beanie (jersey/rib): two identical pieces with a round crown, optional rib brim."""
from __future__ import annotations

import ease as E
import geometry as G
from pattern import Edge, Mark, Pattern, Piece, rect_piece

DEFAULTS = dict(fabric="jersey", stretch=None, brim=True, slouch=False, sa=7.0, hem_sa=20.0, circ_total=None)
FINISHED_LABELS = {"circ": ("Beanie width (relaxed)", "width"), "height": ("Beanie height", "length")}


def draft(measures: dict, options: dict | None = None) -> Pattern:
    o = dict(DEFAULTS)
    o.update({k: v for k, v in (options or {}).items() if v is not None})
    m = measures
    head = m["head"]
    _, stretch, _ = E.fabric_info(o["fabric"], o["stretch"])
    circ = o["circ_total"] or head * (0.86 if stretch >= 30 else 0.98)
    W = circ / 2
    H = head * (0.36 if not o["slouch"] else 0.48)
    Hs = H - W * 0.42
    sa = o["sa"]
    brim_h = 0.10 * head if o["brim"] else 0.0
    right = G.line(G.P(W, 0), G.P(W, Hs))
    dome = G.join(G.tangent_curve(G.P(W, Hs), (0, 1), G.P(W / 2, H), (-1, 0), 0.55, 0.55),
                  G.tangent_curve(G.P(W / 2, H), (-1, 0), G.P(0, Hs), (0, -1), 0.55, 0.55))
    left = G.line(G.P(0, Hs), G.P(0, 0))
    edges = [Edge("bottom", G.line(G.P(0, 0), G.P(W, 0)), sa if o["brim"] else o["hem_sa"],
                  label="Brim seam" if o["brim"] else "Hem", turned=not o["brim"]),
             Edge("right", right, sa, label="Side seam"), Edge("crown", dome, sa, label="Crown seam"),
             Edge("left", left, sa, label="Side seam")]
    p = Piece("beanie", "Beanie", edges, cut_count=2, mirror=False, fabric="Main fabric",
              grain=(G.P(W / 2, H * 0.15), G.P(W / 2, H * 0.7)))
    p.stretch_dir = "Stretch direction: crosswise"
    pieces = [p]
    seams = [dict(name="Crown seam front ↔ back", a=[("beanie", "crown", 1)], b=[("beanie", "crown", 1)],
                  type="equal"),
             dict(name="Side seams", a=[("beanie", "right", 1)], b=[("beanie", "left", 1)], type="equal")]
    if o["brim"]:
        bl = circ * 0.92
        b = rect_piece("brim", "Brim", bl, 2 * brim_h, sa=sa, cut_count=1, fabric="Rib knit",
                       labels=("Seam edge", "Cross seam", "Seam edge", "Cross seam"))
        b.marks.append(Mark(G.line(G.P(0, brim_h), G.P(bl, brim_h)), "fold", "Fold line"))
        pieces.append(b)
        seams.append(dict(name="Brim ↔ beanie edge (stretched)", a=[("beanie", "bottom", 2)],
                          b=[("brim", "bottom", 1)], type="ratio", lo=0.88, hi=0.96))
    corners = [dict(name="Side ↔ crown (smooth)", piece="beanie", a="right", b="crown", target=180),
               dict(name="Bottom edge ↔ side", piece="beanie", a="bottom", b="right", target=90)]
    checks = [dict(name="Beanie fits over the head", kind="min", value=circ * (1 + stretch / 100), target=head * 1.05,
                   note="width incl. stretch"),
              dict(name="Beanie stays on (not too loose)", kind="range", value=circ, lo=head * 0.78, hi=head * 1.0,
                   note="negative ease for jersey")]
    pat = Pattern("beanie", "Beanie", "", pieces, dict(m), o, seams=seams, corners=corners, checks=checks)
    pat.finished = dict(circ=circ, height=H + brim_h)
    return pat


def assembly(pat):
    """The construction as one-action steps (see steps.py)."""
    import steps as ST
    out = [ST.seam("Sew side and crown seams", ["Side seams", "Crown seam"],
                   "Both pieces right sides together; in one go.", section="Beanie")]
    if pat.options.get("brim") and pat.has("brim"):
        out += [ST.ring("Close the brim into a ring", "brim", "Right sides together across the short ends.",
                        section="Brim"),
                ST.fold_band("Fold the brim in half", "brim", "Lengthwise, wrong sides together.", section="Brim"),
                ST.attach_band("Sew the brim on", "brim", ["Brim"], "beanie edge",
                               "Brim seam at the back seam; quarter both with pins.", section="Brim")]
    else:
        hs = pat.piece("beanie").edge("bottom").sa or 20.0
        out.append(ST.hem("Sew the hem", [("beanie", "bottom")], hs, f"Press {ST.cm(hs)} under.", repeat=2,
                          section="Hem"))
    out += [ST.icon("Turn right side out", "turn", section="Finish"), ST.done("")]
    return out


def sewing_steps(pat):
    import steps as ST
    return ST.as_texts(assembly(pat), pat.options)
