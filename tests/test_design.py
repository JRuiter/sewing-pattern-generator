"""Creative silhouettes (design.py): every garment can be reshaped, seams stay matched, the result
is re-checked (room to move, sewability) and the report marks the deviations as intended."""
from __future__ import annotations

import numpy as np
import pytest

import design as DS
import generate as GN
import geometry as G
import i18n
import steps as ST
import validate as V

CASES = [
    ("hoodie", "starfish"), ("hoodie", "dino_spikes"), ("hoodie", "bell_sleeves"),
    ("tshirt_basic", "starfish"), ("tshirt_basic", "zigzag_hem"), ("tshirt_basic", "balloon"),
    ("dress", "tulip_skirt"), ("dress", "petal_hem"), ("skirt", "petal_hem"), ("skirt", "tulip_skirt"),
    ("pants_basic", "balloon_legs"), ("pants_basic", "flared_legs"), ("beanie", "cat_ears"),
    ("beanie", "elf"), ("beanie", "dino_spikes"), ("loop", "wavy_loop"),
]


def draft(garment, design, size=122, **opts):
    p, _, _ = GN.draft_from_spec(dict(garment=garment, size=size, options=opts, design=design))
    return p


@pytest.mark.parametrize("garment,preset", CASES)
def test_presets_are_sewable(garment, preset):
    pat = draft(garment, preset)
    rep = V.validate(pat)
    errs = [f"{c.group}/{c.name}: {c.actual}" for c in rep if c.status == "ERROR"]
    assert not errs, errs
    assert pat.design["name"] == DS.PRESETS[preset]["name"]
    assert any(c.group == "Design (intended)" for c in rep)
    assert all(c.status == "OK" for c in rep if c.group == "Design (intended)")


def test_every_garment_has_zones_and_a_preset():
    from garments import GARMENTS
    for g in GARMENTS:
        assert g in DS.ZONES, g
        assert any(g in p["garments"] for p in DS.PRESETS.values()), g


def test_seam_partners_stay_equal_and_shape_changes():
    base = draft("hoodie", None)
    pat = draft("hoodie", "starfish")
    for key in ("front", "back"):
        a, b = base.piece(key).edge("side"), pat.piece(key).edge("side")
        dx = max(abs(G.point_at(b.pts, s)[0] - G.point_at(a.pts, s * a.length / b.length)[0])
                 for s in np.linspace(0, b.length, 30))
        assert dx > 25, "the side seam bulges out"
    assert abs(pat.piece("front").edge("side").length - pat.piece("back").edge("side").length) < 2
    # attached ends do not move: armhole and underarm stay where they were
    assert np.allclose(pat.piece("front").edge("armhole").pts, base.piece("front").edge("armhole").pts)
    # the hood got its tip
    assert pat.piece("hood").seam_ring()[:, 1].max() > base.piece("hood").seam_ring()[:, 1].max() + 30


def test_prepare_switches_off_what_the_shape_cannot_have():
    pat = draft("hoodie", "starfish")
    assert not pat.has("hem_band") and not pat.has("kangaroo_pocket")
    assert any("hem_band" in n for n in pat.notes)
    front_hem = pat.piece("front").edge("hem")
    assert front_hem.pointed and not front_hem.turned and front_hem.sa <= 10


def test_too_tight_design_is_an_error():
    pat = draft("tshirt_basic", {"name": "Wasp", "features": [
        {"zone": "side", "profile": [[0.5, -9.0]]}]})
    rep = V.validate(pat)
    tight = [c for c in rep if c.group == "Freedom of movement"]
    assert tight and tight[0].status == "ERROR"
    assert not V.is_ok(rep)


def test_short_seam_scales_the_shape_down():
    pat = draft("tshirt_basic", "bell_sleeves")      # short sleeve: 6 cm flare does not fit
    row = next(c for c in pat.design_checks if c["group"] == "Design (intended)")
    assert "scaled to" in row["note"]
    assert V.is_ok(V.validate(pat))


def test_appendages_become_pieces_with_steps_and_notches():
    pat = draft("hoodie", "dino_spikes")
    spike = pat.piece("design_spike")
    assert spike.cut_count == 12
    assert len([n for n in pat.piece("hood").notches if n.edge == "center"]) >= 12
    steps = ST.assembly(pat)
    titles = [s.title for s in steps]
    i = titles.index("Sew the spikes")
    assert titles[i + 1] == "Turn the spikes right side out"
    hood_step = next(s for s in steps[i + 2:] if any("Hood centre" in n for n in s.seams))
    assert "spikes" in hood_step.hint


def test_unknown_zone_and_preset():
    with pytest.raises(DS.DesignError):
        draft("pants_basic", {"features": [{"zone": "hood", "peak": {"cm": 5}}]})
    with pytest.raises(DS.DesignError):
        DS.load("patrick")


def test_describe_lists_features_and_consequences():
    txt = DS.describe("hoodie", "starfish")
    assert "Hem: 2 × points, 7.0 cm deep" in txt
    assert "hem_band = False" in txt and "kangaroo = False" in txt


def test_no_design_changes_nothing():
    a, b = draft("hoodie", None), draft("hoodie", "")
    assert not a.design and not a.design_checks
    assert [p.key for p in a.pieces] == [p.key for p in b.pieces]


def test_german_design_texts():
    pat = draft("hoodie", "starfish")
    with i18n.language("de"):
        i18n.MISSING.clear()
        rows = V.to_rows(V.validate(pat))
        names = [r["name"] for r in rows if r["group"] in ("Design (gewollt)", "Bewegungsfreiheit")]
        assert "Saum: 2 × Zacken, 7,0 cm tief" in names
        assert not {m for m in i18n.MISSING if "design" in m.lower() or "girth" in m}


def test_generate_writes_files_with_design(tmp_path):
    res = GN.run(dict(garment="hoodie", size=128, design="starfish", formats=["a4"], out=str(tmp_path)),
                 verbose=False)
    assert res["ok"]
    assert "Design (intended)" in res["report_md"]
    assert not res["booklet_issues"]
