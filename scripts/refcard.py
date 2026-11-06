"""Referenzkarte 10 × 10 cm mit 4 ArUco-Markern (DICT_4X4_50, IDs 0–3).

Kartenkoordinaten in mm, Ursprung oben links, y nach unten. Marker 20 × 20 mm,
5 mm vom Kartenrand. Ecken je Marker in OpenCV-Reihenfolge (oben links, oben rechts,
unten rechts, unten links).

  python refcard.py  → erzeugt ../assets/referenzkarte.pdf (Vektor, 1:1)
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
    img = cv2.aruco.generateImageMarker(d, mid, 6)     # 4×4 Bits + 1 Zelle schwarzer Rand
    return (img < 128)                                   # True = schwarz


def raster_card(px_per_mm: float) -> np.ndarray:
    """Karte als Graustufenbild (für synthetische Testbilder)."""
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
    # Mittelkreuz
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
    c.setTitle("Referenzkarte 10 × 10 cm – Schnittmuster-Generator")
    c.setFont(R.FONT_B, 15)
    c.drawString(20 * MM, (H - 22) * MM, "Referenzkarte für Fotos (Modus „Lieblingsteil abnehmen“)")
    c.setFont(R.FONT, 9)
    lines = [
        "1. Mit 100 % / „Tatsächliche Größe“ drucken. Das Quadrat muss genau 10 × 10 cm messen.",
        "2. Ausschneiden (an der äußeren Linie) und flach neben das Kleidungsstück legen – nicht knicken.",
        "3. Foto senkrecht von oben, Karte vollständig im Bild, nicht verdeckt, gleiche Ebene wie der Stoff.",
        "4. Am besten auf Karton kleben, damit sie plan liegt. Marker nicht beschriften.",
    ]
    for i, t in enumerate(lines):
        c.drawString(20 * MM, (H - 32 - i * 5.5) * MM, t)
    ox, oy = 55.0, 70.0           # Kartenposition (mm von links/oben)

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
    # zweite Karte als Ersatz und Kontrollquadrat
    R.control_squares_pdf(c, 20.0, 190.0, H)
    c.setFont(R.FONT, 8)
    c.drawString(110 * MM, (H - 200) * MM, "Kontrollquadrat nachmessen: 5 × 5 cm.")
    c.drawString(110 * MM, (H - 206) * MM, "Alternativ: Zollstock entlang zweier Kanten")
    c.drawString(110 * MM, (H - 212) * MM, "ins Bild legen und die Länge nennen.")
    c.showPage()
    c.save()
    return path


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    print(make_pdf(os.path.join(here, "..", "assets", "referenzkarte.pdf")))
