"""Photo modes A and B: measuring accuracy on synthetic test images with known geometry,
feature list/mapping and round-trip test (pattern → photo → reverse engineering → pattern)."""
import cv2
import numpy as np
import pytest

import measurements as M
import photo_analyze as A
import photo_measure as PM
import photo_synth as S
import refcard
from garments import pants_basic as PB
from reverse import pipeline as P
from reverse import store as ST
from reverse import unfold as U
from reverse import verify as VF

# (size, style, seed): three test images
PHOTOS = [(122, "harem", 0), (98, "jogger", 1), (152, "leggings", 2)]
LENGTHS = ["front_rise", "inseam", "outseam", "waistband_h", "cuff_h"]
WIDTHS = ["hip_circ", "thigh_circ", "opening", "waist_relaxed"]


@pytest.fixture(scope="module", params=PHOTOS, ids=[f"{s}-{st}" for s, st, _ in PHOTOS])
def synthetic(request, tmp_path_factory):
    size, style, seed = request.param
    pat = PB.draft(M.size_measures(size), {"style": style})
    path = tmp_path_factory.mktemp("photo") / f"pants_{size}.jpg"
    _, truth = S.synth_pants_photo(pat, str(path), seed=seed)
    return dict(path=str(path), truth=truth, style=style, size=size)


# ---------------------------------------------------------------------------
# Reference card
# ---------------------------------------------------------------------------

def test_reference_card_markers_detected():
    card = refcard.raster_card(4.0)
    img = cv2.copyMakeBorder(card, 80, 80, 80, 80, cv2.BORDER_CONSTANT, value=255)
    _, _, found = PM.detect_card(cv2.cvtColor(img, cv2.COLOR_GRAY2BGR))
    assert found == [0, 1, 2, 3]


def test_missing_card_gives_clear_error():
    img = np.full((600, 800, 3), 180, np.uint8)
    with pytest.raises(PM.MeasureError, match="Reference card"):
        PM.measure(img)


# ---------------------------------------------------------------------------
# Mode B: measuring accuracy (lengths < 1 cm, widths < 2 %)
# ---------------------------------------------------------------------------

def test_mode_b_measurement_accuracy(synthetic, tmp_path):
    r = PM.measure(synthetic["path"], "pants", overlay_path=str(tmp_path / "overlay.png"))
    assert (tmp_path / "overlay.png").exists()
    t = U.unfold("pants", r["measures_mm"])
    truth = synthetic["truth"]
    for k in LENGTHS:
        assert abs(t[k] - truth[k]) < 10.0, (k, t[k], truth[k])
    for k in WIDTHS:
        assert abs(t[k] - truth[k]) / truth[k] < 0.02, (k, t[k], truth[k])


def test_tape_values_override_photo(synthetic):
    r = PM.measure(synthetic["path"], "pants", tape={"inseam": 40.0})
    assert abs(r["measures_mm"]["inseam"] - 400.0) < 1e-6


# ---------------------------------------------------------------------------
# Mode A: feature list with confidence → module + options
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("size,style,expected", [(122, "harem", "harem"), (128, "jogger", "straight"),
                                                 (140, "leggings", "slim")])
def test_mode_a_silhouette_from_flatlay(size, style, expected):
    pat = PB.draft(M.size_measures(size), {"style": style})
    info = S.pants_silhouette(pat, splay_deg=4)
    scene, _, _ = S.render_scene(info, px_per_mm=1.5, seed=size)
    feats = A.classify_pants(A.pants_proportions(scene))
    assert feats["silhouette"]["value"] == expected
    assert 0 < feats["silhouette"]["confidence"] <= 1


