# Konstruktionsregeln

Eigene parametrische Konstruktionen nach den allgemein bekannten Prinzipien der
Bekleidungskonstruktion (Grundschnitt aus Körpermaß + Mehrweite, rechte Winkel an
Mittel- und Seitennähten, Kurven tangential an Nahtenden). Es werden keine Schnitte aus
Büchern oder Heften nachgebaut. Alle Maße in mm; Formeln im Code unter `scripts/garments/`.

Bezeichnungen: `H` Hüftumfang, `B` Brustumfang, `KH` Körperhöhe, `SL` Schrittlänge,
`SeL` Seitenlänge, `k = KH / 1220` (Skalierung kleiner Teile, Kind Gr. 122 = 1,
begrenzt auf 0,75–1,45).

## 1. Allgemeine Regeln

- **Koordinaten:** x nach rechts, y nach oben, Kanten gegen den Uhrzeigersinn, jede Kante
  mit eigener Nahtzugabe. Die Schnittlinie entsteht durch Versatz jeder Kante um ihre
  Nahtzugabe; Ecken werden verschnitten (Schnittpunkt), bei spitzen Winkeln gefast.
- **Nahtzugaben:** 1,0 cm Standard (Overlock/Nähmaschine), Saum Hose 2,5 cm, Saum Shirt
  2,0 cm, Ausschnitt 0,7 cm, Bruchkanten 0.
- **Kurven** sind kubische Bézierkurven mit vorgegebenen End-Tangenten. An jeder
  Ecke, an der zwei Teile zur durchgehenden Kante zusammengenäht werden (z. B. Schulter +
  Armloch, Schrittnaht links + rechts), müssen sich die Winkel zu 180° ergänzen; an
  Mittel-/Bruchkanten trifft jede Kurve rechtwinklig auf.
- **Mehrweite** (`scripts/ease.py`), Anteil des Körperumfangs:

| Passform | Brust Webware | Brust Maschenware* | Hüfte Webware | Hüfte Maschenware* |
|---|---|---|---|---|
| eng | +6 % | ±0 (bei ≥ 40 % Dehnung negativ, bis −10 %) | +6 % | −4 … −12 % (Leggings) |
| normal | +14 % | +9 % | +14 % | +10 % |
| weit | +22 % | +17 % | +22 % | +18 % |
| oversized | +32 % | +27 % | +30 % | +26 % |
| harem | – | – | +34 % | +30 % |

  \* bei 30 % Dehnung; je 10 % mehr Dehnung 1 % weniger Mehrweite.

- **Bündchen-Verhältnis** (Bündchenlänge / Ansatzkante): Bündchenware 0,85 bei 50 %
  Dehnung bis 0,70 bei 80 % Dehnung; Jersey-Streifen 0,80–0,92.
- **Einhaltemenge Ärmelkugel:** Jersey 0–5 mm, Sweat/Fleece 0–8 mm, Webware 10–25 mm.
  Die Kugelhöhe wird per Bisektion so bestimmt, dass die Zielmenge (40 % des Bereichs)
  erreicht wird.

## 2. Hose (`pants_basic`)

1. **Hüftweite** `Hc = H × (1 + Mehrweite)`; Vorderhose `Hc/4 − d`, Hinterhose `Hc/4 + d`
   (d = 5 mm Kinder, 10 mm Erwachsene).
2. **Schrittverlängerung:** vorne 5 % von Hc, hinten 10 % (eng: 4 % / 8 %); per
   `fork_factor` anpassbar (Reverse Engineering).
3. **Leibhöhe** `R = (SeL − SL) + Sitzzugabe + Harem-Absenkung − Bundhöhe`;
   Sitzzugabe 15 mm Kinder / 20 mm Erwachsene (eng ×0,25, weit ×1,3, oversized ×1,6),
   Harem-Absenkung 6 % der Körperhöhe. Hüftlinie bei 0,55 × R unter der Oberkante.
