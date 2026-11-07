#!/usr/bin/env python3
"""Saved body-measurement profiles, e.g. one per family member (issue #12).

A profile is `profiles/<name>.json` (directory: `--profiles-dir`, env `SEWING_PROFILES`,
default `./profiles`):

    {"name": "lena", "kind": "child", "measured": "2026-11-06",
     "measures_cm": {"height": 121, "hip": 64, "waist": 55},
     "fit": "normal", "default_format": "roll610", "machines": ["sewing", "overlocker"],
     "history": [{"measured": "2026-05-01", "measures_cm": {"height": 116, ...}}]}

Precedence when drafting: size table < profile < measurement file < measurements given
explicitly (CLI `--measures`, spec `measures_cm`/`measures_in`). A profile with
`kind: doll` switches on the doll clothes mode (doll.py).

Machines (machines.py) belong to the person who sews, not to the wearer: they are kept once in
the workshop file `profiles/_machines.json` and used for every pattern. A profile may carry its
own `machines` (e.g. sewing at grandma's), and `--machines` / spec `machines` win over both. Children's profiles
(`kind: child`, or height < 160 cm) older than 6 months get a warning (growth).

CLI:
  python profiles.py save lena --measures '{"height": 121, "hip": 64}' [--kind child] [--fit normal]
                                [--format roll610]
  python profiles.py show lena        # current values, growth since the last entry, size
  python profiles.py list
  python profiles.py export lena lena.smis
  python profiles.py machines set sewing,overlocker,twin_needle   # the sewist's machines (workshop)
  python profiles.py machines show
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import machines as MC  # noqa: E402
import measurements as M  # noqa: E402

CHILD_MAX_AGE_DAYS = 183      # ≈ 6 months
CHILD_HEIGHT_CM = 160.0


def profiles_dir(path: str | None = None) -> str:
    return path or os.environ.get("SEWING_PROFILES") or os.path.join(os.getcwd(), "profiles")


def _slug(name: str) -> str:
    s = re.sub(r"[^a-z0-9_-]+", "_", name.strip().lower()).strip("_")
    if not s:
        raise ValueError("profile name is empty")
    return s


def path_for(name: str, directory: str | None = None) -> str:
    if name.endswith(".json") or os.sep in name:
        return name
    return os.path.join(profiles_dir(directory), _slug(name) + ".json")


def load(name: str, directory: str | None = None) -> dict:
    p = path_for(name, directory)
    if not os.path.exists(p):
        raise FileNotFoundError(f"no profile '{name}' ({p})")
    with open(p, encoding="utf-8") as f:
        prof = json.load(f)
    prof.setdefault("name", _slug(name))
    prof["measures_cm"] = M.normalize_keys(prof.get("measures_cm", {}))
    return prof


def is_child(prof: dict) -> bool:
    if prof.get("kind"):
        return prof["kind"] in ("child", "kid", "kids")
    return prof.get("measures_cm", {}).get("height", 999) < CHILD_HEIGHT_CM


def age_days(prof: dict, today: dt.date | None = None) -> int | None:
    if not prof.get("measured"):
        return None
    d = dt.date.fromisoformat(str(prof["measured"])[:10])
    return ((today or dt.date.today()) - d).days


def warnings(prof: dict, today: dt.date | None = None) -> list[str]:
    w = []
    days = age_days(prof, today)
    if days is None:
        w.append(f"Profile '{prof['name']}' has no measuring date.")
    elif is_child(prof) and days > CHILD_MAX_AGE_DAYS:
        w.append(f"The measurements of '{prof['name']}' are {days // 30} months old: children grow, "
                 "please measure again (at least height, chest/hip and inseam).")
    return w


def save(name: str, measures_cm: dict, directory: str | None = None, kind: str | None = None,
         fit: str | None = None, default_format: str | None = None, measured: str | None = None,
         machines=None) -> str:
    """Create or update a profile. Earlier measurements move to `history`."""
    p = path_for(name, directory)
    os.makedirs(os.path.dirname(os.path.abspath(p)), exist_ok=True)
    new = M.normalize_keys(measures_cm)
    if os.path.exists(p):
        prof = load(name, directory)
        old = {"measured": prof.get("measured"), "measures_cm": prof.get("measures_cm", {})}
        prof.setdefault("history", []).append(old)
        merged = dict(prof.get("measures_cm", {}))
        merged.update(new)
        prof["measures_cm"] = merged
    else:
        prof = {"name": _slug(name), "measures_cm": new, "history": []}
    prof["measured"] = measured or dt.date.today().isoformat()
    for k, v in (("kind", kind), ("fit", fit), ("default_format", default_format)):
        if v:
            prof[k] = v
    if machines:
        prof["machines"] = MC.to_list(machines)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(prof, f, ensure_ascii=False, indent=2)
    return p


def growth(prof: dict) -> dict:
    """Change of every measurement since the previous entry (cm)."""
    hist = prof.get("history") or []
    if not hist:
        return {}
    prev = hist[-1].get("measures_cm", {})
    cur = prof.get("measures_cm", {})
    return {k: round(cur[k] - prev[k], 1) for k in cur if k in prev and abs(cur[k] - prev[k]) >= 0.05}


def suggested_size(prof: dict):
    """Kids: next table size ≥ height; adults: None (measurements are used directly)."""
    h = prof.get("measures_cm", {}).get("height")
    if h is None or not is_child(prof):
        return None
    sizes = sorted(M.KIDS_TABLE)
    return next((s for s in sizes if s >= h), sizes[-1])


MACHINES_FILE = "_machines.json"


def save_machines(machines, directory: str | None = None) -> str:
    """Save the sewist's machines in the workshop file (used for every pattern)."""
    d = profiles_dir(directory)
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, MACHINES_FILE)
    with open(p, "w", encoding="utf-8") as f:
        json.dump({"machines": MC.to_list(machines), "saved": dt.date.today().isoformat()}, f, indent=2)
    return p


