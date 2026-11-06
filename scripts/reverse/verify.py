"""Verify: sew the reconstructed pattern together virtually and compare it with the measurement.

Tolerance: lengths ± 1 cm, widths ± 2 %. The sewability validation always applies as well.
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
        target, actual = targets[k], pattern.finished[k]
        d = actual - target
        tol = tolerance(k, target)
        rows.append(dict(key=k, name=labels.get(k, (k,))[0], target=target, actual=actual, delta=d,
                         tol=tol, rel=d / target if target else 0.0, ok=abs(d) <= tol,
                         type="width" if k in WIDTH_KEYS else "length"))
    return rows


def to_markdown(rows, title="Deviation report (target = measured, actual = reconstructed pattern)"):
    out = [f"### {title}", "", "| Measurement | Target | Actual | Δ | Tolerance | Result |", "|---|---|---|---|---|---|"]
    for r in rows:
        tol = f"± {r['tol'] / 10:.1f} cm" if r["type"] == "length" else f"± 2 % ({r['tol'] / 10:.1f} cm)"
        d = f"{r['delta'] / 10:+.1f} cm" + (f" ({r['rel'] * 100:+.1f} %)" if r["type"] == "width" else "")
        out.append(f"| {r['name']} | {r['target'] / 10:.1f} cm | {r['actual'] / 10:.1f} cm | {d} | {tol} | "
                   f"{'✅' if r['ok'] else '❌'} |")
    ok = all(r["ok"] for r in rows)
    out += ["", "**Result:** " + ("all measurements within tolerance." if ok else
                                 "tolerance exceeded: check the measurement (repeat steps 2–4).")]
    return "\n".join(out)


def all_ok(rows):
    return all(r["ok"] for r in rows)
