"""Fitted woven dress: the waist-seam dress with a fitted bodice. Bust dart in the side seam
(adults), waist darts in bodice and skirt (they meet at the waist seam), an invisible zip in the
centre back seam (bodice and the top of the skirt), neckline finished with a bias binding.
Sleeves short, long or none (armholes bound); skirt A-line, gathered or circle."""
from __future__ import annotations

from pattern import Pattern, rect_piece

from . import _parts as PT
from . import dress as D
from ._common import clamp, is_adult

DEFAULTS = dict(fit="slim", fabric="woven", stretch=None, skirt="a_line", length="knee", sleeve_length="short",
                neckline="round", pockets=False, gather=1.6, sa=10.0, hem_sa=25.0, zip_sa=15.0)
FINISHED_LABELS = dict(D.FINISHED_LABELS, waist_fitted=("Waist (darts closed)", "width"),
                       zip_length=("Zip length", "length"))
FIT_CHECK = "do the darts point at the bust, does the waist seam sit at the waist, and does the zip close without " \
            "pulling?"
ZIPS = [20, 22, 25, 30, 35, 40, 45, 50, 55, 60]


def draft(measures: dict, options: dict | None = None) -> Pattern:
    o = dict(DEFAULTS)
    o.update({k: v for k, v in (options or {}).items() if v is not None})
    m = measures
    sa = o["sa"]
    sleeveless = o["sleeve_length"] == "none"
    dopts = {k: v for k, v in o.items() if k not in ("zip_sa",)}
    dopts.update(style="waist_seam", back_opening=True, neck_finish="bias", waist_elastic=False,
                 sleeve_length="short" if sleeveless else o["sleeve_length"])
    pat = D.draft(m, dopts)
    pat.garment = "fitted_dress"
    F = pat.options["_F"]
    f, b = pat.piece("front"), pat.piece("back")
    sf, sb = pat.piece("skirt_front"), pat.piece("skirt_back")
    # bust dart (adults): the front gets the length over the bust, the side seam check takes the intake
    if is_adult(m):
        intake = clamp(0.028 * m["chest"], 15.0, 32.0)
        PT.bust_dart(f, -(F["AD"] + 45.0), intake, 0.095 * m["chest"])
        for s in pat.seams:
            if s["name"].startswith("Side seam"):
                s.update(type="ease", lo=-intake - 2, hi=-intake + 2, note="the front includes the bust dart")
    # waist darts: what the bodice is wider than the fitted waist goes into one dart per quarter;
    # the same dart continues into the skirt, so the waist seam stays the same length
    wq = m["waist"] * 1.05 / 4
    darts = 0.0
    for bod, sk, x_rel, h_rel in ((f, sf, 0.095 * m["chest"] / F["q"], 0.55), (b, sb, 0.42, 0.62)):
        s = bod.edge("hem").length - wq
        w = clamp(s, 0.0, 40.0 if bod is b else 35.0)
        if w < 8:
            continue
        x = F["q"] * x_rel
        PT.waist_dart(bod, "hem", x, w, h_rel * (F["AD"] if bod is f else F["AD"] + 30))
        PT.waist_dart(sk, "waistband", x, w, clamp(0.11 * m["height"], 80, 140), label="Skirt dart")
        darts += w
    waist_fit = 4 * (f.edge("hem").length + b.edge("hem").length) / 2 - 2 * darts
    pat.checks.append(dict(name="Waist with the darts closed", kind="range", value=waist_fit, lo=m["waist"] * 1.0,
                           hi=m["waist"] * 1.2 + 40, note="waist + 0–20 % ease"))
    for c in pat.checks:
        if c["name"] == "Dress goes on through the back opening":
            c["value"] -= 2 * darts
    # invisible zip in the centre back seam instead of the turned-under opening
    zsa = o["zip_sa"]
    for pc, ek in ((b, "center"), (sb, "center_open")):
        e = pc.edge(ek)
        e.sa, e.turned, e.label = zsa, False, "Centre back (zip)"
    sb.edge("center").sa = zsa
    open_len = b.edge("center").length + sb.edge("center_open").length
    fits = [z for z in ZIPS if z * 10 <= open_len + 15]
    zl = (fits[-1] if fits else ZIPS[0]) * 10.0
    pat.notes.append(f"Invisible zip, {zl / 10:.0f} cm long (opening {open_len / 10:.1f} cm).")
    pat.seams.append(dict(name="Zip (centre back bodice ↔ bodice)", a=[("back", "center", 1)],
                          b=[("back", "center", 1)], type="equal"))
    if sleeveless:
        pat.pieces = [p for p in pat.pieces if p.key != "sleeve"]
        pat.seams = [s for s in pat.seams if not any(k == "sleeve" for k, _, _ in s["a"] + s["b"])]
        pat.corners = [c for c in pat.corners if c.get("piece") != "sleeve"]
        pat.checks = [c for c in pat.checks if "leeve" not in c["name"] and "cap" not in c["name"].lower()]
        for pc in (f, b):
            pc.notches = [n for n in pc.notches if n.edge != "armhole"]
            pc.edge("armhole").label = "Armhole (binding)"
        arm = f.edge("armhole").length + b.edge("armhole").length
        ab = rect_piece("armhole_binding", "Armhole binding (bias)", arm + 2 * sa, 4 * 8.0, sa=0.0, cut_count=2,
                        labels=("Binding edge", "End", "Binding edge", "End"), grain_vertical=False)
        for e in ab.edges:
            e.raw = True
        ab.info.append("cut on the bias (45°); press both long edges to the middle")
        pat.pieces.append(ab)
        pat.seams.append(dict(name="Armhole binding ↔ armhole", a=[("front", "armhole", 1), ("back", "armhole", 1)],
                              b=[("armhole_binding", "bottom", 1)], type="ratio", lo=1.0, hi=1.0 + 2 * sa / arm + 0.02,
                              note="binding ends overlap at the side seam"))
        pat.finished = {k: v for k, v in pat.finished.items() if not k.startswith("sleeve") and k != "bicep_circ"}
    pat.options.update(sleeve_length=o["sleeve_length"], _zip_len=zl, _darts=darts)
    pat.finished["waist_fitted"] = waist_fit
    pat.finished["zip_length"] = zl
    pat.title = "Fitted dress" + {"a_line": "", "gathered": " with gathered skirt", "circle": " with circle skirt"}[
        o["skirt"]]
    return pat


