"""Cutting layout on fabric: grainline, nap/one-way prints, fold, mirrored pairs, distances,
stripe/plaid matching and fabric consumption (nesting.py + layout.layout_fabric)."""
from __future__ import annotations

import math

import numpy as np
import pytest
from shapely.geometry import Polygon

import generate as GN
import instructions as I
import layout as L

GAP = 5.0


def draft(garment, size, **opts):
    p, _, _ = GN.draft_from_spec(dict(garment=garment, size=size, options=opts))
    return p


def _check_plan(pattern, pl):
    """Every hard rule of a cutting layout, checked with exact geometry."""
    fold_len = pl.get("fold_length", 0.0) if pl["mode"] == "folded" else 0.0
    polys = []
    for q in pl["placements"]:
        pi, _k = pl["meta"][q.index]
        piece = pattern.pieces[pi]
        P = Polygon(L.placed_ring(pl["rings"][q.index], q))
        minx, miny, maxx, maxy = P.bounds
        in_fold = pl["mode"] == "folded" and q.dy < fold_len
        width = pl["width"] / 2 if in_fold else pl["width"]
        # grainline parallel to the selvage
        g = q.apply(np.array(piece.grain, dtype=float))
        d = g[1] - g[0]
        assert math.degrees(math.atan2(abs(d[0]), abs(d[1]))) < 0.5, piece.name
        # top end of the piece towards the top of the fabric with a nap or a directional print
        if pl["nap"]:
            assert L.up_y(q.angle) > 0, piece.name
        if q.pinned:
            assert abs(minx) < 0.01, f"{piece.name} not on the fold"
        else:
            assert minx >= (L.FOLD_CLEARANCE if in_fold else L.FABRIC_MARGIN) - 0.01, piece.name
        assert maxx <= width - L.FABRIC_MARGIN + 0.01, piece.name
        assert maxy <= pl["length"] + 0.01
        polys.append((in_fold, P, piece.name))
    for i in range(len(polys)):
        for j in range(i + 1, len(polys)):
            if polys[i][0] == polys[j][0]:
                assert polys[i][1].distance(polys[j][1]) >= GAP - 0.05, (polys[i][2], polys[j][2])


CASES = [
    ("pants_basic", "w38", dict(style="trousers", fabric="woven", pockets=["side"])),
    ("pants_basic", 122, dict(style="trousers", fabric="corduroy")),
    ("tshirt_basic", 140, {}),
    ("hoodie", 98, {}),
    ("skirt", "w38", dict(style="a_line")),
    ("tshirt_basic", "w38", dict(fabric_print="stripes", print_repeat_cm=3)),
]


@pytest.mark.parametrize("garment,size,opts", CASES)
@pytest.mark.parametrize("mode", ["single", "folded"])
def test_layout_rules(garment, size, opts, mode):
    p = draft(garment, size, **opts)
    for pl in L.layout_fabric(p, mode=mode).values():
        _check_plan(p, pl)


def test_mirrored_pairs_single_layer():
    """A pair cut on a single layer: one copy is placed face down (the mirror image)."""
    p = draft("pants_basic", 122, style="jogger")
    pl = L.layout_fabric(p, mode="single")["Main fabric"]
    by_piece: dict = {}
    for q in pl["placements"]:
        by_piece.setdefault(pl["meta"][q.index][0], []).append(q.mirrored)
    for pi, flags in by_piece.items():
        piece = p.pieces[pi]
        if piece.mirror and piece.cut_count == 2:
            assert sorted(flags) == [False, True], piece.name


def test_head_to_toe_saves_fabric():
    """Women's trousers 38 on 150 cm: legs nested head to toe instead of one after the other
    (the old packer needed 1.93 m of fabric for this)."""
    p = draft("pants_basic", "w38", style="trousers", fabric="woven", pockets=["side"])
    pl = L.layout_fabric(p, mode="auto")["Main fabric"]
    assert pl["length"] < 1450


def test_deterministic():
    p = draft("hoodie", 140)
    a = L.layout_fabric(p, mode="single")["Main fabric"]
    b = L.layout_fabric(p, mode="single")["Main fabric"]
    assert [(q.index, q.angle, q.dx, q.dy) for q in a["placements"]] == \
        [(q.index, q.angle, q.dx, q.dy) for q in b["placements"]]


