"""Mirrored hem corners, notch projection, DXF export, measurement files, construction values."""
import json
import math

import numpy as np
import pytest
from shapely.geometry import LineString, Polygon

import construction as K
import export_dxf as D
import geometry as G
import layout as L
import measure_files as MF
import measurements as M
import notches as N
import validate as V
from garments import get
from pattern import Edge, Notch, Pattern, Piece

MODULE_CASES = [
    ("pants_basic", {"style": "leggings"}),
    ("pants_basic", {"style": "trousers"}),
    ("pants_basic", {"style": "jogger", "cuffs": False}),
    ("tshirt_basic", {}),
    ("tshirt_basic", {"sleeve_style": "raglan", "sleeve_length": "long"}),
    ("hoodie", {}),
    ("skirt", {"style": "a_line"}),
    ("skirt", {"style": "circle"}),
    ("beanie", {"brim": False}),
    ("loop", {}),
]


def draft(garment, size, **opts):
    mm, _ = M.complete_measures({}, size)
    return get(garment).draft(mm, opts)


def tapered_piece(turned: bool) -> Piece:
    """Leg-like piece narrowing towards a 30 mm hem: side seams at 10° to the vertical."""
    dx = 300 * math.tan(math.radians(10))
    a, b, c, d = G.P(dx, 0), G.P(200 - dx, 0), G.P(200, 300), G.P(0, 300)
    edges = [Edge("hem", G.line(a, b), 30.0, turned=turned, label="Hem"),
             Edge("side", G.line(b, c), 10.0), Edge("top", G.line(c, d), 10.0),
             Edge("inseam", G.line(d, a), 10.0)]
    return Piece("leg", "Leg", edges, grain=(G.P(100, 50), G.P(100, 250)))


def _fold_error(piece):
    pat = Pattern("test", "Test", "", [piece], {}, {})
    return V.check_turned(pat)


# ---------------------------------------------------------------- mirrored corners

def test_mirrored_hem_corner_folds_flat():
    rows = _fold_error(tapered_piece(True))
    assert rows[0].status == "OK", rows[0].actual


def test_mitred_hem_corner_would_not_fold_flat():
    # same geometry, but the hem is not marked as turned: the plain mitre does not match
    p = tapered_piece(False)
    p.edges[0].turned = True                  # only evaluate, the outline stays mitred
    cut_mitre = G.offset_outline([e.pts for e in p.edges], [e.sa for e in p.edges])
    boundary = LineString(np.vstack([cut_mitre, cut_mitre[:1]]))
    err = V._fold_flat_error(p, p.edges[0], True, boundary)
    assert err > 1.0


def test_mirrored_corner_widens_tapered_hem():
    # side seams narrow towards the hem → the folded-up allowance must flare outwards
    mirr = tapered_piece(True).cut_ring()
    mitre = tapered_piece(False).cut_ring()
    assert G.width_at_y(mirr, -25.0) > G.width_at_y(mitre, -25.0) + 10.0
    assert Polygon(mirr).is_valid


@pytest.mark.parametrize("garment,opts", MODULE_CASES)
@pytest.mark.parametrize("size", [98, "w42"])
def test_turned_allowances_and_notches_all_modules(garment, opts, size):
    pat = draft(garment, size, **opts)
    report = V.validate(pat)
    assert V.is_ok(report), V.to_markdown(report)
    for c in report:
        if "turned allowance" in c.name or "notches" in c.name:
            assert c.status == "OK", (c.name, c.actual)


# ---------------------------------------------------------------- notches

def test_corner_notch_uses_bisector_and_hits_cut_line():
    p = tapered_piece(True)
    p.notches = [Notch("side", -0.5)]       # at the corner side → top
    m = N.resolve(p, p.notches[0])[0]
    assert m.corner
    assert not N.on_cut_line(p, [m])
    # bisector of a 90° corner (side edge ends at (200, 300)): roughly diagonal
    d = -m.direction
    assert abs(abs(d[0]) - abs(d[1])) < 0.35


@pytest.mark.parametrize("shape,n_lines", [("slit", 1), ("t", 2), ("v", 1)])
def test_notch_shapes(shape, n_lines):
    p = tapered_piece(True)
    p.notches = [Notch("side", 100.0, 2)]
    marks = N.resolve(p, p.notches[0], shape)
    assert len(marks) == 2
    assert all(len(m.lines) == n_lines for m in marks)
    if shape == "v":
        assert all(len(m.lines[0]) == 3 for m in marks)
    with pytest.raises(ValueError):
        N.resolve(p, p.notches[0], "zigzag")


