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
