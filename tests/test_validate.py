"""Sewability checks, garments in 3 sizes and print output."""
import re
import shutil
import subprocess

import numpy as np
import pytest

import geometry as G
import layout as L
import measurements as M
import render as R
import validate as V
from garments import get

SIZES = [98, 122, 152]
ADULT = ["w38", "m52"]
CASES = [
    ("pants_basic", {"style": "harem", "fabric": "sweat"}),
    ("pants_basic", {"style": "jogger"}),
    ("pants_basic", {"style": "leggings"}),
    ("pants_basic", {"style": "trousers"}),
    ("tshirt_basic", {}),
    ("tshirt_basic", {"sleeve_style": "raglan", "sleeve_length": "long"}),
    ("tshirt_basic", {"neckline": "v", "fabric": "jersey_elastane"}),
    ("hoodie", {}),
    ("hoodie", {"sleeve_style": "raglan", "hood_lining": True}),
    ("skirt", {"style": "gathered"}),
    ("skirt", {"style": "a_line"}),
    ("skirt", {"style": "circle"}),
    ("dress", {}),
    ("dress", {"skirt": "a_line", "pockets": True, "fabric": "woven"}),
    ("dress", {"skirt": "circle", "sleeve_length": "long"}),
    ("dress", {"style": "shirt_dress"}),
    ("beanie", {}),
    ("loop", {}),
]


def draft(garment, size, **opts):
    mm, _ = M.complete_measures({}, size)
    return get(garment).draft(mm, opts)


def statuses(report, area=None):
    return {c.name: c.status for c in report if area is None or c.area == area}


# ---------------------------------------------------------------------------
# Every garment in 3 sizes (+ adults)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("garment,opts", CASES, ids=[f"{g}-{'-'.join(map(str, o.values())) or 'standard'}" for g, o in CASES])
@pytest.mark.parametrize("size", SIZES + ADULT)
def test_garment_is_sewable(garment, opts, size):
    pat = draft(garment, size, **opts)
    report = V.validate(pat)
    bad = [(c.name, c.actual) for c in report if c.status == "ERROR"]
    assert not bad, bad
    for pc in pat.pieces:
        assert pc.grain is not None, pc.name
        assert pc.cut_count >= 1, pc.name
        assert G.ring_is_valid(pc.cut_ring()), pc.name


# ---------------------------------------------------------------------------
# Every check must detect a broken pattern (negative tests)
# ---------------------------------------------------------------------------

@pytest.fixture
def harem():
    return draft("pants_basic", 122, style="harem", fabric="sweat")


def test_seam_length_mismatch_detected(harem):
    e = harem.piece("back").edge("side")
    e.pts = e.pts.copy()
    e.pts[-1] = e.pts[-1] + np.array([0.0, 8.0])          # side seam 8 mm longer
    st = statuses(V.check_seams(harem))
    assert st["Side seam front ↔ back"] == "ERROR"


def test_rib_ratio_out_of_range_detected(harem):
    seam = next(s for s in harem.seams if s.get("type") == "ratio")
    seam["lo"], seam["hi"] = 0.95, 0.99                    # the rib would be far too short
    assert any(c.status != "OK" for c in V.check_seams(harem) if c.name == seam["name"])


def test_sleeve_cap_ease_checked():
    pat = draft("tshirt_basic", 122)
    seam = next(s for s in pat.seams if s.get("type") == "ease")
    seam["lo"], seam["hi"] = 40.0, 60.0                    # implausible amount of ease
    assert any(c.status == "ERROR" for c in V.check_seams(pat) if c.name == seam["name"])


def test_corner_angle_detected(harem):
    corner = next(c for c in harem.corners if "sum" not in c)
    corner["target"] = corner["target"] + 20                # corner is off by 20°
    assert any(c.status == "ERROR" for c in V.check_corners(harem) if c.name == corner["name"])


def test_joined_corner_detected(harem):
    corner = next(c for c in harem.corners if "sum" in c)
    corner["target"] = corner["target"] - 15
    assert any(c.status == "ERROR" for c in V.check_corners(harem) if c.name == corner["name"])


def test_circumference_check_detected(harem):
    chk = next(c for c in harem.checks if c["kind"] == "circ")
    chk["value"] = chk["target"] * 1.05                     # 5 % off
    assert any(c.status == "ERROR" for c in V.check_values(harem) if c.name == chk["name"])


def test_head_opening_check():
    pat = draft("tshirt_basic", 122)
    chk = next(c for c in pat.checks if "head" in c["name"])
    chk["value"] = chk["target"] * 0.8
    assert any(c.status == "ERROR" for c in V.check_values(pat) if c.name == chk["name"])


def test_self_intersection_detected(harem):
    pc = harem.piece("front")
    e = pc.edge("side")
    pts = e.pts.copy()
    mid = len(pts) // 2
    pts[mid] = pts[mid] + np.array([-400.0, 0.0])           # spike across the piece
    e.pts = pts
    st = statuses(V.check_geometry(harem))
    assert st[f"{pc.name}: outline & seam allowance"] == "ERROR"


def test_missing_seam_allowance_detected(harem):
    pc = harem.piece("front")
    pc.edge("side").sa = 0.0
    st = statuses(V.check_geometry(harem))
    assert st[f"{pc.name}: outline & seam allowance"] == "ERROR"


def test_missing_grainline_detected(harem):
    pc = harem.piece("front")
    pc.grain = None
    st = statuses(V.check_geometry(harem))
    assert st[f"{pc.name}: grainline & cutting"] == "ERROR"


def test_raise_on_error(harem):
    harem.piece("front").grain = None
    with pytest.raises(V.ValidationError):
        V.validate(harem, raise_on_error=True)


def test_report_table(harem):
    md = V.to_markdown(V.validate(harem))
    assert "Sewability check" in md and "✅ OK" in md
    assert "sewable" in md


# ---------------------------------------------------------------------------
# Print output
# ---------------------------------------------------------------------------

CTRL = 50.0 / 25.4 * 72.0          # 141.73 pt


def _page_streams(path):
    from pypdf import PdfReader
    rd = PdfReader(str(path))
    out = []
    for pg in rd.pages:
        c = pg.get_contents()
        out.append(c.get_data().decode("latin-1") if c is not None else "")
    return rd, out


def _has_control_square(stream):
    for m in re.finditer(r"(-?[\d.]+) (-?[\d.]+) re", stream):
        w, h = float(m.group(1)), float(m.group(2))
        if abs(w - CTRL) < 0.01 and abs(h - CTRL) < 0.01:
            return True
    return False