def load_machines(directory: str | None = None) -> list[str] | None:
    p = os.path.join(profiles_dir(directory), MACHINES_FILE)
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        return MC.to_list(json.load(f).get("machines"))


def apply_machines(spec: dict, prof: dict | None = None, directory: str | None = None) -> dict:
    """options.machines: explicit (spec/CLI) > profile > workshop file."""
    opts = dict(spec.get("options") or {})
    m = opts.get("machines") or spec.get("machines")
    if not m and prof:
        m = prof.get("machines")
    if not m:
        m = load_machines(directory or spec.get("profiles_dir"))
    if not m:
        return spec
    opts["machines"] = MC.to_list(m)
    out = dict(spec)
    out["options"] = opts
    return out


def apply(spec: dict, directory: str | None = None) -> tuple[dict, list[str]]:
    """Merge a profile (spec['profile']) into a spec. Returns (spec, warnings)."""
    name = spec.get("profile")
    if not name:
        return apply_machines(spec, None, directory), []
    if "_profile_measures_cm" in spec:          # already applied
        return spec, list(spec.get("_profile_warnings", []))
    prof = load(name, directory or spec.get("profiles_dir"))
    out = dict(spec)
    out["_profile_measures_cm"] = dict(prof["measures_cm"])
    opts = dict(out.get("options") or {})
    if prof.get("fit") and not opts.get("fit"):
        opts["fit"] = prof["fit"]
    out["options"] = opts
    out = apply_machines(out, prof, directory)
    if prof.get("kind") == "doll":
        out.setdefault("doll", True)            # doll clothes mode (doll.py)
    if not out.get("formats") and prof.get("default_format"):
        out["formats"] = [x.strip() for x in str(prof["default_format"]).split(",")]
    if out.get("size") is None and "height" not in prof["measures_cm"] and prof.get("size"):
        out["size"] = prof["size"]
    out.setdefault("size_label", f"for {prof['name'].capitalize()} (profile, measured {prof.get('measured', '?')})")
    out["_profile_warnings"] = warnings(prof)
    return out, list(out["_profile_warnings"])


def main(argv=None):
    ap = argparse.ArgumentParser(description="Body-measurement profiles")
    ap.add_argument("--profiles-dir")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("save")
    s.add_argument("name")
    s.add_argument("--measures", required=True, help="measurements in cm as JSON")
    s.add_argument("--kind", choices=["child", "adult", "doll"])
    s.add_argument("--fit")
    s.add_argument("--format")
    s.add_argument("--date", help="measuring date YYYY-MM-DD (default today)")
    s.add_argument("--machines", help="machines for this profile only, e.g. sewing,overlocker (see machines.py)")
    mc = sub.add_parser("machines", help="the sewist's machines (workshop file, used for every pattern)")
    mc.add_argument("action", choices=["set", "show"])
    mc.add_argument("list", nargs="?", help="comma-separated: " + ", ".join(MC.KEYS))
    sh = sub.add_parser("show")
    sh.add_argument("name")
    sub.add_parser("list")
    ex = sub.add_parser("export")
    ex.add_argument("name")
    ex.add_argument("path")
    a = ap.parse_args(argv)
    if a.cmd == "save":
        p = save(a.name, json.loads(a.measures), a.profiles_dir, a.kind, a.fit, a.format, a.date, a.machines)
        print(f"saved {p}")
    elif a.cmd == "show":
        prof = load(a.name, a.profiles_dir)
        print(f"{prof['name']} (measured {prof.get('measured')}):")
        for k, v in prof["measures_cm"].items():
            print(f"  {M.LABELS.get(k, k)}: {v:g} cm")
        g = growth(prof)
        if g:
            print("Change since the previous measurement: " + ", ".join(f"{M.LABELS.get(k, k)} {v:+g} cm"
                                                                      for k, v in g.items()))
        if prof.get("machines"):
            print("Machines (this profile): " + ", ".join(MC.LABELS[k] for k in MC.to_list(prof["machines"]) or []))
        size = suggested_size(prof)
        if size:
            print(f"Suggested kids' size: {size}")
        for w in warnings(prof):
            print("⚠️ " + w)
    elif a.cmd == "machines":
        if a.action == "set":
            if not a.list:
                ap.error("machines set needs a list, e.g. sewing,overlocker")
            print(f"saved {save_machines(a.list, a.profiles_dir)}")
        m = load_machines(a.profiles_dir)
        print("Machines: " + (", ".join(MC.LABELS[k] for k in m) if m else "not saved yet"))
    elif a.cmd == "list":
        d = profiles_dir(a.profiles_dir)
        for f in sorted(os.listdir(d)) if os.path.isdir(d) else []:
            if f.endswith(".json") and f != MACHINES_FILE:
                prof = load(os.path.join(d, f))
                print(f"{prof['name']}: measured {prof.get('measured')}")
    elif a.cmd == "export":
        import measure_files as MF
        prof = load(a.name, a.profiles_dir)
        MF.write_file(a.path, {k: v * 10 for k, v in prof["measures_cm"].items()}, given_name=prof["name"])
        print(f"wrote {a.path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
