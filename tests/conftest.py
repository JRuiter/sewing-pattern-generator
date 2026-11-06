import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(os.path.dirname(HERE), "scripts")
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)

# Tests that render full PDFs or run the photo round trip. Skip them locally with
# `pytest -m "not slow"`; CI always runs everything.
SLOW_TESTS = {
    "test_oversize_piece_on_roll_is_tiled",
    "test_roll_layout_gap_and_width",
    "test_a4_overlap_content_identical",
    "test_svg_master_is_1to1",
    "test_sheets_a0_a1",
    "test_round_trip",
    "test_generate_dxf_measure_file_and_construction",
}
SLOW_FIXTURES = {"roll_pdf", "a4_pdf"}


def pytest_collection_modifyitems(config, items):
    for item in items:
        name = getattr(item, "originalname", item.name)
        if name in SLOW_TESTS or SLOW_FIXTURES & set(getattr(item, "fixturenames", ())):
            item.add_marker(pytest.mark.slow)