@pytest.fixture(scope="module")
def harem_mod():
    return draft("pants_basic", 122, style="harem", fabric="sweat")


@pytest.fixture(scope="module")
def roll_pdf(harem_mod, tmp_path_factory):
    lay = L.layout_roll(harem_mod, 610)
    p = tmp_path_factory.mktemp("roll") / "roll.pdf"
    R.render_roll_pdf(harem_mod, lay, str(p))
    return lay, p


@pytest.fixture(scope="module")
def a4_pdf(harem_mod, tmp_path_factory):
    lay = L.layout_tiles(harem_mod, "A4")
    p = tmp_path_factory.mktemp("a4") / "a4.pdf"
    R.render_tiles_pdf(harem_mod, lay, str(p))
    return lay, p


def test_control_square_exact_roll(roll_pdf):
    _, p = roll_pdf
    _, streams = _page_streams(p)
    assert abs(CTRL - 141.73) < 0.01
    assert all(_has_control_square(s) for s in streams)


def test_control_square_on_every_a4_page(a4_pdf):
    _, p = a4_pdf
    _, streams = _page_streams(p)
    assert len(streams) >= 2
    assert all(_has_control_square(s) for s in streams)


def test_fonts_embedded_and_no_hairlines(roll_pdf, a4_pdf):
    for _, p in (roll_pdf, a4_pdf):
        raw = open(p, "rb").read()
        assert b"/FontFile2" in raw                    # TrueType embedded
        rd, streams = _page_streams(p)
        for s in streams:
            widths = [float(x) for x in re.findall(r"(?<![\w.])([\d.]+) w\b", s)]
            assert widths and min(widths) >= 0.5, min(widths or [0])


def test_roll_page_size_and_portrait(roll_pdf):
    lay, p = roll_pdf
    rd, _ = _page_streams(p)
    w = float(rd.pages[0].mediabox.width) * 25.4 / 72
    h = float(rd.pages[0].mediabox.height) * 25.4 / 72
    assert abs(w - 600.0) < 0.05
    assert h > w


@pytest.mark.parametrize("roll", [610, 914])
def test_roll_layout_gap_and_width(harem_mod, roll):
    lay = L.layout_roll(harem_mod, roll)
    assert abs(lay.page_w - (roll - 10)) < 1e-6
    assert lay.page_h >= lay.page_w                      # portrait
    assert len(lay.placements) == len(harem_mod.pieces)
    rings = [pc.cut_ring() for pc in harem_mod.pieces]
    assert L.min_gap(rings, lay.placements) >= 10.0 - 0.5
    for pl in lay.placements:
        ring = L.placed_ring(harem_mod.pieces[pl.index].cut_ring(), pl)
        assert ring[:, 0].min() >= -0.5 and ring[:, 0].max() <= lay.page_w + 0.5


def test_a4_tiles_no_empty_pages_and_labels(a4_pdf, harem_mod):
    lay, p = a4_pdf
    pages = [t for t in lay.tiles if not t["empty"]]
    rd, _ = _page_streams(p)
    assert len(rd.pages) == len(pages) + 1                # + overview page
    assert all(re.fullmatch(r"[A-Z]\d+", t["label"]) for t in pages)
    text = rd.pages[0].extract_text()
    assert "100" in text                                   # note "print at 100 %"


def test_a4_overlap_windows():
    tiles, (nr, nc) = L._tile_windows(500, 700, 194, 281)
    for t in tiles:
        x0, y0, x1, y1 = t["window"]
        right = [u for u in tiles if u["row"] == t["row"] and u["col"] == t["col"] + 1]
        if right:
            assert abs((x1 - right[0]["window"][0]) - L.OVERLAP) < 1e-9


@pytest.mark.skipif(shutil.which("pdftoppm") is None, reason="pdftoppm (poppler) missing")
def test_a4_overlap_content_identical(harem_mod, tmp_path, monkeypatch):
    """After gluing the pages together, the pattern lines in the overlap strip must coincide."""
    from PIL import Image
    # hide page decorations (glue marks, control squares): only the pattern counts
    monkeypatch.setattr(R, "_tile_decorations", lambda lay: [])
    monkeypatch.setattr(R, "_draw_deco", lambda *a, **k: None)
    monkeypatch.setattr(R, "control_squares_pdf", lambda *a, **k: None)
    monkeypatch.setattr(R, "control_squares_pdf_single", lambda *a, **k: None)
    lay = L.layout_tiles(harem_mod, "A4")
    p = tmp_path / "a4.pdf"
    R.render_tiles_pdf(harem_mod, lay, str(p))
    pages = [t for t in lay.tiles if not t["empty"]]
    by = {(t["row"], t["col"]): i + 2 for i, t in enumerate(pages)}   # page 1 = overview
    dpi = 150
    pxmm = dpi / 25.4
    m, pw, ph, ov = lay.meta["margin"], lay.meta["pw"], lay.meta["ph"], L.OVERLAP
    checked = 0
    for (r, c), pno in by.items():
        if (r, c + 1) not in by:
            continue
        imgs = []
        for n in (pno, by[(r, c + 1)]):
            out = tmp_path / f"p{n}"
            subprocess.run(["pdftoppm", "-r", str(dpi), "-gray", "-f", str(n), "-l", str(n), "-png", str(p), str(out)],
                           check=True)
            f = next(tmp_path.glob(f"p{n}*.png"))
            imgs.append(np.asarray(Image.open(f)) < 110)
        a, b = imgs
        ya, yb = int((m + 15) * pxmm), int((m + ph - 2) * pxmm)        # skip the header line
        xa0, xa1 = int((m + pw - ov + 1.5) * pxmm), int((m + pw - 1.5) * pxmm)
        xb0 = int((m + 1.5) * pxmm)
        sa = a[ya:yb, xa0:xa1]
        sb = b[ya:yb, xb0:xb0 + (xa1 - xa0)]
        if sa.sum() + sb.sum() < 20:
            continue
        from scipy.ndimage import binary_dilation
        miss_a = (sa & ~binary_dilation(sb, iterations=2)).sum() / max(1, sa.sum())
        miss_b = (sb & ~binary_dilation(sa, iterations=2)).sum() / max(1, sb.sum())
        assert miss_a < 0.03 and miss_b < 0.03, (r, c, miss_a, miss_b)
        checked += 1
    assert checked >= 1


def test_sheets_a0_a1(harem_mod):
    for paper in ("A0", "A1"):
        lay, tiled = L.layout_sheets(harem_mod, paper)
        assert lay.sheets >= 1
        assert len(lay.placements) + (len(tiled.placements) if tiled else 0) == len(harem_mod.pieces)


