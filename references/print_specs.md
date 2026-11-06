# Druckvorgaben

Gilt für alle Ausgaben von `scripts/render.py`. Wird von `tests/test_validate.py`
automatisch geprüft (Kontrollquadrat, eingebettete Schriften, Linienstärken, Überlappung).

## Allgemein

| Vorgabe | Umsetzung |
|---|---|
| Vektor-PDF, Maßstab 1:1 | reportlab, Einheiten mm → pt (1 mm = 2,8346 pt), keine Rastergrafik im Schnitt |
| Schriften eingebettet | DejaVu Sans (TrueType, `assets/fonts/`, freie Lizenz) |
| Linienstärken ≥ 0,5 pt | Schnittlinie 1,0 pt, Bruch 1,0 pt, Nählinie 0,6 pt, Markierungen 0,6–0,8 pt, Kachelrahmen 0,5 pt |
| Linienarten | Schnittlinie **durchgezogen**, Nählinie **gestrichelt**, Stoffbruch **Strich-Punkt** |
| Kontrollquadrat | auf jeder Seite/jedem Bogen: 5 × 5 cm (exakt 141,73 pt) + 1 inch (72 pt) |
| Beschriftung je Teil | Name, Größe, „n× zuschneiden“ (gegengleich/im Bruch), Fadenlaufpfeil, Passzeichen (einfach/doppelt), Nahtzugabe-Hinweis, „◄ STOFFBRUCH ►“ |
| Druckhinweis | „Mit 100 % / Tatsächliche Größe drucken – NICHT ‚An Seite anpassen‘“ im Kopf jeder Datei |

## Rolle (Plotter)

- Seitenbreite = Rollenbreite − 10 mm (610 → 600 mm, 914 → 904 mm), Länge variabel,
  **Hochformat** (Seite nie breiter als lang).
- Rand 5 mm, Kopfbereich 80 mm (Titel, Legende, Kontrollquadrate).
- Teile werden platzsparend gepackt: Drehung in 15°-Schritten erlaubt (Fadenlauf dreht
  mit), Abstand ≥ 10 mm, mehrere Strategien, kürzeste Länge gewinnt. Kein Teil wird
  zerschnitten.
- Ausnahme: Ein Teil breiter als die Rolle (z. B. Tellerrock für Erwachsene) wird in
  rollenbreite Bahnen à 120 cm mit 10 mm Überlappung und Klebemarken geteilt; die
  Nähanleitung weist darauf hin.

### Canon imagePROGRAF iPF650 (24"-Rolle, 610 mm)
1. PDF in **Adobe Acrobat** öffnen → Drucken → „Tatsächliche Größe“, „Seite einpassen“ AUS.
2. Papierformat: **benutzerdefiniert, 600 mm × Seitenlänge** (steht im Dateinamen/Kopf),
   **Hochformat**. Nicht drehen lassen („Automatisch drehen“ AUS).
3. Alternativ **imagePROGRAF Direct Print & Share**: Rollenpapier, „Originalgröße“,
   Randlos AUS.
4. Nach dem Druck Kontrollquadrat nachmessen (5,0 × 5,0 cm).

## A0 / A1 (Copyshop)

- Teile ungeteilt auf möglichst wenige Bögen (Rand 10 mm), Kontrollquadrat je Bogen.
- Passt ein Teil auf keinen Bogen, wird es wie A4 gekachelt (Überlappung + Klebemarken)
  und als eigener Abschnitt angehängt.

## A4 / US-Letter zum Kleben

- Kachelung mit **10 mm Überlappung**; die Klebefläche ist grau hinterlegt und auf beiden
  Seiten deckungsgleich (gleicher Inhalt, automatisch getestet). Bei jeder Seite wird der
  linke bzw. obere Rand an der gestrichelten Linie abgeschnitten und auf die Nachbarseite
  geklebt.
- Seitenkennung als Zeile/Spalte (A1, A2, B1 …) groß im Hintergrund und in der Kopfzeile
  („kleben an: links A1, oben …“).
- Passmarken: Rauten mit Kennung beider Seiten (z. B. „A1|A2“) an jeder Klebekante, damit Seiten eindeutig
  zusammenpassen.
- Rand 8 mm (Druckerrand), leere Seiten werden weggelassen.
- **Seite 1 = Übersichtsplan:** verkleinerte Anordnung aller Seiten mit Kennungen,
  Klebeanleitung und Druckhinweis (der Plan selbst ist verkleinert, die Kontrollquadrate
  darauf sind 1:1).
- Kontrollquadrat auf jeder Seite an einer freien Stelle (ohne Schnittlinien).

## Zusätzliche Dateien

- `*_master_1zu1.svg` – SVG mit Einheit mm (`width="…mm"`), 1:1, für Plotter-/CAD-Software.
- `*_vorschau.png` – farbige Vorschau mit Seiten-/Bahnraster.
- `zuschnittplan.png` – Lage der Teile auf dem Stoff (einlagig, Fadenlauf parallel zur
  Webkante, alle Kopien, gegengleiche Teile gespiegelt) mit Stoffverbrauch.
