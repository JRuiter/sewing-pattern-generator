"""Nested multi-size patterns (issue #2).

`--size 98,110,122` drafts every size on its own (each one is validated like a single-size
pattern) and overlays the pieces at the drafting origin, which every module puts at a
construction point shared by all sizes (centre front / waist, centre back / hem, the corner
of a band). Each size gets its own colour and cutting-line dash and its own PDF layer
(optional content group), so a viewer such as Acrobat can switch sizes on and off before
printing. The layout reserves the envelope of all sizes.
"""
from __future__ import annotations

import copy

import numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union

# print-friendly, distinguishable colours (also in greyscale via the dash patterns)
COLORS = [(0.80, 0.10, 0.10), (0.10, 0.33, 0.78), (0.10, 0.52, 0.20), (0.58, 0.20, 0.64),
          (0.88, 0.48, 0.00), (0.00, 0.52, 0.58), (0.50, 0.33, 0.14), (0.25, 0.25, 0.25)]
DASHES = [None, (8, 2), (3, 2), (8, 2, 2, 2), (12, 3), (2, 2), (8, 2, 2, 2, 2, 2), (5, 5)]
MAX_SIZES = len(COLORS)


def parse_sizes(size) -> list:
    """'98,110,122' / '98-122' (kids' steps of 6) / ['w36', 'w38'] → list of sizes; one size → [size]."""
    if size is None:
        return [None]
    if isinstance(size, (list, tuple)):
        return list(size)
    s = str(size).strip()
    if "," in s:
        return [x.strip() for x in s.split(",") if x.strip()]
    if "-" in s and s.replace("-", "").isdigit():
        lo, hi = (int(x) for x in s.split("-"))
        return [str(v) for v in range(lo, hi + 1, 6)]
    return [size]


def _envelope(rings) -> np.ndarray:
    polys = [Polygon(r).buffer(0) for r in rings]
    u = unary_union(polys)
    if u.geom_type != "Polygon":
        u = u.convex_hull
    ring = np.asarray(u.exterior.coords, float)[:-1]
    if Polygon(ring).exterior.is_ccw is False:
        ring = ring[::-1]
    return ring


def _area(p) -> float:
    return sum(Polygon(pc.cut_ring()).area for pc in p.pieces)


def build(patterns, labels):
    """Overlay the drafted sizes. Returns a Pattern whose pieces are the envelopes of all sizes
    (for the layout) and whose attribute `nest` holds the sizes for the renderer."""
    if len(patterns) < 2:
        raise ValueError("a nested pattern needs at least two sizes")
    if len(patterns) > MAX_SIZES:
        raise ValueError(f"at most {MAX_SIZES} sizes in one nested pattern")
    keys = [pc.key for pc in patterns[0].pieces]
    for p in patterns[1:]:
        if [pc.key for pc in p.pieces] != keys:
            raise ValueError("the sizes have different pieces; use the same options for all sizes")
    order = sorted(range(len(patterns)), key=lambda i: _area(patterns[i]))
    small, big = patterns[order[0]], patterns[order[-1]]
    nested = copy.copy(big)
    nested.pieces = []
    for i, pc in enumerate(big.pieces):
        env = copy.copy(pc)
        ring = _envelope([p.pieces[i].cut_ring() for p in patterns])
        env.cut_ring = (lambda r=ring: r.copy())
        nested.pieces.append(env)
    nested.size_label = "sizes " + " · ".join(labels)
    nested.nest = [dict(label=lab, pattern=p, color=COLORS[k], dash=DASHES[k], layer=k)
                   for k, (lab, p) in enumerate(zip(labels, patterns))]
    nested.nest_label_pattern = small           # label block and grainline: inside the smallest size
    nested.nest_big = big
    return nested


def is_nested(pattern) -> bool:
    return bool(getattr(pattern, "nest", None))


def layer_names(pattern) -> list[str]:
    return [f"Size {n['label']}" for n in pattern.nest] if is_nested(pattern) else []


def add_pdf_layers(path: str, pattern) -> None:
    """Register one optional content group per size in a PDF whose content stream already
    wraps each size's drawing in `/OC /ocN BDC … EMC` (see render.PdfPage)."""
    if not is_nested(pattern):
        return
    from pypdf import PdfReader, PdfWriter
    from pypdf.generic import ArrayObject, DictionaryObject, NameObject, TextStringObject

    writer = PdfWriter(clone_from=PdfReader(path))
    ocgs = []
    for name in layer_names(pattern):
        ocg = DictionaryObject({NameObject("/Type"): NameObject("/OCG"),
                                NameObject("/Name"): TextStringObject(name)})
        ocgs.append(writer._add_object(ocg))
    props = DictionaryObject({NameObject(f"/oc{k}"): ref for k, ref in enumerate(ocgs)})
    for page in writer.pages:
        res = page.get("/Resources")
        res = res.get_object() if res is not None else DictionaryObject()
        res[NameObject("/Properties")] = props
        page[NameObject("/Resources")] = res
    writer._root_object[NameObject("/OCProperties")] = DictionaryObject({
        NameObject("/OCGs"): ArrayObject(ocgs),
        NameObject("/D"): DictionaryObject({
            NameObject("/Name"): TextStringObject("Sizes"),
            NameObject("/Order"): ArrayObject(ocgs),
            NameObject("/ON"): ArrayObject(ocgs),
            NameObject("/OFF"): ArrayObject([]),
        }),
    })
    writer._root_object[NameObject("/PageMode")] = NameObject("/UseOC")
    with open(path, "wb") as f:
        writer.write(f)


def size_tag_points(ring: np.ndarray, centre: np.ndarray, direction) -> np.ndarray:
    """Point on the ring farthest along `direction`, pulled 5 mm towards the centre."""
    d = np.asarray(direction, float)
    d = d / np.linalg.norm(d)
    p = ring[int(np.argmax(ring @ d))]
    v = centre - p
    n = np.linalg.norm(v)
    return p + (v / n * 5.0 if n > 1e-6 else 0.0)