def test_oversize_piece_on_roll_is_tiled(tmp_path):
    """Women's circle skirt: piece wider than the roll → strips to glue instead of failing."""
    import generate as GN
    pat = draft("skirt", "w38", style="circle")
    with pytest.raises(ValueError):
        L.layout_roll(pat, 610)
    res = GN.run(dict(garment="skirt", size="w38", options={"style": "circle"}, formats=["roll610"],
                      out=str(tmp_path)), verbose=False)
    assert res["ok"]
    assert any("strips" in k for k in res["files"])
    assert any("wider than the roll" in w for w in res["warnings"])


def test_svg_master_is_1to1(harem_mod, tmp_path):
    lay = L.layout_roll(harem_mod, 610)
    p = tmp_path / "m.svg"
    R.render_svg(harem_mod, lay, str(p))
    head = p.read_text(encoding="utf-8")[:500]
    assert re.search(r'width="[\d.]+mm"', head) and "viewBox" in head


# ---------------------------------------------------------------------------
# Cutting layout on folded fabric (#3)
# ---------------------------------------------------------------------------

def _placed(plan, pl):
    return L.placed_ring(plan["rings"][pl.index], pl)


def test_folded_layout_not_longer_than_single(harem):
    single = L.layout_fabric(harem, mode="single")["Main fabric"]
    folded = L.layout_fabric(harem, mode="folded")["Main fabric"]
    assert folded["mode"] == "folded"
    assert folded["length"] <= single["length"]
    auto = L.layout_fabric(harem, mode="auto")["Main fabric"]
    assert auto["length"] == min(single["length"], folded["length"])


@pytest.mark.parametrize("garment,opts", [("pants_basic", {"style": "harem", "fabric": "sweat"}),
                                          ("tshirt_basic", {}), ("skirt", {"style": "circle"}),
                                          ("hoodie", {})])
def test_folded_layout_geometry(garment, opts):
    pat = draft(garment, 122, **opts)
    plans = L.layout_fabric(pat, mode="folded")
    for plan in plans.values():
        assert plan["mode"] == "folded"
        counts = {}
        for pl in plan["placements"]:
            pi, _ = plan["meta"][pl.index]
            piece = pat.pieces[pi]
            counts[pi] = counts.get(pi, 0) + pl.layers
            ring = _placed(plan, pl)
            # grainline parallel to the selvage (vertical in the plan)
            g = pl.apply(np.array(piece.grain))
            assert abs(g[1, 0] - g[0, 0]) < 0.5, piece.name
            in_fold = ring[:, 1].max() <= plan["fold_length"] + 1e-6
            if in_fold:
                assert ring[:, 0].min() >= -1e-6, piece.name
                assert ring[:, 0].max() <= plan["width"] / 2 + 1e-6, piece.name
            if pl.pinned:
                fe = L._fold_edge(piece)
                assert fe is not None
                ep = pl.apply(fe.pts)
                assert np.abs(ep[:, 0]).max() < 0.5, piece.name   # fold edge on the fabric fold
        for pi, n in counts.items():
            assert n == pat.pieces[pi].cut_count, pat.pieces[pi].name   # every copy is cut exactly once


def test_single_layout_unchanged_for_narrow_fabric(harem):
    plans = L.layout_fabric(harem, mode="auto")
    assert plans["Rib knit"]["mode"] == "single"      # 70 cm rib knit is never folded


def test_fabric_layout_option_rejected():
    with pytest.raises(ValueError):
        L.layout_fabric(draft("loop", 122), mode="diagonal")
# Configurable seam allowance (#1)
# ---------------------------------------------------------------------------

ALLOWANCE_CASES = [("pants_basic", {"style": "harem", "fabric": "sweat"}), ("tshirt_basic", {}),
                   ("hoodie", {}), ("skirt", {"style": "a_line"}), ("beanie", {}), ("loop", {})]


def _draft_sa(garment, size=122, **opts):
    import allowance as A
    mm, _ = M.complete_measures({}, size)
    return A.draft(get(garment), mm, opts)


@pytest.mark.parametrize("garment,opts", ALLOWANCE_CASES, ids=[g for g, _ in ALLOWANCE_CASES])
@pytest.mark.parametrize("sa", [7.5, 15.0])
def test_seam_allowance_applies(garment, opts, sa):
    base = _draft_sa(garment, **opts)
    pat = _draft_sa(garment, seam_allowance_mm=sa, **opts)
    assert not [c.name for c in V.validate(pat) if c.status == "ERROR"]
    changed = 0
    for p0, p1 in zip(base.pieces, pat.pieces):
        for e0, e1 in zip(p0.edges, p1.edges):
            if e0.fold:
                assert e1.sa == 0
            elif e0.sa == base.options.get("sa", 10.0) and not e0.turned:
                assert e1.sa == pytest.approx(sa), (p1.name, e1.name)
                changed += 1
    assert changed
    a0 = sum(abs(G.signed_area(p.cut_ring())) for p in base.pieces)
    a1 = sum(abs(G.signed_area(p.cut_ring())) for p in pat.pieces)
    assert (a1 > a0) == (sa > base.options.get("sa", 10.0))


@pytest.mark.parametrize("garment,opts", ALLOWANCE_CASES, ids=[g for g, _ in ALLOWANCE_CASES])
def test_no_seam_allowance(garment, opts):
    pat = _draft_sa(garment, seam_allowance_mm=0, **opts)
    assert not [c.name for c in V.validate(pat) if c.status == "ERROR"]
    for p in pat.pieces:
        assert all(e.sa == 0 for e in p.edges)
        assert abs(G.signed_area(p.cut_ring()) - G.signed_area(p.seam_ring())) < 1.0
        assert p.sa_text().startswith("NO seam allowance included")
        prims = R.piece_prims(p, pat)
        assert not [x for x in prims if x.kind == "line" and x.style == "seam"]   # only one outline


def test_hem_allowance_option():
    pat = _draft_sa("pants_basic", style="trousers", hem_allowance_mm=40)
    assert pat.piece("front").edge("hem").sa == 40
    assert pat.piece("front").edge("side").sa == 10
    with pytest.raises(ValueError):
        _draft_sa("pants_basic", seam_allowance_mm=80)


def test_cli_seam_allowance(tmp_path):
    import generate as GN
    rc = GN.main(["--garment", "loop", "--size", "122", "--format", "a4", "--seam-allowance", "none",
                  "--out", str(tmp_path)])
    assert rc == 0
    md = (tmp_path / "sewing_instructions.md").read_text(encoding="utf-8")
    assert "NO seam allowance" in md