# ---------------------------------------------------------------- DXF

@pytest.fixture(scope="module")
def harem():
    pat = draft("pants_basic", 122, style="harem")
    return pat, L.layout_roll(pat, 1600.0)


def test_dxf_header_layers_and_blocks(harem):
    pat, lay = harem
    d = D.read_dxf(D.to_dxf(pat, lay))
    assert d["header"]["$ACADVER"] == "AC1009"
    assert d["header"]["$INSUNITS"] == "4"          # millimetres
    assert len(d["blocks"]) == len(pat.pieces)
    assert len(d["entities"]["inserts"]) == len(lay.placements)
    for i, p in enumerate(pat.pieces):
        b = d["blocks"][D.block_name(i, p)]
        layers = {pl["layer"] for pl in b["polylines"]} | {ln["layer"] for ln in b["lines"]}
        assert "1" in layers and "7" in layers
        assert ("8" in layers) or ("6" in layers)
        assert len([pl for pl in b["polylines"] if pl["layer"] == "1"]) == 1
        if p.notches:
            assert sum(ln["layer"] == "4" for ln in b["lines"]) >= len(p.notches)
        if p.on_fold:
            assert any(pl["layer"] == "6" for pl in b["polylines"])
        assert any(t["text"].startswith("Piece Name:") for t in b["texts"])


def test_dxf_round_trip_outline(harem):
    pat, lay = harem
    d = D.read_dxf(D.to_dxf(pat, lay))
    for i, p in enumerate(pat.pieces):
        cut = [pl for pl in d["blocks"][D.block_name(i, p)]["polylines"] if pl["layer"] == "1"][0]
        assert cut["closed"]
        ref = LineString(np.vstack([p.cut_ring(), p.cut_ring()[:1]]))
        got = LineString(np.vstack([cut["pts"], cut["pts"][:1]]))
        assert ref.hausdorff_distance(got) <= 0.1


def test_dxf_inserts_match_layout(harem):
    pat, lay = harem
    d = D.read_dxf(D.to_dxf(pat, lay))
    H = lay.canvas_h or lay.page_h
    for ins, pl in zip(d["entities"]["inserts"], lay.placements):
        cut = [x for x in d["blocks"][ins["name"]]["polylines"] if x["layer"] == "1"][0]["pts"].copy()
        cut[:, 0] *= ins["xscale"]
        a = math.radians(ins["angle"])
        rot = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])
        placed = cut @ rot.T + [ins["x"], ins["y"]]
        ref = pl.apply(pat.pieces[pl.index].cut_ring())
        ref[:, 1] = H - ref[:, 1]
        assert Polygon(placed).symmetric_difference(Polygon(ref)).area < 0.01 * Polygon(ref).area


def test_dxf_control_square_and_seam_layer(harem):
    pat, lay = harem
    d = D.read_dxf(D.to_dxf(pat, lay, seam_layer="14"))
    sq = [pl for pl in d["entities"]["polylines"] if pl["closed"]][0]["pts"]
    w, h = np.ptp(sq[:, 0]), np.ptp(sq[:, 1])
    assert abs(w - 50.0) < 1e-6 and abs(h - 50.0) < 1e-6
    front = d["blocks"][D.block_name(0, pat.pieces[0])]
    assert any(pl["layer"] == "14" for pl in front["polylines"])
    assert not any(pl["layer"] == "8" and not pl["closed"] and len(pl["pts"]) > 50 for pl in front["polylines"])
    with pytest.raises(ValueError):
        D.to_dxf(pat, lay, seam_layer="3")


def test_dxf_is_ascii_and_without_layout(tmp_path):
    pat = draft("loop", 122)
    path = D.write_dxf(pat, str(tmp_path / "loop.dxf"))
    raw = open(path, "rb").read()
    raw.decode("ascii")
    assert raw.rstrip().endswith(b"EOF")
    assert len(D.read_dxf(path)["entities"]["inserts"]) == len(pat.pieces)


# ---------------------------------------------------------------- measurement files

