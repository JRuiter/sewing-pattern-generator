"""Nähbarkeits-Prüfungen, Kleidungsstücke in 3 Größen und Druckausgabe."""
import copy
import re
import shutil
import subprocess
import zlib

import numpy as np
import pytest

import geometry as G
import layout as L
import measurements as M
import render as R
import validate as V
from garments import get

SIZES = [98, 122, 152]
ADULT = ["d38", "h52"]
CASES = [
    ("pants_basic", {"style": "haremshose", "fabric": "sweat"}),
    ("pants_basic", {"style": "jogginghose"}),
    ("pants_basic", {"style": "leggings"}),
    ("pants_basic", {"style": "stoffhose"}),
    ("tshirt_basic", {}),
    ("tshirt_basic", {"sleeve_style": "raglan", "sleeve_length": "lang"}),
    ("tshirt_basic", {"neckline": "v", "fabric": "jersey_elastan"}),
    ("hoodie", {}),
    ("hoodie", {"sleeve_style": "raglan", "hood_lining": True}),
    ("skirt", {"style": "gerafft"}),
    ("skirt", {"style": "a_linie"}),
    ("skirt", {"style": "teller"}),
    ("beanie", {}),
    ("loop", {}),
]


def draft(garment, size, **opts):
    mm, _ = M.complete_measures({}, size)
    return get(garment).draft(mm, opts)


def statuses(report, area=None):
    return {c.name: c.status for c in report if area is None or c.area == area}


# ---------------------------------------------------------------------------
# Jedes Kleidungsstück in 3 Größen (+ Erwachsene)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("garment,opts", CASES, ids=[f"{g}-{'-'.join(map(str, o.values())) or 'standard'}" for g, o in CASES])
@pytest.mark.parametrize("size", SIZES + ADULT)
def test_garment_is_sewable(garment, opts, size):
    pat = draft(garment, size, **opts)
    report = V.validate(pat)
    bad = [(c.name, c.actual) for c in report if c.status == "FEHLER"]
    assert not bad, bad
    for pc in pat.pieces:
        assert pc.grain is not None, pc.name
        assert pc.cut_count >= 1, pc.name
        assert G.ring_is_valid(pc.cut_ring()), pc.name


# ---------------------------------------------------------------------------
# Jede Prüfung muss einen kaputten Schnitt erkennen (Negativtests)
# ---------------------------------------------------------------------------

@pytest.fixture
def harem():
    return draft("pants_basic", 122, style="haremshose", fabric="sweat")


def test_seam_length_mismatch_detected(harem):
    e = harem.piece("hinterhose").edge("seite")
    e.pts = e.pts.copy()
    e.pts[-1] = e.pts[-1] + np.array([0.0, 8.0])          # Seitennaht 8 mm länger
    st = statuses(V.check_seams(harem))
    assert st["Seitennaht vorne ↔ hinten"] == "FEHLER"


def test_rib_ratio_out_of_range_detected(harem):
    seam = next(s for s in harem.seams if s.get("type") == "ratio")
    seam["lo"], seam["hi"] = 0.95, 0.99                    # Bündchen wäre viel zu kurz
    assert any(c.status != "OK" for c in V.check_seams(harem) if c.name == seam["name"])


def test_sleeve_cap_ease_checked():
    pat = draft("tshirt_basic", 122)
    seam = next(s for s in pat.seams if s.get("type") == "ease")
    seam["lo"], seam["hi"] = 40.0, 60.0                    # unplausible Einhaltemenge
    assert any(c.status == "FEHLER" for c in V.check_seams(pat) if c.name == seam["name"])


def test_corner_angle_detected(harem):
    corner = next(c for c in harem.corners if "sum" not in c)
    corner["target"] = corner["target"] + 20                # Ecke weicht 20° ab
    assert any(c.status == "FEHLER" for c in V.check_corners(harem) if c.name == corner["name"])


def test_joined_corner_detected(harem):
    corner = next(c for c in harem.corners if "sum" in c)
    corner["target"] = corner["target"] - 15
    assert any(c.status == "FEHLER" for c in V.check_corners(harem) if c.name == corner["name"])


def test_circumference_check_detected(harem):
    chk = next(c for c in harem.checks if c["kind"] == "circ")
    chk["value"] = chk["target"] * 1.05                     # 5 % daneben
    assert any(c.status == "FEHLER" for c in V.check_values(harem) if c.name == chk["name"])


def test_head_opening_check():
    pat = draft("tshirt_basic", 122)
    chk = next(c for c in pat.checks if "Kopf" in c["name"])
    chk["value"] = chk["target"] * 0.8
    assert any(c.status == "FEHLER" for c in V.check_values(pat) if c.name == chk["name"])


