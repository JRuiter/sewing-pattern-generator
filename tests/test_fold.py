"""Cut-on-fold edges: validation (straight, no allowance, 90° corners, on grain), the printed
fold symbol (fits short edges, avoids inner lines) and the cutting instructions."""
import numpy as np
import pytest

import doll as D
import instructions as I
import render as R
import validate as V
from garments import get
from pattern import Mark, rect_piece

DOLL_CM = {"height": 45, "chest": 30, "waist": 28, "hip": 31, "head": 32, "arm": 12, "inseam": 14,
           "side_length": 22}


def adult(garment, opts=None, size="122"):
    import measurements as M
    m, _ = M.complete_measures(None, size)
    return get(garment).draft(m, dict(get(garment).DEFAULTS, **(opts or {})))


def doll(garment, opts=None):
    m, _ = D.complete_measures(DOLL_CM)
    return D.draft(get(garment), garment, m, D.defaults(garment, opts or {}, m))


@pytest.mark.parametrize("pat", [
    pytest.param(lambda: adult("tshirt_basic"), id="tshirt"),
    pytest.param(lambda: adult("skirt", {"style": "circle"}), id="circle-skirt"),
    pytest.param(lambda: adult("hoodie"), id="hoodie"),
    pytest.param(lambda: doll("dress"), id="doll-dress"),
    pytest.param(lambda: doll("skirt"), id="doll-skirt"),
])
def test_fold_edges_of_all_garments_pass(pat):
    p = pat()
    rows = V.check_folds(p)
    assert rows and len(rows) == sum(pc.on_fold for pc in p.pieces)
    assert all(r.status == "OK" for r in rows), [(r.name, r.actual) for r in rows]


def _fold_piece():
    return rect_piece("panel", "Panel", 100, 200, sa=10, fold_left=True, cut_count=1)


def _check(pc):
    return V.check_folds(type("P", (), {"pieces": [pc]})())[0]


def test_fold_check_flags_slanted_corner_and_allowance():
    import geometry as G
    assert _check(_fold_piece()).status == "OK"
    # a top edge that meets the fold at 80°: opened out, the piece gets a peak at the centre
    pc = _fold_piece()
    top = pc.edge("top")
    top.pts = G.line(G.P(100, 200 + 100 * np.tan(np.radians(10))), G.P(0, 200))
    res = _check(pc)
    assert res.status == "ERROR" and "meets" in res.actual
    pc2 = _fold_piece()
    next(e for e in pc2.edges if e.fold).sa = 10.0
    res2 = _check(pc2)
    assert res2.status == "ERROR" and "seam allowance" in res2.actual
    # a fold edge that is not straight cannot be a mirror line
    pc3 = _fold_piece()
    fe = next(e for e in pc3.edges if e.fold)
    fe.pts = fe.pts + np.c_[np.sin(np.linspace(0, np.pi, len(fe.pts))) * 3, np.zeros(len(fe.pts))]
    assert "not straight" in _check(pc3).actual


def test_fold_symbol_fits_short_doll_waistband():
    band = next(pc for pc in doll("skirt").pieces if pc.key == "waistband")
    fe = next(e for e in band.edges if e.fold)
    assert fe.length < 40
    sym = R.fold_symbol(fe, [mk.pts for mk in band.marks] + [np.array(band.grain, float)])
    assert R.text_w_mm(sym["text"], sym["size"], True) < fe.length
    assert sym["span"] <= fe.length
    # the symbol stays inside the piece and clear of the waistband fold line
    from shapely.geometry import LineString, Polygon
    assert Polygon(band.seam_ring()).buffer(0.5).contains(sym["region"])
    for mk in band.marks:
        assert not sym["region"].intersects(LineString(mk.pts))


def test_fold_symbol_avoids_the_fold_line_of_a_waistband():
    band = rect_piece("waistband", "Waistband", 300, 80, sa=10, fold_left=True)
    band.marks.append(Mark(np.array([[0.0, 40.0], [300.0, 40.0]]), "fold", "Fold line"))
    fe = next(e for e in band.edges if e.fold)
    sym = R.fold_symbol(fe, [mk.pts for mk in band.marks])
    from shapely.geometry import LineString
    assert not sym["region"].intersects(LineString(band.marks[0].pts))
    assert sym["text"] in R.FOLD_TEXTS


def test_long_fold_edge_gets_full_text():
    pc = _fold_piece()
    sym = R.fold_symbol(next(e for e in pc.edges if e.fold))
    assert sym["text"] == "PLACE ON FOLD" and sym["size"] == R.FOLD_SIZES[0]
    assert sym["span"] <= R.FOLD_MAX_SPAN


def test_instructions_explain_cutting_on_fold():
    pat = doll("dress")
    single = {"Main fabric": dict(mode="single")}
    folded = {"Main fabric": dict(mode="folded")}
    t1, t2 = I.fold_text(pat, single), I.fold_text(pat, folded)
    assert "Front" in t1 and "flip it over along the fold edge" in t1 and "fabric fold" not in t1
    assert "lay the fold edge exactly on the fabric fold" in t2
    assert I.fold_text(adult("loop"), single) is None      # no fold piece, no paragraph


def test_label_block_keeps_clear_of_the_fold_symbol():
    from shapely.geometry import Point
    pat = adult("pants_basic", {"style": "harem"})
    band = pat.piece("waistband")
    prims = R.piece_prims(band, pat)
    assert any(p.style == "fold_arrow" for p in prims if p.kind == "line")
    fe = next(e for e in band.edges if e.fold)
    region = R.fold_symbol(fe, [mk.pts for mk in band.marks] + [np.array(band.grain, float)])["region"]
    labels = [p for p in prims if p.kind == "text" and p.style == "label"]
    assert labels and not any(region.contains(Point(R.text_pos(p))) for p in labels)