# ---------------------------------------------------------------------------
# Projector output (#9)
# ---------------------------------------------------------------------------

GRID = 100.0 / 25.4 * 72.0          # 283.46 pt


@pytest.mark.parametrize("dark", [False, True])
def test_projector_pdf(harem_mod, tmp_path, dark):
    lay = L.layout_projector(harem_mod, 1500)
    p = tmp_path / "proj.pdf"
    R.render_projector_pdf(harem_mod, lay, str(p), dark=dark)
    rd, streams = _page_streams(p)
    assert len(rd.pages) == 1
    box_ = rd.pages[0].mediabox
    assert abs(float(box_.width) - 1500 / 25.4 * 72) < 0.1          # 1:1 page
    s = streams[0]
    assert _has_control_square(s)
    cells = [m for m in re.finditer(r"(-?[\d.]+) (-?[\d.]+) re", s)
             if abs(float(m.group(1)) - GRID) < 0.01 and abs(float(m.group(2)) - GRID) < 0.01]
    assert len(cells) == int(lay.page_w // 100) * int(lay.page_h // 100)
    widths = [float(w) for w in re.findall(r"([\d.]+) w\b", s)]
    assert widths and min(widths) >= 1.0                             # lines ≥ 1 pt
    if dark:
        assert "0 0 0 rg" in s                                       # black background
    # grainlines parallel to the long page edge
    for pl in lay.placements:
        g = pl.apply(np.array(harem_mod.pieces[pl.index].grain))
        assert abs(g[1, 0] - g[0, 0]) < 0.5


def test_projector_format_in_generate(tmp_path):
    import generate as GN
    rc = GN.main(["--garment", "beanie", "--size", "122", "--format", "projector", "--out", str(tmp_path)])
    assert rc == 0
    assert list(tmp_path.glob("*_projector.pdf"))


def test_no_allowance_fabric_consumption_includes_allowances():
    with_sa = L.layout_fabric(_draft_sa("tshirt_basic"), mode="single")["Main fabric"]["length"]
    none = L.layout_fabric(_draft_sa("tshirt_basic", seam_allowance="none"), mode="single")["Main fabric"]["length"]
    assert none == pytest.approx(with_sa, abs=10)


# ---------------------------------------------------------------------------
# Imperial units and US/UK sizes (#13)
# ---------------------------------------------------------------------------

def test_unit_conversion():
    import units as U
    assert U.inch_text(25.4) == '1"'
    assert U.inch_text(10.0) == '3/8"'
    assert U.inch_text(63.5) == '2 1/2"'
    assert U.yards(914.4) == 1.0
    assert U.yards(915.0) == 1.125                       # always rounded up to 1/8 yd
    assert U.fabric_length(1000.0, "imperial") == "1 1/8 yd"
    assert U.fabric_length(500.0, "imperial") == "5/8 yd"
    assert U.fabric_width(1500.0, "imperial") == '59"'
    assert U.to_cm({"hip": 10}, "imperial") == {"hip": pytest.approx(25.4)}
    assert U.length(100.0) == "10.0 cm"
    with pytest.raises(ValueError):
        U.check("furlongs")


@pytest.mark.parametrize("size,system,base", [
    ("us8", "us_women", ("women", 38)), ("uk12", "uk_women", ("women", 38)),
    ("US 0", "us_women", ("women", 30)), ("us3t", "us_toddler", ("kids", 98)),
    ("usk8", "us_kids", ("kids", 128)), ("us kids 9", "us_kids", ("kids", 134)),
    ("w38", "women", ("women", 38)), (122, "kids", ("kids", 122)),
])
def test_us_uk_sizes(size, system, base):
    sys_, n = M.parse_size(size)
    assert sys_ == system
    assert M.base_size(sys_, n) == (base[0], pytest.approx(base[1]))


def test_us_size_out_of_range():
    with pytest.raises(ValueError):
        M.parse_size("us24")


def test_imperial_us8_pattern(tmp_path):
    import generate as GN
    rc = GN.main(["--garment", "tshirt_basic", "--size", "us8", "--units", "imperial", "--format", "letter",
                  "--out", str(tmp_path)])
    assert rc == 0
    md = (tmp_path / "sewing_instructions.md").read_text(encoding="utf-8")
    assert "US women's size 8" in md
    assert 'seam allowance 3/8" included' in md
    assert re.search(r"about (\d+ )?(\d/8|\d) yd at 59\" width", md)
    assert " cm |" not in md.split("## Validation report")[0]   # no metric values in the user tables


def test_imperial_measures_input():
    import generate as GN
    pat, src, _ = GN.draft_from_spec(dict(garment="pants_basic", size="usk8", units="imperial",
                                          measures_in={"hip": 28}))
    assert pat.measures["hip"] == pytest.approx(28 * 25.4)
    assert src["hip"] == "user"


# ---------------------------------------------------------------------------
# Pants: leg shapes, cargo pockets, shorts with turn-up (#7)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("shape", ["straight", "tapered", "bootcut", "flare"])
@pytest.mark.parametrize("size", [98, 152, "w38", "m52"])
def test_leg_shapes_sewable(shape, size):
    pat = draft("pants_basic", size, style="trousers", leg_shape=shape)
    report = V.validate(pat)
    assert not [(c.name, c.actual) for c in report if c.status == "ERROR"]
    st = statuses(report)
    assert st["Inseam front ↔ back"] == "OK" and st["Side seam front ↔ back"] == "OK"


def test_flare_matches_flare_cm():
    for size in (122, "w38"):
        pat = draft("pants_basic", size, style="trousers", leg_shape="flare", flare_cm=14)
        o = pat.options
        knee = next(r for r in pat.construction if r["name"] == "knee_width")["value"]
        assert pat.finished["opening"] == pytest.approx(knee + 140, abs=3)
        assert o["_hem_c"] == pytest.approx(knee + 140, abs=0.5)
        straight = draft("pants_basic", size, style="trousers")
        tapered = draft("pants_basic", size, style="trousers", leg_shape="tapered")
        boot = draft("pants_basic", size, style="trousers", leg_shape="bootcut")
        assert tapered.finished["opening"] < straight.finished["opening"] < boot.finished["opening"] \
            < pat.finished["opening"]


def test_leg_shape_needs_long_uncuffed_leg():
    pat = draft("pants_basic", 122, style="jogger", leg_shape="flare")      # joggers have cuffs
    assert pat.options["leg_shape"] == "straight"
    with pytest.raises(ValueError):
        draft("pants_basic", 122, leg_shape="balloon")


@pytest.mark.parametrize("size", [98, 122, "m52"])
def test_cargo_pocket(size):
    pat = draft("pants_basic", size, style="trousers", pockets=["side", "cargo"])
    assert not [c.name for c in V.validate(pat) if c.status == "ERROR"]
    assert pat.has("cargo_pocket") and pat.has("cargo_flap")
    mark = next(mk for mk in pat.piece("front").marks if mk.label == "Cargo pocket")
    from shapely.geometry import Polygon
    assert Polygon(pat.piece("front").seam_ring()).contains(Polygon(mark.pts))
    pk = pat.piece("cargo_pocket")
    w_pocket = pk.edge("top").length
    assert w_pocket == pytest.approx(np.ptp(mark.pts[:, 0]) + 2 * 20.0 * max(0.75, min(1.45, pat.measures["height"] / 1220)), abs=0.5)
    steps = " ".join(get("pants_basic").sewing_steps(pat))
    assert "Cargo pocket" in steps and "box pleat" in steps


@pytest.mark.parametrize("size", [122, "w38"])
def test_shorts_with_turn_up(size):
    plain = draft("pants_basic", size, style="trousers", length="short")
    pat = draft("pants_basic", size, style="trousers", length="short", turn_up=3)
    assert not [c.name for c in V.validate(plain) if c.status == "ERROR"]
    assert not [c.name for c in V.validate(pat) if c.status == "ERROR"]
    assert pat.piece("front").edge("hem").sa == pytest.approx(plain.piece("front").edge("hem").sa + 60)
    assert any(mk.label == "Turn-up fold" for mk in pat.piece("back").marks)
    assert "turn-up" in " ".join(get("pants_basic").sewing_steps(pat)).lower()


# ---------------------------------------------------------------------------
# Zip-up hoodie (#6)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("opts", [{"front": "zip"}, {"front": "zip", "hood": False},
                                  {"front": "zip", "sleeve_style": "raglan", "hood_lining": True}])