def test_self_intersection_detected(harem):
    pc = harem.piece("vorderhose")
    e = pc.edge("seite")
    pts = e.pts.copy()
    mid = len(pts) // 2
    pts[mid] = pts[mid] + np.array([-400.0, 0.0])           # Spitze quer durchs Teil
    e.pts = pts
    st = statuses(V.check_geometry(harem))
    assert st[f"{pc.name}: Kontur & Nahtzugabe"] == "FEHLER"


def test_missing_seam_allowance_detected(harem):
    pc = harem.piece("vorderhose")
    pc.edge("seite").sa = 0.0
    st = statuses(V.check_geometry(harem))
    assert st[f"{pc.name}: Kontur & Nahtzugabe"] == "FEHLER"


def test_missing_grainline_detected(harem):
    pc = harem.piece("vorderhose")
    pc.grain = None
    st = statuses(V.check_geometry(harem))
    assert st[f"{pc.name}: Fadenlauf & Zuschnitt"] == "FEHLER"


def test_raise_on_error(harem):
    harem.piece("vorderhose").grain = None
    with pytest.raises(V.ValidationError):
        V.validate(harem, raise_on_error=True)


def test_report_table_is_german(harem):
    md = V.to_markdown(V.validate(harem))
    assert "Nähbarkeits-Prüfung" in md and "✅ OK" in md
    assert "nähbar" in md


# ---------------------------------------------------------------------------
# Druckausgabe
# ---------------------------------------------------------------------------

CTRL = 50.0 / 25.4 * 72.0          # 141,73 pt


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
    return draft("pants_basic", 122, style="haremshose", fabric="sweat")


@pytest.fixture(scope="module")
def roll_pdf(harem_mod, tmp_path_factory):
    lay = L.layout_roll(harem_mod, 610)
    p = tmp_path_factory.mktemp("rolle") / "rolle.pdf"
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
        assert b"/FontFile2" in raw                    # TrueType eingebettet
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
    assert lay.page_h >= lay.page_w                      # Hochformat
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
    assert len(rd.pages) == len(pages) + 1                # + Übersichtsseite
    assert all(re.fullmatch(r"[A-Z]\d+", t["label"]) for t in pages)
    text = rd.pages[0].extract_text()
    assert "100" in text                                   # Hinweis „100 % drucken“


def test_a4_overlap_windows():
    tiles, (nr, nc) = L._tile_windows(500, 700, 194, 281)
    for t in tiles:
        x0, y0, x1, y1 = t["window"]
        right = [u for u in tiles if u["row"] == t["row"] and u["col"] == t["col"] + 1]
        if right:
            assert abs((x1 - right[0]["window"][0]) - L.OVERLAP) < 1e-9


@pytest.mark.skipif(shutil.which("pdftoppm") is None, reason="pdftoppm (poppler) fehlt")
def test_a4_overlap_content_identical(harem_mod, tmp_path, monkeypatch):
    """Nach dem Übereinanderkleben müssen die Schnittlinien im Überlappungsstreifen deckungsgleich sein."""
    from PIL import Image
    # Seitendekorationen (Klebemarken, Kontrollquadrate) ausblenden: es zählt nur der Schnitt
    monkeypatch.setattr(R, "_tile_decorations", lambda lay: [])
    monkeypatch.setattr(R, "_draw_deco", lambda *a, **k: None)
    monkeypatch.setattr(R, "control_squares_pdf", lambda *a, **k: None)
    monkeypatch.setattr(R, "control_squares_pdf_single", lambda *a, **k: None)
    lay = L.layout_tiles(harem_mod, "A4")
    p = tmp_path / "a4.pdf"
    R.render_tiles_pdf(harem_mod, lay, str(p))
    pages = [t for t in lay.tiles if not t["empty"]]
    by = {(t["row"], t["col"]): i + 2 for i, t in enumerate(pages)}   # Seite 1 = Übersicht
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
        ya, yb = int((m + 15) * pxmm), int((m + ph - 2) * pxmm)        # Kopfzeile auslassen
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
    """Tellerrock Damen: Teil breiter als die Rolle → Bahnen zum Kleben statt Abbruch."""
    import generate as GN
    pat = draft("skirt", "d38", style="teller")
    with pytest.raises(ValueError):
        L.layout_roll(pat, 610)
    res = GN.run(dict(garment="skirt", size="d38", options={"style": "teller"}, formats=["rolle610"],
                      out=str(tmp_path)), verbose=False)
    assert res["ok"]
    assert any("Bahnen" in k for k in res["files"])
    assert any("breiter als die Rolle" in w for w in res["warnings"])


def test_svg_master_is_1to1(harem_mod, tmp_path):
    lay = L.layout_roll(harem_mod, 610)
    p = tmp_path / "m.svg"
    R.render_svg(harem_mod, lay, str(p))
    head = p.read_text(encoding="utf-8")[:500]
    assert re.search(r'width="[\d.]+mm"', head) and "viewBox" in head
