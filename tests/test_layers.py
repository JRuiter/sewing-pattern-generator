"""Fabric layers in the booklet pictures: pieces stacked right sides together lie as on the table.
The top piece is face down (mirror image unless it is cut as a mirrored pair or on the fold) and
stays upright when an upright fit exists (no shoulder turned, no piece upside down)."""
import math

import pytest

import diagrams as DG
import generate as GN
import steps as ST
from garments import GARMENTS, get


def _pattern(g):
    mod = get(g)
    if getattr(mod, "NO_MEASURES", False):
        return GN.draft_from_spec(dict(garment=g, options={}))[0]
    for size in (122, 86, "w38"):
        try:
            return GN.draft_from_spec(dict(garment=g, size=size, options={}))[0]
        except ValueError:
            continue
    pytest.skip(f"{g}: no test size")


@pytest.mark.parametrize("garment", list(GARMENTS))
def test_stacked_layers(garment):
    pat = _pattern(garment)
    bad = []
    for s in ST.assembly(pat):
        if s.diagram != "seam":
            continue
        for sm in ST.resolve_seams(pat, s):
            r = DG.overlay_parts(pat, sm)
            if not r:
                continue
            A, ea, B, eb, (R, _t, flip) = r
            turn = abs(math.degrees(math.atan2(R[1, 0], R[0, 0])))
            if not flip and not (B.mirror or B.on_fold):
                bad.append(f"{s.title}: {B.key} right side up, not face down")
            if A.key == B.key and ea != eb and not flip and turn > 90:
                bad.append(f"{s.title}: {B.key} turned upside down onto itself")
            if (B.mirror or B.on_fold) and {"side", "shoulder", "inseam"} & {ea, eb} and turn > 20:
                bad.append(f"{s.title}: {B.key} turned by {turn:.0f}° (pieces lie upright)")
    assert not bad, bad
