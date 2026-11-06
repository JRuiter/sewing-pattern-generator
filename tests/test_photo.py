"""Foto-Modus A und B: Messgenauigkeit an synthetischen Testbildern mit bekannter Geometrie,
Merkmalsliste/Mapping und Rundlauf-Test (Schnitt → Foto → Reverse Engineering → Schnitt)."""
import cv2
import numpy as np
import pytest

import measurements as M
import photo_analyze as A
import photo_measure as PM
import photo_synth as S
import refcard
from garments import pants_basic as PB
from reverse import fit as F
from reverse import pipeline as P
from reverse import store as ST
from reverse import unfold as U
from reverse import verify as VF

# (Größe, Stil, Seed) – drei Testbilder
PHOTOS = [(122, "haremshose", 0), (98, "jogginghose", 1), (152, "leggings", 2)]
LENGTHS = ["front_rise", "inseam", "outseam", "waistband_h", "cuff_h"]
WIDTHS = ["hip_circ", "thigh_circ", "opening", "waist_relaxed"]


@pytest.fixture(scope="module", params=PHOTOS, ids=[f"{s}-{st}" for s, st, _ in PHOTOS])
def synthetic(request, tmp_path_factory):
    size, style, seed = request.param
    pat = PB.draft(M.size_measures(size), {"style": style})
    path = tmp_path_factory.mktemp("foto") / f"hose_{size}.jpg"
    _, truth = S.synth_pants_photo(pat, str(path), seed=seed)
    return dict(path=str(path), truth=truth, style=style, size=size)


# ---------------------------------------------------------------------------
# Referenzkarte
# ---------------------------------------------------------------------------

def test_reference_card_markers_detected():
    card = refcard.raster_card(4.0)
    img = cv2.copyMakeBorder(card, 80, 80, 80, 80, cv2.BORDER_CONSTANT, value=255)
    _, _, found = PM.detect_card(cv2.cvtColor(img, cv2.COLOR_GRAY2BGR))
    assert found == [0, 1, 2, 3]


def test_missing_card_gives_german_error():
    img = np.full((600, 800, 3), 180, np.uint8)
    with pytest.raises(PM.MeasureError, match="Referenzkarte"):
        PM.measure(img)


# ---------------------------------------------------------------------------
# Modus B: Messgenauigkeit (Längen < 1 cm, Weiten < 2 %)
# ---------------------------------------------------------------------------

def test_mode_b_measurement_accuracy(synthetic, tmp_path):
    r = PM.measure(synthetic["path"], "hose", overlay_path=str(tmp_path / "overlay.png"))
    assert (tmp_path / "overlay.png").exists()
    t = U.unfold("hose", r["measures_mm"])
    truth = synthetic["truth"]
    for k in LENGTHS:
        assert abs(t[k] - truth[k]) < 10.0, (k, t[k], truth[k])
    for k in WIDTHS:
        assert abs(t[k] - truth[k]) / truth[k] < 0.02, (k, t[k], truth[k])


def test_tape_values_override_photo(synthetic):
    r = PM.measure(synthetic["path"], "hose", tape={"inseam": 40.0})
    assert abs(r["measures_mm"]["inseam"] - 400.0) < 1e-6


# ---------------------------------------------------------------------------
# Modus A: Merkmalsliste mit Konfidenz → Modul + Optionen
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("size,style,expected", [(122, "haremshose", "harem"), (128, "jogginghose", "gerade"),
                                                 (140, "leggings", "eng")])
def test_mode_a_silhouette_from_flatlay(size, style, expected):
    pat = PB.draft(M.size_measures(size), {"style": style})
    info = S.pants_silhouette(pat, splay_deg=4)
    scene, _, _ = S.render_scene(info, px_per_mm=1.5, seed=size)
    feats = A.classify_pants(A.pants_proportions(scene))
    assert feats["silhouette"]["wert"] == expected
    assert 0 < feats["silhouette"]["konfidenz"] <= 1


def test_mode_a_mapping_and_confirmation():
    feats = {"kleidungsart": {"wert": "jogginghose", "konfidenz": 0.9},
             "silhouette": {"wert": "harem", "konfidenz": 0.7},
             "taschen": {"wert": ["eingriff"], "konfidenz": 0.6},
             "bein_abschluss": {"wert": "buendchen", "konfidenz": 0.9},
             "bund": {"wert": "tunnelzug", "konfidenz": 0.5},
             "stoff": {"wert": "sweat", "konfidenz": 0.6}}
    txt = A.confirmation_text(feats)
    assert txt.startswith("Ich erkenne") and "Stimmt das" in txt.replace("stimmt das", "Stimmt das")
    m = A.map_to_module(feats)
    assert m["module"] == "pants_basic"
    assert m["options"]["fit"] == "harem"
    assert m["options"]["cuffs"] is True


def test_mode_a_unsupported_is_reported():
    feats = {"kleidungsart": {"wert": "jeans", "konfidenz": 0.9},
             "taschen": {"wert": ["cargo"], "konfidenz": 0.8}}
    m = A.map_to_module(feats)
    assert any("Jeans" in x for x in m["nicht_abgedeckt"])
    assert any("Cargo" in x for x in m["nicht_abgedeckt"])


# ---------------------------------------------------------------------------
# Rundlauf: Schnitt → Foto → Reverse Engineering → Schnitt
# ---------------------------------------------------------------------------

def test_round_trip(synthetic, tmp_path):
    res = P.run(synthetic["path"], "hose", str(tmp_path / "projekt"))
    assert VF.all_ok(res["rows"]), VF.to_markdown(res["rows"])
    assert not any(c.status == "FEHLER" for c in res["report"])
    rec, truth = res["pattern"].finished, synthetic["truth"]
    for k in ("front_rise", "inseam", "outseam"):
        assert abs(rec[k] - truth[k]) < 10.0, (k, rec[k], truth[k])
    for k in ("hip_circ", "thigh_circ", "opening", "waist_relaxed"):
        assert abs(rec[k] - truth[k]) / truth[k] < 0.02, (k, rec[k], truth[k])
    expected_fit = {"haremshose": "harem", "jogginghose": "normal", "leggings": "eng"}[synthetic["style"]]
    assert res["fit"]["fit"] == expected_fit
    # Projekt gespeichert und wieder ladbar, Gradieren um 2 Größen
    proj = ST.load(str(tmp_path / "projekt" / "projekt.json"))
    assert proj["modul"] == "pants_basic"
    g, targets = P.regrade(str(tmp_path / "projekt" / "projekt.json"), 2)
    assert g["pattern"].finished["hip_circ"] > rec["hip_circ"]
