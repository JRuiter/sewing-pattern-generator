"""Pants options from issue #39: fake fly, single back pocket, hem casing, pocket bag fabric,
custom title, fabrics with a nap."""
from __future__ import annotations

import numpy as np
import pytest
from shapely.geometry import LineString, Polygon

import ease as E
import generate as GN
import instructions as I
import layout as L
import steps as ST
import validate as V
from garments import get

KORD = {"style": "trousers", "fabric": "corduroy", "fit": "wide", "crotch_drop": 20, "knee_total": 330,
        "opening_total": 260, "waistband": "rib", "pockets": ["side"], "fake_fly": True, "back_pockets": 1,
        "hem_finish": "elastic_casing", "pocket_bag_fabric": "cotton", "title": "Kordhose"}


def _draft(**opts):
    pat, _, _ = GN.draft_from_spec(dict(garment="pants_basic", size=122, options=opts))
    return pat


@pytest.fixture(scope="module")
def kord():
    return _draft(**KORD)


def test_reference_order_validates(kord):
    rep = V.validate(kord)
    assert V.is_ok(rep)
    assert kord.title == "Kordhose"
    assert GN._basename(kord).startswith("kordhose_")


def test_fake_fly_line_inside_front_and_starts_at_crotch_seam(kord):
    front = kord.piece("front")
    mark = next(m for m in front.marks if m.label.startswith("Fake fly"))
    assert "left front leg only" in mark.label
    poly = Polygon(front.seam_ring())
    j = mark.pts
    # every point except the end on the crotch seam lies inside the front leg
    assert poly.buffer(-0.5).contains(LineString(j[3:-3]))   # between waist and crotch seam
    crotch = LineString(front.edge("crotch").pts)
    assert crotch.distance(LineString([j[-1], j[-1] + 0.01])) < 0.5
    # starts at the waist, 30 mm from centre front, and is length_frac_R × rise long
    assert j[0] == pytest.approx([30.0, 0.0])
    assert -j[:, 1].min() == pytest.approx(0.62 * kord.options["_R"], abs=0.5)


def test_fake_fly_step_does_not_claim_it_catches_the_allowance(kord):
    steps = ST.assembly(kord)
    fly = next(s for s in steps if s.title == "Topstitch the fake fly")
    assert "does not catch" in fly.tip
    assert "left front leg" in fly.text
    # with a 12 mm offset the inner row (6 mm) lies inside a 10 mm allowance
    narrow = _draft(**{**KORD, "fake_fly": {"offset_mm": 12, "radius_mm": 8}})
    fly2 = next(s for s in ST.assembly(narrow) if s.title == "Topstitch the fake fly")
    assert "catches the crotch seam allowance" in fly2.tip


def test_single_back_pocket(kord):
    pocket = kord.piece("back_pocket")
    assert pocket.cut_count == 1 and not pocket.mirror
    labels = [m.label for m in kord.piece("back").marks]
    assert "Back pocket (right back leg only)" in labels
    steps = ST.assembly(kord)
    place = next(s for s in steps if s.title.startswith("Stitch the pocket on"))
    assert place.title.endswith("(right back leg only)") and place.repeat == 1
    left = _draft(**{**KORD, "back_pocket_side": "left"})
    assert "Back pocket (left back leg only)" in [m.label for m in left.piece("back").marks]
    two = _draft(**{**KORD, "back_pockets": 2})
    assert two.piece("back_pocket").cut_count == 2


def test_back_pocket_step_uses_the_real_seam_allowance():
    pat = _draft(**{**KORD, "seam_allowance_mm": 7.5})
    press = next(s for s in ST.assembly(pat) if s.title == "Press the edges under")
    assert press.text.startswith("7.5 mm") and press.amount == pytest.approx(7.5)


def test_hem_casing_allowance_and_steps(kord):
    for key in ("front", "back"):
        assert kord.piece(key).edge("hem").sa == pytest.approx(35.0)       # 5 + 20 mm elastic + 10
    wide = _draft(**{**KORD, "hem_elastic_mm": 30, "hem_elastic_len_cm": 21})
    assert wide.piece("front").edge("hem").sa == pytest.approx(45.0)
    texts = " ".join(ST.as_texts(ST.assembly(wide), wide.options))
    assert "21 cm per leg + 2 cm overlap" in texts
    assert "leave 3 cm open at the inseam" in texts
    # cuffs and casing do not go together: cuffs win
    cuffed = _draft(**{**KORD, "cuffs": True})
    assert cuffed.options["hem_finish"] == "plain"


def test_pocket_bag_fabric_is_its_own_group(kord):
    assert kord.piece("pocket_bag").fabric.startswith("Lining")
    plans = I.fabric_consumption(kord)
    assert "Lining" in plans
    lining_keys = {kord.pieces[i].key for i, _ in plans["Lining"]["meta"]}
    assert lining_keys == {"pocket_bag"}
    default = _draft(style="trousers", fabric="woven", pockets=["side"])
    assert "Lining" not in I.fabric_consumption(default)


def test_nap_layout_keeps_every_piece_waist_up(kord):
    assert E.has_nap(kord.options)
    for mode in ("single", "folded"):
        plans = L.layout_fabric(kord, {"Main fabric": 1500.0}, mode=mode)
        main = plans["Main fabric"]
        assert main["nap"]
        for pl in main["placements"]:
            assert L.up_y(pl.angle) > 0, (mode, kord.pieces[main["meta"][pl.index][0]].key, pl.angle)
    # without a nap, rotating by 180° stays allowed
    plain = _draft(**{**KORD, "fabric": "woven"})
    assert not E.has_nap(plain.options)
    assert not L.layout_fabric(plain, mode="single")["Main fabric"]["nap"]
    assert E.has_nap({"fabric": "woven", "nap": True})


def test_nap_label_on_cutting_layout(kord, tmp_path):
    plans = I.fabric_consumption(kord)
    assert "none turned round" in I.layout_text(plans["Main fabric"])
    I.render_fabric_png(kord, plans, str(tmp_path / "c.png"))
    assert (tmp_path / "c.png").stat().st_size > 1000


def test_pressing_note_per_fabric(kord):
    done = ST.assembly(kord)[-1]
    assert "terry towel" in done.text
    tee, _, _ = GN.draft_from_spec(dict(garment="tshirt_basic", size=122, options={"fabric": "jersey"}))
    assert ST.assembly(tee)[-1].text == "Press all seams with steam."


def test_invalid_options():
    mod = get("pants_basic")
    with pytest.raises(ValueError):
        mod.resolve_options({"back_pockets": 3})
    with pytest.raises(ValueError):
        mod.resolve_options({"hem_finish": "zip"})
    with pytest.raises(ValueError):
        mod.resolve_options({"pocket_bag_fabric": "silk"})
    assert np.isclose(mod.hem_casing_mm({"hem_elastic_mm": 15}), 25.0)
