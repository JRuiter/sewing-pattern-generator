"""Kleidungsmodule. Jedes Modul bietet draft(measures_mm, options) -> Pattern,
DEFAULTS (Standardoptionen) und finished_measures(pattern) für die Verifikation."""
from importlib import import_module

GARMENTS = {
    "pants_basic": "Hose (Jogginghose, Haremshose, Leggings)",
    "tshirt_basic": "T-Shirt / Longsleeve (eingesetzter Ärmel oder Raglan)",
    "hoodie": "Hoodie / Kapuzenpulli",
    "skirt": "Rock (Gummizug, gerade oder ausgestellt)",
    "beanie": "Beanie / Mütze",
    "loop": "Loop / Schlauchschal",
}


def get(name: str):
    if name not in GARMENTS:
        raise ValueError(f"Kein Modul '{name}'. Verfügbar: {', '.join(GARMENTS)}")
    return import_module(f"garments.{name}")
