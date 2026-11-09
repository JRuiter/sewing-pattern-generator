"""German output (issue #39 part 4): central string table, German file names, decimal comma."""
from __future__ import annotations

import html
import re
from pathlib import Path

import pytest
from pypdf import PdfReader

import generate as GN
import i18n

KORD = {"style": "trousers", "fabric": "corduroy", "fit": "wide", "crotch_drop": 20, "knee_total": 330,
        "opening_total": 260, "waistband": "rib", "pockets": ["side"], "fake_fly": True, "back_pockets": 1,
        "hem_finish": "elastic_casing", "pocket_bag_fabric": "cotton", "title": "Kordhose"}

# English words that must not be left in German output (identifiers and option values in backticks are fine)
ENGLISH = re.compile(
    r"\b(the|and|with|of|to|on|for|Sew|Fold|Press|Cut|Pin|piece|pieces|seam|seams|front|back|sleeve|edge|hem|"
    r"Front|Back|Sleeve|Hood|Skirt|Waist|pocket|Pocket|fabric|Fabric|stitch|Stitch|is|are|not|Turn|Topstitch|"
    r"both|inside|right|left|side|Side|width|length|Length|Width|size|Size|page|Page|Legend|cutting|layout|"
    r"Notes|Step|Tip|Important|Done|needle|Needle|thread|Overview|Pattern|pattern)\b")


def _english_lines(text: str) -> list[str]:
    out = []
    for line in text.splitlines():
        line = re.sub(r"`[^`]*`|\b\w+_\w+\b|https?://\S+", "", line)
        if ENGLISH.search(line):
            out.append(line.strip())
    return out


def _texts(out: Path) -> dict[str, str]:
    texts = {}
    for f in out.rglob("*"):
        if f.suffix == ".md":
            texts[f.name] = f.read_text()
        elif f.suffix == ".svg":
            s = f.read_text()
            texts[f.name] = "\n".join(html.unescape(x) for x in re.findall(r"<text[^>]*>(.*?)</text>", s, re.S))
        elif f.suffix == ".pdf":
            texts[f.name] = "\n".join(p.extract_text() or "" for p in PdfReader(str(f)).pages)
    return texts


@pytest.fixture(scope="module")
def german(tmp_path_factory):
    out = tmp_path_factory.mktemp("de")
    GN.run(dict(garment="pants_basic", size=122, options=dict(KORD, machines=["overlocker", "hand"]),
                formats=["a4", "roll610"], language="de", out=str(out)), verbose=False)
    return out


def test_lookup_kinds():
    with i18n.language("de"):
        assert i18n.t("Side seam") == "Seitennaht"
        assert i18n.t("Press 1.5 cm to the inside and stitch it down.") == "1,5 cm nach innen bügeln und feststeppen."
        assert i18n.t("sizes 98 · 110 · 122") == "Größen 98 · 110 · 122"
        assert i18n.t("Seitennaht") == "Seitennaht"          # already German: unchanged
        assert i18n.num(2.5) == "2,5"
    assert i18n.t("Side seam") == "Side seam"
    assert i18n.num(2.5) == "2.5"


def test_language_option():
    assert i18n.check("Deutsch") == "de"
    with pytest.raises(ValueError):
        i18n.check("fr")


def test_german_file_names(german):
    names = {p.name for p in german.iterdir()}
    for n in ("naehanleitung.md", "naehanleitung.pdf", "pruefbericht.md", "zuschnittplan.png", "schnitt.json",
              "schritte", "kordhose_gr122_master_1zu1.svg", "kordhose_gr122_a4_kleben.pdf",
              "kordhose_gr122_rolle610.pdf"):
        assert n in names, (n, sorted(names))
    assert not any("sewing_instructions" in n or "validation_report" in n for n in names)


def test_german_text_decimal_comma_and_size(german):
    md = (german / "naehanleitung.md").read_text()
    assert "Gr. 122" in md
    assert re.search(r"\d,\d+ cm", md)
    assert not re.search(r"\b\d+\.\d+ (cm|m|mm)\b", md)
    assert "Nähanleitung" in md or "Nähschritte" in md


def test_no_english_left(german):
    left = {name: _english_lines(text) for name, text in _texts(german).items()}
    left = {k: v[:5] for k, v in left.items() if v}
    assert not left, left


def test_english_default_unchanged(tmp_path):
    GN.run(dict(garment="pants_basic", size=122, options={}, formats=["a4"], out=str(tmp_path)), verbose=False)
    names = {p.name for p in tmp_path.iterdir()}
    assert "sewing_instructions.md" in names and "validation_report.md" in names
    assert i18n.lang() == "en"


@pytest.mark.slow
@pytest.mark.parametrize("garment,size,opts", [
    ("jumpsuit", "m52", {"style": "boiler"}),
    ("pyjama", 128, {}),
    ("romper", 74, {"feet": True}),
    ("swim_trunks", "m52", {}),
    ("tshirt_basic", "w38", {"style_lines": "princess"}),
])
def test_new_garments_fully_german(tmp_path, garment, size, opts):
    """Every text of the newer garments (combined patterns, prefixes, style lines) has a German entry."""
    i18n.MISSING.clear()
    GN.run(dict(garment=garment, size=size, options=opts, formats=["a4"], language="de", out=str(tmp_path)),
           verbose=False)
    assert not i18n.MISSING, sorted(i18n.MISSING)[:10]


def test_translated_text_is_not_reported_again():
    with i18n.language("de"):
        i18n.MISSING.clear()
        for x in ("Hose: Gummiband 20 mm breit, Länge 51 cm (+2 cm Überlappung zum Zusammennähen)",
                  "Nahtzugabe 1,0 cm enthalten; Saum: 2,0 cm; Halsausschnitt: 0,7 cm",
                  "Saum, Vorderkante (Knopfleiste)"):
            assert i18n.t(x) == x
        assert not i18n.MISSING
        i18n.t("Saum, Frobnicate edge")
        assert i18n.MISSING
        i18n.MISSING.clear()
