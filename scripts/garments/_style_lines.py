"""Style lines as a reusable modifier on the tops and dress blocks (option `style_lines`):

- `princess`: armhole princess seams on front and back, from the armhole curving down to the hem
  (a style line: the fit stays the same, the panels can be cut from different fabrics)
- `yoke`: a front and a back yoke, a straight seam across the chest and the shoulder blades
- `color_block`: the body split across the chest; the upper part in a contrast fabric

Applied after the module drafted the pattern (allowance.draft). The front and back keep their keys
(the part with the neckline); the new panels are `front_side`/`back_side` or `front_lower`/`back_lower`,
part of the front/back view. The steps of the module are re-pointed to the panel that now holds an
edge, and the style seams are sewn first.
"""
from __future__ import annotations

import numpy as np

import geometry as G
from pattern import Notch

from . import _parts as PT

KINDS = ("princess", "yoke", "color_block")
SUPPORTED = ("tshirt_basic", "hoodie", "dress", "sweater")
CONTRAST = "Contrast fabric"


def _cut(pc, kind: str, F: dict, back: bool):
    ring = pc.seam_ring()
    xmax = float(ring[:, 0].max()) + 30
    if kind == "princess":
        arm = pc.edge("armhole").pts
        seg = np.r_[0, np.cumsum(np.hypot(*np.diff(arm, axis=0).T))]
        s = seg[-1] * (0.45 if back else 0.5)
        a = np.array([np.interp(s, seg, arm[:, 0]), np.interp(s, seg, arm[:, 1])])
        hem = pc.edge("hem").pts
        y_h = float(hem[:, 1].min()) - 30
        x_h = 0.5 * F["q"] + (0.03 * F["q"] if back else 0)
        y_w = -F["AD"] - 0.45 * (abs(y_h) - F["AD"])
        start = a + G.P(8, 6)
        return G.cubic(start, a + G.P(-0.18 * F["q"], -0.25 * F["AD"]), G.P(x_h, y_w + 0.25 * F["AD"]), G.P(x_h, y_h))
    y = -(0.62 * F["AD"]) if kind == "yoke" else -(F["AD"] + 30)
    return G.line(G.P(-30, y), G.P(xmax, y))


def apply(pat, kind: str) -> None:
    if kind in (None, "", "none", False):
        return
    if kind not in KINDS:
        raise ValueError(f"style_lines must be one of {', '.join(KINDS)}")
    if pat.garment not in SUPPORTED or not (pat.has("front") and pat.has("back")):
        raise ValueError(f"style lines are available for {', '.join(SUPPORTED)}")
    F = pat.options["_F"]
    for view in ("front", "back"):
        pc = pat.piece(view)
        cut = _cut(pc, kind, F, view == "back")
        other = view + ("_side" if kind == "princess" else "_lower")
        p1, p2 = PT.split_piece(pc, cut, (view, other), (pc.name, pc.name), label="Style seam")
        main, panel = (p1, p2) if any(e.name.startswith("neckline") for e in p1.edges) else (p2, p1)
        main.key, panel.key = view, other
        side_name = "side panel" if kind == "princess" else "lower part"
        if kind == "princess":
            main.name = ("Front" if view == "front" else "Back") + " centre panel"
        elif kind == "yoke":
            main.name = ("Front" if view == "front" else "Back") + " yoke"
        else:
            main.name = ("Front" if view == "front" else "Back") + " upper part (contrast)"
            main.fabric = CONTRAST
        panel.name = ("Front" if view == "front" else "Back") + " " + side_name
        if not panel.on_fold:
            panel.cut_count, panel.mirror = 2, True
        panel.part_of = view
        for p in (main, panel):
            p.notches.append(Notch("split", p.edge("split").length / 2, 1 if view == "front" else 2))
        PT.replace_piece(pat, view, [main, panel])
        pat.seams.append(dict(name=f"Style seam {view}", a=[(view, "split", 1)], b=[(other, "split", 1)],
                              type="equal"))
    pat.options["style_lines"] = kind
    label = {"princess": "princess seams", "yoke": "front and back yoke", "color_block": "colour blocking"}[kind]
    pat.notes.append(f"Style lines: {label}" + (" (upper part in a contrast fabric)" if kind == "color_block" else ""))


def repoint(pat, steps: list) -> list:
    """Steps written for a whole front/back: point each edge (and placement mark) at the panel that
    holds it now (yokes, side panels, style lines)."""
    def holder(k, e):
        if not pat.has(k) or any(x.name == e for x in pat.piece(k).edges):
            return k
        return next((p.key for p in pat.pieces if p.part_of == k and any(x.name == e for x in p.edges)), k)

    def mark_holder(k, label):
        if not pat.has(k) or any(m.label == label for m in pat.piece(k).marks):
            return k
        return next((p.key for p in pat.pieces if p.part_of == k and any(m.label == label for m in p.marks)), k)
    for st in steps:
        st.edges = [(holder(k, e), e) for k, e in st.edges]
        if st.data.get("mark"):
            st.pieces = [mark_holder(k, st.data["mark"]) for k in st.pieces]
    return steps


def adjust_steps(pat, steps: list) -> list:
    """Sew the style seams first."""
    kind = pat.options.get("style_lines")
    if not kind:
        return steps
    import steps as ST
    sa = ST.cm(next(e.sa for e in pat.piece("front").edges if e.name == "split"))
    text = {"princess": "Lay each side panel right sides together onto the centre panel, the notches matching, and "
                        f"sew the princess seam with {sa} seam allowance; ease the curve in, do not stretch it. Press "
                        "the allowances towards the side.",
            "yoke": f"Lay the yoke right sides together onto the lower part and sew with {sa} seam allowance. Press "
                    "the allowances up towards the yoke and topstitch them if you like.",
            "color_block": "Lay the contrast upper part right sides together onto the lower part and sew with "
                           f"{sa} seam allowance. Press the allowances down."}[kind]
    first = [ST.seam("Sew the style seams (front)", ["Style seam front"], text, section="Style lines",
                     repeat=2 if pat.has("front_side") and pat.piece("front_side").cut_count == 2 and
                     kind == "princess" else 1),
             ST.seam("Sew the style seams (back)", ["Style seam back"], "The same on the back.", section="Style lines",
                     repeat=2 if kind == "princess" else 1)]
    return first + steps


class _PieceView:
    def __init__(self, pat, pc):
        self._pat, self._pc = pat, pc

    def edge(self, name):
        for p in [self._pc] + [p for p in self._pat.pieces if p.part_of == self._pc.key]:
            for e in p.edges:
                if e.name == name:
                    return e
        return self._pc.edge(name)

    def __getattr__(self, name):
        return getattr(self._pc, name)


class PanelView:
    """The pattern as the module's assembly sees it: front/back answer for the edges of their panels."""

    def __init__(self, pat):
        self._pat = pat

    def piece(self, key):
        return _PieceView(self._pat, self._pat.piece(key))

    def __getattr__(self, name):
        return getattr(self._pat, name)