@pytest.mark.parametrize("size", [98, 140, "w38", "m52"])
def test_zip_hoodie(opts, size):
    pat = draft("hoodie", size, **opts)
    report = V.validate(pat)
    assert not [(c.name, c.actual) for c in report if c.status == "ERROR"]
    st = statuses(report)
    assert st["Zip: left ↔ right front edge"] == "OK"
    assert st["Zip length fits the front opening"] == "OK"
    front = pat.piece("front")
    assert not front.on_fold and front.cut_count == 2 and front.mirror
    assert front.edge("center").sa > 0
    zl = pat.options["_zip_len"]
    assert zl / 10 in get("hoodie").ZIP_LENGTHS
    assert zl <= pat.finished["zip_opening"]
    assert any(f"zip, {zl / 10:.0f} cm" in n for n in pat.notes)          # bill of materials
    if pat.has("kangaroo_pocket"):
        assert not pat.piece("kangaroo_pocket").on_fold and pat.piece("kangaroo_pocket").cut_count == 2
    if pat.has("hem_band"):
        assert pat.piece("hem_band").edge("right").label == "Front end (zip)"
    if pat.has("neckband"):
        assert pat.piece("neckband").edge("right").label == "Front end (zip)"
    assert pat.has("zip_guard")
    steps = " ".join(get("hoodie").sewing_steps(pat))
    assert "Sew the zip in" in steps
    assert "into a ring" not in steps.replace("cuffs into rings", "")    # bands stay open at the zip


def test_closed_hoodie_unchanged():
    pat = draft("hoodie", 122)
    assert pat.piece("front").on_fold and not pat.has("zip_guard")


def test_mode_a_zip_jacket():
    import photo_analyze as A
    m = A.map_to_module({"garment_type": {"value": "hoodie", "confidence": 0.9},
                         "closure": {"value": "zipper", "confidence": 0.8}})
    assert m["module"] == "hoodie" and m["options"]["front"] == "zip"
    assert not m["not_covered"]



# ---------------------------------------------------------------------------
# Dress (#5)
# ---------------------------------------------------------------------------

def test_dress_waist_seam_cli(tmp_path):
    import generate as GN
    rc = GN.main(["--garment", "dress", "--style", "waist_seam", "--size", "116", "--format", "a4",
                  "--out", str(tmp_path)])
    assert rc == 0
    md = (tmp_path / "sewing_instructions.md").read_text(encoding="utf-8")
    assert "Sew skirt and bodice together" in md and "Gather the skirt" in md


@pytest.mark.parametrize("skirt", ["a_line", "circle"])
def test_dress_waist_seam_matches(skirt):
    pat = draft("dress", 122, skirt=skirt)
    a = pat.edge_len("front.hem") * 2 + pat.edge_len("back.hem") * 2
    b = pat.edge_len("skirt_front.waistband") * 2 + pat.edge_len("skirt_back.waistband") * 2
    assert abs(a - b) < 1.0


@pytest.mark.parametrize("gather,ok", [(1.0, True), (1.6, True), (2.5, True), (0.8, False), (3.0, False)])
def test_dress_gather_ratio_range(gather, ok):
    pat = draft("dress", 122, gather=gather)
    st = statuses(V.check_seams(pat))
    assert (st["Waist seam bodice ↔ skirt (gathered)"] == "OK") == ok


def test_shirt_dress_flare_and_hip():
    pat = draft("dress", "w38", style="shirt_dress", flare_cm=40)
    assert pat.finished["hem_circ"] == pytest.approx(pat.finished["chest_circ"] + 400, rel=0.03)
    st = statuses(V.validate(pat))
    assert st["Dress fits over the hip"] == "OK" and st["Hem ↔ side seam front"] == "OK"


def test_dress_pockets_and_photo_mapping():
    import photo_analyze as A
    pat = draft("dress", 140, pockets=True)
    assert pat.has("pocket_bag") and pat.piece("pocket_bag").cut_count == 4
    assert len([n for n in pat.piece("skirt_front").notches if n.edge == "side"]) == 2
    m = A.map_to_module({"garment_type": {"value": "dress", "confidence": 0.9},
                         "silhouette": {"value": "a-line", "confidence": 0.7},
                         "waist_seam": {"value": "no", "confidence": 0.7}})
    assert m["module"] == "dress" and m["options"]["style"] == "shirt_dress"
    assert not m["not_covered"]


# ---------------------------------------------------------------------------
# Measurement profiles (#12)
# ---------------------------------------------------------------------------

