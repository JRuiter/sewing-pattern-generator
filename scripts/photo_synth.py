"""Synthetische „Flach-hingelegt“-Fotos aus einem Schnitt (für Tests und Rundlauf).

Der Schnitt wird virtuell zusammengenäht und flach (2 Lagen) hingelegt: Bund oben,
Beine leicht gespreizt, Bündchen unten. Daneben liegt die Referenzkarte. Danach wird
eine Kamera mit leichter Schrägstellung (Perspektive), Drehung, Unschärfe, Rauschen,
Helligkeitsverlauf und JPEG-Kompression simuliert.

Rückgabe enthält die Wahrheit (Fertigmaße) für die Prüfung der Messgenauigkeit.
"""
from __future__ import annotations

import math

import cv2
import numpy as np
from shapely.affinity import rotate as srotate
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

import geometry as G
import refcard


def _widths(ring, ys):
    return np.array([G.width_at_y(ring, y) for y in ys])


def pants_silhouette(pat, splay_deg: float = 5.0, step: float = 2.0):
    """Flache Silhouette (mm, y nach unten, x=0 Mitte) + Regionen + Nahtlinien."""
    o, fin = pat.options, pat.finished
    f, b = pat.piece("vorderhose"), pat.piece("hinterhose")
    fr = f.seam_ring()
    if pat.has("seitenteil"):
        u = Polygon(fr).union(Polygon(pat.piece("seitenteil").seam_ring()))
        fr = np.asarray(u.exterior.coords)
    br = b.seam_ring()
    wb, cuff_h = o["_wb_h"], o["_cuff_h"]
    y_cr_f = float(f.edge("innenbein").pts[0, 1])
    y_cr_b = float(b.edge("innenbein").pts[0, 1])
    y_hem = float(f.edge("saum").pts[0, 1])
    y_hip = o["_y_hip"]
    band_w = fin["waist_relaxed"] / 2
    # Rumpf
    ys = np.arange(-0.5, y_cr_f + 0.5, -step)
    full = _widths(fr, ys) + _widths(br, ys)
    blend_end = y_hip * 0.6
    t = np.clip(ys / blend_end, 0, 1)
    torso_w = band_w + (full - band_w) * (0.3 * t + 0.7 * t ** 2) ** 0.5
    torso_w = np.where(ys <= blend_end, full, torso_w)
    sy = wb - ys
    torso = Polygon(np.vstack([np.stack([-torso_w / 2, sy], 1), np.stack([torso_w[::-1] / 2, sy[::-1]], 1)]))
    band = box(-band_w / 2, 0, band_w / 2, wb + 0.5) if wb > 0 else None
    # Beine
    leg_len = y_cr_f - y_hem
    ts = np.arange(0.5, leg_len + 0.01, step)
    circ = _widths(fr, y_cr_f - ts) + _widths(br, y_cr_b - ts)
    flat = circ / 2
    c0 = flat[0] / 2
    crotch_sy = wb - y_cr_f
    legs, cuffs, seams = [], [], []
    cuff_w = fin["opening"] / 2 if cuff_h > 0 else None
    for side in (1, -1):
        xs_in = side * (c0 - flat / 2)
        xs_out = side * (c0 + flat / 2)
        pts = np.vstack([np.stack([xs_in, crotch_sy + ts], 1),
                         np.stack([xs_out[::-1], crotch_sy + ts[::-1]], 1),
                         [[side * c0 * 2, crotch_sy - 1], [0, crotch_sy - 1]]])
        leg = Polygon(pts).buffer(0)
        cuff = None
        if cuff_h > 0:
            cy0 = crotch_sy + leg_len
            cuff = box(side * c0 - cuff_w / 2, cy0 - 0.5, side * c0 + cuff_w / 2, cy0 + cuff_h)
            seams.append(("cuff", side, cy0))
        ang = side * splay_deg   # Drehung um den Schrittpunkt nach außen
        leg = srotate(leg, -ang, origin=(0, crotch_sy), use_radians=False)
        legs.append(leg)
        if cuff is not None:
            cuffs.append(srotate(cuff, -ang, origin=(0, crotch_sy), use_radians=False))
    parts = [torso] + legs + cuffs + ([band] if band is not None else [])
    sil = unary_union([p.buffer(0.3) for p in parts]).buffer(-0.3)
    truth = dict(fin)
    return dict(silhouette=sil, band=band, cuffs=cuffs, legs=legs, crotch=(0.0, crotch_sy),
                splay=splay_deg, truth=truth, wb=wb, cuff_h=cuff_h)


