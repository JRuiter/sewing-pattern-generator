---
name: schnittmuster-generator
description: Erstellt nähbare, maßhaltige und druckfertige Schnittmuster (Vektor-PDF 1:1) aus einer freien Beschreibung, Größe/Körpermaßen und/oder Fotos eines Kleidungsstücks. Auslösen bei „Schnittmuster erstellen/konstruieren/generieren“, „Nähmuster nach Maßen“, „Schnitt nach Foto/Vorbild“, „Kleidungsstück abnehmen/nachnähen“, „Lieblingshose kopieren“, Plotter-/Rollendruck, A0/A1 oder A4 zum Kleben. Hosen (Jogginghose, Haremshose, Leggings, Stoffhose), T-Shirt/Raglan, Hoodie/Sweatshirt, Rock, Mütze, Loop.
---

# Schnittmuster-Generator

Konstruiert Schnittmuster **parametrisch** (Konstruktionsregeln, keine Bildgenerierung),
prüft sie auf Nähbarkeit und erzeugt Druckdateien, Zuschnittplan, Stoffverbrauch und
Nähanleitung. Alle Ausgaben an den Nutzer auf **Deutsch**.

Nur eigene Konstruktionen: keine geschützten Schnittmuster nachbauen oder kopieren. Bei
Designer-Vorbildern entsteht eine eigene Konstruktion im gleichen Stil für den privaten
Gebrauch.

## Einrichtung (einmalig)

```bash
pip install -r requirements.txt   # numpy scipy shapely opencv-contrib-python-headless reportlab matplotlib pillow pypdf
```

Alle Skripte liegen in `scripts/` und werden von dort oder mit Pfad aufgerufen.

## Ablauf

### 1. Eingabe verstehen
Aus der Nachricht herauslesen: Kleidungsstück + Varianten, Größe oder Maße, Stoff und
Dehnung, Passform, Ausgabeformat. Fotos? → Schritt 3.

### 2. Rückfragen – genau EINE Runde, nur was wirklich fehlt
Fehlende Punkte gesammelt in einer kurzen Nachricht fragen, mit Vorschlag als Standard
(„Wenn du nichts sagst, nehme ich …“). Typische Lücken:
- Kleidungsstück/Varianten (Taschen, Bündchen, Länge, Kapuze …)
- Größe (Kinder 86–176, Damen 34–56, Herren 44–60) **oder** Körpermaße
  (Körperhöhe, Brust, Taille, Hüfte, Schrittlänge, Seitenlänge, Armlänge, Kopfumfang)
- Stoff (Webware / Jersey / Jersey mit Elasthan / Interlock / Sweat / Fleece) und Dehnung in %
- Passform (eng / normal / weit / oversized; bei Hosen auch harem)
- Ausgabe: Rolle (Breite in mm, Standard 610), A0, A1, A4 oder US-Letter zum Kleben

Danach nicht erneut fragen; Unklares mit sinnvollem Standard lösen und im Ergebnis nennen.

### 3. Fotos (optional)
Erst entscheiden, welcher Modus vorliegt (Details: `references/photo_guide.md`):

**Modus A – Inspirationsfoto** (getragen, Katalog, Pinterest): Du siehst dir das Foto an
und füllst das Merkmals-JSON (Schema in `scripts/photo_analyze.py`, jedes Merkmal mit
`wert` + `konfidenz` 0–1). Dann:
```bash
python scripts/photo_analyze.py merkmale.json        # Bestätigungstext + Modul/Optionen + „nicht abgedeckt“
python scripts/photo_analyze.py --bild flatlay.jpg   # Hosen-Silhouette automatisch (nur Proportionen)
```
Merkmalsliste mit Konfidenz zeigen und bestätigen lassen („Ich erkenne … – stimmt das?“).
Nicht abgedeckte Merkmale offen nennen und die ausgegebene Alternative anbieten, nicht
improvisieren. **Körpermaße kommen immer vom Nutzer**, nie aus dem Inspirationsfoto.

**Modus B – Kleidungsstück abnehmen** (flach hingelegt, senkrecht von oben, mit
Referenzkarte `assets/referenzkarte.pdf` oder Zollstock): Reverse Engineering.
```bash
cd scripts && python -m reverse.pipeline foto.jpg --type hose --out projekt/
```
Ergebnis: `overlay_messung.png` (erkannte Kontur und Maße, dem Nutzer zur Bestätigung
zeigen), `reverse_bericht.md` (Teile-/Nahtgraph, Soll/Ist/Δ-Abweichungsbericht,
Nähbarkeits-Prüfung) und `projekt.json` (speicherbar für „wie letztes Mal, 2 Größen
größer“ → `reverse.pipeline.regrade(projekt.json, 2)`). Maßband-Werte des Nutzers haben
Vorrang: `photo_measure.measure(..., tape={"inseam": 48})`. Fehlt die Karte, sagt der
Skill genau, was zu tun ist. Fehlende Fotos (z. B. Schrittkurve) nennt
`reverse.decompose.missing_photos`. Toleranz: Längen ± 1 cm, Weiten ± 2 %.
Danach Druckdateien:
```bash
python scripts/generate.py --projekt projekt/projekt.json --format rolle610,a4 --out out/nachbau
```
Modus B ist für **Hosen** vollständig automatisiert; Oberteile werden grob vermessen
(`--type oberteil`: Brustweite, Saumweite, Länge, Ärmel) und über
`tshirt_basic.fit_to_targets` angepasst – Armloch/Ausschnitt dann per Maßband erfragen.

### 4. Maße
`measurements.complete_measures(gegebene_cm, größe)` ergänzt fehlende Maße aus der
Größentabelle bzw. Körperhöhe und meldet Plausibilitätswarnungen. Angegebene Maße haben
Vorrang vor der Tabelle. Tabellen und Herkunft: `references/size_tables.md`.