def test_mode_a_mapping_and_confirmation():
    feats = {"garment_type": {"value": "jogger", "confidence": 0.9},
             "silhouette": {"value": "harem", "confidence": 0.7},
             "pockets": {"value": ["side"], "confidence": 0.6},
             "leg_finish": {"value": "rib", "confidence": 0.9},
             "waistband": {"value": "drawstring", "confidence": 0.5},
             "fabric": {"value": "sweat", "confidence": 0.6}}
    txt = A.confirmation_text(feats)
    assert txt.startswith("I can see") and "Is that right?" in txt
    m = A.map_to_module(feats)
    assert m["module"] == "pants_basic"
    assert m["options"]["fit"] == "harem"
    assert m["options"]["cuffs"] is True


def test_mode_a_unsupported_is_reported():
    feats = {"garment_type": {"value": "jeans", "confidence": 0.9},
             "pockets": {"value": ["cargo"], "confidence": 0.8}}
    m = A.map_to_module(feats)
    assert any("Jeans" in x for x in m["not_covered"])
    assert "cargo" in m["options"]["pockets"]                 # cargo pockets are a module option now
    assert not any("Cargo" in x for x in m["not_covered"])


def test_mode_a_flared_cargo_shorts():
    m = A.map_to_module({"garment_type": {"value": "pants", "confidence": 0.9},
                         "silhouette": {"value": "flared", "confidence": 0.8},
                         "pockets": {"value": ["cargo"], "confidence": 0.8}})
    assert m["options"]["leg_shape"] == "flare" and m["options"]["cuffs"] is False
    assert "cargo" in m["options"]["pockets"]
    assert not m["not_covered"]
    m = A.map_to_module({"garment_type": {"value": "shorts", "confidence": 0.9},
                         "leg_finish": {"value": "turn_up", "confidence": 0.8}})
    assert m["options"]["turn_up"] == 3.0 and m["options"]["length"] == "short"


# ---------------------------------------------------------------------------
# Round trip: pattern → photo → reverse engineering → pattern
# ---------------------------------------------------------------------------

def test_round_trip(synthetic, tmp_path):
    res = P.run(synthetic["path"], "pants", str(tmp_path / "project"))
    assert VF.all_ok(res["rows"]), VF.to_markdown(res["rows"])
    assert not any(c.status == "ERROR" for c in res["report"])
    rec, truth = res["pattern"].finished, synthetic["truth"]
    for k in ("front_rise", "inseam", "outseam"):
        assert abs(rec[k] - truth[k]) < 10.0, (k, rec[k], truth[k])
    for k in ("hip_circ", "thigh_circ", "opening", "waist_relaxed"):
        assert abs(rec[k] - truth[k]) / truth[k] < 0.02, (k, rec[k], truth[k])
    expected_fit = {"harem": "harem", "jogger": "normal", "leggings": "slim"}[synthetic["style"]]
    assert res["fit"]["fit"] == expected_fit
    # project saved and loadable again, grading by 2 sizes
    proj = ST.load(str(tmp_path / "project" / "project.json"))
    assert proj["module"] == "pants_basic"
    g, targets = P.regrade(str(tmp_path / "project" / "project.json"), 2)
    assert g["pattern"].finished["hip_circ"] > rec["hip_circ"]


# ---------------------------------------------------------------------------
# Mode B for tops (issue #4): T-shirt with set-in or raglan sleeves
# ---------------------------------------------------------------------------

TOP_CASES = [("set_in", "98", "short"), ("set_in", "140", "long"), ("set_in", "w38", "short"),
             ("raglan", "98", "short"), ("raglan", "140", "long"), ("raglan", "w38", "short")]


def _top(style, size, sleeve):
    import generate as GEN
    pat, _, _ = GEN.draft_from_spec({"garment": "tshirt_basic", "size": size,
                                     "options": {"sleeve_style": style, "sleeve_length": sleeve}})
    return pat


@pytest.fixture(scope="module", params=TOP_CASES, ids=["-".join(c) for c in TOP_CASES])
def top_photo(request, tmp_path_factory):
    style, size, sleeve = request.param
    pat = _top(style, size, sleeve)
    path = tmp_path_factory.mktemp("top") / f"top_{style}_{size}.jpg"
    S.synth_top_photo(pat, str(path), seed=1, tilt=0.01)
    return dict(path=str(path), pattern=pat, style=style)


