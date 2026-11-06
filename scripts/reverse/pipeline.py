"""Complete flow of photo mode B (reverse engineering) with intermediate results.

  python -m reverse.pipeline photo.jpg --type pants --out project/   (from scripts/)
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

# flat features of a top that are compared as lengths (the widths are compared as circumferences)
LENGTH_FEATURES = ["length", "armhole_depth", "sleeve_reach", "neck_half", "front_neck", "back_neck",
                   "shoulder_x", "shoulder_y"]


def run(image, garment="pants", out="project", tape=None, base_options=None, fits=None,
        grade_steps: int = 0, max_rounds: int = 2):
    os.makedirs(out, exist_ok=True)
    steps = {}
    # 2 measure (incl. reference/perspective)
    meas = PM.measure(image, garment, overlay_path=os.path.join(out, "overlay_measurement.png"), tape=tape)
    steps["measurement"] = meas
    flat = meas["measures_mm"]
    # 1 decompose
    top = garment not in ("pants", "pants_basic")
    feat = D.features_from_measurement(garment, flat)
    if top:
        feat["options"].update(base_options or {})
    else:
        feat.update(base_options or {})
    graph = D.decompose(feat)
    steps["piece_graph"] = graph
    # 3 unfold
    targets = U.unfold(garment, flat)
    steps["targets"] = targets
    # 4 reconstruct (+ 5 verify, repeat with all fits if needed)
    opts = D.options_from_features(feat)
    if top:
        # tops: the fit matches the virtual flat lay of the pattern to every photo feature
        res = F.fit(garment, flat, opts)
        rows = VF.compare(res["pattern"], targets)
        lab = {k: (v,) for k, v in PM.TOP_LABELS.items()}
        rows += VF.compare(res["pattern"], {k: v for k, v in flat.items() if k in LENGTH_FEATURES},
                           actual_values=res["features"], labels=lab)
    else:
        kw = dict(fits=fits) if fits else {}
        res = F.fit(garment, targets, opts, **kw)
        rows = VF.compare(res["pattern"], targets)
        rounds = 1
        while not VF.all_ok(rows) and rounds < max_rounds:
            res = F.fit(garment, targets, opts, fits=("harem", "normal", "wide", "oversized", "slim"))
            rows = VF.compare(res["pattern"], targets)
            rounds += 1
    pat = res["pattern"]
    pat.size_label = f"copied from garment (≈ size {res['size']})"
    style = f", {res['sleeve_style'].replace('_', '-')} sleeves" if top else ""
    report = V.validate(pat)
    steps["deviation"] = rows
    project = dict(module=pat.garment, fit=res["fit"], options=res["options"], params=res["params"],
                   size_estimate=res["size"], flat_mm={k: v for k, v in flat.items() if not k.startswith("_")},
                   target_mm=targets,
                   actual_mm=pat.finished, piece_graph=graph, source=str(image))
    S.save(os.path.join(out, "project.json"), project)
    md = ["## Reverse engineering: result", "",
          f"Detected module: **{pat.title}**{style}, fit **{res['fit']}**, estimated size ≈ {res['size']}", "",
          D.describe(graph), "", VF.to_markdown(rows), "", V.to_markdown(report)]
    with open(os.path.join(out, "reverse_report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    return dict(pattern=pat, rows=rows, report=report, project=project, steps=steps, fit=res,
                markdown="\n".join(md))


def regrade(project_path, steps: int):
    """Shift a saved project by n sizes and reconstruct it again."""
    p = S.load(project_path)
    src = p["size_estimate"]
    dst = S.size_step(src, steps)
    if p["module"] != "pants_basic":
        res = F.regrade_top(p["options"], src, dst)
        res["pattern"].size_label = f"copied from garment, size {dst:g}"
        return res, res["pattern"].finished
    t = S.grade_targets(p["target_mm"], src, dst)
    opts = {k: v for k, v in p["options"].items() if not k.startswith("_") and k not in F.PANTS_PARAMS + ["knee_total"]}
    res = F.fit("pants_basic", t, opts, fits=(p["fit"],), size=dst)
    res["pattern"].size_label = f"copied from garment, size {dst:g}"
    return res, t


def main(argv=None):
    ap = argparse.ArgumentParser(description="Photo mode B: reverse-engineer a pattern from a flat photo")
    ap.add_argument("image")
    ap.add_argument("--type", default="pants", help="pants or top (T-shirt / raglan)")
    ap.add_argument("--out", default="project")
    a = ap.parse_args(argv)
    r = run(a.image, a.type, a.out)
    print(r["markdown"])


if __name__ == "__main__":
    main()
