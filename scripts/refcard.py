"""Reference card 10 × 10 cm with 4 ArUco markers (DICT_4X4_50, IDs 0–3).

Card coordinates in mm, origin top left, y down. Markers are 20 × 20 mm,
5 mm from the card edge. Corners per marker in OpenCV order (top left, top right,
bottom right, bottom left).

  python refcard.py  → writes ../assets/reference-card.pdf (vector, 1:1)
"""
from __future__ import annotations

import os

import cv2
import numpy as np

CARD = 100.0
MARKER = 20.0
INSET = 5.0
DICT_ID = cv2.aruco.DICT_4X4_50
ORIGINS = {0: (INSET, INSET), 1: (CARD - INSET - MARKER, INSET),
           2: (CARD - INSET - MARKER, CARD - INSET - MARKER), 3: (INSET, CARD - INSET - MARKER)}


def marker_corners_mm() -> dict[int, np.ndarray]:
    out = {}
    for mid, (x, y) in ORIGINS.items():
        out[mid] = np.array([[x, y], [x + MARKER, y], [x + MARKER, y + MARKER], [x, y + MARKER]], float)
    return out


def marker_bits(mid: int) -> np.ndarray:
    d = cv2.aruco.getPredefinedDictionary(DICT_ID)
    img = cv2.aruco.generateImageMarker(d, mid, 6)     # 4×4 bits + 1 cell black border
    return (img < 128)                                   # True = black


def raster_card(px_per_mm: float) -> np.ndarray:
    """Card as a greyscale image (for synthetic test images)."""
    n = int(round(CARD * px_per_mm))
    img = np.full((n, n), 250, np.uint8)
    cv2.rectangle(img, (0, 0), (n - 1, n - 1), 40, max(1, int(px_per_mm * 0.4)))
    cell = MARKER / 6
    for mid, (x, y) in ORIGINS.items():
        bits = marker_bits(mid)
        for r in range(6):
            for c in range(6):
                if bits[r, c]:
                    x0 = int(round((x + c * cell) * px_per_mm))
                    y0 = int(round((y + r * cell) * px_per_mm))
                    x1 = int(round((x + (c + 1) * cell) * px_per_mm))
                    y1 = int(round((y + (r + 1) * cell) * px_per_mm))
                    img[y0:y1, x0:x1] = 0
    # centre cross
    m = n // 2
    t = max(1, int(px_per_mm * 0.4))
    cv2.line(img, (m - int(8 * px_per_mm), m), (m + int(8 * px_per_mm), m), 40, t)
    cv2.line(img, (m, m - int(8 * px_per_mm)), (m, m + int(8 * px_per_mm)), 40, t)
    return img


def make_pdf(path: str):
    from reportlab.lib.colors import black
    from reportlab.pdfgen import canvas

    import render as R
    R.register_fonts()
    MM = R.MM
    W, H = 210.0, 297.0
    c = canvas.Canvas(path, pagesize=(W * MM, H * MM))
    c.setTitle("Reference card 10 × 10 cm · sewing-pattern-generator")
    c.setFont(R.FONT_B, 15)
    c.drawString(20 * MM, (H - 22) * MM, "Reference card for photos (mode \"copy a favourite garment\")")
    c.setFont(R.FONT, 9)
    lines = [
        "1. Print at 100 % / \"Actual size\". The square must measure exactly 10 × 10 cm.",
        "2. Cut it out (along the outer line) and lay it flat next to the garment. Do not fold it.",
        "3. Take the photo straight from above, card fully visible, uncovered, on the same plane as the fabric.",
        "4. Ideally glue it onto cardboard so it lies flat. Do not write on the markers.",
    ]
    for i, t in enumerate(lines):
        c.drawString(20 * MM, (H - 32 - i * 5.5) * MM, t)
    ox, oy = 55.0, 70.0           # card position (mm from left/top)

    def P(x, y):
        return (ox + x) * MM, (H - oy - y) * MM

    c.setLineWidth(0.6)
    c.setStrokeColor(black)
    x0, y0 = P(0, CARD)
    c.rect(x0, y0, CARD * MM, CARD * MM, stroke=1, fill=0)
    cell = MARKER / 6
    c.setFillColor(black)
    for mid, (x, y) in ORIGINS.items():
        bits = marker_bits(mid)
        for r in range(6):
            for cc in range(6):
                if bits[r, cc]:
                    px, py = P(x + cc * cell, y + (r + 1) * cell)
                    c.rect(px, py, cell * MM, cell * MM, stroke=0, fill=1)
    c.setLineWidth(0.6)
    mx, my = P(50, 50)
    c.line(mx - 8 * MM, my, mx + 8 * MM, my)
    c.line(mx, my - 8 * MM, mx, my + 8 * MM)
    c.setFont(R.FONT, 7)
    tx, ty = P(50, 38)
    c.drawCentredString(tx, ty, "10 × 10 cm")
    tx, ty = P(50, 64)
    c.drawCentredString(tx, ty, "ArUco 4×4 · ID 0–3")
    # control square
    R.control_squares_pdf(c, 20.0, 190.0, H)
    c.setFont(R.FONT, 8)
    c.drawString(110 * MM, (H - 200) * MM, "Measure the control square: 5 × 5 cm.")
    c.drawString(110 * MM, (H - 206) * MM, "Alternative: lay a folding ruler along two edges")
    c.drawString(110 * MM, (H - 212) * MM, "in the picture and give its length.")
    c.showPage()
    c.save()
    return path


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    print(make_pdf(os.path.join(here, "..", "assets", "reference-card.pdf")))
