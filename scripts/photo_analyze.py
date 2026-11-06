"""Foto-Modus A (Inspirationsfoto): Merkmalsliste mit Konfidenz → Modul + Optionen.

Die eigentliche Bildbeschreibung macht Claude beim Ansehen des Fotos und füllt das
Merkmals-JSON (Schema unten). Dieses Skript
  1. prüft und normalisiert die Merkmalsliste,
  2. formuliert die Bestätigungsfrage („Ich erkenne: … – stimmt das?“),
  3. bildet die Merkmale auf ein vorhandenes Modul + Optionen ab und meldet offen, was
     kein Modul abdeckt (mit nächstliegender Alternative),
  4. kann bei freigestellten Bildern (Produktfoto/Flat-Lay vor einfarbigem Grund) die
     Silhouette automatisch aus Proportionen schätzen (nur Verhältnisse, keine Maße!).

Körpermaße kommen immer vom Nutzer (Größe oder Maße), nie aus einem Inspirationsfoto.

CLI:
  python photo_analyze.py merkmale.json            → Mapping + Bestätigungstext
  python photo_analyze.py --bild foto.jpg           → automatische Proportionen (Hose)
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

SCHEMA = {
    "kleidungsart": ["hose", "jogginghose", "haremshose", "leggings", "shorts", "tshirt", "longsleeve",
                     "hoodie", "sweatshirt", "pullover", "rock", "muetze", "loop", "kleid", "jacke",
                     "bluse", "hemd", "jeans", "latzhose", "body"],
    "silhouette": ["eng", "gerade", "weit", "oversized", "harem", "ausgestellt", "a-linie", "tellerrock"],
    "laenge": ["lang", "7/8", "knie", "kurz", "mini", "midi", "maxi", "hueftlang", "tunika"],
    "taschen": ["keine", "eingriff", "schraeg", "aufgesetzt_hinten", "aufgesetzt_vorne", "kaenguru",
                "cargo", "paspel", "leisten"],
    "bund": ["gummizug", "bund_gummi", "buendchen", "tunnelzug", "yoga", "knopf_reissverschluss"],
    "bein_abschluss": ["buendchen", "saum", "tunnelzug"],
    "ausschnitt": ["rund", "v", "u-boot", "stehkragen", "kragen", "kapuze"],
    "aermel": ["eingesetzt", "raglan", "ueberschnitten", "ohne"],
    "aermellaenge": ["kurz", "lang", "3/4", "ohne"],
    "aermel_abschluss": ["buendchen", "saum"],
    "saum": ["buendchen", "umgenaeht"],
    "verschluss": ["keiner", "knopfleiste", "reissverschluss", "druckknoepfe"],
    "kapuze": ["ja", "nein"],
    "stoff": ["jersey", "jersey_elastan", "sweat", "fleece", "interlock", "webware", "strick"],
    "teilungsnaehte": ["keine", "passe", "laengsteilung", "querteilung"],
}

LABELS = {
    "kleidungsart": "Kleidungsart", "silhouette": "Silhouette", "laenge": "Länge", "taschen": "Taschen",
    "bund": "Bund", "bein_abschluss": "Beinabschluss", "ausschnitt": "Ausschnitt", "aermel": "Ärmelform",
    "aermellaenge": "Ärmellänge", "aermel_abschluss": "Ärmelabschluss", "saum": "Saum",
    "verschluss": "Verschluss", "kapuze": "Kapuze", "stoff": "vermuteter Stoff",
    "teilungsnaehte": "Teilungsnähte",
}

VALUE_DE = {"eingriff": "Eingrifftaschen", "schraeg": "schräge Eingrifftaschen",
            "aufgesetzt_hinten": "aufgesetzte Gesäßtaschen", "kaenguru": "Kängurutasche",
            "bund_gummi": "Stoffbund mit Gummi", "gummizug": "Gummizug", "buendchen": "Bündchen",
            "tunnelzug": "Tunnelzug", "harem": "Harem (tiefer Schritt, schmal zulaufend)",
            "jersey_elastan": "Jersey mit Elasthan", "sweat": "Sweat", "knopf_reissverschluss":
            "Knopf + Reißverschluss", "ueberschnitten": "überschnittene Schulter"}

UNSUPPORTED = {
    "kleid": "Kleid ist (noch) kein Modul – Alternative: T-Shirt-Modul verlängert (Länge „tunika“) "
             "oder Oberteil + Rock.",
    "jacke": "Jacken mit Futter/Reißverschluss sind nicht abgedeckt – Alternative: Hoodie (offen ohne "
             "Reißverschluss nicht möglich) bzw. Sweatshirt.",
    "bluse": "Blusen mit Knopfleiste/Kragen sind nicht abgedeckt – Alternative: T-Shirt aus Webware mit "
             "mehr Mehrweite.",
    "hemd": "Hemden sind nicht abgedeckt – Alternative: T-Shirt-Modul.",
    "jeans": "Jeans mit Hosenschlitz sind nicht abgedeckt – Alternative: Schlupfhose aus Webware mit "
             "Tunnelzug.",
    "latzhose": "Latzhose ist nicht abgedeckt – Alternative: Hose; Latz müsste separat ergänzt werden.",
    "body": "Body ist nicht abgedeckt – Alternative: T-Shirt-Modul.",
    "cargo": "Cargotaschen sind nicht abgedeckt – Alternative: aufgesetzte Gesäßtaschen.",
    "paspel": "Paspeltaschen sind nicht abgedeckt – Alternative: Eingrifftaschen.",
    "leisten": "Leistentaschen sind nicht abgedeckt – Alternative: Eingrifftaschen.",
    "aufgesetzt_vorne": "Aufgesetzte Vordertaschen sind nicht als Option vorhanden – Alternative: "
                        "Eingrifftaschen.",
    "knopf_reissverschluss": "Bund mit Knopf und Reißverschluss ist nicht abgedeckt – Alternative: "
                             "Gummibund (Schlupfhose).",
    "ausgestellt": "Ausgestellte Hosenbeine (Schlag) sind nicht abgedeckt – Alternative: weite Passform.",
    "knopfleiste": "Knopfleisten sind nicht abgedeckt – Alternative: ohne Verschluss.",
    "reissverschluss": "Reißverschlüsse sind nicht abgedeckt – Alternative: ohne Verschluss.",
    "druckknoepfe": "Druckknopfleisten sind nicht abgedeckt – Alternative: ohne Verschluss.",
    "stehkragen": "Stehkragen ist nicht abgedeckt – Alternative: Rundhals mit breitem Bündchen.",
    "kragen": "Hemdkragen ist nicht abgedeckt – Alternative: Rundhals.",
    "passe": "Teilungsnähte (Passe) sind nicht abgedeckt – der Schnitt wird ohne Teilung konstruiert.",
    "laengsteilung": "Längsteilungen sind nicht abgedeckt – der Schnitt wird ohne Teilung konstruiert.",
    "querteilung": "Querteilungen sind nicht abgedeckt – der Schnitt wird ohne Teilung konstruiert.",
    "u-boot": "U-Boot-Ausschnitt nicht als Option – Alternative: weiter Rundhals.",
    "ueberschnitten": "Überschnittene Schulter nicht als Option – Alternative: Raglan oder oversized.",
}


def normalize(features: dict) -> dict:
    """Merkmalsliste prüfen. Format je Merkmal: {"wert": ..., "konfidenz": 0..1} oder nur Wert."""
    out = {}
    for k, v in features.items():
        if k in ("proportionen", "hinweise"):
            out[k] = v
            continue
        if k not in SCHEMA:
            raise ValueError(f"Unbekanntes Merkmal '{k}'. Erlaubt: {', '.join(SCHEMA)}")
        if not isinstance(v, dict):
            v = {"wert": v, "konfidenz": 0.7}
        vals = v["wert"] if isinstance(v["wert"], list) else [v["wert"]]
        for x in vals:
            if x not in SCHEMA[k]:
                raise ValueError(f"Wert '{x}' für '{k}' nicht erlaubt. Erlaubt: {', '.join(SCHEMA[k])}")
        out[k] = {"wert": v["wert"], "konfidenz": float(v.get("konfidenz", 0.7))}
    if "kleidungsart" not in out:
        raise ValueError("Merkmal 'kleidungsart' fehlt.")
    return out


def _val(f, k, default=None):
    return f[k]["wert"] if k in f else default


def _conf_word(c):
    return "sicher" if c >= 0.8 else ("wahrscheinlich" if c >= 0.55 else "unsicher")


def confirmation_text(features: dict) -> str:
    f = normalize(features)
    parts = []
    for k, v in f.items():
        if k in ("proportionen", "hinweise"):
            continue
        vals = v["wert"] if isinstance(v["wert"], list) else [v["wert"]]
        txt = ", ".join(VALUE_DE.get(x, x) for x in vals)
        parts.append(f"- {LABELS[k]}: **{txt}** ({_conf_word(v['konfidenz'])}, {v['konfidenz'] * 100:.0f} %)")
    unsure = [LABELS[k] for k, v in f.items() if k in LABELS and v["konfidenz"] < 0.55]
    text = "Ich erkenne auf dem Foto:\n" + "\n".join(parts)
    if unsure:
        text += f"\n\nUnsicher bin ich bei: {', '.join(unsure)}. Bitte kurz bestätigen oder korrigieren."
    text += ("\n\nStimmt das so? Die Körpermaße nehme ich nicht aus dem Foto – bitte Größe oder Maße "
             "nennen. Rückseite und verdeckte Details frage ich nach, statt sie zu erfinden.")
    return text


def map_to_module(features: dict) -> dict:
    """Merkmale → (Modul, Optionen, nicht abgedeckt + Alternativen)."""
    f = normalize(features)
    art = _val(f, "kleidungsart")
    issues = []
    for k, v in f.items():
        if k in ("proportionen", "hinweise"):
            continue
        for x in (v["wert"] if isinstance(v["wert"], list) else [v["wert"]]):
            if x in UNSUPPORTED:
                issues.append(UNSUPPORTED[x])
    sil = _val(f, "silhouette", "gerade")
    fit = {"eng": "eng", "gerade": "normal", "weit": "weit", "oversized": "oversized",
           "harem": "harem", "ausgestellt": "weit"}.get(sil, "normal")
    stoff = _val(f, "stoff")
    opts = {}
    if art in ("hose", "jogginghose", "haremshose", "leggings", "shorts", "jeans", "latzhose"):
        module = "pants_basic"
        style = {"haremshose": "haremshose", "leggings": "leggings"}.get(art, "jogginghose")
        if fit == "harem":
            style = "haremshose"
        if fit == "eng" and art != "jogginghose":
            style = "leggings"
        opts["style"] = style
        opts["fit"] = fit
        t = _val(f, "taschen", [])
        t = t if isinstance(t, list) else [t]
        pk = []
        if any(x in ("eingriff", "schraeg", "paspel", "leisten", "aufgesetzt_vorne") for x in t):
            pk.append("eingriff")
        if any(x in ("aufgesetzt_hinten", "cargo") for x in t):
            pk.append("aufgesetzt_hinten")
        opts["pockets"] = pk
        b = _val(f, "bund")
        if b:
            opts["waistband"] = {"gummizug": "bund_gummi", "bund_gummi": "bund_gummi", "buendchen": "buendchen",
                                 "tunnelzug": "tunnel", "yoga": "yoga",
                                 "knopf_reissverschluss": "bund_gummi"}[b]
        ba = _val(f, "bein_abschluss")
        if ba:
            opts["cuffs"] = ba == "buendchen"
        lg = _val(f, "laenge")
        if art == "shorts":
            lg = lg or "kurz"
        if lg in ("lang", "7/8", "knie", "kurz"):
            opts["length"] = lg
    elif art in ("tshirt", "longsleeve", "body", "kleid", "bluse", "hemd"):
        module = "tshirt_basic"
        opts["fit"] = fit
        opts["sleeve_style"] = "raglan" if _val(f, "aermel") == "raglan" else "eingesetzt"
        al = _val(f, "aermellaenge", "lang" if art == "longsleeve" else "kurz")
        opts["sleeve_length"] = {"kurz": "kurz", "lang": "lang", "3/4": "3/4", "ohne": "kurz"}[al]
        opts["neckline"] = "v" if _val(f, "ausschnitt") == "v" else "rund"
        if art == "kleid" or _val(f, "laenge") == "tunika":
            opts["length"] = "tunika"
        if _val(f, "aermel_abschluss") == "buendchen":
            opts["sleeve_cuffs"] = True
        if _val(f, "saum") == "buendchen":
            opts["hem_band"] = True
    elif art in ("hoodie", "sweatshirt", "pullover", "jacke"):
        module = "hoodie"
        opts["fit"] = fit if fit != "harem" else "weit"
        opts["hood"] = _val(f, "kapuze", "ja" if art == "hoodie" else "nein") == "ja" or \
            _val(f, "ausschnitt") == "kapuze"
        t = _val(f, "taschen", [])
        t = t if isinstance(t, list) else [t]
        opts["kangaroo"] = "kaenguru" in t
        opts["sleeve_style"] = "raglan" if _val(f, "aermel") == "raglan" else "eingesetzt"
    elif art == "rock":
        module = "skirt"
        opts["style"] = {"a-linie": "a_linie", "tellerrock": "teller", "weit": "gerafft",
                         "gerade": "gerafft", "eng": "gerade"}.get(sil, "gerafft")
        lg = _val(f, "laenge", "knie")
        opts["length"] = {"mini": "mini", "knie": "knie", "midi": "midi", "maxi": "maxi", "kurz": "mini",
                          "lang": "maxi"}.get(lg, "knie")
    elif art == "muetze":
        module = "beanie"
    elif art == "loop":
        module = "loop"
    else:
        module = "pants_basic"
        issues.append(f"Für „{art}“ gibt es kein Modul.")
    if stoff:
        opts["fabric"] = stoff if stoff != "strick" else "jersey"
    prop = f.get("proportionen", {})
    if module == "pants_basic" and prop:
        # Proportionen steuern Optionsparameter (keine Körpermaße!)
        if "bein_unten_zu_huefte" in prop and not opts.get("cuffs"):
            opts["_hem_ratio"] = float(prop["bein_unten_zu_huefte"])
        if prop.get("schritt") == "tief":
            opts["fit"] = "harem"
            opts["style"] = "haremshose"
    low = [LABELS[k] for k, v in f.items() if k in LABELS and v["konfidenz"] < 0.55]
    return dict(module=module, options=opts, nicht_abgedeckt=issues, unsicher=low)


# ---------------------------------------------------------------------------
# Automatische Proportionen aus freigestellten Bildern (Hose)
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
    """Verhältnisse einer flach liegenden/freigestellten Hose (maßstabsfrei)."""
    import cv2

    import photo_measure as PM
    img = cv2.imread(image) if isinstance(image, str) else image
    mask = _simple_mask(img)
    mask, img2, _ = PM.upright(mask, img, 1.0)
    res, geo, _ = PM.measure_pants(mask, img2, 1.0)
    hip = res["hip_flat"]
    r = dict(schritt_zu_laenge=res["front_rise"] / res["outseam"],
             bein_unten_zu_huefte=res["opening_flat"] / hip,
             beinmitte_zu_huefte=res["knee_flat"] / hip,
             unten_zu_beinmitte=res["opening_flat"] / max(res["knee_flat"], 1),
             buendchen=res["cuff_h"] > 0.04 * res["outseam"])
    return r


def classify_pants(r: dict) -> dict:
    harem_score = (r["schritt_zu_laenge"] - 0.30) / 0.03 + (0.52 - r["unten_zu_beinmitte"]) / 0.04
    if harem_score > 1.0:
        sil, conf = "harem", min(0.95, 0.6 + harem_score * 0.1)
    elif r["beinmitte_zu_huefte"] < 0.43 and r["unten_zu_beinmitte"] > 0.62:
        sil, conf = "eng", 0.75
    elif r["bein_unten_zu_huefte"] > 0.40:
        sil, conf = "weit", 0.65
    else:
        sil, conf = "gerade", 0.6
    feats = {"kleidungsart": {"wert": "hose", "konfidenz": 0.9},
             "silhouette": {"wert": sil, "konfidenz": round(conf, 2)},
             "bein_abschluss": {"wert": "buendchen" if r["buendchen"] else "saum", "konfidenz": 0.7},
             "proportionen": {k: round(float(v), 3) for k, v in r.items() if k != "buendchen"}}
    if sil == "harem":
        feats["proportionen"]["schritt"] = "tief"
    return feats


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("merkmale", nargs="?")
    ap.add_argument("--bild")
    a = ap.parse_args(argv)
    if a.bild:
        feats = classify_pants(pants_proportions(a.bild))
    else:
        with open(a.merkmale, encoding="utf-8") as f:
            feats = json.load(f)
    print(confirmation_text(feats))
    print()
    print(json.dumps(map_to_module(feats), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
