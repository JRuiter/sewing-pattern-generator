"""Booklet v2 (issue #39 part 5): page structure, step content, nothing leaves its panel."""
from __future__ import annotations

import pytest
from pypdf import PdfReader

import booklet as B
import generate as GN
import steps as S

KORD = {"style": "trousers", "fabric": "corduroy", "fit": "wide", "crotch_drop": 20, "knee_total": 330,
        "opening_total": 260, "waistband": "rib", "pockets": ["side", "back_patch"], "fake_fly": True,
        "back_pockets": 1, "hem_finish": "elastic_casing", "pocket_bag_fabric": "cotton", "title": "Kordhose",
        "machines": ["overlocker", "hand"]}


def _run(tmp_path, garment, options, lang="en", size=122):
    B.CHECKS = []
    try:
        GN.run(dict(garment=garment, size=size, options=options, formats=["a4"], language=lang,
                    out=str(tmp_path)), verbose=False)
        return B.CHECKS
    finally:
        B.CHECKS = None


def _problems(checks):
    bad = []
    for rec in checks:
        x, y, w, h = rec["rect"]
        texts = [b for b in rec["boxes"] if b[0] == "text"]
        for kind, txt, (x0, y0, x1, y1) in rec["boxes"]:
            if x0 < x - 0.002 or y0 < y - 0.002 or x1 > x + w + 0.002 or y1 > y + h + 0.002:
                bad.append((rec["step"], kind, txt))
        for i in range(len(texts)):
            for j in range(i + 1, len(texts)):
                a, b = texts[i][2], texts[j][2]
                if min(a[2], b[2]) - max(a[0], b[0]) > 0.003 and min(a[3], b[3]) - max(a[1], b[1]) > 0.003:
                    bad.append((rec["step"], "overlap", texts[i][1], texts[j][1]))
    return bad


@pytest.fixture(scope="module")
def kord(tmp_path_factory):
    out = tmp_path_factory.mktemp("kord")
    checks = _run(out, "pants_basic", KORD, "de")
    pdf = PdfReader(str(out / "naehanleitung.pdf"))
    pages = [p.extract_text() or "" for p in pdf.pages]
    pat, _, _ = GN.draft_from_spec(dict(garment="pants_basic", size=122, options=KORD))
    return checks, pages, S.assembly(pat), pat


def test_reference_booklet_structure(kord):
    checks, pages, steps, _pat = kord
    text = "\n".join(pages)
    assert "KORDHOSE" in pages[0] and "Vorderansicht" in pages[0] and "Rückansicht" in pages[0]
    assert "Genäht mit" in pages[0] and "Schwierigkeit" in pages[0] and "Nahtzugabe" in pages[0]
    assert "Teile" in pages[1] and "Farben und Linien" in pages[1]
    assert "Grundlagen: die Overlock" in text and "Grundlagen: Handstiche" in text
    assert "Schablone" in text and "5 × 5 cm" in text
    assert "Fertig!" in text
    # two steps per page
    step_pages = {rec["page"] for rec in checks}
    assert len(checks) == len(steps) and len(step_pages) == -(-len(steps) // 2)


def test_reference_steps_have_important_or_tip(kord):
    _checks, _pages, steps, _pat = kord
    body = [s for s in steps if s.section not in ("Prepare", "Finish")]
    missing = [s.title for s in body if not (s.tip or s.hint) and s.stitch not in ("finish", "topstitch")]
    assert not missing, missing
    titles = [s.title for s in steps]
    assert "Label the pieces" in titles
    pocket = next(s for s in steps if s.title.startswith("Stitch the pocket on"))
    assert pocket.data.get("only") == "right" and "ONE" in pocket.tip


def test_reference_nothing_leaves_its_panel(kord):
    checks = kord[0]
    assert checks and not _problems(checks)


def test_template_for_the_fake_fly(kord):
    pat = kord[3]
    tpl = B.templates(pat)
    assert len(tpl) == 1 and tpl[0][0].key == "front"


@pytest.mark.parametrize("garment,options,size", [
    ("tshirt_basic", {}, 122), ("hoodie", {"front": "zip"}, 140), ("skirt", {}, 122), ("dress", {}, 122),
])
def test_other_modules_fit_their_panels(tmp_path, garment, options, size):
    checks = _run(tmp_path, garment, options, "de", size)
    assert checks and not _problems(checks)


def test_difficulty_estimate():
    pat, _, _ = GN.draft_from_spec(dict(garment="loop", size=122))
    level, hours = B.difficulty(pat, S.assembly(pat))
    assert level == "easy" and hours >= 1.0
