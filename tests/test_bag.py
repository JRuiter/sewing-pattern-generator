"""Tote bag review (shopper instructions): the bag is turned before the hem, the handles are
reinforced, and no garment texts (body measurements, fit, test garment) reach a bag."""
import pytest

import booklet as B
import generate as GN
import i18n
import instructions as I
import steps as ST

OVERLOCK_ONLY = ["overlocker", "hand"]


def _bag(**opts):
    spec = dict(garment="bag", options=dict(bag_size="large", fabric="woven", **opts))
    pat, sources, _ = GN.draft_from_spec(spec)
    return pat, sources


@pytest.mark.parametrize("lining", [False, True])
def test_bag_is_turned_before_the_top_edge(lining):
    pat, _ = _bag(lining=lining, pocket=lining, machines=OVERLOCK_ONLY)
    titles = [s.title for s in ST.assembly(pat)]
    assert "Turn the bag" in titles
    first_top = next(i for i, t in enumerate(titles) if "top edge" in t or "handles on" in t)
    assert titles.index("Turn the bag") < first_top


def test_unlined_bag_overlock_single_fold_and_strong_handles():
    pat, _ = _bag(lining=False, pocket=False, machines=OVERLOCK_ONLY)
    steps = {s.title: s for s in ST.assembly(pat)}
    assert "Finish the top edge" in steps                       # overlocked edge, one fold
    hem = steps["Hem the top edge"]
    assert "then" not in hem.text
    # the stitching that holds the handles is a back stitch, never a blind stitch
    assert ST.tool_for(pat.options, hem.stitch)["stitch"].startswith("back stitch")
    assert "cross" in steps["Secure the handles"].hint
    assert steps["Sew the boxed corners"].diagram == "boxed_corner"


def test_bag_hand_sewing_counts_in_the_time():
    pat, _ = _bag(lining=False, pocket=False, machines=OVERLOCK_ONLY)
    steps = ST.assembly(pat)
    assert B.hand_stitched_mm(pat, steps) > 4000                 # handles 2.4 m + top edge twice
    assert B.difficulty(pat, steps)[1] >= 3.0


def test_bag_texts_are_not_for_garments():
    pat, sources = _bag(lining=False, pocket=False, machines=OVERLOCK_ONLY)
    plans = I.fabric_consumption(pat)
    with i18n.language("de"):
        md = I.build_markdown(pat, "", plans, {}, sources)
    for word in ("Körpermaß", "Probeteil", "Passform", "Bündchen", "Tunnel"):
        assert word not in md, word
    steps = ST.assembly(pat)
    assert "garment" not in steps[0].text
    assert "pair" not in steps[1].hint                          # identical bag pieces: no "turn the paper over"
    assert "as worn" not in B._sides_note(pat)
    assert "test garment" not in B._fit_check(pat)


def test_bag_file_names_have_no_times_sign():
    pat, _ = _bag(lining=False)
    name = GN._basename(pat)
    assert "×" not in name and " " not in name
    assert name.endswith("45x42x14_cm")


def test_stacked_bag_pieces_lie_face_down_and_upright():
    """Shopper review: the back bag piece was drawn upside down on the front in 'sew side seams'."""
    import diagrams as DG
    pat, _ = _bag(lining=False, pocket=False, machines=OVERLOCK_ONLY)
    side = next(sm for sm in pat.seams if sm["name"] == "Side seams")
    _A, _ea, _B, _eb, (R, _t, flip) = DG.overlay_parts(pat, side)
    assert flip                          # face down = mirror image
    assert R[1, 1] > 0.99                # not turned round: bottom to bottom


def test_press_handles_shows_the_folded_edges():
    pat, _ = _bag(lining=False, pocket=False)
    press = next(s for s in ST.assembly(pat) if s.title == "Press the handles")
    assert press.amount > 0 and press.data.get("band") == 1.0


@pytest.mark.parametrize("opts, names", [({"lining": False, "pocket": False}, {"front", "angle"}),
                                         ({}, {"front", "angle"}), ({"style": "drawstring"}, {"front"})])
def test_finished_bag_is_drawn_not_its_pieces(opts, names):
    """Title page and "Done!": the finished bag (front view and a view at an angle with the gusset),
    not the flat pattern pieces side by side."""
    import views as V
    pat, _ = _bag(**opts)
    views = V.garment_views(pat)
    assert set(views) == names
    if "angle" in views:
        keys = [pc.key for _r, pc, _z in views["angle"]["layers"]]
        assert keys.count("handle") == 2 and views["angle"]["inside"]
