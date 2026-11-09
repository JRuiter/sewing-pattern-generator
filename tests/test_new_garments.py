"""The garments added for the open issues: sewable in several sizes, steps that point at real pieces,
edges and seams, and the style-line modifier."""
import pytest

import allowance as A
import geometry as G
import measurements as M
import steps as ST
import validate as V
from garments import get

KIDS_ADULT = [122, 152, "w38", "m52"]
BABY = [62, 74, 86]
CASES = [
    ("shirt", {}, KIDS_ADULT),
    ("shirt", {"style": "blouse", "sleeve_length": "short"}, ["w38", 128]),
    ("shirt", {"collar": "peter_pan"}, [104, 128]),
    ("shirt", {"collar": "none"}, ["w38"]),
    ("polo", {}, KIDS_ADULT),
    ("cardigan", {}, KIDS_ADULT),
    ("vest", {}, KIDS_ADULT),
    ("vest", {"closure": "snaps"}, [122]),
    ("jacket", {}, ["w38", "m52", 140]),
    ("jacket", {"pockets": "jetted"}, ["m52"]),
    ("coat", {}, ["w38", "m52"]),
    ("softshell", {}, [122, "m52"]),
    ("fitted_dress", {}, ["w38", "w44"]),
    ("fitted_dress", {"sleeve_length": "none"}, ["w38"]),
    ("wrap", {}, ["w38", 152]),
    ("wrap", {"style": "dress"}, ["w38"]),
    ("pinafore", {}, [104, 128, "w38"]),
    ("jeans", {}, KIDS_ADULT),
    ("dungarees", {}, [98, 122, "w38"]),
    ("bodysuit", {}, [74, 98, "w38"]),
    ("bodysuit", {"style": "swimsuit"}, ["w38", 140]),
    ("bodysuit", {"style": "wrap"}, [62, 74]),
    ("underwear", {}, [122, "w38", "m52"]),
    ("underwear", {"style": "boxers"}, [128, "m52"]),
    ("swim_trunks", {}, [128, "m52"]),
    ("swim_trunks", {"liner": False, "length": "knee"}, ["m52"]),
    ("jumpsuit", {}, ["w38", 128]),
    ("jumpsuit", {"style": "boiler"}, ["m52"]),
    ("jumpsuit", {"length": "short"}, [116]),
    ("pyjama", {}, [104, "w38"]),
    ("pyjama", {"top": "shirt"}, ["m52"]),
    ("pyjama", {"length": "short"}, [140]),
    ("romper", {}, BABY),
    ("romper", {"feet": True}, [68, 86]),
    ("sleeping_bag", {}, BABY + [104]),
    ("sleeping_bag", {"style": "swaddle", "tog": 2.5}, ["b56", 62]),
    ("tshirt_basic", {"style_lines": "princess"}, ["w38", 128]),
    ("hoodie", {"style_lines": "yoke"}, [128, "m52"]),
    ("dress", {"style_lines": "color_block"}, [116, "w38"]),
]
PARAMS = [(g, o, s) for g, o, sizes in CASES for s in sizes]


def _draft(garment, size, opts):
    mm, _ = M.complete_measures({}, str(size))
    return A.draft(get(garment), mm, dict(opts))


@pytest.mark.parametrize("garment,opts,size", PARAMS,
                         ids=[f"{g}-{'-'.join(map(str, o.values())) or 'standard'}-{s}" for g, o, s in PARAMS])
def test_new_garment_is_sewable(garment, opts, size):
    pat = _draft(garment, size, opts)
    bad = [(c.name, c.actual) for c in V.validate(pat) if c.status == "ERROR"]
    assert not bad, bad
    keys = [pc.key for pc in pat.pieces]
    assert len(keys) == len(set(keys)), "piece keys must be unique"
    for pc in pat.pieces:
        assert pc.grain is not None, pc.name
        assert G.ring_is_valid(pc.cut_ring()), pc.name
    # every step points at pieces, edges and seams that exist
    names = [s["name"] for s in pat.seams]
    for st in ST.assembly(pat):
        for k, e in st.edges:
            assert any(x.name == e for x in pat.piece(k).edges), (st.title, k, e)
        for k in st.pieces:
            assert pat.has(k), (st.title, k)
        for p in st.seams:
            assert any(n.startswith(p) for n in names), (st.title, p)


def test_style_lines_keep_the_garment_measures():
    plain = _draft("tshirt_basic", "w38", {})
    for kind in ("princess", "yoke", "color_block"):
        pat = _draft("tshirt_basic", "w38", {"style_lines": kind})
        area = sum(G.signed_area(p.seam_ring()) for p in pat.pieces if p.key.startswith(("front", "back")))
        ref = sum(G.signed_area(p.seam_ring()) for p in plain.pieces if p.key in ("front", "back"))
        assert abs(area - ref) / ref < 0.005, kind
        assert pat.has("front_side" if kind == "princess" else "front_lower")


def test_style_lines_rejected_where_not_supported():
    with pytest.raises(ValueError):
        _draft("jeans", "w38", {"style_lines": "princess"})


def test_sleeping_bag_tog_layers():
    warm = _draft("sleeping_bag", 74, {"tog": 2.5})
    summer = _draft("sleeping_bag", 74, {"tog": 0.5})
    assert warm.has("front_wadding") and not summer.has("front_wadding")
    assert any("2.5 TOG" in n for n in warm.notes)


def test_romper_snaps_along_the_inner_legs():
    pat = _draft("romper", 74, {})
    assert pat.options["_snaps"] >= 8
    assert not any(s["name"].startswith("Legs: Inseam") for s in pat.seams)