### 5. Konstruktion, Validierung, Layout, Render – ein Aufruf
```bash
python scripts/generate.py --garment pants_basic --style haremshose --size 122 \
    --fabric sweat --format rolle610,a4 --out out/harem122
# weitere Beispiele
python scripts/generate.py --garment tshirt_basic --size 140 --options '{"sleeve_style":"raglan","sleeve_length":"lang"}' --format a4
python scripts/generate.py --garment hoodie --size d38 --fabric sweat --format rolle914,a0
python scripts/generate.py --garment skirt --size 128 --style teller --format a1
python scripts/generate.py --spec auftrag.json          # alles als JSON (siehe Kopf von generate.py)
```
Module und wichtigste Optionen:

| Modul | Stile/Optionen |
|---|---|
| `pants_basic` | style: jogginghose, haremshose, leggings, stoffhose · fit · fabric · stretch · length (lang, 7/8, knie, kurz) · waistband (bund_gummi, buendchen, yoga, tunnel) · cuffs · pockets ([eingriff], [schraeg], [aufgesetzt_hinten]) |
| `tshirt_basic` | fit · fabric · sleeve_style (eingesetzt, raglan) · sleeve_length (kurz, 3/4, lang) · neckline (rund, v) · length (normal, tunika) · sleeve_cuffs · hem_band |
| `hoodie` | wie T-Shirt + hood, hood_lining, kangaroo (Standard: Sweat, weit, Bündchen) |
| `skirt` | style: gerafft, a_linie, teller · length (mini, knie, midi, maxi) · gather · flare_deg |
| `beanie` | brim (Umschlag), slouch |
| `loop` | wraps (1 = einfach, 2 = doppelt gelegt), height |

Formate: `rolleNNN` (Seitenbreite = Rolle − 10 mm, Hochformat; Teile breiter als die
Rolle werden automatisch in Bahnen mit Klebemarken geteilt), `a0`, `a1` (Teile ungeteilt,
Übergrößen gekachelt), `a4`, `letter` (Kacheln mit 10 mm Überlappung, Übersichtsseite).
Immer zusätzlich: SVG-Master 1:1, PNG-Vorschau, Zuschnittplan-PNG, Nähanleitung
(MD + PDF), `schnitt.json`, `pruefbericht.md`.

**Validierung ist Pflicht:** Schlägt eine Prüfung fehl (❌), beendet `generate.py` mit
Exit-Code 2 und schreibt **keine** Druckdateien. Dann Ursache aus `pruefbericht.md`
beheben (meist widersprüchliche Maße/Optionen) und neu erzeugen – nie einen Schnitt mit
Fehlern ausliefern. Regeln: `references/drafting_rules.md`.

### 6. Selbstprüfung der Vorschau
Die PNG-Vorschau(en) und den Zuschnittplan **ansehen**, bevor du auslieferst: Teile
vollständig, nichts überlappt, Beschriftung lesbar, Fadenlauf plausibel, Kontrollquadrat
vorhanden. Auffälligkeiten beheben oder dem Nutzer offen sagen.

### 7. Auslieferung an den Nutzer
- PDFs (Rolle/Bogen/A4), SVG-Master, Vorschau-PNG
- Nähanleitung mit Stoffverbrauch und Zuschnittplan
- **Validierungstabelle** (Inhalt von `pruefbericht.md`) in der Antwort
- Druckhinweis: „In **100 % / tatsächlicher Größe** drucken, nicht ‚an Seite anpassen‘.
  Kontrollquadrat nachmessen (5 × 5 cm).“ Für den Canon iPF650 (24"-Rolle): PDF als
  benutzerdefiniertes Format 600 mm × Länge, Hochformat, über Direct Print & Share oder
  Acrobat (`references/print_specs.md`).
- **Hinweis Probeteil:** „Beim ersten Nähen eines neuen Schnitts bitte ein Probeteil
  aus günstigem Stoff mit ähnlicher Dehnung nähen und die Passform prüfen.“

## Grenzen (offen kommunizieren)
- Aus getragenen Fotos lassen sich **keine exakten Maße** ableiten, nur Stil und
  Proportionen. Exakte Maße nur mit Modus B (Maßstab im Bild) oder Maßband.
- Rückseite und verdeckte Details werden erfragt, nicht erfunden.
- Nicht abgedeckt (Alternative anbieten): Kleider, Jacken mit Reißverschluss/Futter,
  Hemden/Blusen mit Kragen und Knopfleiste, Jeans mit Hosenschlitz, Cargo-/Paspeltaschen,
  Teilungsnähte, Schlaghosen.
- Gradieren über Gradierregeln je Größensprung (`reverse/store.py`), nie durch lineares
  Skalieren.

## Dateien
- `scripts/generate.py` – Gesamtablauf (CLI)
- `scripts/geometry.py`, `pattern.py`, `measurements.py`, `ease.py` – Grundlagen
- `scripts/garments/*.py` – Kleidungsmodule `draft(measures, options) -> Pattern`
- `scripts/validate.py` – Nähbarkeitsprüfungen
- `scripts/layout.py`, `render.py`, `instructions.py` – Anordnung, PDF/SVG/PNG, Anleitung
- `scripts/photo_analyze.py`, `photo_measure.py`, `reverse/` – Foto-Modi A und B
- `scripts/refcard.py` – erzeugt `assets/referenzkarte.pdf`; `photo_synth.py` – Testfotos
- `references/` – Konstruktionsregeln, Maßtabellen, Druckvorgaben, Fotoanleitung
- `tests/` – `python -m pytest tests`
