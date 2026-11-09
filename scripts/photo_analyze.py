"""Photo mode A (inspiration photo): feature list with confidence → module + options.

The actual image description is done by Claude while looking at the photo; it fills the
feature JSON (schema below). This script
  1. checks and normalises the feature list,
  2. phrases the confirmation question ("I can see: … is that right?"),
  3. maps the features onto an existing module + options and openly reports what no
     module covers (with the closest alternative),
  4. can estimate the silhouette automatically from proportions for cut-out images
     (product photo / flat lay on a plain background); ratios only, never measurements!

Body measurements always come from the user (size or measurements), never from an
inspiration photo.

CLI:
  python photo_analyze.py features.json        → mapping + confirmation text
  python photo_analyze.py --image photo.jpg    → automatic proportions (pants)
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

SCHEMA = {
    "garment_type": ["pants", "jogger", "harem", "leggings", "shorts", "tshirt", "longsleeve",
                     "hoodie", "sweatshirt", "sweater", "skirt", "beanie", "loop", "dress", "jacket",
                     "blouse", "shirt", "jeans", "overalls", "body", "coat", "cardigan", "vest", "polo",
                     "softshell", "jumpsuit", "pyjama", "swimsuit", "swim_trunks", "underwear", "romper",
                     "sleeping_bag", "wrap", "pinafore"],
    "silhouette": ["slim", "straight", "wide", "oversized", "harem", "flared", "bootcut", "tapered",
                   "a-line", "circle_skirt"],
    "length": ["long", "7/8", "knee", "short", "mini", "midi", "maxi", "hip_length", "tunic"],
    "pockets": ["none", "side", "slant", "back_patch", "front_patch", "kangaroo",
                "cargo", "welt", "jetted"],
    "waistband": ["elastic", "casing", "rib", "drawstring", "yoga", "button_zip"],
    "leg_finish": ["rib", "hem", "drawstring", "turn_up"],
    "neckline": ["round", "v", "u-boot", "stand_collar", "collar", "hood"],
    "sleeve": ["set_in", "raglan", "dropped", "none"],
    "sleeve_length": ["short", "long", "3/4", "none"],
    "sleeve_finish": ["rib", "hem"],
    "hem": ["rib", "hemmed"],
    "closure": ["none", "button_placket", "zipper", "snaps"],
    "hood": ["yes", "no"],
    "waist_seam": ["yes", "no"],
    "fabric": ["jersey", "jersey_elastane", "sweat", "fleece", "interlock", "woven", "knit"],
    "style_lines": ["none", "yoke", "vertical_seams", "horizontal_seams"],
}

LABELS = {
    "garment_type": "Garment type", "silhouette": "Silhouette", "length": "Length", "pockets": "Pockets",
    "waistband": "Waistband", "leg_finish": "Leg finish", "neckline": "Neckline", "sleeve": "Sleeve type",
    "sleeve_length": "Sleeve length", "sleeve_finish": "Sleeve finish", "hem": "Hem",
    "closure": "Closure", "hood": "Hood", "waist_seam": "Waist seam", "fabric": "Likely fabric",
    "style_lines": "Style lines",
}

VALUE_LABELS = {"side": "side pockets", "slant": "slanted side pockets",
                "back_patch": "back patch pockets", "kangaroo": "kangaroo pocket",
                "casing": "fabric waistband with elastic", "elastic": "elastic", "rib": "rib knit",
                "drawstring": "drawstring", "harem": "harem (dropped crotch, tapered)",
                "jersey_elastane": "jersey with elastane", "sweat": "sweat", "button_zip":
                "button + zip", "dropped": "dropped shoulder"}

UNSUPPORTED = {
    "front_patch": "Front patch pockets are not an option. Alternative: side pockets.",
    "u-boot": "Boat necks are not an option. Alternative: wide round neck.",
    "dropped": "Dropped shoulders are not an option. Alternative: raglan or oversized fit.",
}
# features that only some modules cover: (modules that cover it, text for the others)
PARTIAL = {
    "welt": (("jacket", "coat"), "Welt pockets only exist on the lined jacket and coat. Alternative: side pockets."),
    "jetted": (("jacket", "coat"), "Jetted pockets only exist on the lined jacket and coat. Alternative: side "
                                   "pockets."),
    "button_zip": (("jeans",), "A waistband with button and zip only exists on the jeans. Alternative: elastic "
                               "waistband (pull-on pants)."),
    "button_placket": (("shirt", "polo", "cardigan", "jacket", "coat", "jumpsuit", "pyjama"),
                       "Button plackets are not covered for this garment. Alternative: no closure."),
    "zipper": (("hoodie", "vest", "softshell", "jumpsuit", "fitted_dress", "jeans", "sleeping_bag"),
               "Zips are not covered for this garment. Alternative: no closure."),
    "snaps": (("vest", "bodysuit", "romper"), "Snap plackets are not covered for this garment. Alternative: no "
                                             "closure."),
    "stand_collar": (("shirt", "jacket", "coat", "vest", "jumpsuit"),
                     "Stand collars are not covered for this garment. Alternative: round neck with a wide "
                     "neckband."),
    "collar": (("shirt", "polo", "jumpsuit", "pyjama"), "Shirt collars are not covered for this garment. "
                                                       "Alternative: round neck."),
    "yoke": (("tshirt_basic", "hoodie", "dress", "shirt", "jeans"),
             "Style lines (yoke) are not covered for this garment. The pattern is drafted without the split."),
    "vertical_seams": (("tshirt_basic", "hoodie", "dress"), "Vertical style lines are not covered for this "
                                                          "garment. The pattern is drafted without the split."),
    "horizontal_seams": (("tshirt_basic", "hoodie", "dress"), "Horizontal style lines are not covered for this "
                                                            "garment. The pattern is drafted without the split."),
}
# garment types with their own module (options from the features below)
DIRECT = {"jeans": "jeans", "overalls": "dungarees", "body": "bodysuit", "swimsuit": "bodysuit",
          "blouse": "shirt", "shirt": "shirt", "jacket": "jacket", "coat": "coat", "cardigan": "cardigan",
          "vest": "vest", "polo": "polo", "softshell": "softshell", "jumpsuit": "jumpsuit", "pyjama": "pyjama",
          "swim_trunks": "swim_trunks", "underwear": "underwear", "romper": "romper",
          "sleeping_bag": "sleeping_bag", "wrap": "wrap", "pinafore": "pinafore"}


def normalize(features: dict) -> dict:
    """Check the feature list. Format per feature: {"value": ..., "confidence": 0..1} or just the value."""
    out = {}
    for k, v in features.items():
        if k in ("proportions", "notes"):
            out[k] = v
            continue
        if k not in SCHEMA:
            raise ValueError(f"Unknown feature '{k}'. Allowed: {', '.join(SCHEMA)}")
        if not isinstance(v, dict):
            v = {"value": v, "confidence": 0.7}
        vals = v["value"] if isinstance(v["value"], list) else [v["value"]]
        for x in vals:
            if x not in SCHEMA[k]:
                raise ValueError(f"Value '{x}' is not allowed for '{k}'. Allowed: {', '.join(SCHEMA[k])}")
        out[k] = {"value": v["value"], "confidence": float(v.get("confidence", 0.7))}
    if "garment_type" not in out:
        raise ValueError("Feature 'garment_type' is missing.")
    return out


def _val(f, k, default=None):
    return f[k]["value"] if k in f else default


def _conf_word(c):
    return "certain" if c >= 0.8 else ("likely" if c >= 0.55 else "uncertain")


def confirmation_text(features: dict) -> str:
    f = normalize(features)
    parts = []
    for k, v in f.items():
        if k in ("proportions", "notes"):
            continue
        vals = v["value"] if isinstance(v["value"], list) else [v["value"]]
        txt = ", ".join(VALUE_LABELS.get(x, x) for x in vals)
        parts.append(f"- {LABELS[k]}: **{txt}** ({_conf_word(v['confidence'])}, {v['confidence'] * 100:.0f} %)")
    unsure = [LABELS[k] for k, v in f.items() if k in LABELS and v["confidence"] < 0.55]
    text = "I can see in the photo:\n" + "\n".join(parts)
    if unsure:
        text += f"\n\nI am unsure about: {', '.join(unsure)}. Please confirm or correct."
    text += ("\n\nIs that right? I don't take body measurements from the photo, so please give a size or "
             "measurements. I will ask about the back and hidden details instead of inventing them.")
    return text


ZIP_KINDS = ("hoodie", "sweatshirt", "sweater")


def _direct_options(kind, f, fit, sil) -> dict:
    """Options for the garment types with their own module."""
    o = {}
    sl = _val(f, "sleeve_length")
    lg = _val(f, "length")
    pk = _val(f, "pockets", [])
    pk = pk if isinstance(pk, list) else [pk]
    if kind == "blouse":
        o["style"] = "blouse"
    if kind == "swimsuit":
        o["style"] = "swimsuit"
    if kind in ("shirt", "blouse", "jacket", "coat", "cardigan", "polo", "jumpsuit", "wrap") and fit != "harem":
        o["fit"] = fit
    if sl in ("short", "long") and kind in ("shirt", "blouse", "polo", "cardigan", "jumpsuit", "wrap", "body",
                                            "romper"):
        o["sleeve_length"] = sl
    if kind in ("shirt", "blouse"):
        nk = _val(f, "neckline")
        if nk == "stand_collar":
            o["collar"] = "stand"
        elif nk in ("round", "v"):
            o["collar"] = "none"
    if kind == "jeans" and sil in ("flared", "bootcut", "tapered"):
        o["leg_shape"] = {"flared": "flare"}.get(sil, sil)
    if kind in ("jacket", "coat"):
        for x in ("welt", "jetted"):
            if x in pk:
                o["pockets"] = x
    if kind == "jumpsuit":
        if lg == "short":
            o["length"] = "short"
        if _val(f, "closure") == "zipper":
            o["closure"] = "zip"
    if kind == "pyjama":
        if lg == "short":
            o["length"] = "short"
        if _val(f, "closure") == "button_placket":
            o["top"] = "shirt"
    if kind == "vest":
        c = _val(f, "closure")
        if c in ("zipper", "snaps", "none"):
            o["closure"] = {"zipper": "zip"}.get(c, c)
    if kind == "wrap" and lg in ("knee", "midi", "maxi"):
        o["style"] = "dress"
    if kind == "swim_trunks" and lg == "knee":
        o["length"] = "knee"
    return o


def map_to_module(features: dict) -> dict:
    """Features → (module, options, not covered + alternatives)."""
    f = normalize(features)
    kind = _val(f, "garment_type")
    issues, partial = [], []
    for k, v in f.items():
        if k in ("proportions", "notes"):
            continue
        for x in (v["value"] if isinstance(v["value"], list) else [v["value"]]):
            if x == "zipper" and kind in ZIP_KINDS:
                continue                      # zip-up hoodie / sweat jacket is covered
            if x in UNSUPPORTED:
                issues.append(UNSUPPORTED[x])
            elif x in PARTIAL:
                partial.append(x)
    sil = _val(f, "silhouette", "straight")
    fit = {"slim": "slim", "straight": "normal", "wide": "wide", "oversized": "oversized",
           "harem": "harem", "flared": "normal", "bootcut": "normal", "tapered": "normal"}.get(sil, "normal")
    fabric = _val(f, "fabric")
    opts = {}
    if kind in DIRECT:
        module = DIRECT[kind]
        opts.update(_direct_options(kind, f, fit, sil))
    elif kind in ("pants", "jogger", "harem", "leggings", "shorts"):
        module = "pants_basic"
        style = {"harem": "harem", "leggings": "leggings"}.get(kind, "jogger")
        if fit == "harem":
            style = "harem"
        if fit == "slim" and kind != "jogger":
            style = "leggings"
        opts["style"] = style
        opts["fit"] = fit
        t = _val(f, "pockets", [])
        t = t if isinstance(t, list) else [t]
        pk = []
        if any(x in ("side", "slant", "welt", "jetted", "front_patch") for x in t):
            pk.append("side")
        if "back_patch" in t:
            pk.append("back_patch")
        if "cargo" in t:
            pk.append("cargo")
        opts["pockets"] = pk
        b = _val(f, "waistband")
        if b:
            opts["waistband"] = {"elastic": "casing", "casing": "casing", "rib": "rib",
                                 "drawstring": "tunnel", "yoga": "yoga",
                                 "button_zip": "casing"}[b]
        ba = _val(f, "leg_finish")
        if ba:
            opts["cuffs"] = ba == "rib"
            if ba == "turn_up":
                opts["turn_up"] = 3.0
        if sil in ("flared", "bootcut", "tapered"):
            opts["leg_shape"] = {"flared": "flare"}.get(sil, sil)
            opts["cuffs"] = False
        lg = _val(f, "length")
        if kind == "shorts":
            lg = lg or "short"
        if lg in ("long", "7/8", "knee", "short"):
            opts["length"] = lg
    elif kind == "dress":
        module = "dress"
        has_waist = _val(f, "waist_seam", "yes") == "yes"
        sil_d = sil
        if sil_d in ("a-line", "flared") and not has_waist:
            opts["style"] = "shirt_dress"
        else:
            opts["style"] = "waist_seam"
            opts["skirt"] = {"a-line": "a_line", "circle_skirt": "circle"}.get(sil_d, "gathered")
        opts["fit"] = fit if fit != "harem" else "normal"
        opts["sleeve_style"] = "raglan" if _val(f, "sleeve") == "raglan" else "set_in"
        al = _val(f, "sleeve_length", "short")
        opts["sleeve_length"] = {"short": "short", "long": "long", "3/4": "3/4", "none": "short"}[al]
        opts["neckline"] = "v" if _val(f, "neckline") == "v" else "round"
        lg = _val(f, "length", "knee")
        opts["length"] = {"mini": "mini", "knee": "knee", "midi": "midi", "maxi": "maxi", "short": "mini",
                          "long": "maxi"}.get(lg, "knee")
        t = _val(f, "pockets", [])
        opts["pockets"] = "side" in (t if isinstance(t, list) else [t])
    elif kind in ("tshirt", "longsleeve"):
        module = "tshirt_basic"
        opts["fit"] = fit
        opts["sleeve_style"] = "raglan" if _val(f, "sleeve") == "raglan" else "set_in"
        al = _val(f, "sleeve_length", "long" if kind == "longsleeve" else "short")
        opts["sleeve_length"] = {"short": "short", "long": "long", "3/4": "3/4", "none": "short"}[al]
        opts["neckline"] = "v" if _val(f, "neckline") == "v" else "round"
        if _val(f, "length") == "tunic":
            opts["length"] = "tunic"
        if _val(f, "sleeve_finish") == "rib":
            opts["sleeve_cuffs"] = True
        if _val(f, "hem") == "rib":
            opts["hem_band"] = True
    elif kind in ("hoodie", "sweatshirt", "sweater"):
        module = "hoodie"
        opts["fit"] = fit if fit != "harem" else "wide"
        opts["hood"] = _val(f, "hood", "yes" if kind == "hoodie" else "no") == "yes" or \
            _val(f, "neckline") == "hood"
        t = _val(f, "pockets", [])
        t = t if isinstance(t, list) else [t]
        opts["kangaroo"] = "kangaroo" in t
        opts["sleeve_style"] = "raglan" if _val(f, "sleeve") == "raglan" else "set_in"
        if _val(f, "closure") == "zipper":
            opts["front"] = "zip"
    elif kind == "skirt":
        module = "skirt"
        opts["style"] = {"a-line": "a_line", "circle_skirt": "circle", "wide": "gathered",
                         "straight": "gathered", "slim": "straight"}.get(sil, "gathered")
        lg = _val(f, "length", "knee")
        opts["length"] = {"mini": "mini", "knee": "knee", "midi": "midi", "maxi": "maxi", "short": "mini",
                          "long": "maxi"}.get(lg, "knee")
    elif kind == "beanie":
        module = "beanie"
    elif kind == "loop":
        module = "loop"
    else:
        module = "pants_basic"
        issues.append(f"There is no module for \"{kind}\".")
    for x in partial:
        if module not in PARTIAL[x][0] and PARTIAL[x][1] not in issues:
            issues.append(PARTIAL[x][1])
    st = _val(f, "style_lines")
    if module in ("tshirt_basic", "hoodie", "dress") and st in ("yoke", "vertical_seams", "horizontal_seams"):
        opts["style_lines"] = {"yoke": "yoke", "vertical_seams": "princess", "horizontal_seams": "color_block"}[st]
    if fabric:
        opts["fabric"] = fabric if fabric != "knit" else "jersey"
    prop = f.get("proportions", {})
    if module == "pants_basic" and prop:
        # proportions drive option parameters (never body measurements!)
        if "hem_to_hip" in prop and not opts.get("cuffs"):
            opts["_hem_ratio"] = float(prop["hem_to_hip"])
        if prop.get("crotch") == "deep":
            opts["fit"] = "harem"
            opts["style"] = "harem"
    low = [LABELS[k] for k, v in f.items() if k in LABELS and v["confidence"] < 0.55]
    return dict(module=module, options=opts, not_covered=issues, uncertain=low)


# ---------------------------------------------------------------------------
# Automatic proportions from cut-out images (pants)
# ---------------------------------------------------------------------------

def _simple_mask(img):
    import cv2
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32)
    lab = cv2.GaussianBlur(lab, (0, 0), 3)
    h, w = lab.shape[:2]
    b = np.concatenate([lab[:10].reshape(-1, 3), lab[-10:].reshape(-1, 3), lab[:, :10].reshape(-1, 3),
                        lab[:, -10:].reshape(-1, 3)])
    d = np.linalg.norm(lab - np.median(b, axis=0), axis=2)
    d8 = np.clip(d / d.max() * 255, 0, 255).astype(np.uint8)
    _, m = cv2.threshold(d8, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((7, 7), np.uint8))
    n, lab_, st, _ = cv2.connectedComponentsWithStats(m)
    k = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
    return (lab_ == k).astype(np.uint8) * 255


def pants_proportions(image) -> dict:
    """Ratios of flat-lying / cut-out pants (scale-free)."""
    import cv2

    import photo_measure as PM
    img = cv2.imread(image) if isinstance(image, str) else image
    mask = _simple_mask(img)
    mask, img2, _ = PM.upright(mask, img, 1.0)
    res, geo, _ = PM.measure_pants(mask, img2, 1.0)
    hip = res["hip_flat"]
    r = dict(rise_to_length=res["front_rise"] / res["outseam"],
             hem_to_hip=res["opening_flat"] / hip,
             midleg_to_hip=res["knee_flat"] / hip,
             hem_to_midleg=res["opening_flat"] / max(res["knee_flat"], 1),
             rib=res["cuff_h"] > 0.04 * res["outseam"])
    return r


def classify_pants(r: dict) -> dict:
    harem_score = (r["rise_to_length"] - 0.30) / 0.03 + (0.52 - r["hem_to_midleg"]) / 0.04
    if harem_score > 1.0:
        sil, conf = "harem", min(0.95, 0.6 + harem_score * 0.1)
    elif r["midleg_to_hip"] < 0.43 and r["hem_to_midleg"] > 0.62:
        sil, conf = "slim", 0.75
    elif r["hem_to_hip"] > 0.40:
        sil, conf = "wide", 0.65
    else:
        sil, conf = "straight", 0.6
    feats = {"garment_type": {"value": "pants", "confidence": 0.9},
             "silhouette": {"value": sil, "confidence": round(conf, 2)},
             "leg_finish": {"value": "rib" if r["rib"] else "hem", "confidence": 0.7},
             "proportions": {k: round(float(v), 3) for k, v in r.items() if k != "rib"}}
    if sil == "harem":
        feats["proportions"]["crotch"] = "deep"
    return feats


def main(argv=None):
    ap = argparse.ArgumentParser(description="Photo mode A: map garment features to a module")
    ap.add_argument("features", nargs="?", help="feature JSON file")
    ap.add_argument("--image", help="cut-out photo of pants (automatic proportions)")
    a = ap.parse_args(argv)
    if a.image:
        feats = classify_pants(pants_proportions(a.image))
    else:
        if not a.features:
            ap.error("give a feature JSON file or --image")
        with open(a.features, encoding="utf-8") as f:
            feats = json.load(f)
    print(confirmation_text(feats))
    print()
    print(json.dumps(map_to_module(feats), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
