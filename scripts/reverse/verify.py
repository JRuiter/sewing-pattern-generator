"""Verifizieren: rekonstruierten Schnitt virtuell zusammennähen und mit der Messung vergleichen.

Toleranz: Längen ± 1 cm, Weiten ± 2 %. Zusätzlich gilt immer die Nähbarkeits-Validierung.
"""
from __future__ import annotations

from garments import get

from .fit import WIDTH_KEYS, tolerance


def compare(pattern, targets: dict, keys=None):
    mod = get(pattern.garment)
    labels = getattr(mod, "FINISHED_LABELS", {})
    rows = []
    for k in keys or targets:
        if k not in pattern.finished:
            continue
        soll, ist = targets[k], pattern.finished[k]
        d = ist - soll
        tol = tolerance(k, soll)
        rows.append(dict(key=k, name=labels.get(k, (k,))[0], soll=soll, ist=ist, delta=d,
                         tol=tol, rel=d / soll if soll else 0.0, ok=abs(d) <= tol,
                         art="Weite" if k in WIDTH_KEYS else "Länge"))
    return rows


def to_markdown(rows, title="Abweichungsbericht (Soll = gemessen, Ist = rekonstruierter Schnitt)"):
    out = [f"### {title}", "", "| Maß | Soll | Ist | Δ | Toleranz | Ergebnis |", "|---|---|---|---|---|---|"]
    for r in rows:
        tol = f"± {r['tol'] / 10:.1f} cm" if r["art"] == "Länge" else f"± 2 % ({r['tol'] / 10:.1f} cm)"
        d = f"{r['delta'] / 10:+.1f} cm" + (f" ({r['rel'] * 100:+.1f} %)" if r["art"] == "Weite" else "")
        out.append(f"| {r['name']} | {r['soll'] / 10:.1f} cm | {r['ist'] / 10:.1f} cm | {d} | {tol} | "
                   f"{'✅' if r['ok'] else '❌'} |".replace(".", ","))
    ok = all(r["ok"] for r in rows)
    out += ["", "**Ergebnis:** " + ("alle Maße innerhalb der Toleranz." if ok else
                                    "Toleranz überschritten – Messung prüfen (Schritt 2–4 wiederholen).")]
    return "\n".join(out)


def all_ok(rows):
    return all(r["ok"] for r in rows)
