"""Photo mode B: garment photographed flat → measurements in mm.

Steps:
  1. Detect the reference (ArUco reference card, 4 markers) → homography image → mm plane
     (alternatively: 4 points of a known rectangle / folding ruler via `manual_ref`).
  2. Rectify the image (top view, `px_per_mm` pixels per mm).
  3. Segment the garment (distance to the background colour, Otsu, morphology),
     mask out the card, take the largest contour.
  4. Derive measurements (pants: waist, hip, thigh, leg opening, lengths, rise,
     waistband/cuff height via seam line detection).
  5. Overlay PNG with contour and measuring lines for the user to confirm.

All widths are **measured flat (one layer)**; conversion to circumferences (×2) happens
in reverse/unfold.py. Values the user measures with a tape measure take precedence.

CLI:  python photo_measure.py photo.jpg --type pants --out measurement
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
import flatlay as FL  # noqa: E402
import refcard  # noqa: E402


class MeasureError(Exception):
    pass


# ---------------------------------------------------------------------------
# 1–2 Reference and rectification
# ---------------------------------------------------------------------------

def detect_card(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if img.ndim == 3 else img
    params = cv2.aruco.DetectorParameters()
    params.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_SUBPIX
    det = cv2.aruco.ArucoDetector(cv2.aruco.getPredefinedDictionary(refcard.DICT_ID), params)
    corners, ids, _ = det.detectMarkers(gray)
    if ids is None:
        raise MeasureError("Reference card not found. Please place the whole card flat and "
                           "uncovered in the picture (or give folding-ruler measurements).")
    ref = refcard.marker_corners_mm()
    img_pts, mm_pts = [], []
    found = []
    for c, i in zip(corners, ids.ravel()):
        if int(i) in ref:
            img_pts.append(c.reshape(4, 2))
            mm_pts.append(ref[int(i)])
            found.append(int(i))
    if not found:
        raise MeasureError("No markers of the reference card detected.")
    return np.vstack(img_pts), np.vstack(mm_pts), sorted(found)


def homography(img, manual_ref=None, prefer_affine=False):
    """Homography image pixels → mm (card plane). manual_ref: dict(img=[[x,y]*4], mm=[[x,y]*4])."""
    if manual_ref:
        ip = np.float32(manual_ref["img"])
        mp = np.float32(manual_ref["mm"])
        H, _ = cv2.findHomography(ip, mp)
        return H, dict(method="manual", markers=[])
    ip, mp, found = detect_card(img)
    H, inl = cv2.findHomography(ip, mp, cv2.RANSAC if len(ip) > 4 else 0, 1.0)
    # residual error on the card
    proj = cv2.perspectiveTransform(ip.reshape(-1, 1, 2), H).reshape(-1, 2)
    err = float(np.sqrt(np.mean(np.sum((proj - mp) ** 2, axis=1))))
    if len(found) < 2:
        note = "only one marker detected: accuracy is limited"
    else:
        note = ""
    if prefer_affine:
        # a 10 cm card cannot pin down the perspective of a garment 1.5 m wide: when the card
        # looks frontal (an affine map fits it as well), use the affine map, whose errors grow
        # only linearly with the distance from the card
        A, _ = cv2.estimateAffine2D(ip, mp, method=cv2.LMEDS)
        if A is not None:
            pa = ip @ A[:, :2].T + A[:, 2]
            err_a = float(np.sqrt(np.mean(np.sum((pa - mp) ** 2, axis=1))))
            if err_a < max(0.35, 1.5 * err):
                return np.vstack([A, [0, 0, 1]]), dict(method="reference card (affine)", markers=found,
                                                      rms_mm=err_a, note=note)
    return H, dict(method="reference card", markers=found, rms_mm=err, note=note)


def rectify(img, H, px_per_mm=2.0, max_side_mm=2500):
    """Top view on a mm grid. Returns: image, validity mask, matrix mm→px of the result image."""
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
# 3 Segmentation
# ---------------------------------------------------------------------------

def segment(rect, valid, T, px_per_mm, clean_mm=0.0):
    lab = cv2.cvtColor(rect, cv2.COLOR_BGR2LAB).astype(np.float32)
    lab = cv2.GaussianBlur(lab, (0, 0), 1.5 * px_per_mm)
    v = valid > 0
    # hide the card area (mm 0..100)
    card = np.zeros(valid.shape, np.uint8)
    cpts = np.float32([[-8, -8], [108, -8], [108, 108], [-8, 108]])
    cpx = (np.c_[cpts, np.ones(4)] @ T.T)[:, :2]
    cv2.fillPoly(card, [np.int32(cpx)], 255)
    # estimate the background colour from the image border (valid area)
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
        raise MeasureError("Cannot separate the garment from the background. Please lay it on a "
                           "plain, high-contrast surface.")
    best = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
    mask = (labels == best).astype(np.uint8) * 255
    if clean_mm > 0:
        # hysteresis: keep only what is reachable from clearly-garment pixels (removes background
        # patches whose colour drifts towards the garment), then open with a large disc and give
        # back the original edge within reach of the opened shape
        hi = (d8 > thr + 0.5 * (np.median(d8[mask > 0]) - thr)).astype(np.uint8) * 255
        hi = cv2.morphologyEx(hi, cv2.MORPH_CLOSE, np.ones((k, k), np.uint8))
        grow = cv2.dilate(hi, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)),
                          iterations=max(1, int(2 * px_per_mm)))
        mask = cv2.bitwise_and(mask, grow)
        kk = max(3, int(clean_mm * px_per_mm) | 1)
        disc = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kk, kk))
        core = cv2.morphologyEx(mask, cv2.MORPH_OPEN, disc)
        reach = cv2.dilate(core, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)), iterations=max(1, kk // 2))
        mask = cv2.bitwise_and(mask, reach)
        n2, lab2, st2, _ = cv2.connectedComponentsWithStats(mask)
        mask = (lab2 == 1 + int(np.argmax(st2[1:, cv2.CC_STAT_AREA]))).astype(np.uint8) * 255
    # fill holes
    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    filled = np.zeros_like(mask)
    cv2.drawContours(filled, cnts, -1, 255, -1)
    return filled, max(cnts, key=cv2.contourArea)


def _symmetry_angle(mask, centre):
    """Rotation (degrees, ±45) that makes the garment mirror-symmetric about a vertical axis."""
    f = 300.0 / max(mask.shape)
    small = cv2.resize(mask, None, fx=f, fy=f, interpolation=cv2.INTER_AREA)
    c = (float(centre[0] * f), float(centre[1] * f))
    h, w = small.shape
    d = int(math.hypot(h, w)) + 4

    def score(a):
        M = cv2.getRotationMatrix2D(c, a, 1.0)
        M[0, 2] += d / 2 - c[0]
        M[1, 2] += d / 2 - c[1]
        r = cv2.warpAffine(small, M, (d, d)).astype(np.float32) / 255
        cols = np.nonzero(r.sum(axis=0) > 0)[0]
        xm = (r.sum(axis=0) * np.arange(d)).sum() / max(r.sum(), 1)
        sh = int(round(2 * xm - (d - 1)))
        fl = np.roll(r[:, ::-1], sh, axis=1)
        return float((r * fl).sum() / max(r.sum(), 1)) if len(cols) else 0.0

    best = max(np.arange(-45, 45.5, 3.0), key=score)
    best = max(np.arange(best - 3, best + 3.01, 0.5), key=score)
    return float(best)


def upright(mask, rect, px_per_mm, top=False):
    """Rotate the garment so that its long axis is vertical and the waistband is at the top."""
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
    # fold the angle into ±45° so only a real tilt is corrected
    if top:
        ang = _symmetry_angle(mask, mean)     # tops are nearly square: use the mirror axis
    h, w = mask.shape
    diag = int(math.hypot(h, w)) + 4
    M = cv2.getRotationMatrix2D((float(mean[0]), float(mean[1])), ang, 1.0)
    M[0, 2] += diag / 2 - mean[0]
    M[1, 2] += diag / 2 - mean[1]
    mr = cv2.warpAffine(mask, M, (diag, diag), flags=cv2.INTER_NEAREST)
    rr = cv2.warpAffine(rect, M, (diag, diag), flags=cv2.INTER_LINEAR)
    # waistband at the top? The bottom must show two legs (two runs)
    def runs_at(m, frac):
        ys_, = np.nonzero(m.any(axis=1))
        y = int(ys_[0] + (ys_[-1] - ys_[0]) * frac)
        row = m[y] > 0
        return int(np.sum(np.diff(row.astype(np.int8)) == 1))
    def width_at(m, frac):
        ys_, = np.nonzero(m.any(axis=1))
        y = int(ys_[0] + (ys_[-1] - ys_[0]) * frac)
        xs_, = np.nonzero(m[y])
        return int(xs_[-1] - xs_[0]) if len(xs_) else 0
    # pants: the bottom shows two legs; tops: the sleeves (widest part) are at the top
    flip = (width_at(mr, 0.15) < width_at(mr, 0.9)) if top else (runs_at(mr, 0.92) < runs_at(mr, 0.08))
    if flip:
        M2 = cv2.getRotationMatrix2D((diag / 2, diag / 2), 180, 1.0)
        mr = cv2.warpAffine(mr, M2, (diag, diag), flags=cv2.INTER_NEAREST)
        rr = cv2.warpAffine(rr, M2, (diag, diag), flags=cv2.INTER_LINEAR)
        ang += 180
    if top:
        # fine-tune: the centre line of the body (below the sleeves) must be vertical
        def warp(a):
            M_ = cv2.getRotationMatrix2D((float(mean[0]), float(mean[1])), a, 1.0)
            M_[0, 2] += diag / 2 - mean[0]
            M_[1, 2] += diag / 2 - mean[1]
            return M_
        a0 = _midline_slope(mr)
        if a0 is not None and abs(a0) > 1e-4:
            dlt = math.degrees(math.atan(a0))
            cands = []
            for a in (ang + dlt, ang - dlt):
                m_ = cv2.warpAffine(mask, warp(a), (diag, diag), flags=cv2.INTER_NEAREST)
                sl = _midline_slope(m_)
                cands.append((abs(sl) if sl is not None else 1e9, a, m_))
            sl_best, a_best, m_best = min(cands, key=lambda c: c[0])
            if sl_best < abs(a0):
                ang, mr = a_best, m_best
                rr = cv2.warpAffine(rect, warp(ang), (diag, diag), flags=cv2.INTER_LINEAR)
    return mr, rr, ang


def _midline_slope(m):
    """Slope dx/dy of the centre of the widest run per row, 55–92 % of the height (top body)."""
    ys_, = np.nonzero(m.any(axis=1))
    if len(ys_) < 20:
        return None
    y0, y1 = ys_[0], ys_[-1]
    yy, mids = [], []
    for y in range(int(y0 + 0.55 * (y1 - y0)), int(y0 + 0.92 * (y1 - y0))):
        rr = _row_runs(m[y])
        if rr:
            a, b = max(rr, key=lambda r: r[1] - r[0])
            yy.append(y)
            mids.append((a + b) / 2)
    if len(yy) < 10:
        return None
    return float(np.polyfit(np.asarray(yy, float), np.asarray(mids, float), 1)[0])


# ---------------------------------------------------------------------------
# 4 Measuring: pants
# ---------------------------------------------------------------------------

def _row_runs(row):
    r = np.concatenate([[0], (row > 0).astype(np.int8), [0]])
    d = np.diff(r)
    return list(zip(np.nonzero(d == 1)[0], np.nonzero(d == -1)[0]))


def _seam_from_profile(gray, mask, y_from, y_to, x_from=None, x_to=None, px_per_mm=2.0):
    """Horizontal seam line: the row with the strongest vertical gradient in the range."""
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


def _hem_angle(lm, crotch) -> float:
    """Leg rotation (degrees, as used for the principal axis) that makes the hem edge horizontal."""
    ys, xs = np.nonzero(lm)
    cols = np.unique(xs)
    if len(cols) < 10:
        return 0.0
    bot = np.array([ys[xs == c].max() for c in cols], float)
    lo, hi = np.percentile(cols, [20, 80])
    sel = (cols >= lo) & (cols <= hi)
    best = (1e18, 0.0)
    for cand in np.linspace(-25, 25, 101):
        M = cv2.getRotationMatrix2D((float(crotch[0]), float(crotch[1])), -cand, 1.0)
        p = np.stack([cols[sel], bot[sel], np.ones(sel.sum())], 1) @ M.T
        spread = float(np.ptp(p[:, 1]))
        if spread < best[0]:
            best = (spread, float(cand))
    return best[1]


def measure_pants(mask, img, px_per_mm):
    s = px_per_mm
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    rows = np.nonzero(mask.any(axis=1))[0]
    top, bottom = int(rows[0]), int(rows[-1])
    # crotch point: highest point of the gap between the legs (background from below)
    cols = np.nonzero(mask.any(axis=0))[0]
    xl, xr = int(cols[0]), int(cols[-1])
    y_start, runs = None, []
    for y in range(bottom - 2, top + (bottom - top) // 3, -2):
        rr = [r for r in _row_runs(mask[y]) if r[1] - r[0] > 20 * s]
        if len(rr) >= 2:
            y_start, runs = y - int(10 * s), rr
            break
    if y_start is None:
        raise MeasureError("The legs cannot be told apart at the bottom. Please spread the legs slightly.")
    runs = sorted(runs, key=lambda r: r[1] - r[0], reverse=True)[:2]
    runs.sort()
    seed = ((runs[0][1] + runs[1][0]) // 2, y_start)
    # background "between" fabric: there is fabric left and right of it in the same row
    m = mask > 0
    left_any = np.maximum.accumulate(m, axis=1)
    right_any = np.maximum.accumulate(m[:, ::-1], axis=1)[:, ::-1]
    between = ((~m) & left_any & right_any).astype(np.uint8)
    n_, lab_ = cv2.connectedComponents(between)
    lid = lab_[seed[1], seed[0]]
    if lid == 0:
        raise MeasureError("Crotch point not found.")
    gy, gx = np.nonzero(lab_ == lid)
    k = int(np.argmin(gy))
    crotch = (int(np.median(gx[gy == gy[k]])), int(gy[k]))
    # Refine: extend the inner leg edges (just below the tip of the gap) upwards as
    # straight lines; their intersection is the crotch point (blur/morphology would
    # otherwise close the tip of the gap by a few mm).
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
    # waistband seam at the top
    wb_y, wb_q = _seam_from_profile(gray, mask, top + 8 * s, top + min(110 * s, (crotch[1] - top) * 0.45),
                                    px_per_mm=s)
    wb_h = (wb_y - top) / s if (wb_y is not None and wb_q > 2.5) else 0.0
    def width_at(y):
        rr = _row_runs(mask[int(y)])
        return (max(r[1] for r in rr) - min(r[0] for r in rr)) / s if rr else 0.0
    # without a detected waistband: the top 3 cm (small garments: the top fifth of the rise)
    wb_ref = wb_h if wb_h else min(30.0, 0.2 * front_rise)
    waist_flat = np.median([width_at(top + wb_ref * s * f) for f in (0.3, 0.5, 0.7)])
    hip_y = top + (wb_h + 0.55 * (front_rise - wb_h)) * s
    hip_flat = width_at(hip_y)
    # legs one by one, aligned to their own axis
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
        ang = math.degrees(math.atan2(u[0], u[1]))      # deviation from vertical
        if evals.max() < 3.0 * evals.min():
            # short, wide leg (doll clothes, shorts): the principal axis is undefined; turn
            # the leg so that its hem edge is horizontal instead
            ang = _hem_angle(lm, crotch)
        M = cv2.getRotationMatrix2D((float(crotch[0]), float(crotch[1])), -ang, 1.0)
        lr = cv2.warpAffine(lm, M, mask.shape[::-1], flags=cv2.INTER_NEAREST)
        gr = cv2.warpAffine(gray, M, mask.shape[::-1], flags=cv2.INTER_LINEAR)
        lrows = np.nonzero(lr.any(axis=1))[0]
        lb = int(lrows[-1])
        inseam = (lb - crotch[1]) / s
        def lw(y):
            rr = _row_runs(lr[int(y)])  # noqa: B023 - called within the same iteration
            return (max(r[1] for r in rr) - min(r[0] for r in rr)) / s if rr else 0.0
        # thigh: perpendicular to the leg axis, 2.5 cm below the crotch
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
    # plausibility
    warn = []
    if abs(legs[0]["inseam"] - legs[1]["inseam"]) > 15:
        warn.append("Left/right leg lengths differ by more than 1.5 cm. Smooth the pants out?")
    if wb_h == 0:
        warn.append("Waistband seam not detected reliably. Please measure the waistband height with a tape measure.")
    return res, geo, warn


# ---------------------------------------------------------------------------
# 5 Overlay
# ---------------------------------------------------------------------------

LABELS = {
    "waist_flat": "Waist (flat)", "hip_flat": "Hip (flat)", "thigh_flat": "Thigh (flat)", "knee_flat": "Mid-leg width (flat)",
    "opening_flat": "Leg opening (flat)", "front_rise": "Front rise", "inseam": "Inseam",
    "outseam": "Outseam", "waistband_h": "Waistband height", "cuff_h": "Cuff height",
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
    lines = ["Detected measurements (please check):"] + [f"{LABELS[k]}: {v / 10:.1f} cm"
                                                 for k, v in res.items() if k in LABELS]
    box_w = 500
    d.rectangle([8, 8, 8 + box_w, 16 + 28 * len(lines)], fill=(255, 255, 255))
    for i, t in enumerate(lines):
        d.text((16, 12 + 28 * i), t, fill=(0, 0, 0), font=f)
    pil.save(path)
    return path


# ---------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------

def measure(image, garment="pants", px_per_mm=2.0, overlay_path=None, manual_ref=None, tape=None):
    """Main function. image: path or BGR array. tape: tape-measure values in cm (take precedence)."""
    img = cv2.imread(image) if isinstance(image, str) else image
    if img is None:
        raise MeasureError(f"Cannot read image: {image}")
    top = garment in ("top", "tshirt", "tshirt_basic", "hoodie")
    H, ref_info = homography(img, manual_ref, prefer_affine=top)
    rect, valid, T = rectify(img, H, px_per_mm)
    mask, cnt = segment(rect, valid, T, px_per_mm, clean_mm=10.0 if top else 0.0)
    mask_u, rect_u, ang = upright(mask, rect, px_per_mm, top=top)
    if garment in ("pants", "pants_basic"):
        res, geo, warn = measure_pants(mask_u, rect_u, px_per_mm)
    elif garment in ("top", "tshirt", "tshirt_basic", "hoodie"):
        res, geo, warn = measure_top_both(mask_u, rect_u, px_per_mm)
    else:
        raise MeasureError(f"Measuring '{garment}' is not supported (pants, top).")
    source = {k: "photo" for k in res if not k.startswith("_")}
    if top and tape and tape.get("chest_flat") and res.get("chest_flat"):
        # tops: the tape-measured chest width corrects the scale of every photo value (a
        # 10 cm card cannot pin the scale of a 1.5 m wide flat lay down to better than ~2 %)
        f = float(tape["chest_flat"]) * 10 / res["chest_flat"]
        for k in res:
            if not k.startswith("_"):
                res[k] *= f
        ref_info = dict(ref_info, scale_from_tape=f)
        if abs(f - 1) > 0.03:
            warn.append(f"The tape-measured chest width differs by {(f - 1) * 100:+.1f} % from the photo: "
                        "all photo values were scaled. Was the card printed at 100 %?")
    for k, v in (tape or {}).items():
        res[k] = float(v) * 10
        source[k] = "tape measure"
    if overlay_path:
        if top:
            if geo.get("mirrored"):
                rect_u, mask_u = (np.ascontiguousarray(a[:, ::-1]) for a in (rect_u, mask_u))
            overlay_top(rect_u, mask_u, geo, res, px_per_mm, overlay_path)
        else:
            overlay(rect_u, mask_u, None, geo, res, px_per_mm, overlay_path)
    return dict(measures_mm=res, source=source, reference=ref_info, warnings=warn,
                rotation_deg=ang, px_per_mm=px_per_mm)


# ---------------------------------------------------------------------------
# Top (T-shirt / raglan): body, sleeves, neckline (issue #4)
# ---------------------------------------------------------------------------

TOP_LABELS = {
    "chest_flat": "Chest width (flat)", "hem_flat": "Hem width (flat)", "length": "Length from the highest point",
    "armhole_depth": "Underarm depth", "neck_half": "Neck width (half)", "back_neck": "Back neck depth",
    "front_neck": "Front neck depth", "shoulder_x": "Shoulder point (from centre)",
    "shoulder_y": "Shoulder point (drop)", "sleeve_reach": "Sleeve reach (from centre line)",
    "bicep_flat": "Upper-arm width (flat)", "opening_flat": "Sleeve opening (flat)",
}


def _fit_line(x, y):
    A = np.stack([x, np.ones_like(x)], 1)
    sol, *_ = np.linalg.lstsq(A, y, rcond=None)
    r = y - A @ sol
    return sol, float(r @ r)


def measure_top(mask, img, px_per_mm):
    """T-shirt/raglan lying flat, front up, sleeves spread sideways. Everything in mm, measured
    flat; the reference is the highest point of the garment and the centre line. The feature
    set matches flatlay.top_flatlay, which the fit uses to reconstruct the pattern."""
    s = px_per_mm
    m = mask > 0
    gray = cv2.GaussianBlur(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32), (0, 0), 0.6 * s)
    rows = np.nonzero(m.any(axis=1))[0]
    top, bottom = int(rows[0]), int(rows[-1])
    H = bottom - top
    warn: list[str] = []
    # centre line from the body in the lower third
    mids = []
    for y in range(int(bottom - 0.3 * H), bottom - int(5 * s)):
        rr = _row_runs(m[y])
        if rr:
            a, b = max(rr, key=lambda r: r[1] - r[0])
            mids.append((a + b) / 2)
    xc = float(np.median(mids))

    def centre_run(y):
        rr = _row_runs(m[int(y)])
        for a, b in rr:
            if a <= xc <= b:
                return a, b
        return None

    # hem at the centre line (a slight shear of the photo tilts the hem: its corners do not count)
    xi0 = int(round(xc))
    bottom = int(np.nonzero(m[:, xi0 - int(s):xi0 + int(s) + 1].any(axis=1))[0][-1])
    hem_w = [r for r in (centre_run(y) for y in range(bottom - int(12 * s), bottom - int(8 * s))) if r]
    hem_flat = float(np.median([b - a for a, b in hem_w])) / s
    # reference: the highest point of the neck/shoulder area (a sleeve end may be higher when
    # the sleeves point slightly upwards or the photo is tilted)
    wz = int(FL.TOP_ZONE * hem_flat * s)
    top = int(np.nonzero(m[:, max(int(xc) - wz, 0):int(xc) + wz + 1].any(axis=1))[0][0])
    H = bottom - top
    length = H / s
    # underarm: going up, the right body edge jumps outwards where the sleeve begins
    edge = np.full(bottom + 1, np.nan)
    for y in range(top, bottom + 1):
        r = centre_run(y)
        if r:
            edge[y] = r[1]
    k = int(3 * s)
    u_est = None
    for y in range(bottom - int(20 * s), top + k, -1):
        if (not np.isnan(edge[y]) and not np.isnan(edge[y + k]) and not np.isnan(edge[y - 2 * k])
                and edge[y] - edge[y + k] > 2.0 * s and edge[y - 2 * k] - edge[y + k] > 5.0 * s):
            u_est = y + k
            break
    if u_est is None:
        raise MeasureError("Underarm not found. Please spread the sleeves out sideways.")
    ys = np.arange(u_est + int(8 * s), min(u_est + int(60 * s), bottom - int(20 * s)))
    ys = ys[~np.isnan(edge[ys])]
    (a_s, b_s), _ = _fit_line(ys.astype(float), edge[ys])          # side seam: x = a*y + b
    x_side = a_s * u_est + b_s
    # underside of the sleeve next to the underarm: lowest mask pixel of the sleeve per column
    xs_u, ys_u = [], []
    prev = float(u_est)
    for x in range(int(x_side + 3 * s), int(x_side + 25 * s)):
        col = m[:, x]
        runs = _row_runs(col)
        if not runs:
            break
        cand = [r for r in runs if r[0] < prev + 3 * s]
        if not cand:
            break
        bot = min((r[1] - 1 for r in cand), key=lambda v: abs(v - prev))
        xs_u.append(x)
        ys_u.append(bot)
        prev = bot
    if len(xs_u) < 5:
        raise MeasureError("Sleeve underside not found next to the underarm.")
    (c_u, d_u), _ = _fit_line(np.array(xs_u, float), np.array(ys_u, float))   # y = c*x + d
    Uy = (c_u * b_s + d_u) / (1 - c_u * a_s)
    Ux = a_s * Uy + b_s
    chest_w = [r for r in (centre_run(y) for y in range(int(Uy + 20 * s), int(Uy + 30 * s))) if r]
    chest_flat = float(np.median([b - a for a, b in chest_w])) / s
    # top contour (right half)
    cols = np.nonzero(m.any(axis=0))[0]
    x_max = int(cols[-1])
    y_top = np.full(m.shape[1], np.nan)
    for x in range(int(xc), x_max + 1):
        c = np.nonzero(m[:, x])[0]
        if len(c):
            y_top[x] = c[0]
    xi = int(round(xc))
    back_neck = (np.nanmedian(y_top[xi - int(s):xi + int(s) + 1]) - top) / s
    # front neckline: dark line below the back neck, traced from the centre outwards
    inner = cv2.erode(mask, np.ones((max(3, int(1 * s)),) * 2, np.uint8)) > 0
    level = float(np.median(gray[inner]))
    local = cv2.GaussianBlur(gray, (0, 0), 3 * s)
    dark = (gray < np.minimum(local, level) - max(8.0, 0.06 * level)) & inner
    y_start = int(top + back_neck * s + 2 * s)
    col = dark[y_start:int(Uy), xi]
    hits = np.nonzero(col)[0]
    front_neck = neck_half = None
    raglan = False
    style_conf = 0.0
    trace = []
    if len(hits):
        y_c = y_start + int(hits[0])
        front_neck = (y_c - top) / s
        y_prev = y_c
        miss = 0
        x = xi
        while x < x_max and miss < int(4 * s):
            x += 1
            lo, hi = int(y_prev - 8 * s), int(y_prev + 1 * s)
            c = np.nonzero(dark[max(lo, 0):hi, x])[0]
            if len(c) == 0:
                miss += 1
                continue
            miss = 0
            # dark runs in this column; follow the one nearest to the line so far (noise specks
            # above or below are skipped)
            c = c + max(lo, 0)
            br = np.nonzero(np.diff(c) > 1)[0]
            runs = [(int(a), int(b)) for a, b in zip(np.r_[c[0], c[br + 1]], np.r_[c[br], c[-1]])]
            a, b = min(runs, key=lambda r: max(r[0] - y_prev, y_prev - r[1], 0))
            if max(a - y_prev, y_prev - b, 0) > 3 * s:
                miss += 1
                continue
            y_prev = a
            trace.append((x, (a + b) / 2))   # centre of the line
            if not np.isnan(y_top[x]) and y_prev - y_top[x] < 1.5 * s:
                break
        # cut at a sharp corner (raglan seam leaving the neckline)
        w = max(2, int(2 * s))
        corner = False
        def _cos(i):
            v1 = np.subtract(trace[i], trace[i - w])
            v2 = np.subtract(trace[i + w], trace[i])
            return float(v1 @ v2) / max(np.linalg.norm(v1) * np.linalg.norm(v2), 1e-9)
        for i in range(w, len(trace) - w):
            if _cos(i) < math.cos(math.radians(55)):
                # the sharpest turn near the first sharp one is the corner itself
                i = min(range(i, min(i + 2 * w, len(trace) - w)), key=_cos)
                trace = trace[:i + 1]
                corner = True
                break
        if len(trace) > 3 * s and not corner:
            # the line fades within ~1 mm of the outline: extend it along its last direction
            tail = np.asarray(trace[-int(3 * s):], float)
            dv = tail[-1] - tail[0]
            if np.linalg.norm(dv) > 0:
                dv /= np.linalg.norm(dv)
                q = tail[-1].copy()
                for _ in range(int(6 * s)):
                    xi_ = int(round(q[0]))
                    if xi_ >= len(y_top) or np.isnan(y_top[xi_]) or q[1] <= y_top[xi_]:
                        break
                    q += dv
                trace.append((int(round(q[0])), int(round(q[1]))))
        if trace:
            ex, ey = trace[-1]
            gap = (ey - y_top[ex]) / s if not np.isnan(y_top[ex]) else 0.0
            raglan = corner or gap > 4.0
            style_conf = 1.0 if corner else float(min(1.0, abs(gap - 4.0) / 3.0))
            # raglan: the front raglan point (corner of the line); set-in: replaced below by the
            # neck point from the shoulder line (the outline peak is rounded off in a photo)
            neck_half = (ex - xc) / s
    if neck_half is None:
        warn.append("Front neckline not found: photograph the neckline flat in good light.")
        neck_half = float(np.nanargmin(y_top[xi:x_max]) / s)
        style_conf = 0.0
    # sleeve top line (and shoulder line for set-in sleeves)
    x0 = int(xc + (neck_half + (10 if raglan else 2)) * s)
    x1 = int(x_max - 8 * s)
    X = np.arange(x0, x1).astype(float)
    Y = y_top[x0:x1]
    jumps = np.nonzero(np.abs(np.diff(Y)) > 1.5 * s)[0]
    jumps = jumps[X[jumps] > Ux + 20 * s]          # the sleeve end lies well outside the underarm
    if len(jumps):                       # stop at the sleeve end (a steep edge in the top contour)
        X, Y = X[:jumps[0]], Y[:jumps[0]]
    ok = ~np.isnan(Y)
    X, Y = X[ok], Y[ok]

    def robust(xv, yv):
        sel = np.ones(len(xv), bool)
        for _ in range(3):
            (kk, cc), _ = _fit_line(xv[sel], yv[sel])
            sel = np.abs(yv - (kk * xv + cc)) < 2.0 * s
            if sel.sum() < 5:
                break
        return _fit_line(xv[sel], yv[sel]) if sel.sum() >= 5 else _fit_line(xv, yv)
    if raglan:
        # reference for raglan tops: the centre back neck (see flatlay.top_flatlay)
        sh = back_neck * s
        top = top + sh
        length -= back_neck
        if front_neck is not None:
            front_neck -= back_neck
        back_neck = 0.0
    res = {}
    if raglan:
        (k_l, c_l), _ = robust(X, Y)
        S = None
    else:
        best = None
        for xb in np.linspace(X[0] + 10 * s, X[-1] - 20 * s, 60):
            i = X <= xb
            if i.sum() < 5 or (~i).sum() < 5:
                continue
            l1, e1 = robust(X[i], Y[i])
            l2, e2 = robust(X[~i], Y[~i])
            if best is None or e1 + e2 < best[0]:
                best = (e1 + e2, l1, l2)
        _, (k1, c1), (k_l, c_l) = best
        sx_ = (c_l - c1) / (k1 - k_l) if abs(k1 - k_l) > 1e-6 else X[len(X) // 3]
        S = np.array([sx_, k1 * sx_ + c1])
        if abs(k1) > 1e-3:
            # neck point: corner between the shoulder line and the back neckline (the outline
            # peak itself is rounded off in a photo); fallback: shoulder line at the top
            est = (top - c1) / k1
            lo_, hi_ = int(est - 10 * s), int(est + 10 * s)
            x_pk = lo_ + int(np.nanargmin(y_top[lo_:hi_]))
            xs_mm = (np.arange(len(y_top)) - xc) / s
            nc = FL.neck_corner(xs_mm, (y_top - top) / s, (x_pk - xc) / s, back_neck,
                                (k1, (k1 * xc + c1 - top) / s))
            neck_half = nc if nc is not None else float((est - xc) / s)
        res["shoulder_x"] = float((S[0] - xc) / s)
        res["shoulder_y"] = float((S[1] - top) / s)
    d = np.array([1.0, k_l]) / math.hypot(1.0, k_l)
    n = np.array([-d[1], d[0]])
    Pc = np.array([xc, k_l * xc + c_l])
    U = np.array([Ux, Uy])
    w = U - Pc
    bicep_flat = float(abs(d[0] * w[1] - d[1] * w[0])) / s
    yy, xx = np.nonzero(m[:, int(Ux):])
    pts = np.stack([xx + int(Ux), yy], 1).astype(float)
    off = (pts - Pc) @ n                      # distance below the sleeve top line
    pts = pts[off < bicep_flat * s * 1.1 + 3 * s]      # sleeve only (not the body hem corner)
    proj = (pts - Pc) @ d
    reach = float(proj.max())
    band = pts[(proj > reach - 4 * s) & (proj < reach - 2 * s)]
    opening_flat = float(np.ptp(band @ n)) / s if len(band) else 0.0
    res.update(chest_flat=chest_flat, hem_flat=hem_flat, length=length, armhole_depth=float((Uy - top) / s),
               neck_half=float(neck_half), back_neck=float(back_neck),
               sleeve_reach=reach / s, sleeve_line_y=float((Pc[1] - top) / s),
               opening_flat=opening_flat, bicep_flat=bicep_flat)
    if front_neck is not None:
        res["front_neck"] = float(front_neck)
    res["_sleeve_style"] = "raglan" if raglan else "set_in"
    res["_sleeve_style_confidence"] = style_conf
    if style_conf < 0.5:
        warn.append("Set-in or raglan sleeve could not be told apart reliably: please confirm.")
    geo = dict(top=top, bottom=bottom, xc=xc, U=U, S=S, Pc=Pc, d=d, reach=reach, trace=trace, y_top=y_top, s=s)
    return res, geo, warn


def measure_top_both(mask, img, px_per_mm):
    """Measure the right half and the mirrored left half and average them: a slight camera
    tilt raises one side and lowers the other, which mostly cancels out."""
    res, geo, warn = measure_top(mask, img, px_per_mm)
    try:
        res2, _, _ = measure_top(np.ascontiguousarray(mask[:, ::-1]), np.ascontiguousarray(img[:, ::-1]),
                                 px_per_mm)
    except MeasureError:
        return res, geo, warn
    if res2["_sleeve_style"] != res["_sleeve_style"]:
        if res2["_sleeve_style_confidence"] > res["_sleeve_style_confidence"]:
            _, geo, warn = measure_top(*(np.ascontiguousarray(a[:, ::-1]) for a in (mask, img)), px_per_mm)
            geo["mirrored"] = True
            return res2, geo, warn
        return res, geo, warn
    out = {k: (v + res2[k]) / 2 if not k.startswith("_") and k in res2 else v for k, v in res.items()}
    out["_sleeve_style_confidence"] = min(res["_sleeve_style_confidence"], res2["_sleeve_style_confidence"])
    return out, geo, warn


def overlay_top(img, mask, geo, res, px_per_mm, path):
    from PIL import Image, ImageDraw, ImageFont
    s = px_per_mm
    vis = img.copy()
    lw = max(2, int(s))
    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cv2.drawContours(vis, cnts, -1, (40, 200, 40), lw)
    xc, top = geo["xc"], geo["top"]
    cv2.line(vis, (int(xc), int(top)), (int(xc), int(geo["bottom"])), (200, 90, 20), lw)
    P = geo["Pc"]
    E = P + geo["d"] * geo["reach"]
    cv2.line(vis, tuple(np.int32(P)), tuple(np.int32(E)), (0, 140, 255), lw)
    cv2.circle(vis, tuple(np.int32(geo["U"])), int(6 * s), (0, 0, 255), lw)
    if geo["S"] is not None:
        cv2.circle(vis, tuple(np.int32(geo["S"])), int(6 * s), (0, 0, 255), lw)
    for x, y in geo["trace"][::5]:
        cv2.circle(vis, (int(x), int(y)), max(1, int(s)), (220, 40, 220), -1)
    scale = min(1.0, 1600 / max(vis.shape[:2]))
    vis = cv2.resize(vis, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    pil = Image.fromarray(cv2.cvtColor(vis, cv2.COLOR_BGR2RGB))
    dr = ImageDraw.Draw(pil)
    font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "fonts", "DejaVuSans.ttf")
    f = ImageFont.truetype(font_path, 20)
    lines = [f"Detected: {res['_sleeve_style'].replace('_', '-')} sleeve (please check):"] + [
        f"{TOP_LABELS[k]}: {v / 10:.1f} cm" for k, v in res.items() if k in TOP_LABELS]
    dr.rectangle([8, 8, 470, 16 + 25 * len(lines)], fill=(255, 255, 255))
    for i, t in enumerate(lines):
        dr.text((16, 12 + 25 * i), t, fill=(0, 0, 0), font=f)
    pil.save(path)
    return path


def main(argv=None):
    ap = argparse.ArgumentParser(description="Measure a garment from a photo (mode B)")
    ap.add_argument("image")
    ap.add_argument("--type", default="pants")
    ap.add_argument("--out", default="measurement")
    ap.add_argument("--tape", help='tape-measure values in cm as JSON, e.g. {"inseam": 48}')
    a = ap.parse_args(argv)
    os.makedirs(a.out, exist_ok=True)
    r = measure(a.image, a.type, overlay_path=os.path.join(a.out, "overlay.png"),
                tape=json.loads(a.tape) if a.tape else None)
    with open(os.path.join(a.out, "measurement.json"), "w", encoding="utf-8") as f:
        json.dump(r, f, ensure_ascii=False, indent=2, default=float)
    for k, v in r["measures_mm"].items():
        if k.startswith("_"):
            print(f"{k[1:]}: {v}")
            continue
        print(f"{LABELS.get(k, TOP_LABELS.get(k, k))}: {v / 10:.1f} cm ({r['source'][k]})")
    for w in r["warnings"]:
        print("Note:", w)


if __name__ == "__main__":
    main()
