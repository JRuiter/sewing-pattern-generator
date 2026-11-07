"""Doll clothes mode (doll.py): measurements, narrow allowances, back opening, all garments
sewable across doll sizes, photo mode B for doll clothes, and generate.py end to end."""
import json
import os

import numpy as np
import pytest

import doll as D
import generate as GEN
import photo_synth as S
import validate as V
from garments import get
from reverse import pipeline as P

DOLL_CM = {"height": 45, "chest": 30, "waist": 28, "hip": 31, "head": 32, "arm": 12, "inseam": 14,
           "side_length": 22}
GARMENTS = [
    ("dress", {}),
    ("dress", {"style": "shirt_dress"}),
    ("dress", {"skirt": "circle", "sleeve_length": "long"}),
    ("dress", {"skirt": "a_line", "sleeve_style": "raglan"}),
    ("skirt", {}),
    ("skirt", {"style": "circle"}),
    ("pants_basic", {}),
    ("pants_basic", {"style": "jogger", "fabric": "sweat", "length": "short"}),
    ("tshirt_basic", {}),
    ("tshirt_basic", {"sleeve_style": "raglan", "sleeve_length": "long"}),
    ("tshirt_basic", {"fabric": "jersey"}),
]


def doll_pattern(garment, opts=None, cm=None):
    m, _ = D.complete_measures(cm or DOLL_CM)
    return D.draft(get(garment), garment, m, D.defaults(garment, opts or {}, m))


def test_measurements_need_height_and_follow_given_values():
    with pytest.raises(ValueError, match="height"):
        D.complete_measures({"chest": 30})
    with pytest.raises(ValueError, match="range"):
        D.complete_measures({"height": 150})
    m, src = D.complete_measures({"height": 40, "chest": 30})
    assert src["chest"] == "user" and src["hip"] == "derived"
    assert m["chest"] == 300
    # a chunky doll: the circumferences that were not given follow the chest
    assert m["hip"] > D.PROPORTIONS["hip"] * 400 * 1.1
    assert m["crotch_depth"] == pytest.approx(m["side_length"] - m["inseam"])
    assert D.validate_measures(m) == []


@pytest.mark.parametrize("garment,opts", GARMENTS, ids=[f"{g}-{'-'.join(map(str, o.values())) or 'default'}"
                                                         for g, o in GARMENTS])
def test_doll_garments_are_sewable(garment, opts):
    pat = doll_pattern(garment, opts)
    rep = V.validate(pat)
    assert V.is_ok(rep), V.to_markdown(rep)
    # narrow doll allowances: 6 mm seams, hems ≤ 10 mm (circle-skirt hem narrower)
    for pc in pat.pieces:
        for e in pc.edges:
            if e.fold:
                continue
            assert e.sa <= 15.5, (pc.name, e.label, e.sa)
    side = pat.piece("front").edge("side")
    assert side.sa == pytest.approx(6.0)
    assert pat.options["doll"] is True


def test_doll_pieces_are_doll_sized():
    pat = doll_pattern("dress")
    # dress length: neck point to hem on a 45 cm doll (body below the neck ≈ 33 cm)
    assert 150 < pat.finished["length"] < 300
    chest = pat.finished["chest_circ"]
    assert 300 * 1.1 < chest < 300 * 1.4
    for pc in pat.pieces:
        ring = pc.cut_ring()
        assert np.ptp(ring[:, 0]) < 400 and np.ptp(ring[:, 1]) < 400


def test_back_opening_instead_of_a_huge_neckline():
    pat = doll_pattern("tshirt_basic")
    back = pat.piece("back")
    ce = back.edge("center")
    assert not ce.fold and ce.turned and ce.sa == pytest.approx(15.0)
    assert back.cut_count == 2 and back.mirror
    assert pat.piece("front").edge("center").fold
    assert pat.has("neckband") and "bias" in pat.piece("neckband").name
    names = [c["name"] for c in pat.checks]
    assert "Head fits through the back opening" in names
    assert "Neckline fits over the head" not in names
    # the neckline was not enlarged to the doll's big head
    assert pat.finished["neckline"] < 0.8 * pat.measures["head"]
    steps = " ".join(get("tshirt_basic").sewing_steps(pat))
    assert "Velcro" in steps and "neck binding" in steps


def test_dress_skirt_back_seam_below_the_opening():
    pat = doll_pattern("dress")
    sb = pat.piece("skirt_back")
    names = [e.name for e in sb.edges]
    assert "center_open" in names and "center" in names
    assert sb.edge("center_open").sa == pytest.approx(15.0)
    assert sb.edge("center").sa == pytest.approx(6.0)
    assert any(s["name"].startswith("Skirt centre back seam") for s in pat.seams)


def test_pants_and_skirt_doll_defaults():
    pat = doll_pattern("pants_basic")
    assert pat.options["pockets"] == [] and not pat.options["cuffs"]
    assert pat.options["waistband"] == "tunnel"
    assert any("Elastic 6 mm wide" in n for n in pat.notes)
    steps = " ".join(get("pants_basic").sewing_steps(pat))
    assert "7 mm" not in steps                     # the casing text follows the doll scale
    sk = doll_pattern("skirt")
    assert "3 cm open" not in " ".join(get("skirt").sewing_steps(sk))