def test_measure_file_round_trip(tmp_path):
    mm, _ = M.complete_measures({}, "w40")
    path = MF.write_file(str(tmp_path / "w40.smis"), mm, given_name="Test")
    back, warn = MF.read_file(path)
    assert not warn
    for k, v in back.items():
        assert abs(v * 10 - mm[k]) < 0.06, k
    assert set(back) >= {"chest", "waist", "hip", "inseam", "side_length", "height"}


def test_measure_file_formulas_units_and_old_format(tmp_path):
    p = tmp_path / "old.vit"
    p.write_text("""<?xml version="1.0" encoding="UTF-8"?>
<vit><version>0.3.3</version><unit>inch</unit>
<body-measurements>
  <m name="hip_circ" value="40"/>
  <m name="waist_circ" value="hip_circ - 10"/>
  <m name="leg_crotch_to_floor" value="(30)"/>
  <m name="neck_mid_circ" value="14,5"/>
  <m name="foot_length" value="10"/>
  <m name="height_knee" value="__import__('os')"/>
</body-measurements></vit>""", encoding="utf-8")
    vals, warn = MF.read_file(str(p))
    assert vals["hip"] == pytest.approx(101.6)
    assert vals["waist"] == pytest.approx(76.2)
    assert vals["inseam"] == pytest.approx(76.2)
    assert vals["neck"] == pytest.approx(36.83)             # fallback name, decimal comma
    assert any("height_knee" in w for w in warn)
    assert any("not used" in w for w in warn)


# ---------------------------------------------------------------- construction values

def test_construction_values_recorded_and_overridable():
    base = draft("pants_basic", 122, style="harem")
    names = {r["name"] for r in base.construction}
    assert {"hip_width", "back_crotch_extension", "rise", "hem_width"} <= names
    rise = next(r["value"] for r in base.construction if r["name"] == "rise")
    adj = draft("pants_basic", 122, style="harem", construction={"rise": rise + 20, "nonsense": 1})
    row = next(r for r in adj.construction if r["name"] == "rise")
    assert row["overridden"] and row["value"] == pytest.approx(rise + 20)
    assert any("nonsense" in n for n in adj.notes)
    assert V.is_ok(V.validate(adj))
    h0 = G.bbox(base.piece("front").seam_ring())
    h1 = G.bbox(adj.piece("front").seam_ring())
    assert (h1[3] - h1[1]) - (h0[3] - h0[1]) == pytest.approx(20, abs=1.0)
    md = K.to_markdown(adj.construction)
    assert "| `rise` |" in md and "overridden" in md


def test_construction_values_tops():
    for g in ("tshirt_basic", "hoodie"):
        pat = draft(g, "w38")
        names = {r["name"] for r in pat.construction}
        assert {"chest_width", "armhole_depth", "body_length"} <= names
    json.dumps(pat.summary(), default=str)


# ---------------------------------------------------------------- size tables

def test_kids_size_table_is_smooth():
    """Every measurement grows with the size and no step is an outlier (> 2.5 × median step)."""
    keys = sorted(M.KIDS_TABLE)
    arr = np.array([M.KIDS_TABLE[k] for k in keys])
    for j, col in enumerate(M.KIDS_COLS):
        steps = np.diff(arr[:, j])
        assert (steps >= 0).all(), col
        med = float(np.median(steps))
        assert steps.max() <= 2.5 * med + 0.5, (col, steps)


# ---------------------------------------------------------------- end to end

def test_generate_dxf_measure_file_and_construction(tmp_path):
    import generate

    src = MF.write_file(str(tmp_path / "kid.smis"), M.complete_measures({}, 128)[0])
    res = generate.run(dict(garment="pants_basic", size=122, measures_file=src, measures_cm={"hip": 70},
                            options={"style": "jogger", "notch_style": "v", "construction": {"rise": 240}},
                            formats=["dxf"], export_measures=True, out=str(tmp_path / "out")), verbose=False)
    assert res["ok"]
    files = res["files"]
    dxf = next(v for k, v in files.items() if k.startswith("DXF"))
    assert dxf.endswith("_aama.dxf") and D.read_dxf(dxf)["blocks"]
    assert res["pattern"].measures["hip"] == pytest.approx(700)          # explicit value beats the file
    assert res["pattern"].measures["height"] == pytest.approx(1280)      # from the file
    exported, _ = MF.read_file(files["Body measurements (XML measurement file)"])
    assert exported["hip"] == pytest.approx(70)
    assert "### Construction values" in res["report_md"] and "overridden" in res["report_md"]