def _texture(h, w, base, rng, stripes=False, amp=10):
    img = np.zeros((h, w, 3), np.float32)
    img[:] = base
    noise = rng.normal(0, amp, (h // 4 + 1, w // 4 + 1, 1)).astype(np.float32)
    noise = cv2.resize(noise, (w, h))[:, :, None]
    img += noise
    if stripes:
        xs = np.arange(w)
        img += (np.sin(xs / 2.2) * 9)[None, :, None]
    return img


def render_scene(sil_info, px_per_mm=3.0, seed=0, card_pos=None, garment_rgb=(150, 152, 165),
                 rib_rgb=(120, 122, 140), bg_rgb=(176, 140, 104)):
    """Draufsicht (ideal, ohne Perspektive) rendern. Rückgabe: Bild, Szene→Pixel-Matrix."""
    rng = np.random.default_rng(seed)
    sil = sil_info["silhouette"]
    x0, y0, x1, y1 = sil.bounds
    margin = 60.0
    card_w = refcard.CARD + 30
    W = (x1 - x0) + 2 * margin + card_w
    H = (y1 - y0) + 2 * margin
    w, h = int(W * px_per_mm), int(H * px_per_mm)
    ox, oy = -x0 + margin, -y0 + margin

    def to_px(pts):
        pts = np.asarray(pts, float)
        return np.round(np.stack([(pts[:, 0] + ox) * px_per_mm, (pts[:, 1] + oy) * px_per_mm], 1) * 8).astype(np.int32)

    bg = _texture(h, w, bg_rgb[::-1], rng, amp=8)
    planks = (np.sin(np.arange(h) / (px_per_mm * 40)) * 6)[:, None, None]
    bg += planks
    mask = np.zeros((h, w), np.uint8)
    geoms = [sil] if sil.geom_type == "Polygon" else list(sil.geoms)
    for g in geoms:
        cv2.fillPoly(mask, [to_px(g.exterior.coords)], 255, lineType=cv2.LINE_AA, shift=3)
    fabric = _texture(h, w, garment_rgb[::-1], rng, amp=7)
    rib = _texture(h, w, rib_rgb[::-1], rng, stripes=True, amp=5)
    rib_mask = np.zeros((h, w), np.uint8)
    for g in ([sil_info["band"]] if sil_info["band"] is not None else []) + sil_info["cuffs"]:
        cv2.fillPoly(rib_mask, [to_px(g.exterior.coords)], 255, shift=3)
    garment = np.where(rib_mask[:, :, None] > 0, rib, fabric)
    a = (mask.astype(np.float32) / 255)[:, :, None]
    img = bg * (1 - a) + garment * a
    # Nähte (dunkle Linien) an Bundansatz, Bündchenansatz und Schrittnaht
    dark = (garment_rgb[2] * 0.55, garment_rgb[1] * 0.55, garment_rgb[0] * 0.55)
    lw = max(1, int(px_per_mm * 0.8))
    if sil_info["wb"] > 0:
        bw = sil_info["band"].bounds
        cv2.line(img, tuple(to_px([[bw[0], bw[3]]])[0] // 8), tuple(to_px([[bw[2], bw[3]]])[0] // 8), dark, lw)
    for cf in sil_info["cuffs"]:
        cc = np.asarray(cf.exterior.coords)[:4]
        top = sorted(cc, key=lambda p: p[1])[:2]
        cv2.line(img, tuple(to_px([top[0]])[0] // 8), tuple(to_px([top[1]])[0] // 8), dark, lw)
    cx, cy = sil_info["crotch"]
    cv2.line(img, tuple(to_px([[0, sil_info["wb"]]])[0] // 8), tuple(to_px([[cx, cy]])[0] // 8), dark, lw)
    # Schatten unter dem Stoff (leicht)
    shadow = cv2.GaussianBlur(mask, (0, 0), px_per_mm * 2).astype(np.float32) / 255
    img = img * (1 - 0.12 * np.clip(shadow - a[:, :, 0], 0, 1))[:, :, None]
    # Referenzkarte
    card = refcard.raster_card(px_per_mm)
    if card_pos is None:
        card_pos = (x1 + 25, y1 - refcard.CARD - 40)
    cxp, cyp = int((card_pos[0] + ox) * px_per_mm), int((card_pos[1] + oy) * px_per_mm)
    ch, cw = card.shape
    img[cyp:cyp + ch, cxp:cxp + cw] = card[:, :, None].astype(np.float32)
    scene_to_px = np.array([[px_per_mm, 0, ox * px_per_mm], [0, px_per_mm, oy * px_per_mm], [0, 0, 1]])
    return np.clip(img, 0, 255).astype(np.uint8), scene_to_px, card_pos


def camera(img, seed=0, tilt=0.04, rot_deg=4.0, blur=1.0, noise=3.0, jpeg=88, out_long=2600):
    """Kamera simulieren: Perspektive (tilt = relative Eckverschiebung), Drehung, Unschärfe…"""
    rng = np.random.default_rng(seed + 100)
    h, w = img.shape[:2]
    src = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
    jit = rng.uniform(-tilt, tilt, (4, 2)) * np.array([w, h])
    dst = src + jit
    ang = math.radians(rng.uniform(-rot_deg, rot_deg))
    c = dst.mean(axis=0)
    R = np.array([[math.cos(ang), -math.sin(ang)], [math.sin(ang), math.cos(ang)]])
    dst = (dst - c) @ R.T + c
    dst -= dst.min(axis=0)
    scale = out_long / max(dst[:, 0].max(), dst[:, 1].max())
    dst *= scale
    Hm = cv2.getPerspectiveTransform(src, np.float32(dst))
    size = (int(dst[:, 0].max()) + 1, int(dst[:, 1].max()) + 1)
    out = cv2.warpPerspective(img, Hm, size, flags=cv2.INTER_AREA if scale < 1 else cv2.INTER_LINEAR,
                              borderMode=cv2.BORDER_REFLECT)
    # Helligkeitsverlauf / Vignette
    yy, xx = np.mgrid[0:size[1], 0:size[0]].astype(np.float32)
    grad = 1.0 + 0.10 * (xx / size[0] - 0.5) - 0.06 * (yy / size[1] - 0.5)
    vig = 1 - 0.15 * (((xx / size[0] - 0.5) ** 2 + (yy / size[1] - 0.5) ** 2) * 2)
    out = out.astype(np.float32) * (grad * vig)[:, :, None]
    if blur > 0:
        out = cv2.GaussianBlur(out, (0, 0), blur)
    out += rng.normal(0, noise, out.shape)
    out = np.clip(out, 0, 255).astype(np.uint8)
    ok, enc = cv2.imencode(".jpg", out, [cv2.IMWRITE_JPEG_QUALITY, jpeg])
    return cv2.imdecode(enc, cv2.IMREAD_COLOR), Hm


def synth_pants_photo(pat, path=None, seed=0, px_per_mm=3.0, splay_deg=5.0, **cam):
    info = pants_silhouette(pat, splay_deg=splay_deg)
    scene, _, _ = render_scene(info, px_per_mm=px_per_mm, seed=seed)
    img, _ = camera(scene, seed=seed, **cam)
    if path:
        cv2.imwrite(path, img)
    return img, info["truth"]