@pytest.mark.parametrize("height", [20, 30, 60, 90])
def test_doll_sizes(height):
    for garment in ("dress", "pants_basic", "skirt", "tshirt_basic"):
        pat = doll_pattern(garment, cm={"height": height})
        assert V.is_ok(V.validate(pat)), (garment, height)
    small = doll_pattern("skirt", cm={"height": 25})
    assert small.piece("front").edge("side").sa == pytest.approx(D.DOLL_SA_SMALL_MM)


def test_user_allowance_and_overrides_in_doll_millimetres():
    pat = doll_pattern("skirt", {"seam_allowance_mm": 8, "hem_allowance_mm": 12})
    assert pat.piece("front").edge("side").sa == pytest.approx(8.0)
    assert pat.piece("front").edge("hem").sa == pytest.approx(12.0)
    with pytest.raises(ValueError, match="seam_allowance_mm"):
        doll_pattern("skirt", {"seam_allowance_mm": 40})
    bare = doll_pattern("skirt", {"seam_allowance": "none"})
    assert all(e.sa == 0 for pc in bare.pieces for e in pc.edges)
    tee = doll_pattern("tshirt_basic", {"construction": {"chest_width": 400}})
    assert tee.finished["chest_circ"] == pytest.approx(400, rel=0.01)
    adj = doll_pattern("tshirt_basic", {"adjustments": {"chest": "+2cm"}})
    base = doll_pattern("tshirt_basic")
    assert adj.finished["chest_circ"] - base.finished["chest_circ"] == pytest.approx(20, abs=2)


def test_unsupported_garment_is_reported():
    with pytest.raises(ValueError, match="Doll mode supports"):
        D.defaults("hoodie", {})


def test_scale_text():
    assert D.scale_text("Elastic 25 mm wide, length 45 cm (+2 cm)", 0.4) == \
        "Elastic 10 mm wide, length 18 cm (+0.8 cm)"
    assert D.scale_text("Woven: 10–25 mm", 0.4) == "Woven: 4–10 mm"


def test_generate_doll_end_to_end(tmp_path):
    out = tmp_path / "doll"
    res = GEN.run(dict(garment="dress", doll=True, measures_cm=DOLL_CM, formats=["a4"], out=str(out)),
                  verbose=False)
    assert res["ok"]
    md = (out / "sewing_instructions.md").read_text(encoding="utf-8")
    assert "doll 45 cm" in md and "Velcro" in md
    data = json.loads((out / "pattern.json").read_text(encoding="utf-8"))
    assert data["options"]["doll"] is True
    assert any(f.endswith("_a4_tiled.pdf") for f in os.listdir(out))
    assert GEN.main(["--doll", "--garment", "skirt", "--measures", json.dumps(DOLL_CM), "--format", "a4",
                     "--out", str(tmp_path / "cli")]) == 0


def test_doll_profile(tmp_path, monkeypatch):
    import profiles as PR
    monkeypatch.setenv("SEWING_PROFILES", str(tmp_path))
    PR.save("rosa", DOLL_CM, kind="doll")
    spec, warn = PR.apply(dict(garment="skirt", profile="rosa"))
    assert spec["doll"] is True and warn == []
    pat, _, _ = GEN.draft_from_spec(spec)
    assert pat.options["doll"] and pat.size_label.startswith("for Rosa")


@pytest.mark.parametrize("kind,garment,opts", [("pants", "pants_basic", {}),
                                               ("top", "tshirt_basic", {"sleeve_length": "long"})])
def test_doll_photo_round_trip(kind, garment, opts, tmp_path):
    truth_pat = doll_pattern(garment, opts)
    path = str(tmp_path / f"doll_{kind}.jpg")
    (S.synth_pants_photo if kind == "pants" else S.synth_top_photo)(truth_pat, path, seed=3, px_per_mm=6.0)
    res = P.run(path, kind, str(tmp_path / "project"), doll=True)
    bad = [r for r in res["rows"] if not r["ok"]]
    assert not bad, bad
    assert V.is_ok(res["report"])
    pat = res["pattern"]
    assert pat.options["doll"] and pat.piece("front").edge("side").sa == pytest.approx(6.0, abs=0.01)
    for k in ("hip_circ", "outseam") if kind == "pants" else ("chest_circ", "length"):
        assert pat.finished[k] == pytest.approx(truth_pat.finished[k], rel=0.03)
    # project → print files
    out = tmp_path / "copy"
    r = GEN.run(dict(project=str(tmp_path / "project" / "project.json"), formats=["a4"], out=str(out)),
                verbose=False)
    assert r["ok"] and r["pattern"].size_label == "doll clothes (copied from garment)"
    assert r["pattern"].finished[k] == pytest.approx(pat.finished[k], rel=0.005)
    with pytest.raises(ValueError, match="no sizes"):
        P.regrade(str(tmp_path / "project" / "project.json"), 1)
