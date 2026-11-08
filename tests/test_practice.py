"""Defaults follow common practice (practice.py); special values only via options."""
import numpy as np
import pytest

import measurements as M
import validate as V
from garments import get
from garments import tshirt_basic as T


def _m(size):
    r = M.complete_measures({}, size)
    return r[0] if isinstance(r, tuple) else r


def _practice(pat):
    return [c for c in V.validate(pat) if c.group == "Common practice"]


CASES = [
    ("tshirt_basic", "110", {}),
    ("tshirt_basic", "m52", {}),
    ("tshirt_basic", "w40", {"sleeve_style": "raglan", "sleeve_length": "long"}),
    ("tshirt_basic", "128", {"fit": "oversized", "fabric": "sweat", "sleeve_length": "long",
                             "sleeve_cuffs": True, "hem_band": True}),
    ("tshirt_basic", "128", {"fit": "boxy", "fabric": "sweat", "sleeve_length": "long",
                             "sleeve_cuffs": True, "hem_band": True}),
    ("hoodie", "140", {"fabric": "sweat"}),
    ("dress", "116", {}),
    ("pants_basic", "104", {"style": "jogger"}),
    ("pants_basic", "w38", {"style": "trousers"}),
    ("pants_basic", "86", {"style": "harem"}),
    ("pants_basic", "98", {"style": "leggings"}),
]


@pytest.mark.parametrize("garment,size,opts", CASES)
def test_defaults_meet_common_practice(garment, size, opts):
    checks = _practice(get(garment).draft(_m(size), opts))
    assert checks, "no common-practice checks"
    assert all(c.status == "OK" for c in checks), [(c.name, c.actual, c.target) for c in checks]


def _cap_height(pat):
    s = pat.piece("sleeve")
    cap = np.vstack([s.edge("cap_front").pts, s.edge("cap_back").pts])
    return float(np.ptp(cap[:, 1]))


def test_dropped_shoulder_lowers_the_cap_and_widens_the_sleeve():
    m = _m("128")
    base = dict(fabric="sweat", sleeve_length="long")
    normal = T.draft(m, dict(base, fit="normal"))
    over = T.draft(m, dict(base, fit="oversized"))
    boxy = T.draft(m, dict(base, fit="boxy"))
    assert _cap_height(boxy) < _cap_height(over) < _cap_height(normal) * 1.25
    assert boxy.options["_sinfo"]["SW"] > over.options["_sinfo"]["SW"] > normal.options["_sinfo"]["SW"]


def test_boxy_is_straight_with_a_loose_hem_band():
    pat = T.draft(_m("128"), dict(fit="boxy", fabric="sweat", sleeve_length="long", hem_band=True))
    hem = pat.piece("front").edge("hem").length + pat.piece("back").edge("hem").length
    band = pat.piece("hem_band")
    band_len = 2 * max(np.ptp(np.vstack([e.pts for e in band.edges])[:, 0]), 0)
    assert 0.92 <= band_len / (2 * hem) <= 1.0


def test_crew_neck_is_about_as_deep_as_half_wide():
    for size in ("128", "m52", "w38"):
        pat = T.draft(_m(size), {})
        c = {v["name"]: v["value"] for v in pat.construction}
        assert 0.8 <= c["front_neck_depth"] / c["neck_width_half"] <= 1.1


def test_special_values_skip_the_practice_check():
    pat = T.draft(_m("m52"), {"neckline": "v"})
    names = [c.name for c in _practice(pat)]
    assert "Crew neck depth (front)" not in names
    pat = T.draft(_m("m52"), {"construction": {"chest_width": 1500}})
    assert not any(n.startswith("Chest ease") for n in [c.name for c in _practice(pat)])