def test_profile_precedence(tmp_path):
    import datetime as dt

    import generate as GN
    import profiles as PR
    d = str(tmp_path / "profiles")
    PR.save("Lena", {"height": 121, "hip": 64, "waist": 55}, d, kind="child", fit="wide",
            default_format="a4", measured=dt.date.today().isoformat())
    spec = dict(garment="pants_basic", size=122, profile="lena", profiles_dir=d,
                measures_cm={"waist": 57})
    pat, src, warn = GN.draft_from_spec(spec)
    assert pat.measures["hip"] == pytest.approx(640)          # profile beats the size table
    assert src["hip"] == "profile"
    assert pat.measures["waist"] == pytest.approx(570)        # explicit beats the profile
    assert src["waist"] == "user"
    assert pat.measures["inseam"] != pytest.approx(M.size_measures(122)["inseam"])   # scaled by height 121
    assert pat.options["fit"] == "wide"                       # profile default
    assert not [w for w in warn if "months old" in w]
    spec2, _ = PR.apply(dict(garment="pants_basic", profile="lena", profiles_dir=d))
    assert spec2["formats"] == ["a4"]
    spec3, _ = PR.apply(dict(garment="pants_basic", profile="lena", profiles_dir=d, formats=["roll610"]))
    assert spec3["formats"] == ["roll610"]


def test_profile_age_warning_and_history(tmp_path):
    import datetime as dt

    import profiles as PR
    d = str(tmp_path)
    old = (dt.date.today() - dt.timedelta(days=200)).isoformat()
    PR.save("max", {"height": 110, "hip": 60}, d, measured=old)
    prof = PR.load("max", d)
    assert PR.is_child(prof)
    assert any("months old" in w for w in PR.warnings(prof))
    PR.save("max", {"height": 116}, d)
    prof = PR.load("max", d)
    assert len(prof["history"]) == 1 and prof["measures_cm"]["hip"] == 60
    assert PR.growth(prof) == {"height": 6.0}
    assert PR.suggested_size(prof) == 116
    assert not PR.warnings(prof)
    adult = PR.load(PR.save("anna", {"height": 168, "hip": 98}, d, measured=old), d)
    assert not PR.warnings(adult)                            # adults: no growth warning


def test_profile_cli(tmp_path, capsys):
    import generate as GN
    import profiles as PR
    d = str(tmp_path / "p")
    assert PR.main(["--profiles-dir", d, "save", "lena", "--measures", '{"height": 121, "hip": 64}',
                    "--format", "a4"]) == 0
    assert PR.main(["--profiles-dir", d, "show", "lena"]) == 0
    assert "Suggested kids' size: 122" in capsys.readouterr().out
    os_env = __import__("os").environ
    os_env["SEWING_PROFILES"] = d
    try:
        rc = GN.main(["--garment", "beanie", "--profile", "lena", "--out", str(tmp_path / "out")])
    finally:
        del os_env["SEWING_PROFILES"]
    assert rc == 0
    assert list((tmp_path / "out").glob("*_a4_tiled.pdf"))      # profile's default format
    md = (tmp_path / "out" / "sewing_instructions.md").read_text(encoding="utf-8")
    assert "| profile |" in md


ADJ_CASES = [
    ("pants_basic", "122", {"style": "jogger"}, "hip", "+2cm", "hip_circ", 20),
    ("pants_basic", "122", {"style": "jogger"}, "rise", "-15mm", "front_rise", -15),
    ("pants_basic", "122", {"style": "jogger"}, "inseam", "-2", "inseam", -20),
    ("pants_basic", "122", {"style": "trousers", "fabric": "woven", "cuffs": False}, "opening", "+3cm",
     "opening", 30),
    ("pants_basic", "122", {"style": "jogger"}, "waist", "+2cm", "waist_relaxed", 20),
    ("tshirt_basic", "140", {}, "chest", "+4cm", "chest_circ", 40),
    ("tshirt_basic", "140", {}, "length", "-2cm", "length", -20),
    ("tshirt_basic", "140", {"sleeve_length": "long"}, "sleeve_length", "-3cm", "sleeve_len", -30),
    ("tshirt_basic", "140", {}, "neckline", "+0.5cm", "neckline", 1),
    ("hoodie", "140", {}, "chest", "-4cm", "chest_circ", -40),
]


@pytest.mark.parametrize("garment,size,opts,key,val,fin,expect", ADJ_CASES)
def test_adjustment_changes_finished_measure(garment, size, opts, key, val, fin, expect):
    import generate as GN
    pat, _, _ = GN.draft_from_spec({"garment": garment, "size": size, "options": opts,
                                    "adjustments": {key: val}})
    before = pat.options["_finished_before"][fin]
    d = pat.finished[fin] - before
    if abs(expect) < 5:                       # only the direction is defined
        assert d * expect > 0
    else:
        assert abs(d - expect) <= max(3.0, abs(expect) * 0.1), (fin, before, pat.finished[fin])
    assert V.is_ok(V.validate(pat))


def test_adjustment_shape_values():
    import adjust as ADJ
    import generate as GN
    pat, _, _ = GN.draft_from_spec({"garment": "pants_basic", "size": "122", "adjustments": {"seat": "+2cm"}})
    base, _, _ = GN.draft_from_spec({"garment": "pants_basic", "size": "122"})
    cv = {r["name"]: r["value"] for r in pat.construction}
    cb = {r["name"]: r["value"] for r in base.construction}
    assert cv["back_crotch_extension"] - cb["back_crotch_extension"] == pytest.approx(10, abs=0.5)
    top, _, _ = GN.draft_from_spec({"garment": "tshirt_basic", "size": "140",
                                    "adjustments": {"armhole": "+1cm", "shoulder": "-1cm"}})
    tb, _, _ = GN.draft_from_spec({"garment": "tshirt_basic", "size": "140"})
    cv = {r["name"]: r["value"] for r in top.construction}
    cb = {r["name"]: r["value"] for r in tb.construction}
    assert cv["armhole_depth"] - cb["armhole_depth"] == pytest.approx(10, abs=0.5)
    assert cv["shoulder_length"] - cb["shoulder_length"] == pytest.approx(-10, abs=0.5)
    assert len(ADJ.ADJUSTMENTS["pants_basic"]) >= 5 and len(ADJ.ADJUSTMENTS["tshirt_basic"]) >= 5


def test_fit_issues_resolve():
    import adjust as ADJ
    assert ADJ.resolve("pants_basic", {"hip_tight": "2cm", "crotch_low": "1.5cm", "legs_long": "-1in"}) == \
        {"hip": 20.0, "rise": -15.0, "inseam": pytest.approx(-25.4)}
    assert ADJ.resolve("tshirt_basic", {"sleeves_long": "3cm", "chest": "+1", "chest_tight": "1cm"}) == \
        {"sleeve_length": -30.0, "chest": 20.0}
    with pytest.raises(ValueError):
        ADJ.resolve("pants_basic", {"sleeves_long": "3cm"})
    with pytest.raises(ValueError):
        ADJ.parse_delta("a bit")