def test_top_measurement_matches_flat_lay_model(top_photo, tmp_path):
    import flatlay as FL
    r = PM.measure(top_photo["path"], "top", overlay_path=str(tmp_path / "overlay.png"))
    mm = r["measures_mm"]
    assert mm["_sleeve_style"] == top_photo["style"]
    assert mm["_sleeve_style_confidence"] >= 0.5
    model = FL.top_flatlay(top_photo["pattern"])["features"]
    for k in (FL.FEATURES if top_photo["style"] == "raglan" else FL.FEATURES_SET_IN):
        tol = 0.02 * model[k] if k in ("chest_flat", "hem_flat") else 5.0
        assert abs(mm[k] - model[k]) <= tol, (k, mm[k], model[k])
    assert (tmp_path / "overlay.png").exists()


def test_top_round_trip(top_photo, tmp_path):
    """Pattern → synthetic photo → reverse engineering → pattern: the finished measurements come
    back within the project tolerance (widths ± 2 %, everything else ± 1 cm)."""
    res = P.run(top_photo["path"], "top", str(tmp_path / "project"))
    assert res["fit"]["sleeve_style"] == top_photo["style"]
    assert VF.all_ok(res["rows"]), VF.to_markdown(res["rows"])
    assert not any(c.status == "ERROR" for c in res["report"])
    got, truth = res["pattern"].finished, top_photo["pattern"].finished
    for k in ("chest_circ", "hem_circ", "length", "sleeve_len", "sleeve_opening", "bicep_circ", "neckline"):
        tol = 0.02 * truth[k] if k in ("chest_circ", "hem_circ") else 10.0
        assert abs(got[k] - truth[k]) <= tol, (k, got[k], truth[k])
    proj = ST.load(str(tmp_path / "project" / "project.json"))
    assert proj["module"] == "tshirt_basic" and proj["options"]["sleeve_style"] == top_photo["style"]
    assert (tmp_path / "project" / "reverse_report.md").exists()


def test_top_tape_chest_corrects_the_scale(tmp_path):
    pat = _top("set_in", "122", "short")
    path = tmp_path / "top.jpg"
    S.synth_top_photo(pat, str(path), seed=4, tilt=0.01)
    import flatlay as FL
    model = FL.top_flatlay(pat)["features"]
    r = PM.measure(str(path), "top", tape={"chest_flat": model["chest_flat"] / 10})
    mm = r["measures_mm"]
    assert r["source"]["chest_flat"] == "tape measure"
    for k in ("hem_flat", "length", "sleeve_reach"):
        assert abs(mm[k] / model[k] - 1) < 0.01, (k, mm[k], model[k])


def test_top_regrade_two_sizes_up(tmp_path):
    pat = _top("raglan", "110", "short")
    path = tmp_path / "top.jpg"
    S.synth_top_photo(pat, str(path), seed=1, tilt=0.01)
    P.run(str(path), "top", str(tmp_path / "project"))
    res, finished = P.regrade(str(tmp_path / "project" / "project.json"), 2)
    ref = _top("raglan", "122", "short").finished
    assert res["size"] == 122
    for k in ("chest_circ", "length", "bicep_circ", "neckline"):
        assert abs(finished[k] - ref[k]) <= max(10.0, 0.02 * ref[k]), (k, finished[k], ref[k])


def test_top_missing_photos():
    from reverse import decompose as D
    feat = D.features_from_measurement("top", {"_sleeve_style": "raglan"})
    assert feat["options"]["sleeve_style"] == "raglan"
    msgs = D.missing_photos(feat)
    assert any("front neckline was not found" in m for m in msgs)
    assert any("armhole" in m for m in msgs)
    feat = D.features_from_measurement("top", {"_sleeve_style": "set_in", "front_neck": 80.0})
    assert not any("front neckline" in m for m in D.missing_photos(feat))
