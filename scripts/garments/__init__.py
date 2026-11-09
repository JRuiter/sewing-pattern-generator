"""Garment modules. Each module offers draft(measures_mm, options) -> Pattern,
DEFAULTS (default options) and finished_measures(pattern) for verification."""
from importlib import import_module

GARMENTS = {
    "pants_basic": "Pants (joggers, harem pants, leggings, pull-on trousers)",
    "jeans": "Jeans (zip fly, scoop pockets, back yoke, patch and coin pockets, waistband with button)",
    "dungarees": "Dungarees (pants with bib, crossed straps with buttons, bib pocket)",
    "tshirt_basic": "T-shirt / long sleeve (set-in or raglan sleeve)",
    "hoodie": "Hoodie / sweatshirt",
    "skirt": "Skirt (elastic waist: gathered, A-line, circle)",
    "dress": "Dress (T-shirt bodice + skirt, or A-line T-shirt dress)",
    "fitted_dress": "Fitted woven dress (bust and waist darts, invisible zip, bias-bound neckline)",
    "wrap": "Wrap top / wrap dress (knit, band along the wrap edge, ties)",
    "jumpsuit": "Jumpsuit / playsuit / boiler suit (bodice + pants, buttons or zip, back waist elastic, belt)",
    "pinafore": "Pinafore / strap dress (lined bib bodice, crossed straps, gathered skirt)",
    "pyjama": "Pyjama set (top + pants in one booklet and one cutting layout; long or shorty)",
    "beanie": "Beanie",
    "loop": "Loop scarf",
    "scarf": "Scarf (tube or flat, optional fringe)",
    "headband": "Headband / ear warmer (plain or twist)",
    "neckwear": "Neck gaiter or triangle neckerchief",
    "bib": "Baby bib (classic with snap, or bandana)",
    "mittens": "Mittens (thumb in profile, optional rib cuff; thumbless for babies)",
    "gloves": "Five-finger gloves (outline style, or with fourchettes and a set-in thumb)",
    "socks": "Socks (profile with shaped heel, or house socks with a sole)",
    "earflap_hat": "Hat with ear flaps (lined, optional ties)",
    "bucket_hat": "Bucket hat / sun hat (lined or reversible)",
    "cap": "Baseball cap (six panels, stiffened peak, adjustable strap)",
    "shirt": "Shirt / blouse (woven: button stand, collar, yoke, cuffs, bust dart)",
    "polo": "Polo shirt (half placket, knit collar)",
    "cardigan": "Cardigan (knit, continuous button band, V or round neck)",
    "vest": "Vest / gilet (sleeveless; zip, snaps or pullover; armhole binding)",
    "jacket": "Lined woven jacket (button front, facings, stand collar, welt/jetted/flap pockets)",
    "coat": "Coat (lined, knee length, flap pockets)",
    "softshell": "Softshell / outdoor jacket (zip, hood, zip pockets, Velcro sleeve tabs, drawcord hem)",
    "bodysuit": "Bodysuit / swimsuit / baby wrap body (knit, snap crotch or crotch seam, leg bands or elastic)",
    "underwear": "Underwear: briefs with lined gusset, or boxer briefs (knit, elastic finishes)",
    "swim_trunks": "Swim trunks (quick-dry fabric, drawcord waistband, mesh pockets and brief liner)",
    "romper": "Baby romper / footed sleeper (sizes 50–92, snaps along the inner legs, cuffs or feet)",
    "bag": "Bags: tote with lining and boxed corners, drawstring bag (no body measurements)",
}


def get(name: str):
    if name not in GARMENTS:
        raise ValueError(f"No module '{name}'. Available: {', '.join(GARMENTS)}")
    return import_module(f"garments.{name}")
