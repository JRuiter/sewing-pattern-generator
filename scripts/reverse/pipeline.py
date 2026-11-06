"""Gesamtablauf Foto-Modus B (Reverse Engineering) mit Zwischenergebnissen.

  python -m reverse.pipeline foto.jpg --type hose --out projekt/   (aus scripts/)
"""
from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import photo_measure as PM  # noqa: E402
import validate as V  # noqa: E402

from . import decompose as D  # noqa: E402
from . import fit as F  # noqa: E402
from . import store as S  # noqa: E402
from . import unfold as U  # noqa: E402
from . import verify as VF  # noqa: E402


def run(image, garment="hose", out="projekt", tape=None, base_options=None, fits=None,
        grade_steps: int = 0, max_rounds: int = 2):
    os.makedirs(out, exist_ok=True)
    steps = {}
    # 2 Vermessen (inkl. Referenz/Perspektive)
    meas = PM.measure(image, garment, overlay_path=os.path.join(out, "overlay_messung.png"), tape=tape)
    steps["vermessung"] = meas
    flat = meas["measures_mm"]
    # 1 Zerlegen
    feat = D.features_from_measurement(garment, flat)
    feat.update(base_options or {})
    graph = D.decompose(feat)
    steps["teilegraph"] = graph
    # 3 Abwickeln
    targets = U.unfold(garment, flat)
    steps["fertigmasse_soll"] = targets
    # 4 Rekonstruieren (+ 5 Verifizieren, ggf. Wiederholung mit allen Passformen)
    opts = D.options_from_features(feat)
    kw = dict(fits=fits) if fits else {}
    res = F.fit(garment, targets, opts, **kw)
    rows = VF.compare(res["pattern"], targets)
    rounds = 1
    while not VF.all_ok(rows) and rounds < max_rounds:
        res = F.fit(garment, targets, opts, fits=("harem", "normal", "weit", "oversized", "eng"))
        rows = VF.compare(res["pattern"], targets)
        rounds += 1
    pat = res["pattern"]
    pat.size_label = f"nach Vorbild (≈ Gr. {res['size']})"
    report = V.validate(pat)
    steps["abweichung"] = rows
    project = dict(modul=pat.garment, passform=res["fit"], optionen=res["options"], parameter=res["params"],
                   groesse_geschaetzt=res["size"], messung_flach_mm=flat, fertigmasse_soll_mm=targets,
                   fertigmasse_ist_mm=pat.finished, teilegraph=graph, quelle=str(image))
    S.save(os.path.join(out, "projekt.json"), project)
    md = ["## Reverse Engineering – Ergebnis", "",
          f"Erkanntes Modul: **{pat.title}**, Passform **{res['fit']}**, geschätzte Größe ≈ {res['size']}", "",
          D.describe(graph), "", VF.to_markdown(rows), "", V.to_markdown(report)]
    with open(os.path.join(out, "reverse_bericht.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    return dict(pattern=pat, rows=rows, report=report, project=project, steps=steps, fit=res,
                markdown="\n".join(md))


def regrade(project_path, steps: int):
    """Gespeichertes Projekt um n Größen verschieben und neu rekonstruieren."""
    p = S.load(project_path)
    src = p["groesse_geschaetzt"]
    dst = S.size_step(src, steps)
    t = S.grade_targets(p["fertigmasse_soll_mm"], src, dst)
    opts = {k: v for k, v in p["optionen"].items() if not k.startswith("_") and k not in F.PANTS_PARAMS + ["knee_total"]}
    res = F.fit("pants_basic", t, opts, fits=(p["passform"],), size=dst)
    res["pattern"].size_label = f"nach Vorbild, Gr. {dst:g}"
    return res, t


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("--type", default="hose")
    ap.add_argument("--out", default="projekt")
    a = ap.parse_args(argv)
    r = run(a.image, a.type, a.out)
    print(r["markdown"])


if __name__ == "__main__":
    main()