def _phases(p, pl):
    rep = pl["repeat"]
    out = {}
    for q in pl["placements"]:
        my, mx = pl["match_pts"][q.index]
        if my is None:
            continue
        y = q.apply(np.array([my[0]], dtype=float))[0][1]
        ry = (y - my[1]) % rep[1]
        x = None
        if mx is not None:
            x = q.apply(np.array([mx[0]], dtype=float))[0][0] % rep[0]
            x = min(x, rep[0] - x)
        out.setdefault(p.pieces[pl["meta"][q.index][0]].key, []).append((min(ry, rep[1] - ry), x))
    return out


def test_stripes_match_at_side_seams_and_sleeves():
    p = draft("tshirt_basic", 140, fabric_print="stripes", print_repeat_cm=4)
    pl = L.layout_fabric(p, mode="single")["Main fabric"]
    assert pl["print"] == "stripes" and pl["nap"] and pl["repeat"] == (40.0, 40.0)
    ph = _phases(p, pl)
    assert {"front", "back", "sleeve"} <= set(ph)
    for key, vals in ph.items():
        for dy, _ in vals:
            assert dy < 0.01, key
    # sleeve underarm on the same stripe as the body's underarm: offset = side seam length
    front = p.pieces[[pc.key for pc in p.pieces].index("front")]
    side = front.edge("side")
    assert any(abs(L.match_points(p, range(len(p.pieces)))[i][0][1] + float(side.pts[-1][1] - side.pts[0][1])) < 0.01
               for i, pc in enumerate(p.pieces) if pc.key == "sleeve")
    _check_plan(p, pl)
    plain = L.layout_fabric(draft("tshirt_basic", 140), mode="single")["Main fabric"]
    assert pl["length"] >= plain["length"]       # matching never comes for free


def test_plaid_matches_both_ways_single_layer():
    p = draft("pants_basic", 122, style="trousers", fabric_print="plaid", print_repeat_cm=[5, 7])
    plans = L.layout_fabric(p, mode="auto")
    pl = plans["Main fabric"]
    assert pl["mode"] == "single" and pl["repeat"] == (50.0, 70.0)   # checks: single layer
    ph = _phases(p, pl)
    assert {"front", "back"} <= set(ph)
    for key, vals in ph.items():
        for dy, dx in vals:
            assert dy < 0.01 and dx is not None and dx < 0.01, key
    _check_plan(p, pl)


def test_one_way_print_is_cut_like_a_nap():
    p = draft("hoodie", 122, fabric_print="one_way")
    pl = L.layout_fabric(p, mode="single")["Main fabric"]
    assert pl["nap"] and pl["print"] == "one_way" and pl["repeat"] is None
    assert all(L.up_y(q.angle) > 0 for q in pl["placements"])
    assert not L.layout_fabric(p, mode="single")["Rib knit"]["nap"]


def test_print_options_validated():
    with pytest.raises(ValueError):
        L.fabric_print({"fabric_print": "polka"})
    kind, rep, note = L.fabric_print({"fabric_print": "stripes"})
    assert kind == "stripes" and rep == (50.0, 50.0) and note


def test_print_text_in_instructions(tmp_path):
    res = GN.run(dict(garment="tshirt_basic", size=122, formats=["a4"], out=str(tmp_path),
                      options=dict(fabric_print="stripes", print_repeat_cm=2.5)), verbose=False)
    md = (tmp_path / "sewing_instructions.md").read_text()
    assert "Matching stripes and checks" in md and "stripes: all pieces top end up" in md
    assert res["ok"]
    with pytest.raises(SystemExit):
        GN.main(["--garment", "tshirt_basic", "--size", "122", "--fabric-print", "polka"])


def test_cli_print_options(tmp_path):
    assert GN.main(["--garment", "skirt", "--size", "98", "--style", "a_line", "--format", "a4",
                    "--fabric-print", "plaid", "--print-repeat", "4,6", "--out", str(tmp_path)]) == 0
    md = (tmp_path / "sewing_instructions.md").read_text()
    assert "checks: all pieces top end up" in md


def test_fabric_consumption_render(tmp_path):
    p = draft("tshirt_basic", 98, fabric_print="stripes", print_repeat_cm=3)
    plans = I.fabric_consumption(p)
    out = I.render_fabric_png(p, plans, str(tmp_path / "cl.png"))
    assert (tmp_path / "cl.png").stat().st_size > 10_000 and out
