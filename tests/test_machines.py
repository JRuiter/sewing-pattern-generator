"""The sewist's machines: parsing, step methods, seam allowances, instructions, profiles."""
import json

import pytest

import generate as GN
import instructions as I
import machines as MC
import profiles as PR


def test_parse_aliases_and_sewing_machine_assumed():
    assert MC.parse(None) is None
    assert MC.parse("") is None
    assert MC.parse("Overlock, Coverlock") == {"sewing", "overlocker", "coverstitch"}
    assert MC.parse(["serger", "Zwillingsnadel"]) == {"sewing", "overlocker", "twin_needle"}
    assert MC.to_list("coverstitch,overlocker,stretch") == ["sewing", "stretch_stitch", "overlocker", "coverstitch"]
    with pytest.raises(ValueError, match="Unknown machine"):
        MC.parse("embroidery")


def test_unknown_machines_keep_generic_wording():
    assert MC.method({}, "seam", True) is None
    assert MC.tool_for({}, "hem", True) is None
    assert MC.seam_phrase({}, True) == MC.GENERIC_SEAM_KNIT
    assert MC.hem_phrase({}, False) == MC.GENERIC_HEM_WOVEN
    assert MC.markdown(type("P", (), {"options": {"fabric": "jersey"}})()) is None


@pytest.mark.parametrize("machines,knit,kind,tool,stitch", [
    ("overlocker", True, "seam", "overlocker", "4-thread overlock"),
    ("sewing", True, "seam", "sewing", "narrow zigzag"),
    ("stretch_stitch", True, "seam", "sewing", "stretch stitch"),
    ("straight_only", True, "seam", "sewing", "long straight stitch"),
    ("straight_only", False, "seam", "sewing", "French seam"),
    ("overlocker", False, "finish", "overlocker", "3-thread overlock"),
    ("sewing", False, "finish", "sewing", "zigzag"),
    ("coverstitch,twin_needle", True, "hem", "coverstitch", "2-needle cover stitch"),
    ("twin_needle", True, "hem", "sewing", "twin needle"),
    ("sewing", True, "hem", "sewing", "narrow zigzag"),
    ("coverstitch", False, "hem", "sewing", "straight stitch"),
    ("overlocker", True, "band", "overlocker", "4-thread overlock"),
    ("overlocker", False, "band", "sewing", "straight stitch"),
])
def test_method_per_machine(machines, knit, kind, tool, stitch):
    d = MC.method({"machines": machines}, kind, knit)
    assert d["machine"] == tool and d["stitch"] == stitch
    assert MC.tool_for({"machines": machines}, kind, knit) == tool
    assert set(d) == {"machine", "stitch", "width_mm", "length_mm", "needle", "text"}


def _draft(garment, machines=None, **kw):
    opts = dict(kw.pop("options", {}))
    if machines:
        opts["machines"] = machines
    spec = dict(garment=garment, size=kw.pop("size", 122), options=opts, **kw)
    spec, _ = PR.apply(spec)
    return GN.draft_from_spec(spec)[0]


def _seam_sa(pat, piece="front", edge="side"):
    return pat.piece(piece).edge(edge).sa


def test_overlocker_narrows_knit_seam_allowance():
    pat = _draft("pants_basic", "overlocker", options={"fabric": "sweat"})
    assert _seam_sa(pat) == pytest.approx(MC.OVERLOCK_SA_MM)
    assert pat.options["machines"] == ["sewing", "overlocker"]
    assert pat.options["_sa_from_machines"] == MC.OVERLOCK_SA_MM
    # no machines, or overlocker with a woven fabric: default 10 mm
    assert _seam_sa(_draft("pants_basic", None, options={"fabric": "sweat"})) == pytest.approx(10.0)
    assert _seam_sa(_draft("pants_basic", "overlocker", options={"fabric": "woven"})) == pytest.approx(10.0)


def test_straight_only_woven_gets_french_seam_allowance():
    pat = _draft("skirt", "straight_only")
    assert _seam_sa(pat) == pytest.approx(MC.FRENCH_SEAM_SA_MM)
    assert "French seam" in MC.markdown(pat)


def test_explicit_allowance_and_doll_win_over_machines():
    pat = _draft("pants_basic", "overlocker", options={"fabric": "sweat", "seam_allowance_mm": 12})
    assert _seam_sa(pat) == pytest.approx(12.0)
    doll = _draft("dress", "overlocker", doll=True, measures_cm={"height": 45}, size=None,
                  options={"fabric": "jersey"})
    assert doll.options["sa"] == pytest.approx(6.0)
    assert doll.options["machines"] == ["sewing", "overlocker"]


def test_steps_and_instructions_name_the_machines():
    pat = _draft("tshirt_basic", "overlocker,coverstitch", size=140)
    steps = " ".join(I.all_steps(pat))
    assert "with the overlocker" in steps and "coverstitch machine" in steps
    assert "overlocker or a narrow zigzag" not in steps
    md = MC.markdown(pat)
    assert "| Seams | Overlocker |" in md and "| Hems | Coverstitch |" in md
    assert "7.5 mm" in md
    zig = _draft("tshirt_basic", "sewing", size=140)
    steps = " ".join(I.all_steps(zig))
    assert "narrow zigzag" in steps and "wide zigzag" in steps
    assert any("twin needle" in t for t in MC.missing_tips(MC.of(zig.options), True))
    # generic text without machines (unchanged behaviour)
    plain = " ".join(I.all_steps(_draft("tshirt_basic", None, size=140)))
    assert MC.GENERIC_SEAM_KNIT.removeprefix("with ") in plain


