"""Foto-Modus B: Kleidungsstück flach fotografiert → Maße in mm.

Ablauf:
  1. Referenz erkennen (ArUco-Referenzkarte, 4 Marker) → Homographie Bild → mm-Ebene
     (alternativ: 4 Punkte eines bekannten Rechtecks/Zollstock über `manual_ref`).
  2. Bild entzerren (Draufsicht, `px_per_mm` Pixel je mm).
  3. Kleidungsstück segmentieren (Abstand zur Hintergrundfarbe, Otsu, Morphologie),
     Karte ausmaskieren, größte Kontur.
  4. Messgrößen ableiten (Hose: Bund, Hüfte, Oberschenkel, Beinöffnung, Längen, Leibhöhe,
     Bund-/Bündchenhöhe über Nahtlinien-Erkennung).
  5. Overlay-PNG mit Kontur und Messlinien zur Bestätigung durch den Nutzer.

Alle Weiten sind **flach gemessen (eine Lage)**; die Umrechnung auf Umfänge (×2) erfolgt
in reverse/unfold.py. Messwerte, die der Nutzer per Maßband nennt, haben Vorrang.

CLI:  python photo_measure.py foto.jpg --type hose --out messung
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys

import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refcard  # noqa: E402


class MeasureError(Exception):
    pass


# ---------------------------------------------------------------------------
# 1–2 Referenz und Entzerrung
# ---------------------------------------------------------------------------

def detect_card(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if img.ndim == 3 else img
    params = cv2.aruco.DetectorParameters()
    params.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_SUBPIX
    det = cv2.aruco.ArucoDetector(cv2.aruco.getPredefinedDictionary(refcard.DICT_ID), params)
    corners, ids, _ = det.detectMarkers(gray)
    if ids is None:
        raise MeasureError("Referenzkarte nicht gefunden. Bitte die Karte vollständig, flach und "
                           "unverdeckt ins Bild legen (oder Zollstock-Maße angeben).")
    ref = refcard.marker_corners_mm()
    img_pts, mm_pts = [], []
    found = []
    for c, i in zip(corners, ids.ravel()):
        if int(i) in ref:
            img_pts.append(c.reshape(4, 2))
            mm_pts.append(ref[int(i)])
            found.append(int(i))
    if not found:
        raise MeasureError("Keine Marker der Referenzkarte erkannt.")
    return np.vstack(img_pts), np.vstack(mm_pts), sorted(found)


def homography(img, manual_ref=None):
    """Homographie Bildpixel → mm (Kartenebene). manual_ref: dict(img=[[x,y]*4], mm=[[x,y]*4])."""
    if manual_ref:
        ip = np.float32(manual_ref["img"])
        mp = np.float32(manual_ref["mm"])
        H, _ = cv2.findHomography(ip, mp)
        return H, dict(method="manuell", markers=[])
    ip, mp, found = detect_card(img)
    H, inl = cv2.findHomography(ip, mp, cv2.RANSAC if len(ip) > 4 else 0, 1.0)
    # Restfehler auf der Karte
    proj = cv2.perspectiveTransform(ip.reshape(-1, 1, 2), H).reshape(-1, 2)
    err = float(np.sqrt(np.mean(np.sum((proj - mp) ** 2, axis=1))))
    if len(found) < 2:
        note = "nur ein Marker erkannt – Genauigkeit eingeschränkt"
    else:
        note = ""
    return H, dict(method="Referenzkarte", markers=found, rms_mm=err, note=note)


def rectify(img, H, px_per_mm=2.0, max_side_mm=2500):
    """Draufsicht in mm-Raster. Rückgabe: Bild, Matrix mm→px des Ergebnisbilds."""
    h, w = img.shape[:2]
    corners = cv2.perspectiveTransform(np.float32([[0, 0], [w, 0], [w, h], [0, h]]).reshape(-1, 1, 2), H).reshape(-1, 2)
    x0, y0 = corners.min(axis=0)
    x1, y1 = corners.max(axis=0)
    x0, y0 = max(x0, -max_side_mm), max(y0, -max_side_mm)
    x1, y1 = min(x1, max_side_mm), min(y1, max_side_mm)
    T = np.array([[px_per_mm, 0, -x0 * px_per_mm], [0, px_per_mm, -y0 * px_per_mm], [0, 0, 1]])
    size = (int((x1 - x0) * px_per_mm) + 1, int((y1 - y0) * px_per_mm) + 1)
    out = cv2.warpPerspective(img, T @ H, size, flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0))
    valid = cv2.warpPerspective(np.full((h, w), 255, np.uint8), T @ H, size, flags=cv2.INTER_NEAREST)
    return out, valid, T


# ---------------------------------------------------------------------------
# 3 Segmentierung
# ---------------------------------------------------------------------------

def segment(rect, valid, T, px_per_mm):
    lab = cv2.cvtColor(rect, cv2.COLOR_BGR2LAB).astype(np.float32)
    lab = cv2.GaussianBlur(lab, (0, 0), 1.5 * px_per_mm)
    v = valid > 0
    # Kartenbereich (mm 0..100) ausblenden
    card = np.zeros(valid.shape, np.uint8)
    cpts = np.float32([[-8, -8], [108, -8], [108, 108], [-8, 108]])
    cpx = (np.c_[cpts, np.ones(4)] @ T.T)[:, :2]
    cv2.fillPoly(card, [np.int32(cpx)], 255)
    # Hintergrundfarbe vom Bildrand (gültiger Bereich) schätzen
    er = cv2.erode(valid, np.ones((15, 15), np.uint8))
    border = (er > 0) & (cv2.erode(er, np.ones((int(40 * px_per_mm),) * 2, np.uint8)) == 0)
    bg = np.median(lab[border], axis=0)
    dist = np.linalg.norm(lab - bg, axis=2)
    dist[~v] = 0
    dist[card > 0] = 0
    d8 = np.clip(dist / max(dist.max(), 1) * 255, 0, 255).astype(np.uint8)
    thr, m = cv2.threshold(d8[v], 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    mask = ((d8 > thr) & v & (card == 0)).astype(np.uint8) * 255
    k = max(3, int(3 * px_per_mm) | 1)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((k, k), np.uint8))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((k, k), np.uint8))
    n, labels, stats, _ = cv2.connectedComponentsWithStats(mask)
    if n < 2:
        raise MeasureError("Kleidungsstück nicht vom Hintergrund zu trennen – bitte auf "
                           "einfarbigen, kontrastreichen Untergrund legen.")
    best = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
    mask = (labels == best).astype(np.uint8) * 255
    # Löcher füllen
    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    filled = np.zeros_like(mask)
    cv2.drawContours(filled, cnts, -1, 255, -1)
    return filled, max(cnts, key=cv2.contourArea)


def upright(mask, rect, px_per_mm):
    """Kleidungsstück so drehen, dass die Längsachse senkrecht steht und der Bund oben ist."""
    ys, xs = np.nonzero(mask)
    pts = np.stack([xs, ys], 1).astype(np.float32)
    mean = pts.mean(axis=0)
    cov = np.cov((pts - mean).T)
    evals, evecs = np.linalg.eigh(cov)
    major = evecs[:, np.argmax(evals)]
    ang = math.degrees(math.atan2(major[1], major[0])) - 90.0
    while ang > 45:
        ang -= 90
    while ang < -45:
        ang += 90
    # nur sinnvolle Drehung, wenn das Teil deutlich schräg liegt
    h, w = mask.shape
    diag = int(math.hypot(h, w)) + 4
    M = cv2.getRotationMatrix2D((float(mean[0]), float(mean[1])), ang, 1.0)
    M[0, 2] += diag / 2 - mean[0]
    M[1, 2] += diag / 2 - mean[1]
    mr = cv2.warpAffine(mask, M, (diag, diag), flags=cv2.INTER_NEAREST)
    rr = cv2.warpAffine(rect, M, (diag, diag), flags=cv2.INTER_LINEAR)
    # Bund oben? Unten müssen zwei Beine (zwei Läufe) sein
    def runs_at(m, frac):
        ys_, = np.nonzero(m.any(axis=1))
        y = int(ys_[0] + (ys_[-1] - ys_[0]) * frac)
        row = m[y] > 0
        return int(np.sum(np.diff(row.astype(np.int8)) == 1))
    if runs_at(mr, 0.92) < runs_at(mr, 0.08):
        M2 = cv2.getRotationMatrix2D((diag / 2, diag / 2), 180, 1.0)
        mr = cv2.warpAffine(mr, M2, (diag, diag), flags=cv2.INTER_NEAREST)
        rr = cv2.warpAffine(rr, M2, (diag, diag), flags=cv2.INTER_LINEAR)
        ang += 180
    return mr, rr, ang


# ---------------------------------------------------------------------------
# 4 Messen: Hose
# ---------------------------------------------------------------------------

def _row_runs(row):
    r = np.concatenate([[0], (row > 0).astype(np.int8), [0]])
    d = np.diff(r)
    return list(zip(np.nonzero(d == 1)[0], np.nonzero(d == -1)[0]))


def _seam_from_profile(gray, mask, y_from, y_to, x_from=None, x_to=None, px_per_mm=2.0):
    """Waagerechte Nahtlinie: Zeile mit stärkstem vertikalem Gradienten im Bereich."""
    y_from, y_to = int(max(y_from, 0)), int(min(y_to, gray.shape[0] - 1))
    if y_to <= y_from + 3:
        return None, 0.0
    g = cv2.Sobel(cv2.GaussianBlur(gray, (0, 0), 1.0), cv2.CV_32F, 0, 1, ksize=3)
    inner = cv2.erode(mask, np.ones((int(6 * px_per_mm),) * 2, np.uint8)) > 0
    sl = slice(x_from, x_to)
    prof = []
    for y in range(y_from, y_to):
        m = inner[y, sl]
        prof.append(np.mean(np.abs(g[y, sl][m])) if m.sum() > 10 else 0.0)
    prof = np.array(prof)
    if prof.max() <= 0:
        return None, 0.0
    i = int(np.argmax(prof))
    base = np.median(prof)
    return y_from + i, float(prof[i] / max(base, 1e-6))


def measure_pants(mask, img, px_per_mm):
    s = px_per_mm
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    rows = np.nonzero(mask.any(axis=1))[0]
    top, bottom = int(rows[0]), int(rows[-1])
    # Schrittpunkt: höchster Punkt der Lücke zwischen den Beinen (Hintergrund von unten)
    cols = np.nonzero(mask.any(axis=0))[0]
    xl, xr = int(cols[0]), int(cols[-1])
    y_start, runs = None, []
    for y in range(bottom - 2, top + (bottom - top) // 3, -2):
        rr = [r for r in _row_runs(mask[y]) if r[1] - r[0] > 20 * s]
        if len(rr) >= 2:
            y_start, runs = y - int(10 * s), rr
            break
    if y_start is None:
        raise MeasureError("Hosenbeine unten nicht getrennt erkennbar – Beine leicht auseinanderlegen.")
    runs = sorted(runs, key=lambda r: r[1] - r[0], reverse=True)[:2]
    runs.sort()
    seed = ((runs[0][1] + runs[1][0]) // 2, y_start)
    # Hintergrund "zwischen" Stoff: links und rechts davon liegt in derselben Zeile Stoff
    m = mask > 0
    left_any = np.maximum.accumulate(m, axis=1)
    right_any = np.maximum.accumulate(m[:, ::-1], axis=1)[:, ::-1]
    between = ((~m) & left_any & right_any).astype(np.uint8)
    n_, lab_ = cv2.connectedComponents(between)
    lid = lab_[seed[1], seed[0]]
    if lid == 0:
        raise MeasureError("Schrittpunkt nicht gefunden.")
    gy, gx = np.nonzero(lab_ == lid)
    k = int(np.argmin(gy))
    crotch = (int(np.median(gx[gy == gy[k]])), int(gy[k]))
    # Verfeinern: Innenkanten der Beine (knapp unterhalb der Lückenspitze) als Geraden
    # nach oben verlängern; ihr Schnittpunkt ist der Schrittpunkt (Unschärfe/Morphologie
    # schließen die Spitze der Lücke sonst um einige mm).
    ys_fit, xl_fit, xr_fit = [], [], []
    comp = lab_ == lid
    for y in range(int(crotch[1] + 2 * s), int(crotch[1] + 45 * s)):
        xs_ = np.nonzero(comp[y])[0]
        if len(xs_) >= 2:
            ys_fit.append(y)
            xl_fit.append(xs_.min())
            xr_fit.append(xs_.max())
    if len(ys_fit) > 10:
        ys_a = np.array(ys_fit, float)
        wid = np.array(xr_fit, float) - np.array(xl_fit, float)
        mid = (np.array(xr_fit, float) + np.array(xl_fit, float)) / 2
        c2 = np.polyfit(ys_a, wid, 2)
        roots = np.roots(c2)
        roots = [r.real for r in roots if abs(r.imag) < 1e-6 and crotch[1] - 40 * s < r.real <= crotch[1] + 1]
        if roots:
            yc = max(roots)
            xc_ = np.polyval(np.polyfit(ys_a, mid, 1), yc)
            crotch = (int(round(xc_)), int(round(yc)))
    front_rise = (crotch[1] - top) / s
    # Bundnaht oben
    wb_y, wb_q = _seam_from_profile(gray, mask, top + 8 * s, top + min(110 * s, (crotch[1] - top) * 0.45),
                                    px_per_mm=s)
    wb_h = (wb_y - top) / s if (wb_y is not None and wb_q > 2.5) else 0.0
    def width_at(y):
        rr = _row_runs(mask[int(y)])
        return (max(r[1] for r in rr) - min(r[0] for r in rr)) / s if rr else 0.0
    waist_flat = np.median([width_at(top + (wb_h * s if wb_h else 30 * s) * f) for f in (0.3, 0.5, 0.7)])
    hip_y = top + (wb_h + 0.55 * (front_rise - wb_h)) * s
    hip_flat = width_at(hip_y)
    # Beine einzeln, an der eigenen Achse ausgerichtet
    legs = []
    for side in (-1, 1):
        lm = np.zeros_like(mask)
        if side < 0:
            lm[crotch[1]:, :crotch[0]] = mask[crotch[1]:, :crotch[0]]
        else:
            lm[crotch[1]:, crotch[0]:] = mask[crotch[1]:, crotch[0]:]
        ys, xs = np.nonzero(lm)
        lower = ys > crotch[1] + 0.25 * (bottom - crotch[1])
        pts = np.stack([xs[lower], ys[lower]], 1).astype(np.float64)
        mean = pts.mean(axis=0)
        evals, evecs = np.linalg.eigh(np.cov((pts - mean).T))
        u = evecs[:, np.argmax(evals)]
        if u[1] < 0:
            u = -u
        ang = math.degrees(math.atan2(u[0], u[1]))      # Abweichung von senkrecht
        M = cv2.getRotationMatrix2D((float(crotch[0]), float(crotch[1])), -ang, 1.0)
        lr = cv2.warpAffine(lm, M, mask.shape[::-1], flags=cv2.INTER_NEAREST)
        gr = cv2.warpAffine(gray, M, mask.shape[::-1], flags=cv2.INTER_LINEAR)
        lrows = np.nonzero(lr.any(axis=1))[0]
        lb = int(lrows[-1])
        inseam = (lb - crotch[1]) / s
        def lw(y):
            rr = _row_runs(lr[int(y)])  # noqa: B023 - called within the same iteration
            return (max(r[1] for r in rr) - min(r[0] for r in rr)) / s if rr else 0.0
        # Oberschenkel: senkrecht zur Beinachse, 2,5 cm unter dem Schritt
        lm2 = np.zeros_like(mask)
        y_up = int(crotch[1] - 60 * s)
        if side < 0:
            lm2[y_up:, :crotch[0]] = mask[y_up:, :crotch[0]]
        else:
            lm2[y_up:, crotch[0]:] = mask[y_up:, crotch[0]:]
        lr2 = cv2.warpAffine(lm2, M, mask.shape[::-1], flags=cv2.INTER_NEAREST)
        thigh = 0.0
        rr = _row_runs(lr2[int(crotch[1] + 25 * s)])
        if rr:
            thigh = (max(r[1] for r in rr) - min(r[0] for r in rr)) / s
        cy0, cq0 = _seam_from_profile(gr, lr, lb - 160 * s, lb - 15 * s, px_per_mm=s)
        cuff_px = (lb - cy0) if (cy0 is not None and cq0 > 2.5) else 0
        knee = lw(crotch[1] + 0.5 * (lb - cuff_px - crotch[1]))
        opening = float(np.median([lw(lb - f * s) for f in (4, 6, 8, 10, 12)]))
        cy, cq = _seam_from_profile(gr, lr, lb - 160 * s, lb - 15 * s, px_per_mm=s)
        cuff_h = (lb - cy) / s if (cy is not None and cq > 2.5) else 0.0
        legs.append(dict(inseam=inseam, thigh=thigh, knee=knee, opening=opening, cuff_h=cuff_h, angle=ang,
                         bottom=lb, M=M))
    def avg(k):
        return float(np.mean([l[k] for l in legs]))
    res = dict(
        waist_flat=float(waist_flat), hip_flat=float(hip_flat), thigh_flat=avg("thigh"), knee_flat=avg("knee"),
        opening_flat=avg("opening"), front_rise=float(front_rise), inseam=avg("inseam"),
        outseam=float(front_rise + avg("inseam")), waistband_h=float(wb_h), cuff_h=avg("cuff_h"),
        leg_splay_deg=avg("angle") if False else float(np.mean([abs(l["angle"]) for l in legs])),
    )
    geo = dict(top=top, bottom=bottom, crotch=crotch, hip_y=hip_y, wb_y=top + wb_h * s, legs=legs, xl=xl, xr=xr)
    # Plausibilität
    warn = []
    if abs(legs[0]["inseam"] - legs[1]["inseam"]) > 15:
        warn.append("Beinlängen links/rechts weichen > 1,5 cm ab – Hose glattstreichen?")
    if wb_h == 0:
        warn.append("Bundnaht nicht sicher erkannt – Bundhöhe bitte per Maßband angeben.")
    return res, geo, warn


# ---------------------------------------------------------------------------
# 5 Overlay
# ---------------------------------------------------------------------------

LABELS = {
    "waist_flat": "Bund (flach)", "hip_flat": "Hüfte (flach)", "thigh_flat": "Oberschenkel (flach)", "knee_flat": "Beinweite Mitte (flach)",
    "opening_flat": "Beinöffnung (flach)", "front_rise": "Leibhöhe vorne", "inseam": "Innenbein",
    "outseam": "Seitenlänge", "waistband_h": "Bundhöhe", "cuff_h": "Bündchenhöhe",
}


def overlay(img, mask, cnt, geo, res, px_per_mm, path):
    from PIL import Image, ImageDraw, ImageFont
    s = px_per_mm
    vis = img.copy()
    cv2.drawContours(vis, [cnt] if cnt is not None else cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[0],
                     -1, (40, 200, 40), max(2, int(s)))
    top, crotch = geo["top"], geo["crotch"]
    lw = max(2, int(s))
    red, blue = (40, 40, 220), (200, 90, 20)
    def hline(y, color):
        rr = _row_runs(mask[int(y)])
        if rr:
            cv2.line(vis, (int(min(r[0] for r in rr)), int(y)), (int(max(r[1] for r in rr)), int(y)), color, lw)
    hline(geo["hip_y"], red)
    if res["waistband_h"]:
        hline(geo["wb_y"], blue)
    cv2.line(vis, (crotch[0], top), (crotch[0], crotch[1]), red, lw)
    cv2.circle(vis, crotch, int(6 * s), (0, 0, 255), lw)
    for l in geo["legs"]:
        Mi = cv2.invertAffineTransform(l["M"])
        p0 = Mi @ np.array([crotch[0], crotch[1], 1.0])
        p1 = Mi @ np.array([crotch[0], l["bottom"], 1.0])
        cv2.line(vis, tuple(np.int32(p0)), tuple(np.int32(p1)), (0, 140, 255), lw)
    scale = min(1.0, 1600 / max(vis.shape[:2]))
    vis = cv2.resize(vis, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    pil = Image.fromarray(cv2.cvtColor(vis, cv2.COLOR_BGR2RGB))
    d = ImageDraw.Draw(pil)
    font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "fonts", "DejaVuSans.ttf")
    f = ImageFont.truetype(font_path, 22)
    lines = ["Erkannte Maße (bitte prüfen):"] + [f"{LABELS[k]}: {v / 10:.1f} cm".replace(".", ",")
                                                 for k, v in res.items() if k in LABELS]
    box_w = 420
    d.rectangle([8, 8, 8 + box_w, 16 + 28 * len(lines)], fill=(255, 255, 255))
    for i, t in enumerate(lines):
        d.text((16, 12 + 28 * i), t, fill=(0, 0, 0), font=f)
    pil.save(path)
    return path


# ---------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------

def measure(image, garment="hose", px_per_mm=2.0, overlay_path=None, manual_ref=None, tape=None):
    """Hauptfunktion. image: Pfad oder BGR-Array. tape: Maßband-Werte in cm (Vorrang)."""
    img = cv2.imread(image) if isinstance(image, str) else image
    if img is None:
        raise MeasureError(f"Bild nicht lesbar: {image}")
    H, ref_info = homography(img, manual_ref)
    rect, valid, T = rectify(img, H, px_per_mm)
    mask, cnt = segment(rect, valid, T, px_per_mm)
    mask_u, rect_u, ang = upright(mask, rect, px_per_mm)
    if garment in ("hose", "pants", "pants_basic"):
        res, geo, warn = measure_pants(mask_u, rect_u, px_per_mm)
    elif garment in ("oberteil", "tshirt", "tshirt_basic", "hoodie"):
        res, geo, warn = measure_top(mask_u, rect_u, px_per_mm)
    else:
        raise MeasureError(f"Messung für '{garment}' nicht unterstützt (hose, oberteil).")
    source = {k: "Foto" for k in res}
    for k, v in (tape or {}).items():
        res[k] = float(v) * 10
        source[k] = "Maßband"
    if overlay_path:
        overlay(rect_u, mask_u, None, geo, res, px_per_mm, overlay_path)
    return dict(measures_mm=res, source=source, reference=ref_info, warnings=warn,
                rotation_deg=ang, px_per_mm=px_per_mm)


# ---------------------------------------------------------------------------
# Oberteil (T-Shirt/Hoodie): Breite, Länge, Ärmel
# ---------------------------------------------------------------------------

def measure_top(mask, img, px_per_mm):
    """T-Shirt flach, Ärmel seitlich ausgebreitet. Maße flach (eine Lage)."""
    s = px_per_mm
    rows = np.nonzero(mask.any(axis=1))[0]
    top, bottom = int(rows[0]), int(rows[-1])
    widths, spans = [], []
    for y in range(top, bottom + 1):
        rr = _row_runs(mask[y])
        widths.append((max(r[1] for r in rr) - min(r[0] for r in rr)) if rr else 0)
        spans.append(rr)
    widths = np.array(widths) / s
    cols = np.nonzero(mask.any(axis=0))[0]
    xc = (cols[0] + cols[-1]) / 2
    # Rumpfbreite unten (Saum) und Länge
    hem_w = float(np.median(widths[-int(15 * s):-int(5 * s)]))
    # Achselpunkt: von unten nach oben, wo die Breite sprunghaft zunimmt (Ärmel beginnen)
    body_w = []
    for y in range(bottom, top, -1):
        rr = _row_runs(mask[y])
        c = [r for r in rr if r[0] <= xc <= r[1]]
        body_w.append((c[0][1] - c[0][0]) / s if c else 0)
    body_w = np.array(body_w)
    full_w = widths[::-1][:len(body_w)]
    jump = np.nonzero(full_w > body_w + 30)[0]
    if len(jump) == 0:
        raise MeasureError("Ärmel nicht erkannt – Ärmel seitlich ausbreiten.")
    underarm_y = bottom - int(jump[0])
    chest_flat = float(np.median(body_w[max(0, jump[0] - int(30 * s)):jump[0] - int(20 * s)]))
    length = (bottom - top) / s
    res = dict(chest_flat=chest_flat, hem_flat=hem_w, length=length,
               underarm_from_top=(underarm_y - top) / s, span=float(widths.max()))
    return res, dict(top=top, bottom=bottom, underarm=underarm_y), []


def main(argv=None):
    ap = argparse.ArgumentParser(description="Kleidungsstück aus Foto vermessen (Modus B)")
    ap.add_argument("image")
    ap.add_argument("--type", default="hose")
    ap.add_argument("--out", default="messung")
    ap.add_argument("--tape", help='Maßband-Werte in cm als JSON, z. B. {"inseam": 48}')
    a = ap.parse_args(argv)
    os.makedirs(a.out, exist_ok=True)
    r = measure(a.image, a.type, overlay_path=os.path.join(a.out, "overlay.png"),
                tape=json.loads(a.tape) if a.tape else None)
    with open(os.path.join(a.out, "messung.json"), "w", encoding="utf-8") as f:
        json.dump(r, f, ensure_ascii=False, indent=2, default=float)
    for k, v in r["measures_mm"].items():
        print(f"{LABELS.get(k, k)}: {v / 10:.1f} cm ({r['source'][k]})")
    for w in r["warnings"]:
        print("Hinweis:", w)


if __name__ == "__main__":
    main()