4. **Beinlänge** ab Schrittlinie: `SL − 15/25 mm − Absenkung + Blusigkeit`; bei
   Bündchen 15 mm × k (Harem 30 mm × k) Blusigkeit über dem Bündchen.
5. **Beinöffnung:** mit Bündchen `max(1,12 × Knöchel, Knöchel + 15 mm) / Bündchen-Verhältnis`;
   ohne Bündchen: normal 0,46 × Hc, weit 0,62 × Hc, harem 0,40 × Hc, eng = Knöchel
   (+8 % bei < 50 % Dehnung). Vorder-/Hinterbein ±2 d um die Hälfte.
6. **Beinlinien:** geklemmte kubische Splines x(y) von der Schrittlinie zum Saum; ein
   Kniepunkt (halbe Beinlänge) nur bei enger Passform oder wenn `knee_total` gesetzt ist.
7. **Schrittkurve vorne:** von der Hüftlinie (vordere Mitte senkrecht) zum
   Schrittpunkt; sie trifft **rechtwinklig auf das Innenbein**.
8. **Hinterhose:** hintere Mitte oben um 15/25 mm nach innen und 15/25 mm (eng 20/35)
   erhöht; der hintere Schrittpunkt wird per Bisektion so abgesenkt, dass **Innenbein
   hinten = Innenbein vorne**. Oberkante tangential, rechtwinklig zur hinteren Mitte.
   Die Seitennaht hinten wird oben angeglichen, sodass **Seitennähte gleich lang** sind.
9. **Bund:** Gummibund als doppelt gelegter Stoffstreifen, Länge = Oberkante der Hose
   (ungerafft), im Bruch zugeschnitten (halbe Länge); Gummi ≈ 0,9 × Taille.
   Alternativen: Bündchen (Verhältnis s. o.), Yogabund (60 mm × k), Tunnel (umgeschlagen).
10. **Taschen:** Eingrifftasche (Seitenteil + Taschenbeutel), schräge Eingrifftasche,
    aufgesetzte Gesäßtasche. Tascheneingriff vorne: 0,28 × Vorderhosenbreite, Tiefe an der
    Seitennaht 0,62 × R (95–170 mm).

**Fertigmaße für Reverse Engineering:** `hip_total`, `fork_factor`, `front_rise_total`,
`inseam_total`, `opening_total`, `knee_total` (alle als Option überschreibbar).

## 3. T-Shirt / Raglan (`tshirt_basic`)

1. **Brustweite** `Ct = B × (1 + Mehrweite)`, Viertel `q = Ct/4`.
2. **Halsausschnitt:** halbe Breite `nw = Hals/5 + 15`; Tiefe vorne `nw + 15/25`
   (V-Ausschnitt +60), hinten 15/20. Ausschnitt trifft rechtwinklig auf Mitte und
   Schulter. Passt der Ausschnitt (inkl. Dehnung) nicht über den Kopf, wird er
   automatisch erweitert, bis die Prüfung „Halsausschnitt passt über den Kopf“ besteht.
3. **Schulter:** Länge = Schulterbreite (+15 mm weit, +4 % Brust oversized),
   Neigung 17°.
4. **Armlochtiefe** `0,18 × Ct + 25` (+3 % Ct bei weit/oversized); das Armloch beginnt
   rechtwinklig zur Schulter und endet rechtwinklig zur Seitennaht.
5. **Länge** = Rückenlänge + 0,13 × KH (Tunika +0,12 × KH).
6. **Ärmel:** Weite = Oberarm × (1 + 8/18/30/40 %); Kugel als symmetrische Bézierkurve,
   Kugelhöhe per Bisektion auf die Ziel-Einhaltemenge. Kurzarm-Unterarmnaht ≥ 35 mm.
   Ärmelnähte vorne/hinten gleich lang, Achselecken 90°.
7. **Raglan:** Raglanlinien vom Halsausschnitt zur Achsel werden starr auf den Ärmel
   übertragen; der Ärmel-Hals ist eine Kurve rechtwinklig zu beiden Raglannähten; die
   hintere Raglannaht wird per Bisektion auf gleiche Länge gebracht.