def test_hem_phrase_in_pants_and_beanie():
    pants = _draft("pants_basic", "twin_needle", options={"fabric": "jersey", "cuffs": False})
    assert "stretch twin needle" in " ".join(I.all_steps(pants))
    plain = _draft("pants_basic", None, options={"fabric": "jersey", "cuffs": False})
    assert MC.GENERIC_HEM_KNIT.removeprefix("with ") in " ".join(I.all_steps(plain))
    beanie = _draft("beanie", "coverstitch", options={"brim": False})
    assert "coverstitch machine" in " ".join(I.all_steps(beanie))


def test_workshop_file_profile_and_explicit_precedence(tmp_path, monkeypatch):
    d = str(tmp_path)
    monkeypatch.setenv("SEWING_PROFILES", d)
    assert PR.load_machines() is None
    PR.save_machines("overlocker,coverstitch")
    assert PR.load_machines() == ["sewing", "overlocker", "coverstitch"]
    # workshop file applies without a profile
    spec, _ = PR.apply({"garment": "pants_basic", "size": 122})
    assert spec["options"]["machines"] == ["sewing", "overlocker", "coverstitch"]
    # a profile's own machines beat the workshop file
    PR.save("lena", {"height": 121}, kind="child", machines="sewing")
    with open(PR.path_for("lena")) as f:
        assert json.load(f)["machines"] == ["sewing"]
    spec, _ = PR.apply({"garment": "pants_basic", "profile": "lena"})
    assert spec["options"]["machines"] == ["sewing"]
    # explicit (CLI / spec) beats both
    spec, _ = PR.apply({"garment": "pants_basic", "profile": "lena", "machines": ["twin_needle"]})
    assert spec["options"]["machines"] == ["sewing", "twin_needle"]
    # the workshop file is not listed as a profile
    assert PR.main(["list"]) == 0


def test_profiles_cli_machines(tmp_path, capsys):
    assert PR.main(["--profiles-dir", str(tmp_path), "machines", "set", "serger,twin"]) == 0
    out = capsys.readouterr().out
    assert "Overlocker / serger" in out and "Twin needle" in out
    assert PR.main(["--profiles-dir", str(tmp_path), "machines", "show"]) == 0


def test_project_options_survive_machines(tmp_path):
    proj = "examples/3_photo_mode_b/project/project.json"
    import os
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    spec = GN.spec_from_project(os.path.join(root, proj), {"options": {"machines": ["sewing", "overlocker"]}})
    assert spec["options"]["machines"] == ["sewing", "overlocker"]
    assert spec["options"].get("style")


# ------------------------------------------------------------------ no sewing machine (#39)

def test_parse_without_sewing_machine():
    assert MC.parse("overlocker,hand") == {"overlocker", "hand", "no_sewing_machine"}
    assert MC.parse("overlocker_only") == {"overlocker", "hand", "no_sewing_machine"}
    assert MC.parse(["overlocker", "no_sewing_machine"]) == {"overlocker", "hand", "no_sewing_machine"}
    # a sewing-machine key wins over "hand"
    assert MC.parse("sewing,overlocker,hand") == {"sewing", "overlocker", "hand"}
    assert MC.parse("overlocker") == {"sewing", "overlocker"}
    assert not MC.has_sewing_machine(MC.parse("overlocker,hand"))


@pytest.mark.parametrize("kind,knit,machine,stitch", [
    ("seam", False, "overlocker", "4-thread overlock"),
    ("seam", True, "overlocker", "4-thread overlock"),
    ("finish", False, "overlocker", "already finished"),
    ("hem", False, "hand", "blind stitch"),
    ("topstitch", False, "hand", "back stitch"),
    ("band", True, "overlocker", "4-thread overlock"),
])
def test_method_without_sewing_machine(kind, knit, machine, stitch):
    d = MC.method({"machines": "overlocker,hand"}, kind, knit)
    assert (d["machine"], d["stitch"]) == (machine, stitch)


def test_overlocker_only_pants_steps():
    import steps as ST
    opts = {"style": "trousers", "fabric": "corduroy", "pockets": ["side"], "fake_fly": True,
            "back_pockets": 1, "hem_finish": "elastic_casing"}
    pat = _draft("pants_basic", "overlocker,hand", options=opts)
    assert _seam_sa(pat) == pytest.approx(7.5)            # woven seams on the overlocker too
    steps = ST.assembly(pat)
    tools = {ST.tool_for(pat.options, s.stitch, s.data.get("knit"))["machine"] for s in steps if s.stitch}
    assert "sewing" not in tools and {"overlocker", "hand"} <= tools
    text = " ".join(ST.as_texts(steps, pat.options)).lower()
    for bad in ("sewing machine", "zigzag", "straight stitch", "topstitch on the machine"):
        assert bad not in text, bad
    assert "by hand with a back stitch" in text and "blind" in text and "tacking stitch" in text
    assert "box of small hand stitches" in text
    assert not any(s.title.startswith("Finish the") for s in steps)      # the overlock seam finishes
    casing = next(s for s in steps if s.title == "Sew the hem casing")
    assert "overlocker, fold 3.5 cm to the inside once" in casing.text
    crotch = next(s for s in steps if s.title == "Sew the crotch seam")
    assert "slowly" in crotch.tip
    assert steps[3].title == "Set up the overlocker"
    md = MC.markdown(pat)
    assert "by hand" in md and "before they reach the knife" in md and "thread chain" in md
