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
    import booklet_qa as QA
    return [p for rec in checks for p in QA.text_problems(rec)]


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
    assert "Kordhose" in pages[0] and "Vorderansicht" in pages[0] and "Rückansicht" in pages[0]
    assert "Genäht mit: Overlock + Handnadel" in pages[0] and "Schritte" in pages[0]
    assert "Teile" in pages[1] and "Nahtzugabe" in pages[1] and "Material" in pages[1]
    assert "0,85 m bei 150 cm Breite" in pages[1] and "Farben in dieser Anleitung" in pages[1]
    assert "Grundlagen: die Overlock" in text and "Grundlagen: Handstiche" in text
    assert "Schablone" in text and "5 × 5 cm" in text
    assert "Fertig!" in text
    # two steps per page; "Done!" before the templates
    step_pages = {rec["page"] for rec in checks}
    assert len(checks) == len(steps) and len(step_pages) == -(-len(steps) // 2)
    assert text.index("Fertig!") < text.index("5 × 5 cm")


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


def test_garment_views_are_whole_garments():
    from shapely.geometry import LineString, Polygon

    import views as V
    harem, _, _ = GN.draft_from_spec(dict(garment="pants_basic", size=122, options={"style": "harem"}))
    for name, view in V.garment_views(harem).items():
        keys = [pc.key for _r, pc, _z in view["layers"]]
        assert keys.count("waistband") == 1 and keys.count("leg_cuff") == 2, (name, keys)
        body = Polygon(view["layers"][0][0])
        y0, y1 = body.bounds[1], body.bounds[3]
        low = body.intersection(LineString([(-1e5, y0 + 0.05 * (y1 - y0)), (1e5, y0 + 0.05 * (y1 - y0))]))
        assert low.geom_type == "MultiLineString", name          # two separate legs at the hem
    hoodie, _, _ = GN.draft_from_spec(dict(garment="hoodie", size=140, options={"kangaroo": True}))
    for name, view in V.garment_views(hoodie).items():
        keys = [pc.key for _r, pc, _z in view["layers"]]
        assert keys.count("sleeve") == 2 and keys.count("sleeve_cuff") == 2 and "hem_band" in keys, (name, keys)
        assert "hood" in keys


def test_seams_of_different_shape_are_shown_side_by_side(kord):
    """Side seams and inseams of front and back differ: no skewed stacked picture."""
    import diagrams as DG
    _checks, _pages, steps, pat = kord
    for title in ("Sew the side seams", "Sew the inseams"):
        st = next(s for s in steps if s.title == title)
        sms = S.resolve_seams(pat, st)
        assert len(sms) == 1 and DG.overlay_parts(pat, sms[0]) is None, title


def test_booklet_qa_finds_broken_drawings():
    """The automatic booklet check reports the mistakes that once slipped through."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    import booklet_qa as QA
    import views as V
    hoodie, _, _ = GN.draft_from_spec(dict(garment="hoodie", size=140, options={"kangaroo": True}))
    views = V.garment_views(hoodie)
    views["front"]["layers"] = [lay for lay in views["front"]["layers"] if lay[1].key != "sleeve"]
    QA.reset()
    QA.check_views(hoodie, views)
    assert any("'sleeve' missing" in i["text"] for i in QA.ISSUES)
    harem, _, _ = GN.draft_from_spec(dict(garment="pants_basic", size=122, options={"style": "harem"}))
    views = V.garment_views(harem)
    views["back"]["layers"] = [lay for lay in views["back"]["layers"] if lay[1].key != "leg_cuff"]
    QA.reset()
    QA.check_views(harem, views)
    assert any("leg_cuff" in i["text"] for i in QA.ISSUES)
    # a tiny drawing in a big picture area
    fig = plt.figure(figsize=B.PAGE)
    ax = fig.add_axes((0.1, 0.1, 0.5, 0.4))
    ax.plot([0, 1], [0, 1])
    ax.set_xlim(-20, 20)
    ax.set_ylim(-20, 20)
    QA.reset()
    QA.check_picture(ax, 3, "x", (0.1, 0.1, 0.5, 0.4))
    plt.close(fig)
    assert QA.ISSUES and QA.ISSUES[0]["kind"] == "picture"
    QA.reset()


@pytest.mark.parametrize("garment,options,size", [
    ("pants_basic", {"style": "harem"}, 122), ("hoodie", {"kangaroo": True}, 140), ("dress", {}, 122),
])
def test_booklet_check_is_clean_and_reported(tmp_path, garment, options, size):
    res = GN.run(dict(garment=garment, size=size, options=options, formats=["a4"], out=str(tmp_path)),
                 verbose=False)
    assert res["booklet_issues"] == []
    assert "Booklet check" in (tmp_path / "validation_report.md").read_text(encoding="utf-8")


def test_kord_booklet_check_is_clean(kord):
    import booklet_qa as QA
    assert QA.ISSUES == []