def assembly(pat):
    import steps as ST
    o = pat.options
    out = []
    if any(mk.label in ("Bust dart", "Waist dart", "Skirt dart") for p in pat.pieces for mk in p.marks):
        out.append(PT.dart_steps("Darts", "Fold each dart right sides together on its middle, the dart lines on top of "
                                 "each other. Sew from the wide end to the point and run off the fold. Press bust "
                                 "darts down and waist darts towards the centre."))
    base = D.assembly(pat)
    sleeveless = o.get("sleeve_length") == "none"
    for st in base:
        if st.section == "Back opening":
            continue
        if sleeveless and ("leeve" in st.title or st.title.startswith("Finish the armhole")):
            if st.title == "Sew side and sleeve seams":
                st.title = "Sew the side seams"
                st.text = ("Lay front and back right sides together and sew the side seams from the hem to the "
                           "armhole. Press the allowances open.")
                st.data = {}
                out.append(st)
            continue
        if st.title.startswith("Sew the skirt centre back seam"):
            st.text = ("Lay the skirt back pieces right sides together and sew the centre back seam from the hem "
                       "up to the notch; above the notch the zip goes in.")
        if st.title == "Final pressing":
            if sleeveless:
                out.append(ST.seam("Bind the armholes", ["Armhole binding"],
                                   "Unfold one edge of the binding and sew it right sides together onto the armhole, "
                                   "the ends overlapping at the side seam. Fold it to the inside over the allowance "
                                   "and stitch it down.", section="Armholes", repeat=2))
            out.append(ST.icon("Sew in the invisible zip", "zip",
                               f"Open the {o.get('_zip_len', 400) / 10:.0f} cm zip and press its coils flat. Pin each "
                               "half right sides together onto a centre back edge, the coil on the seam line, the "
                               "top stop just below the binding. Sew with the invisible-zip foot as close to the "
                               "coil as possible, down to the notch. Close the seam below it.", section="Zip"))
        out.append(st)
    return out


def sewing_steps(pat):
    import steps as ST
    return ST.as_texts(assembly(pat), pat.options)