def test_adjustments_persist_and_regrade(tmp_path):
    import generate as GN
    adj = {"hip_tight": "2cm"}
    pat, _, _ = GN.draft_from_spec({"garment": "pants_basic", "size": "122", "adjustments": adj})
    assert pat.options["adjustments"] == adj
    assert "construction" not in pat.options          # not baked in: re-applied in other sizes
    big, _, _ = GN.draft_from_spec({"garment": "pants_basic", "size": "134", "options": dict(pat.options)})
    ref, _, _ = GN.draft_from_spec({"garment": "pants_basic", "size": "134"})
    assert big.finished["hip_circ"] - ref.finished["hip_circ"] == pytest.approx(20, abs=3)
    user, _, _ = GN.draft_from_spec({"garment": "pants_basic", "size": "122", "adjustments": adj,
                                     "options": {"construction": {"hip_width": 760}}})
    assert user.options["construction"] == {"hip_width": 760}       # explicit override wins


def test_adjust_cli(tmp_path):
    import generate as GN
    out = tmp_path / "o"
    rc = GN.main(["--garment", "pants_basic", "--size", "122", "--format", "a4", "--out", str(out),
                  "--adjust", '{"hip_tight": "2cm", "crotch_low": "1cm"}'])
    assert rc == 0
    md = (out / "sewing_instructions.md").read_text(encoding="utf-8")
    assert "## Fit adjustments" in md and "| Before | After | Change |" in md
    js = __import__("json").loads((out / "pattern.json").read_text(encoding="utf-8"))
    assert js["options"]["adjustments"] == {"hip_tight": "2cm", "crotch_low": "1cm"}


DIAGRAM_CASES = [
    ("pants_basic", "122", {"pockets": ["side", "back_patch"]}),
    ("pants_basic", "122", {"style": "trousers", "fabric": "woven", "waistband": "rib"}),
    ("tshirt_basic", "140", {"sleeve_style": "raglan", "sleeve_cuffs": True, "hem_band": True}),
    ("hoodie", "140", {}),
    ("hoodie", "140", {"front": "zip", "zip_guard": True}),
    ("skirt", "128", {"style": "gathered"}),
    ("dress", "140", {"style": "waist_seam"}),
    ("beanie", "122", {}),
    ("loop", "122", {}),
]


@pytest.mark.parametrize("garment,size,opts", DIAGRAM_CASES)
def test_step_diagrams_cover_every_seam(garment, size, opts):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    import diagrams as DG
    import generate as GN
    import steps as ST
    pat, _, _ = GN.draft_from_spec({"garment": garment, "size": size, "options": opts})
    steps = ST.assembly(pat)
    # every seam of the seam graph is sewn in some step, and steps only name real seams
    assert ST.covered_seams(pat, steps) == {s["name"] for s in pat.seams}
    for st in steps:
        assert st.title and len(st.title) <= 45, st.title          # one short action
        assert st.diagram in DG.DIAGRAMS
        if st.seams:
            assert ST.resolve_seams(pat, st), st.title
        for p, e in st.edges:
            pat.piece(p).edge(e)                                   # edges exist
        for p in st.pieces:
            assert pat.has(p), (st.title, p)
    # every step draws from the real pieces without falling back to the placeholder
    DG.STRICT = True
    try:
        for st in steps:
            fig, ax = plt.subplots()
            DG.draw(ax, pat, st)
            plt.close(fig)
    finally:
        DG.STRICT = False


def test_seam_overlay_puts_the_pieces_on_top_of_each_other():
    import diagrams as DG
    import generate as GN
    pat, _, _ = GN.draft_from_spec({"garment": "pants_basic", "size": "122"})
    shirt, _, _ = GN.draft_from_spec({"garment": "tshirt_basic", "size": "140"})
    for name in ("Inseam", "Pocket bag seam", "Shoulder seam"):
        if name == "Shoulder seam":
            pat = shirt
        seam = next(s for s in pat.seams if s["name"].startswith(name))
        A, ea, B, eb, T = DG.overlay_parts(pat, seam)
        moved = DG._apply(T, B.edge(eb).pts)
        target = A.edge(ea).pts
        # the edges to sew lie on top of each other (either direction)
        d = min(np.abs(DG._resample(moved) - DG._resample(target)).max(),
                np.abs(DG._resample(moved)[::-1] - DG._resample(target)).max())
        assert d < 0.06 * A.edge(ea).length, (name, d)
    pat, _, _ = GN.draft_from_spec({"garment": "pants_basic", "size": "122"})
    inseam = next(s for s in pat.seams if s["name"].startswith("Inseam"))
    R = DG.overlay_parts(pat, inseam)[4][0]
    assert R[1, 1] > 0.9                    # back leg face down on the front leg, upright (hem to hem),
    #                                         not turned upside down (shopper review: layers lie as on the table)
    side = next(s for s in pat.seams if s["name"].startswith("Side seam"))
    assert DG.overlay_parts(pat, side) is None                     # pocket: edges differ, side by side
    bag = next(s for s in pat.seams if s["name"].startswith("Pocket bag seam"))
    assert DG.overlay_parts(pat, bag)[4][2] is False               # pocket bags lie the same way up
    band = next(s for s in pat.seams if s["name"].startswith("Waistband"))
    assert DG.overlay_parts(pat, band) is None                     # several edges: join diagram


def test_step_png_shows_stitch_line(tmp_path):
    import diagrams as DG
    import generate as GN
    import steps as ST
    pat, _, _ = GN.draft_from_spec({"garment": "pants_basic", "size": "122"})
    st = next(s for s in ST.assembly(pat) if s.title == "Sew the inseams")
    p = DG.render_step(pat, st, str(tmp_path / "s.png"), 5)
    from PIL import Image
    a = np.asarray(Image.open(p).convert("RGB")).astype(int)
    red = int(((a[..., 0] > 150) & (a[..., 1] < 90) & (a[..., 2] < 90)).sum())
    assert red > 200                                                  # stitch line and direction