8. **Halsbündchen:** Länge = Ausschnitt × Bündchen-Verhältnis, Breite 2 × Bündchenhöhe.

## 4. Hoodie (`hoodie`)

T-Shirt-Konstruktion mit Passform „weit“, Sweat, Bündchen an Ärmel und Saum.
**Kapuze:** Höhe `0,58 × Kopfumfang + 25`, Breite `0,44 × Kopfumfang + 15`; die
Halsnaht der Kapuze wird per Bisektion exakt auf die halbe Ausschnittlänge gebracht und
trifft rechtwinklig auf die Vorderkante (Tunnel/Beleg 25 mm). Kängurutasche: 0,62 × q
breit, Eingriffe schräg.

## 5. Rock (`skirt`)

- **Gerafft:** Rechtecke, Weite oben = max(1,6 × H, 1,25 × H), im Bruch; Bund mit Gummi.
- **A-Linie:** Weite oben 1,10 × H, Seitennaht 12° ausgestellt; Saum und Taille treffen
  rechtwinklig auf Mitte und Seitennaht (Saum in der Mitte tiefer: `L × (1/cos α − 1)`).
- **Teller:** Viertelkreis im Bruch; Innenradius `r = Weite oben / 2π`, Außenradius
  `r + Rocklänge`. Teile breiter als die Rolle werden in Bahnen gekachelt.
- Längen: mini, knie (Seitenlänge − 0,285 × KH), midi, maxi.

## 6. Mütze (`beanie`) und Loop (`loop`)

- **Beanie:** Weite = Kopfumfang × 0,86 (Maschenware ≥ 30 % Dehnung, sonst × 0,98),
  Höhe 0,36 × Kopfumfang (Slouch 0,48). 2 Teile mit runder Kuppel; die Kuppelkurve
  beginnt rechtwinklig an der Seitennaht und läuft waagerecht über die Mitte. Optional
  Umschlag (0,10 × Kopfumfang).
- **Loop:** Rechteck, Umfang 1,2 × Kopfumfang (einfach) bzw. 2,6 × Kopfumfang (doppelt
  gewickelt), Höhe 0,17 × KH (Erwachsene 30 cm), in der Höhe doppelt gelegt; Umfang inkl.
  halber Dehnung muss ≥ 1,1 × Kopfumfang sein.

## 7. Nähbarkeits-Validierung (`scripts/validate.py`)

| Prüfung | Regel |
|---|---|
| Nahtpaare gleich lang | ± 2 mm (Seitennähte, Innenbein, Schritt, Schulter, Ärmelnähte, Kapuze) |
| Bündchen ↔ Ansatzkante | Verhältnis im Bereich des Bündchenstoffs (70–85 %, Jersey bis 92 %) |
| Einreihen | Rock ↔ Bund innerhalb der gewollten Kräuselmenge |
| Ärmelkugel ↔ Armloch | Einhaltemenge im Stoffbereich (s. o.) |
| Ecken | 90° bzw. 180° (zusammengesetzt); OK ≤ 3°, Warnung ≤ 6°, sonst Fehler (zusammengesetzte Ecken +4° Toleranz) |
| Umfänge | Fertigumfang = Körpermaß + Mehrweite, ± 1 % |
| Längen | Leibhöhe, Schrittlänge, Ärmellänge plausibel zur Körperhöhe |
| Kopf | Halsausschnitt/Bund inkl. Dehnung ≥ Kopf- bzw. Hüftumfang |
| Geometrie | Kontur geschlossen, gegen den Uhrzeigersinn, nicht selbstüberschneidend; Nahtzugabe an jeder Nicht-Bruch-Kante per Normalenstrahl gemessen |
| Beschriftung | Jedes Teil hat Fadenlauf (innerhalb des Teils) und Zuschnittangabe |

Ein Fehler (❌) blockiert die Ausgabe der Druckdateien.
