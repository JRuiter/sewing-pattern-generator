"""Garment modules. Each module offers draft(measures_mm, options) -> Pattern,
DEFAULTS (default options) and finished_measures(pattern) for verification."""
from importlib import import_module

GARMENTS = {
    "pants_basic": "Pants (joggers, harem pants, leggings, pull-on trousers)",
    "tshirt_basic": "T-shirt / long sleeve (set-in or raglan sleeve)",
    "hoodie": "Hoodie / sweatshirt",
    "skirt": "Skirt (elastic waist: gathered, A-line, circle)",
    "dress": "Dress (T-shirt bodice + skirt, or A-line T-shirt dress)",
    "beanie": "Beanie",
    "loop": "Loop scarf",
}


def get(name: str):
    if name not in GARMENTS:
        raise ValueError(f"No module '{name}'. Available: {', '.join(GARMENTS)}")
    return import_module(f"garments.{name}")