def test_machine_dependent_steps():
    import generate as GN
    import steps as ST
    pat, _, _ = GN.draft_from_spec({"garment": "tshirt_basic", "size": "140"})
    seam = next(s for s in ST.assembly(pat) if s.title == "Sew the shoulder seams")
    hem = next(s for s in ST.assembly(pat) if s.title == "Sew the hem")
    plain = dict(pat.options)
    assert ST.tool_for(plain, seam.stitch)["machine"] == "sewing"
    assert "zigzag" in ST.tool_for(plain, seam.stitch)["stitch"]
    full = dict(pat.options, machines=["sewing", "overlocker", "coverstitch"])
    assert ST.tool_for(full, seam.stitch)["machine"] == "overlocker"
    assert ST.tool_for(full, hem.stitch)["machine"] == "coverstitch"
    assert "overlocker" in seam.as_text(full)
    woven = dict(pat.options, fabric="woven")
    assert ST.tool_for(woven, "seam", knit=False)["stitch"].startswith("straight")
    assert ST.tool_for(dict(woven, machines="sewing,overlocker"), "finish", knit=False)["machine"] == "overlocker"
    names = [t["machine"] for t in ST.machines_needed(ST.assembly(pat), full)]
    assert {"overlocker", "coverstitch", "iron"} <= set(names)


def test_illustrated_instructions(tmp_path):
    import generate as GN
    out = tmp_path / "o"
    assert GN.main(["--garment", "hoodie", "--size", "140", "--format", "a4", "--out", str(out)]) == 0
    md = (out / "sewing_instructions.md").read_text(encoding="utf-8")
    imgs = re.findall(r"!\[Step (\d+)\]\((steps/step_\d+\.png)\)", md)
    assert len(imgs) >= 10 and all((out / p).exists() for _, p in imgs)
    pdf = out / "sewing_instructions.pdf"
    assert pdf.stat().st_size < 3_000_000
    from pypdf import PdfReader
    pages = PdfReader(str(pdf)).pages
    text = " ".join(pg.extract_text() for pg in pages[:6])
    # booklet: cover, parts and tools, numbered one-action steps; then the reference pages
    assert "Hoodie" in text and "Parts" in text and "Material" in text and "Basics" in text
    text = " ".join(pg.extract_text() for pg in pages[:16])
    assert "Sew the shoulder seams" in text and "Set in the sleeves" in text
    n_steps = len(re.findall(r"^\d+\. ", md.split("## Sewing instructions")[1].split("## ")[0], re.M))
    assert len(pages) >= 3 + -(-n_steps // 2) + 1
    assert "Validation report" in " ".join(pg.extract_text() for pg in pages[-4:])


def test_parse_sizes():
    import nested as NE
    assert NE.parse_sizes("98,110, 122") == ["98", "110", "122"]
    assert NE.parse_sizes("98-122") == ["98", "104", "110", "116", "122"]
    assert NE.parse_sizes(["w36", "w38"]) == ["w36", "w38"]
    assert NE.parse_sizes("122") == ["122"] and NE.parse_sizes(122) == [122]


def _line_prims(prims, layer=None):
    return [(p.style, np.round(np.asarray(p.pts), 3)) for p in prims
            if p.kind == "line" and p.style not in ("grain", "fold_arrow") and (layer is None or p.layer == layer)]


def test_nested_layers_match_single_sizes():
    import generate as GN
    import nested as NE
    sizes = ["98", "122", "140"]
    singles = [GN.draft_from_spec({"garment": "tshirt_basic", "size": s})[0] for s in sizes]
    nest = NE.build([GN.draft_from_spec({"garment": "tshirt_basic", "size": s})[0] for s in sizes], sizes)
    for i, pc in enumerate(nest.pieces):
        prims = R.nested_piece_prims(nest, i)
        env = __import__("shapely.geometry", fromlist=["Polygon"]).Polygon(pc.cut_ring()).buffer(0.5)
        for k, single in enumerate(singles):
            got = _line_prims(prims, layer=k)
            want = _line_prims(R.piece_prims(single.pieces[i], single))
            assert len(got) == len(want)
            for (s1, a), (s2, b) in zip(got, want):
                assert s1 == s2 and np.allclose(a, b)
            # the layout reserves the envelope: every size lies inside it
            assert env.contains(__import__("shapely.geometry", fromlist=["Polygon"]).Polygon(
                single.pieces[i].cut_ring()))
    with pytest.raises(ValueError):
        NE.build(singles[:1], sizes[:1])


def test_nested_outputs(tmp_path):
    from pypdf import PdfReader

    import generate as GN
    out = tmp_path / "n"
    res = GN.run(dict(garment="beanie", size="98,122,140", formats=["roll610", "a4", "a1"], out=str(out)),
                 verbose=False)
    assert res["ok"]
    pdfs = sorted(out.glob("*.pdf"))
    pattern_pdfs = [p for p in pdfs if p.name != "sewing_instructions.pdf"]
    assert len(pattern_pdfs) == 3
    for p in pattern_pdfs:
        r = PdfReader(str(p))
        names = [o.get_object()["/Name"] for o in r.trailer["/Root"]["/OCProperties"]["/OCGs"]]
        assert names == ["Size 98", "Size 122", "Size 140"]
        data = b"".join(pg.get_contents().get_data() for pg in r.pages if pg.get_contents() is not None)
        assert all(f"/OC /oc{k} BDC".encode() in data for k in range(3))
    svg = next(out.glob("*_master_1to1.svg")).read_text(encoding="utf-8")
    assert svg.count('class="size-layer"') == 3 and 'id="size_140"' in svg
    rep = (out / "validation_report.md").read_text(encoding="utf-8")
    assert rep.count("### Sewability check") == 3
    md = (out / "sewing_instructions.md").read_text(encoding="utf-8")
    assert "## Sizes in this pattern (nested)" in md and md.startswith("# Beanie · sizes 98 · 122 · 140")
    js = __import__("json").loads((out / "pattern.json").read_text(encoding="utf-8"))
    assert [s["layer"] for s in js["nested_sizes"]] == ["Size 98", "Size 122", "Size 140"]


def test_nested_blocks_on_any_failing_size(tmp_path, monkeypatch):
    import generate as GN
    real = V.validate

    def fake(pat, raise_on_error=False):
        rep = real(pat)
        if "122" in pat.size_label:
            rep.append(V.Check("Measurements", "forced", "ERROR", "", "", ""))
        return rep

    monkeypatch.setattr(GN.V, "validate", fake)
    res = GN.run(dict(garment="beanie", size="98,122", formats=["a4"], out=str(tmp_path / "f")), verbose=False)
    assert not res["ok"]
    assert not list((tmp_path / "f").glob("*.pdf"))
    assert (tmp_path / "f" / "validation_report.md").read_text(encoding="utf-8").count("### Sewability check") == 2
