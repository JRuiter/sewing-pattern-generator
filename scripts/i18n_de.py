"""German string table for i18n.py (English source text → German).

Keys with {n} are number templates (the numbers are put back in order, with a decimal
comma), keys with {s} are pattern templates whose slots are translated on their own.
Sorted roughly by topic. Construction value keys and option names stay English.
"""
from __future__ import annotations

TABLE: dict[str, str] = {
    # ------------------------------------------------------------------ numbers and units
    "{n} cm": "{n} cm", "{n} mm": "{n} mm", "{n} m": "{n} m", "{n}°": "{n}°", "{n} %": "{n} %",
    "{n} inch": "{n} Zoll", "1 inch": "1 Zoll",

    # ------------------------------------------------------------------ general
    "size {n}": "Gr. {n}", "Size {n}": "Größe {n}", "Size {s}": "Größe {s}", "made to measure": "nach Maß",
    "{s} (adjusted)": "{s} (angepasst)", "doll clothes (copied from garment)": "Puppenkleidung (vom Vorbild kopiert)",
    "copied from garment (≈ size {n})": "vom Vorbild kopiert (≈ Gr. {n})",
    "Files": "Dateien", "Printing": "Drucken", "Step": "Schritt", "Tip:": "Tipp:",
    "Do this twice.": "Zweimal machen.", "Do this three times.": "Dreimal machen.",
    "Do this four times.": "Viermal machen.", "Do this {n} times.": "{n}-mal machen.",
    "left": "links", "top": "oben", "glue to": "kleben an", "empty": "leer",
    "Page {n}/{n}": "Seite {n}/{n}", "{s} (p. {n})": "{s} (S. {n})",
    "preview (roll)": "Vorschau (Rolle)", "preview (tiles)": "Vorschau (Kacheln)",
    "preview (sheets)": "Vorschau (Bögen)", "preview (projector)": "Vorschau (Beamer)",
    "{s} sheet {n}": "{s} Bogen {n}", "A0 sheet {n}": "A0 Bogen {n}", "A1 sheet {n}": "A1 Bogen {n}",
    "A0 sheet {n} of {n} · {n} × {n} mm": "A0 Bogen {n} von {n} · {n} × {n} mm",
    "A1 sheet {n} of {n} · {n} × {n} mm": "A1 Bogen {n} von {n} · {n} × {n} mm",
    "scale {n}:{n} (unit mm)": "Maßstab {n}:{n} (Einheit mm)",
    "sewing instructions": "Nähanleitung", "Sewing instructions": "Nähanleitung",
    "Sewing": "Nähen", "What you need": "Das brauchst du",
    "Original parametric draft · sew a test garment first": "Eigene parametrische Konstruktion · zuerst ein Probeteil nähen",
    "Original parametric draft. Sew a test garment the first time you use this pattern.":
        "Eigene parametrische Konstruktion. Nähe beim ersten Mal ein Probeteil.",
    "original parametric draft. The pattern is yours to use.":
        "eigene parametrische Konstruktion. Du darfst den Schnitt frei verwenden.",
    "**Important:** With a new pattern, first sew a **test garment** from inexpensive fabric with similar stretch "
    "and check the fit.":
        "**Wichtig:** Nähe bei einem neuen Schnitt zuerst ein **Probeteil** aus günstigem Stoff mit ähnlicher "
        "Dehnbarkeit und prüfe die Passform.",
    "VALIDATION FAILED: no print files were written.": "PRÜFUNG FEHLGESCHLAGEN: es wurden keine Druckdateien geschrieben.",

    # ------------------------------------------------------------------ file list
    "SVG master {n}:{n}": "SVG-Master {n}:{n}", "Cutting layout": "Zuschnittplan",
    "Sewing instructions (PDF)": "Nähanleitung (PDF)", "Sewing instructions (Markdown)": "Nähanleitung (Markdown)",
    "Pattern data (JSON)": "Schnittdaten (JSON)", "PDF A4 tiles to glue ({n} pages + overview)":
        "PDF A4-Kacheln zum Kleben ({n} Seiten + Übersicht)",
    "PDF LETTER tiles to glue ({n} pages + overview)": "PDF Letter-Kacheln zum Kleben ({n} Seiten + Übersicht)",
    "Preview A4 tiles": "Vorschau A4-Kacheln", "Preview LETTER tiles": "Vorschau Letter-Kacheln",
    "PDF roll {n} mm ({n} × {n} mm)": "PDF Rolle {n} mm ({n} × {n} mm)", "Preview roll {n} mm": "Vorschau Rolle {n} mm",
    "PDF roll {n} mm, {n} strips of {n} cm to glue (piece wider than the roll)":
        "PDF Rolle {n} mm, {n} Streifen à {n} cm zum Kleben (Teil breiter als die Rolle)",
    "PDF A0 ({n} sheet(s))": "PDF A0 ({n} Bogen)", "PDF A1 ({n} sheet(s))": "PDF A1 ({n} Bogen)",
    "PDF A0 ({n} sheet(s), oversized pieces tiled)": "PDF A0 ({n} Bogen, übergroße Teile gekachelt)",
    "PDF A1 ({n} sheet(s), oversized pieces tiled)": "PDF A1 ({n} Bogen, übergroße Teile gekachelt)",
    "Preview A0": "Vorschau A0", "Preview A1": "Vorschau A1",
    "PDF projector, {n} page {n}:{n} ({n} × {n} mm)": "PDF Beamer, {n} Seite {n}:{n} ({n} × {n} mm)",
    "PDF projector (dark), {n} page {n}:{n} ({n} × {n} mm)": "PDF Beamer (dunkel), {n} Seite {n}:{n} ({n} × {n} mm)",
    "DXF for cutters/CAD (AAMA layers, mm, {n}:{n})": "DXF für Cutter/CAD (AAMA-Layer, mm, {n}:{n})",
    "Body measurements (XML measurement file)": "Körpermaße (XML-Maßdatei)",

    # ------------------------------------------------------------------ printing
    "Always print at **{n} % / \"Actual size\"** (not \"Fit to page\").":
        "Immer mit **{n} % / „Tatsächliche Größe“** drucken (nicht „An Seite anpassen“).",
    "Measure the **{n} × {n} cm** control square before you cut.":
        "Miss vor dem Zuschneiden das **{n} × {n} cm**-Kontrollquadrat nach.",
    "Measure the **{n} × {n} cm** control square (or the **1 inch** square) before you cut.":
        "Miss vor dem Zuschneiden das **{n} × {n} cm**-Kontrollquadrat (oder das **1-Zoll**-Quadrat) nach.",
    "Plotter ({n} mm roll): the page is {n} mm wide in portrait. In the print dialog choose a custom paper size "
    "with exactly this width and length, and turn rotation/scaling off.":
        "Plotter ({n}-mm-Rolle): die Seite ist {n} mm breit, Hochformat. Wähle im Druckdialog ein eigenes "
        "Papierformat mit genau dieser Breite und Länge und schalte Drehen/Skalieren aus.",
    "Print at {n} % / \"Actual size\". Do NOT use \"Fit to page\".":
        "Mit {n} % / „Tatsächliche Größe“ drucken. NICHT „An Seite anpassen“.",
    "Print at {n} % / actual size. Measure the {n} × {n} cm control square.":
        "Mit {n} % / tatsächlicher Größe drucken. Das {n} × {n} cm-Kontrollquadrat nachmessen.",
    "Measure the control square before cutting.": "Vor dem Zuschneiden das Kontrollquadrat nachmessen.",
    "Roll {n} mm · page size {n} × {n} mm (portrait) · {n} pattern pieces":
        "Rolle {n} mm · Seitengröße {n} × {n} mm (Hochformat) · {n} Schnittteile",
    "Overview · A4 tiles · {n} pages to print + this overview":
        "Übersicht · A4-Kacheln · {n} Seiten zum Drucken + diese Übersicht",
    "Overview · LETTER tiles · {n} pages to print + this overview":
        "Übersicht · Letter-Kacheln · {n} Seiten zum Drucken + diese Übersicht",
    "How to assemble:": "So klebst du zusammen:",
    "{n}. Print all pages at {n} %. Measure the control square ({n} × {n} cm).":
        "{n}. Alle Seiten mit {n} % drucken. Das Kontrollquadrat ({n} × {n} cm) nachmessen.",
    "{n}. On every page, trim the left and top margin along the dashed line.":
        "{n}. Bei jeder Seite den linken und oberen Rand an der gestrichelten Linie abschneiden.",
    "{n}. Lay the pages onto the grey glue areas of their neighbours as in the plan below:":
        "{n}. Die Seiten wie im Plan unten auf die grauen Klebeflächen der Nachbarseiten legen:",
    "   diamonds and lines must match exactly. Then glue them down.":
        "   Rauten und Linien müssen genau passen. Dann festkleben.",
    "{n}. Cut the pieces out along the solid cutting line (seam allowance is included).":
        "{n}. Die Teile an der durchgezogenen Schnittlinie ausschneiden (Nahtzugabe ist enthalten).",
    "{n}. Cut the pieces out along the solid line and add the seam allowances listed on each piece.":
        "{n}. Die Teile an der durchgezogenen Linie ausschneiden und beim Zuschneiden die auf jedem Teil "
        "genannten Nahtzugaben zugeben.",
    "Projector file · {n}:{n} · {n} × {n} mm · grid {n} cm · calibrate until the grid squares and the control "
    "square measure exactly.":
        "Beamer-Datei · {n}:{n} · {n} × {n} mm · Raster {n} cm · kalibrieren, bis Rasterquadrate und "
        "Kontrollquadrat genau stimmen.",
    "Grainline arrows are parallel to the long page edge (lay the selvage along it).":
        "Fadenlaufpfeile liegen parallel zur langen Seitenkante (Webkante daran ausrichten).",

    # ------------------------------------------------------------------ legend / piece labels
    "Cutting line (seam allowance included)": "Schnittlinie (Nahtzugabe enthalten)",
    "Seam line": "Nahtlinie", "Fold": "Bruch", "Fold-over / pressing line": "Umschlag- / Bügellinie",
    "Seam line = outline: NO seam allowance included": "Nahtlinie = Umriss: KEINE Nahtzugabe enthalten",
    "Add the allowances listed on each piece when cutting": "Beim Zuschneiden die auf jedem Teil genannten Zugaben zugeben",
    "Grainline (parallel to the selvage)": "Fadenlauf (parallel zur Webkante)",
    "Notches (single = front, double = back)": "Knipse (einfach = vorne, doppelt = hinten)",
    "Sizes (PDF layers: switch sizes on/off before printing)": "Größen (PDF-Ebenen: vor dem Drucken ein-/ausschalten)",
    "Grainline": "Fadenlauf", "place this edge on the fold": "diese Kante in den Stoffbruch legen",
    "PLACE ON FOLD": "IM BRUCH", "ON FOLD": "BRUCH", "FOLD": "BRUCH",
    "cut 1 on fold": "1× im Bruch", "cut {n} on fold": "{n}× im Bruch",
    "cut {n} (mirrored pair)": "{n}× (gegengleich)", "cut {n}": "{n}×",
    "no seam allowance": "keine Nahtzugabe", "NO seam allowance included": "KEINE Nahtzugabe enthalten",
    "NO seam allowance included: add {n} cm": "KEINE Nahtzugabe enthalten: {n} cm zugeben",
    "NO seam allowance included: add {n}\"": "KEINE Nahtzugabe enthalten: {n}\" zugeben",
    "seam allowance {n} cm included": "Nahtzugabe {n} cm enthalten",
    "Stretch direction: along the length": "Dehnrichtung: in der Länge",
    "Stretch direction: across": "Dehnrichtung: quer",

    # ------------------------------------------------------------------ fabrics and fits
    "Main fabric": "Oberstoff", "Lining": "Futter", "Rib knit": "Bündchen", "Lining: thin cotton": "Futter: dünne Baumwolle",
    "Lining: cotton jersey": "Futter: Baumwolljersey", "Main fabric or cotton jersey": "Oberstoff oder Baumwolljersey",
    "Main fabric or lining": "Oberstoff oder Futter",
    "Woven": "Webware", "Corduroy": "Cord", "Velvet": "Samt", "Jersey": "Jersey",
    "Jersey with elastane": "Jersey mit Elasthan", "Interlock": "Interlock", "Sweat / French Terry": "Sweat / French Terry",
    "Fleece": "Fleece",
    "slim / close-fitting fit": "schmale / enge Passform", "normal fit": "normale Passform", "wide fit": "weite Passform",
    "oversized fit": "Oversize-Passform", "harem (wide, dropped crotch) fit": "Haremspassform (weit, tiefer Schritt)",
    "{n} % stretch": "{n} % Dehnung",

    # ------------------------------------------------------------------ cutting layout
    "fold": "Bruch", "selvages (both layers)": "Webkanten (beide Lagen)", "unfolded: single layer": "aufgefaltet: einlagig",
    "(on fold)": "(im Bruch)", "(unfolded)": "(aufgefaltet)", "(flipped)": "(gewendet)",
    "Nap ↓, all pieces waist up": "Strich ↓, alle Teile Bund oben", "grainline / selvage": "Fadenlauf / Webkante",
    "folded (double layer)": "im Bruch (doppelt)", "single layer": "einlagig", "folded": "im Bruch",
    "{n} cm wide": "{n} cm breit", "{n}\" wide": "{n}\" breit", "needed": "Bedarf",
    "folded selvage to selvage, cut on fold pieces at the fold":
        "Webkante auf Webkante gefaltet, Bruchteile am Stoffbruch",
    "; nap: all pieces with the waist towards the same end, none turned round":
        "; Strich: alle Teile mit dem Bund zum selben Ende, keins gedreht",
    ", incl. {n} % for shrinkage": ", inkl. {n} % für Einlaufen",
    "would need {n} m": "bräuchte {n} m", "would need {s}": "bräuchte {s}",
    "about {n} m at {n} cm width": "etwa {n} m bei {n} cm Breite", "{n} m at {n} cm width": "{n} m bei {n} cm Breite",
    "Cutting layout: see `cutting_layout.png` (grainline arrow parallel to the selvage, \"flipped\" = place the "
    "piece face down, \"×{n}\" = cut through both layers of the folded fabric, which gives a mirrored pair, "
    "\"(unfolded)\" = cut-on-fold piece shown opened out).":
        "Zuschnittplan: siehe `zuschnittplan.png` (Fadenlaufpfeil parallel zur Webkante, „gewendet“ = Teil mit "
        "der bedruckten Seite nach unten auflegen, „×{n}“ = durch beide Lagen des gefalteten Stoffs schneiden, "
        "das ergibt ein gegengleiches Paar, „(aufgefaltet)“ = Bruchteil aufgeklappt gezeigt).",
    "Cut on fold": "Im Bruch zuschneiden",
    "the paper piece is only one half. Its fold edge (dash-dot line, bracket arrows \"PLACE ON FOLD\") is the "
    "centre of the piece: it gets no seam allowance and is never cut.":
        "das Papierteil ist nur eine Hälfte. Seine Bruchkante (Strich-Punkt-Linie, Klammerpfeile „IM BRUCH“) ist "
        "die Mitte des Teils: sie bekommt keine Nahtzugabe und wird nie geschnitten.",
    "On the folded fabric, lay the fold edge exactly on the fabric fold, pin it and cut through both layers; "
    "opened out you get the whole piece.":
        "Auf dem gefalteten Stoff die Bruchkante genau an den Stoffbruch legen, feststecken und durch beide Lagen "
        "schneiden; aufgeklappt ergibt das das ganze Teil.",
    "Where the cutting layout shows a piece \"(unfolded)\" on a single layer, fold the fabric along the grain "
    "just wide enough for the piece and place the fold edge on that fold, or trace the paper piece, flip it over "
    "along the fold edge and trace the second half.":
        "Wo der Zuschnittplan ein Teil „(aufgefaltet)“ einlagig zeigt, den Stoff im Fadenlauf gerade so breit "
        "falten, wie das Teil braucht, und die Bruchkante an diesen Bruch legen, oder das Papierteil "
        "abzeichnen, an der Bruchkante umklappen und die zweite Hälfte abzeichnen.",
    "{s}: the last copy is cut through the top layer only.": "{s}: das letzte Exemplar nur durch die obere Lage schneiden.",
    "Unfold the rest of the fabric for: {s} (single layer, wider than the folded fabric).":
        "Den restlichen Stoff aufklappen für: {s} (einlagig, breiter als der gefaltete Stoff).",

    # ------------------------------------------------------------------ instructions sections
    "Body measurements": "Körpermaße", "Finished measurements (virtually sewn)": "Fertigmaße (virtuell genäht)",
    "Fit adjustments (from the test garment)": "Passformänderungen (vom Probeteil)",
    "The adjustments are saved in `pattern.json` and are applied again when you generate this pattern from it "
    "(also in another size).":
        "Die Änderungen sind in `schnitt.json` gespeichert und werden wieder angewendet, wenn du den Schnitt "
        "daraus erzeugst (auch in einer anderen Größe).",
    "Pattern pieces": "Schnittteile", "Fabric needed": "Stoffverbrauch", "Your machines": "Deine Maschinen",
    "Validation report": "Prüfbericht",
    "The printed instructions (`sewing_instructions.pdf`) show every step as a picture of your pieces, IKEA "
    "style: parts list, tools, then one action per step.":
        "Die gedruckte Anleitung (`naehanleitung.pdf`) zeigt jeden Schritt als Bild deiner Teile, im IKEA-Stil: "
        "Teileliste, Werkzeug, dann eine Handlung pro Schritt.",
    "Seam allowance is included in the pattern (see table).": "Die Nahtzugabe ist im Schnitt enthalten (siehe Tabelle).",
    "**The pattern has NO seam allowance.** Add the allowances from the table when you cut.":
        "**Der Schnitt hat KEINE Nahtzugabe.** Gib beim Zuschneiden die Zugaben aus der Tabelle zu.",
    "Use a jersey/stretch needle for jersey and sweat.": "Für Jersey und Sweat eine Jersey-/Stretchnadel verwenden.",
    "Piece": "Teil", "Cutting": "Zuschnitt", "Fabric": "Stoff", "Seam allowance": "Nahtzugabe",
    "Finished measurement": "Fertigmaß", "Before": "Vorher", "After": "Nachher", "Change": "Änderung", "Value": "Wert",
    "Body measurement": "Körpermaß", "Source": "Quelle", "table": "Tabelle", "user": "Angabe", "profile": "Profil",
    "estimated from the garment": "vom Kleidungsstück geschätzt", "measurement file": "Maßdatei",
    "Adjustment": "Änderung", "Acts on": "Wirkt auf",
    "Sizes in this pattern (nested)": "Größen in diesem Schnitt (ineinander)", "Line": "Linie",
    "All sizes are drawn on top of each other, aligned at the same construction point. Every size has its own "
    "colour and line and its own **PDF layer**: in Acrobat/Reader open the *Layers* panel and switch off the "
    "sizes you do not need before printing. Cut along the line of your size. Sizes can be blended: e.g. width of "
    "one size, length of another, by drawing a smooth line between the two outlines.":
        "Alle Größen liegen übereinander, am selben Konstruktionspunkt ausgerichtet. Jede Größe hat eine eigene "
        "Farbe, Linie und **PDF-Ebene**: in Acrobat/Reader das Fenster *Ebenen* öffnen und vor dem Drucken die "
        "nicht benötigten Größen ausschalten. An der Linie deiner Größe schneiden. Größen lassen sich mischen, "
        "z. B. Weite der einen, Länge der anderen Größe, mit einer weichen Linie zwischen beiden Umrissen.",
    "Fabric, finished measurements and sewing steps below refer to the largest size":
        "Stoffverbrauch, Fertigmaße und Nähschritte unten beziehen sich auf die größte Größe",
    "the validation report has one table per size.": "der Prüfbericht hat eine Tabelle pro Größe.",
    "red": "rot", "blue": "blau", "green": "grün", "purple": "lila", "orange": "orange", "teal": "petrol",
    "brown": "braun", "grey": "grau", "solid": "durchgezogen", "long dashes": "lange Striche",
    "short dashes": "kurze Striche", "dash-dot": "Strich-Punkt", "dots": "Punkte", "dash-dot-dot": "Strich-Punkt-Punkt",
    "even dashes": "gleichmäßige Striche",

    # ------------------------------------------------------------------ body measurements
    "Body height": "Körpergröße", "Chest": "Brustumfang", "Waist": "Taillenumfang", "Hip": "Hüftumfang",
    "Head": "Kopfumfang", "Neck": "Halsumfang", "Inseam": "Innenbeinlänge", "Side length": "Seitenlänge",
    "Arm length": "Armlänge", "Back length": "Rückenlänge", "Shoulder width": "Schulterbreite", "Thigh": "Oberschenkel",
    "Ankle": "Knöchel", "Knee": "Knieumfang", "Wrist": "Handgelenk", "Upper arm": "Oberarm",
    "Measurements": "Maße",

    # ------------------------------------------------------------------ finished measurements (pants)
    "Hip width": "Hüftweite", "Thigh width": "Oberschenkelweite", "Leg width at mid-leg": "Beinweite Mitte",
    "Leg opening": "Beinsaumweite", "Waistband relaxed": "Bund entspannt",
    "Waistband stretched (pants top edge)": "Bund gedehnt (Hosenoberkante)", "Outseam": "Seitenlänge",
    "Front rise": "vordere Leibhöhe", "Back rise": "hintere Leibhöhe", "Waistband height": "Bundhöhe",
    "Cuff height": "Bündchenhöhe", "Crotch seam total": "Schrittnaht gesamt",

    # ------------------------------------------------------------------ pieces, edges, marks (pants)
    "Front leg": "Vorderhose", "Back leg": "Hinterhose", "Side panel (outer pocket bag)": "Seitenteil (äußerer Taschenbeutel)",
    "Inner pocket bag": "Innerer Taschenbeutel", "Back patch pocket": "Gesäßtasche", "Rib waistband": "Bündchenbund",
    "Waistband (elastic)": "Bund (Gummi)", "Wide yoga waistband": "Breiter Yogabund", "Leg cuff": "Beinbündchen",
    "Cargo pocket": "Cargotasche", "Cargo pocket flap": "Cargotaschenklappe",
    "Crotch seam": "Schrittnaht", "Side seam": "Seitennaht", "Hem": "Saum", "Cuff seam": "Bündchennaht",
    "Waistband seam": "Bundnaht", "Pocket opening": "Tascheneingriff", "Pocket bag seam": "Taschenbeutelnaht",
    "Pocket facing": "Taschenbeleg", "Seam edge": "Nahtkante", "Cross seam": "Quernaht", "Centre front": "vordere Mitte",
    "Fold line": "Bruchlinie", "Fold casing": "Tunnel umschlagen", "Back pocket": "Gesäßtasche",
    "Back pocket (right back leg only)": "Gesäßtasche (nur rechte Hinterhose)",
    "Back pocket (left back leg only)": "Gesäßtasche (nur linke Hinterhose)",
    "Fake fly (left front leg only)": "Fake-Hosenschlitz (nur linke Vorderhose)",
    "Fake fly (right front leg only)": "Fake-Hosenschlitz (nur rechte Vorderhose)",
    "Hem edge (casing)": "Saumkante (Tunnel)", "Hem edge": "Saumkante", "Turn-up fold": "Aufschlag-Bruch",
    "Flap": "Klappe", "Flap edge": "Klappenkante", "Stitching edge": "Annähkante", "Pleat fold": "Faltenbruch",
    "Pleat centre": "Faltenmitte", "{n} outer + {n} facing": "{n} außen + {n} Beleg",
    "Joggers": "Jogginghose", "Harem pants": "Haremshose", "Leggings": "Leggings", "Pull-on trousers": "Schlupfhose",
    "Pants": "Hose", "Kordhose": "Kordhose",
    "CF": "VM", "CB": "HM", "side": "Seite", "Sides": "Seiten", "Side": "Seite",

    # ------------------------------------------------------------------ pants notes
    "Fake fly on the left front leg (as worn): J line {n} cm from centre front, {n} cm long, curve radius {n} cm; "
    "two rows {n} mm apart, bar tack at the crotch seam. The stitching does not catch the crotch seam allowance; "
    "a strip of fabric (about {n} × {n} cm) underneath makes it sturdier.":
        "Fake-Hosenschlitz auf der linken Vorderhose (getragen): J-Linie {n} cm neben der vorderen Mitte, {n} cm "
        "lang, Rundung {n} cm; zwei Reihen im Abstand von {n} mm, Riegel an der Schrittnaht. Die Steppnaht "
        "erfasst die Schrittnahtzugabe nicht; ein Stoffstreifen (etwa {n} × {n} cm) darunter macht sie stabiler.",
    "Fake fly on the right front leg (as worn): J line {n} cm from centre front, {n} cm long, curve radius {n} cm; "
    "two rows {n} mm apart, bar tack at the crotch seam. The stitching does not catch the crotch seam allowance; "
    "a strip of fabric (about {n} × {n} cm) underneath makes it sturdier.":
        "Fake-Hosenschlitz auf der rechten Vorderhose (getragen): J-Linie {n} cm neben der vorderen Mitte, {n} cm "
        "lang, Rundung {n} cm; zwei Reihen im Abstand von {n} mm, Riegel an der Schrittnaht. Die Steppnaht "
        "erfasst die Schrittnahtzugabe nicht; ein Stoffstreifen (etwa {n} × {n} cm) darunter macht sie stabiler.",
    "Fake fly on the left front leg (as worn): J line {n} cm from centre front, {n} cm long, curve radius {n} cm; "
    "two rows {n} mm apart, bar tack at the crotch seam.":
        "Fake-Hosenschlitz auf der linken Vorderhose (getragen): J-Linie {n} cm neben der vorderen Mitte, {n} cm "
        "lang, Rundung {n} cm; zwei Reihen im Abstand von {n} mm, Riegel an der Schrittnaht.",
    "One back pocket, on the right back leg (as worn). The back leg piece, right side up as printed, is the right "
    "back leg.":
        "Eine Gesäßtasche, auf der rechten Hinterhose (getragen). Das Hinterhosenteil, so wie gedruckt mit der "
        "rechten Stoffseite nach oben, ist die rechte Hinterhose.",
    "One back pocket, on the left back leg (as worn). The back leg piece, right side up as printed, is the right "
    "back leg.":
        "Eine Gesäßtasche, auf der linken Hinterhose (getragen). Das Hinterhosenteil, so wie gedruckt mit der "
        "rechten Stoffseite nach oben, ist die rechte Hinterhose.",
    "Hem casing for {n} mm elastic: per leg {n} cm elastic + {n} cm overlap (try it on the child first); leave "
    "{n} cm open at the inseam.":
        "Saumtunnel für {n} mm breites Gummi: pro Bein {n} cm Gummi + {n} cm Überlappung (vorher am Kind "
        "anprobieren); an der Innenbeinnaht {n} cm offen lassen.",
    "Elastic {n} mm wide, length {n} cm (+{n} cm overlap for joining)":
        "Gummiband {n} mm breit, Länge {n} cm (+{n} cm Überlappung zum Zusammennähen)",
    "Elastic {n} mm wide, length {n} cm ({n} cm overlap for joining)":
        "Gummiband {n} mm breit, Länge {n} cm ({n} cm Überlappung zum Zusammennähen)",
    "Elastic {n} mm wide, length {n} cm ({n} cm)": "Gummiband {n} mm breit, Länge {n} cm ({n} cm)",
    "Cargo pocket {n} × {n} cm with box pleat and flap; a snap or Velcro for the flap is optional.":
        "Cargotasche {n} × {n} cm mit Kellerfalte und Klappe; Druckknopf oder Klett für die Klappe nach Wunsch.",
    "Cargo pocket {n} × {n} cm with box pleat; a snap or Velcro for the flap is optional.":
        "Cargotasche {n} × {n} cm mit Kellerfalte; Druckknopf oder Klett nach Wunsch.",
    "Cargo pocket {n} × {n} cm and flap; a snap or Velcro for the flap is optional.":
        "Cargotasche {n} × {n} cm mit Klappe; Druckknopf oder Klett für die Klappe nach Wunsch.",
    "Cargo pocket {n} × {n} cm; a snap or Velcro for the flap is optional.":
        "Cargotasche {n} × {n} cm; Druckknopf oder Klett nach Wunsch.",
    "Turn-up {n} cm: the hem allowance includes twice its height plus {n} cm to turn under.":
        "Aufschlag {n} cm: die Saumzugabe enthält die doppelte Höhe plus {n} cm zum Einschlagen.",

    # ------------------------------------------------------------------ validation
    "Sewability check": "Nähbarkeitsprüfung", "Area": "Bereich", "Check": "Prüfung", "Target": "Soll",
    "Actual": "Ist", "Result": "Ergebnis", "Note": "Hinweis", "Warning": "Warnung", "Error": "Fehler",
    "**Result:** {n} OK, {n} warning(s), {n} error(s): ": "**Ergebnis:** {n} OK, {n} Warnung(en), {n} Fehler: ",
    "the pattern is sewable.": "der Schnitt ist nähbar.", "do NOT deliver this pattern.": "diesen Schnitt NICHT ausliefern.",
    "Seam pairs": "Nahtpaare", "Angles/transitions": "Winkel/Übergänge", "Measurements ": "Maße",
    "Geometry": "Geometrie", "Labels": "Beschriftung",
    "{s}: outline & seam allowance": "{s}: Umriss & Nahtzugabe", "{s}: grainline & cutting": "{s}: Fadenlauf & Zuschnitt",
    "{s}: notches": "{s}: Knipse", "{s}: turned allowance lies flat": "{s}: umgeschlagene Zugabe liegt flach",
    "{s}: cut-on-fold edge": "{s}: Bruchkante", "{s}: corners mirrored at the fold line": "{s}: Ecken an der Bruchlinie gespiegelt",
    "closed, SA present": "geschlossen, NZ vorhanden", "ok": "ok", "present": "vorhanden",
    "on the cutting line": "auf der Schnittlinie", "{n} notch mark(s)": "{n} Knips(e)",
    "ok, corners ≤ {n}° off {n}°": "ok, Ecken ≤ {n}° von {n}° abweichend",
    "straight, no SA, {n}° corners, on grain": "gerade, ohne NZ, {n}°-Ecken, im Fadenlauf",
    "{n} at corners": "{n} an Ecken", "fixed": "fest",
    "Side seam front ↔ back": "Seitennaht vorne ↔ hinten", "Inseam front ↔ back": "Innenbeinnaht vorne ↔ hinten",
    "Front crotch seam (left ↔ right piece)": "vordere Schrittnaht (linkes ↔ rechtes Teil)",
    "Back crotch seam (left ↔ right piece)": "hintere Schrittnaht (linkes ↔ rechtes Teil)",
    "Pocket opening: front leg ↔ pocket bag": "Tascheneingriff: Vorderhose ↔ Taschenbeutel",
    "Pocket bag seam: pocket bag ↔ side panel": "Taschenbeutelnaht: Taschenbeutel ↔ Seitenteil",
    "Pocket bag ↔ side panel at the side seam": "Taschenbeutel ↔ Seitenteil an der Seitennaht",
    "Waistband ↔ pants top edge": "Bund ↔ Hosenoberkante", "Waistband ↔ pants top edge (stretched)":
        "Bund ↔ Hosenoberkante (gedehnt)", "Leg cuff ↔ leg opening (stretched)": "Beinbündchen ↔ Beinsaum (gedehnt)",
    "Centre front ↔ waistband": "vordere Mitte ↔ Bund", "Centre back ↔ waistband": "hintere Mitte ↔ Bund",
    "Crotch ↔ inseam (front + back)": "Schritt ↔ Innenbein (vorne + hinten)",
    "Inseam ↔ hem front": "Innenbein ↔ Saum vorne", "Hem ↔ side seam front": "Saum ↔ Seitennaht vorne",
    "Inseam ↔ hem back": "Innenbein ↔ Saum hinten", "Hem ↔ side seam back": "Saum ↔ Seitennaht hinten",
    "Side seam ↔ waistband back": "Seitennaht ↔ Bund hinten",
    "Side seam ↔ waistband (front + back)": "Seitennaht ↔ Bund (vorne + hinten)",
    "Side seam ↔ waistband at the side panel": "Seitennaht ↔ Bund am Seitenteil",
    "Hip circumference pattern = body + ease": "Hüftumfang Schnitt = Körper + Bewegungszugabe",
    "Top edge fits over the hip": "Oberkante passt über die Hüfte", "Front rise plausible": "vordere Leibhöhe plausibel",
    "Inseam length plausible": "Innenbeinlänge plausibel", "Foot fits through the leg opening": "Fuß passt durch den Beinsaum",
    "Fabric stretchy enough for leggings": "Stoff dehnbar genug für Leggings",
    "body {n} cm + {n} % ease": "Körper {n} cm + {n} % Zugabe", "target from measurement/override": "Soll aus Messung/Vorgabe",
    "top edge incl. usable stretch ≥ hip": "Oberkante inkl. nutzbarer Dehnung ≥ Hüfte",
    "body rise {n} cm": "Körper-Leibhöhe {n} cm", "body rise {n} cm, harem drop {n} cm":
        "Körper-Leibhöhe {n} cm, Haremsabsenkung {n} cm",
    "body inseam {n} cm": "Körper-Innenbein {n} cm", "heel-instep circumference ≈ {n} × ankle":
        "Fersen-Rist-Umfang ≈ {n} × Knöchel",
    "rib band is stretched while sewing": "Bündchen wird beim Nähen gedehnt",
    "leggings need ≥ {n} % crosswise stretch": "Leggings brauchen ≥ {n} % Querdehnung",
    "{n}–{n} % of {n} cm": "{n}–{n} % von {n} cm",

    # ------------------------------------------------------------------ construction values
    "Construction values": "Konstruktionswerte",
    "Override any of these with the option `construction`, values in mm":
        "Jeder Wert lässt sich mit der Option `construction` überschreiben, Werte in mm",
    "e.g.": "z. B.", "Name": "Name", "Derived from": "Abgeleitet aus", "overridden (drafted:": "überschrieben (konstruiert:",
    "Unknown construction value(s) ignored:": "Unbekannte Konstruktionswerte ignoriert:",
    "hip × ({n} + {n} % ease)": "Hüfte × ({n} + {n} % Zugabe)", "option {s}": "Option {s}",
    "front quarter narrower, back quarter wider by this amount": "vorderes Viertel schmaler, hinteres breiter um diesen Betrag",
    "{n} % of hip_width": "{n} % von hip_width",
    "{n} % of hip_width × fork_factor {n}": "{n} % von hip_width × fork_factor {n}",
    "(side length − inseam) + seat ease + harem drop − waistband height":
        "(Seitenlänge − Innenbein) + Sitzzugabe + Haremsabsenkung − Bundhöhe",
    "(side length − inseam) + seat ease − waistband height": "(Seitenlänge − Innenbein) + Sitzzugabe − Bundhöhe",
    "(side length − inseam) + seat ease": "(Seitenlänge − Innenbein) + Sitzzugabe",
    "(side length − inseam) + seat ease + harem drop": "(Seitenlänge − Innenbein) + Sitzzugabe + Haremsabsenkung",
    "option front_rise_total − waistband height": "Option front_rise_total − Bundhöhe",
    "inseam − allowance to the floor": "Innenbein − Abstand zum Boden",
    "inseam − allowance to the floor − harem drop": "Innenbein − Abstand zum Boden − Haremsabsenkung",
    "inseam − allowance to the floor + blousing": "Innenbein − Abstand zum Boden + Bauschzugabe",
    "inseam − allowance to the floor − harem drop + blousing":
        "Innenbein − Abstand zum Boden − Haremsabsenkung + Bauschzugabe",
    "leg opening for fit '{s}'": "Beinsaumweite für Passform '{s}'", "cuff length / cuff stretch ratio":
        "Bündchenlänge / Dehnverhältnis",
    "leg width at the knee for the shaped leg": "Beinweite am Knie für das geformte Bein",
    "tapered: {n} % of the narrower of knee and straight opening (foot must fit)":
        "schmal zulaufend: {n} % der engeren von Knie- und gerader Saumweite (Fuß muss durchpassen)",
    "bootcut: knee width + flare {n} cm": "Bootcut: Kniebreite + Ausstellung {n} cm",
    "flare: knee width + flare {n} cm": "ausgestellt: Kniebreite + Ausstellung {n} cm",

    # ------------------------------------------------------------------ machines
    "You told me you sew with:": "Du nähst mit:", "Machine": "Maschine", "Stitch": "Stich",
    "Settings": "Einstellungen", "width": "Breite", "length": "Länge",
    "Sewing machine (straight stitch and zigzag)": "Nähmaschine (Gerad- und Zickzackstich)",
    "Sewing machine with straight stitch only": "Nähmaschine nur mit Geradstich",
    "Stretch stitch on the sewing machine": "Stretchstich an der Nähmaschine", "Twin needle": "Zwillingsnadel",
    "Overlocker / serger": "Overlock", "Coverstitch machine": "Coverlock", "Hand needle": "Handnadel",
    "No sewing machine": "keine Nähmaschine", "Sewing machine": "Nähmaschine", "Overlocker": "Overlock",
    "Coverstitch": "Coverlock", "Iron": "Bügeleisen",
    "Seams": "Nähte", "Edge finish": "Versäubern", "Hems": "Säume", "Topstitching": "Absteppen",
    "Cuffs, bands, waistband": "Bündchen, Blenden, Bund",
    "There is no sewing machine, so every step that needs a straight stitch is done **by hand**: topstitching "
    "with a back stitch, hems and casings with a blind stitch, basting with a tacking stitch, bar tacks by hand, "
    "elastic ends with a box of hand stitches.":
        "Es gibt keine Nähmaschine, deshalb wird jeder Schritt, der einen Geradstich braucht, **von Hand** "
        "genäht: Absteppen mit Rückstich, Säume und Tunnel mit Blindstich, Heften mit Heftstich, Riegel von "
        "Hand, Gummienden mit einem Kästchen aus Handstichen.",
    "Seam allowance {n} mm because you sew the seams on the overlocker: guide the fabric so the knife just skims "
    "the edge.":
        "Nahtzugabe {n} mm, weil du die Nähte mit der Overlock nähst: führe den Stoff so, dass das Messer die "
        "Kante gerade streift.",
    "Seam allowance {n} mm so every seam can be sewn as a French seam ({n} mm + {n} mm).":
        "Nahtzugabe {n} mm, damit jede Naht als Französische Naht genäht werden kann ({n} mm + {n} mm).",
    "At the overlocker:": "An der Overlock:",
    "Pull pins out before they reach the knife (clips are safer at the overlocker).":
        "Stecknadeln herausziehen, bevor sie das Messer erreichen (Clips sind an der Overlock sicherer).",
    "Sew curves (crotch, pocket bag) slowly and guide only the fabric just in front of the presser foot.":
        "Rundungen (Schritt, Taschenbeutel) langsam nähen und nur den Stoff direkt vor dem Nähfuß führen.",
    "Leave a thread chain of {n} cm at the end of every seam; thread it back under the stitches with a darning "
    "needle or secure it with a drop of seam sealant.":
        "Am Ende jeder Naht {n} cm Fadenkette stehen lassen; mit einer Stopfnadel unter die Stiche zurückziehen "
        "oder mit einem Tropfen Nahtsicherung fixieren.",
    "Test the stitch on a scrap of your fabric first (two layers, same direction as the seam).":
        "Teste den Stich zuerst an einem Rest deines Stoffs (zwei Lagen, gleiche Richtung wie die Naht).",
    "No overlocker: that is fine. Sew knit seams with the narrow zigzag or stretch stitch; the fabric does not "
    "fray, so the edges need no further finishing (optional wide zigzag).":
        "Keine Overlock: kein Problem. Nähe Jerseynähte mit schmalem Zickzack- oder Stretchstich; der Stoff "
        "franst nicht, die Kanten müssen nicht weiter versäubert werden (wahlweise breiter Zickzack).",
    "A stretch twin needle ({n} mm, about {n} €) fits almost every household machine and gives hems that look "
    "like a coverstitch.":
        "Eine Stretch-Zwillingsnadel ({n} mm, etwa {n} €) passt in fast jede Haushaltsmaschine und gibt Säume, "
        "die wie Coverlock aussehen.",
    "A straight-stitch-only machine is not ideal for knits: seams can pop when stretched. Prefer a woven fabric, "
    "or use the double row of long straight stitches described below.":
        "Eine reine Geradstichmaschine ist für Jersey nicht ideal: Nähte können beim Dehnen reißen. Nimm lieber "
        "Webware oder die unten beschriebene doppelte Reihe langer Geradstiche.",
    # method texts
    "with the overlocker ({n}-thread overlock stitch, differential feed about {n} so the seam does not wave)":
        "mit der Overlock ({n}-Faden-Overlockstich, Differential etwa {n}, damit die Naht nicht wellt)",
    "with the overlocker ({n}-thread overlock stitch, differential {n})":
        "mit der Overlock ({n}-Faden-Overlockstich, Differential {n})",
    "with the overlocker ({n}-thread overlock stitch, differential feed about {n})":
        "mit der Overlock ({n}-Faden-Overlockstich, Differential etwa {n})",
    "with the overlocker ({n}-thread overlock stitch, differential feed about {n}, stretching only the band)":
        "mit der Overlock ({n}-Faden-Overlockstich, Differential etwa {n}, nur das Bündchen dehnen)",
    "with the overlocker ({n}-thread overlock stitch, differential {n}, stretching only the band)":
        "mit der Overlock ({n}-Faden-Overlockstich, Differential {n}, nur das Bündchen dehnen)",
    "with the overlocker, stretching only the band": "mit der Overlock, nur das Bündchen dehnen",
    "with the stretch stitch (lightning bolt) of the sewing machine": "mit dem Stretchstich (Blitzstich) der Nähmaschine",
    "with a narrow zigzag (width {n} mm, length {n} mm)": "mit schmalem Zickzack (Breite {n} mm, Länge {n} mm)",
    "with a long straight stitch ({n} mm), stretching the fabric slightly as you sew, and a second row {n} mm beside "
    "it (a plain straight stitch would pop when the knit stretches)":
        "mit langem Geradstich ({n} mm), den Stoff beim Nähen leicht dehnen, und einer zweiten Reihe {n} mm daneben "
        "(ein normaler Geradstich würde beim Dehnen reißen)",
    "with a straight stitch ({n} mm)": "mit Geradstich ({n} mm)",
    "as a French seam: sew wrong sides together {n} mm from the edge, trim to {n} mm, fold right sides together "
    "and sew again {n} mm from the fold":
        "als Französische Naht: links auf links {n} mm von der Kante nähen, auf {n} mm zurückschneiden, rechts auf "
        "rechts falten und {n} mm vom Bruch noch einmal nähen",
    "nothing to do: the overlock seam is already finished": "nichts zu tun: die Overlocknaht ist schon versäubert",
    "nothing to do: the overlock seam is already finished; press the allowances to one side":
        "nichts zu tun: die Overlocknaht ist schon versäubert; Zugaben zu einer Seite bügeln",
    "press both allowances to one side and finish them together with a wide zigzag (width {n} mm, length {n} mm)":
        "beide Zugaben zu einer Seite bügeln und zusammen mit breitem Zickzack versäubern (Breite {n} mm, Länge {n} mm)",
    "knit fabric does not fray: the edges can stay raw": "Jersey franst nicht: die Kanten können offen bleiben",
    "finish each allowance with the overlocker ({n}-thread) and press the seam open":
        "jede Zugabe einzeln mit der Overlock ({n}-Faden) versäubern und die Naht auseinanderbügeln",
    "finish each allowance edge with a zigzag (width {n} mm, length {n} mm, or the three-step zigzag) and press "
    "the seam open":
        "jede Zugabe mit Zickzack versäubern (Breite {n} mm, Länge {n} mm, oder Dreifach-Zickzack) und die Naht "
        "auseinanderbügeln",
    "French seams enclose the edges; where that is not possible, trim the edges with pinking shears":
        "Französische Nähte schließen die Kanten ein; wo das nicht geht, die Kanten mit der Zackenschere schneiden",
    "with the coverstitch machine from the right side ({n} needles, {n} mm apart), catching the raw edge underneath":
        "mit der Coverlock von rechts ({n} Nadeln, {n} mm Abstand), die offene Kante unten mitfassen",
    "with the coverstitch machine from the right side": "mit der Coverlock von rechts",
    "with the stretch twin needle ({n} mm) from the right side, stitch length {n} mm":
        "mit der Stretch-Zwillingsnadel ({n} mm) von rechts, Stichlänge {n} mm",
    "with the stretch stitch from the right side": "mit dem Stretchstich von rechts",
    "with a narrow zigzag (width {n} mm, length {n} mm) from the right side":
        "mit schmalem Zickzack (Breite {n} mm, Länge {n} mm) von rechts",
    "with a long straight stitch ({n} mm) while stretching the hem gently; for a hem that stretches a lot, hand-sew "
    "it with a catch stitch":
        "mit langem Geradstich ({n} mm), den Saum dabei leicht dehnen; einen Saum, der sich stark dehnt, von Hand "
        "mit Hexenstich nähen",
    "with a straight stitch ({n} mm) close to the inner fold": "mit Geradstich ({n} mm) knapp an der inneren Bruchkante",
    "with the coverstitch machine": "mit der Coverlock", "with the twin needle": "mit der Zwillingsnadel",
    "with a narrow zigzag (width {n} mm, length {n} mm) or the stretch stitch":
        "mit schmalem Zickzack (Breite {n} mm, Länge {n} mm) oder dem Stretchstich",
    "with an overlocker or a narrow zigzag/stretch stitch": "mit Overlock oder schmalem Zickzack-/Stretchstich",
    "with a straight stitch, then finish the edges": "mit Geradstich, dann die Kanten versäubern",
    "with a twin needle/coverstitch": "mit Zwillingsnadel/Coverlock", "with a straight stitch": "mit Geradstich",
    "{s}, then finish both allowances together with a wide zigzag": "{s}, dann beide Zugaben zusammen mit breitem Zickzack versäubern",
    "{s}, then finish the edges with the overlocker": "{s}, dann die Kanten mit der Overlock versäubern",
    "{s}, then finish the edges with a zigzag": "{s}, dann die Kanten mit Zickzack versäubern",
    "by hand with a back stitch (stitches {n}–{n} mm)": "von Hand mit Rückstich (Stiche {n}–{n} mm)",
    "by hand with a back stitch (stitches {n}–{n} mm, visible from the right side)":
        "von Hand mit Rückstich (Stiche {n}–{n} mm, von rechts sichtbar)",
    "overcast the edges by hand": "die Kanten von Hand umstechen",
    "by hand with a blind (hem) stitch, catching only a thread or two of the outer fabric":
        "von Hand mit Blindstich (Saumstich), nur ein, zwei Fäden des Oberstoffs fassen",
    "by hand with a blind (hem) stitch, catching only a thread or two of the outer fabric; finish the raw edge "
    "with the overlocker first":
        "von Hand mit Blindstich (Saumstich), nur ein, zwei Fäden des Oberstoffs fassen; die offene Kante vorher "
        "mit der Overlock versäubern",
    "by hand with a tacking stitch (long running stitches)": "von Hand mit Heftstich (lange Vorstiche)",
    "by hand: two rows of running stitches, pull the threads": "von Hand: zwei Reihen Vorstiche, Fäden anziehen",
    "overlap the ends and sew a box of small hand stitches through both":
        "Enden überlappen und mit kleinen Handstichen ein Kästchen durch beide nähen",
    "by hand with a back stitch": "von Hand mit Rückstich",
    "by hand: {n}–{n} stitches on top of each other, then wrap them with buttonhole stitches":
        "von Hand: {n}–{n} Stiche übereinander, dann mit Knopflochstichen umwickeln",
    "by hand, ladder stitch": "von Hand, Matratzenstich",
    "with a bar tack (dense narrow zigzag)": "mit einem Riegel (dichter schmaler Zickzack)",
    # stitches / needles
    "{n}-thread overlock": "{n}-Faden-Overlock", "{n}-thread overlock {n} × {n} mm": "{n}-Faden-Overlock {n} × {n} mm",
    "already finished": "schon versäubert", "back stitch": "Rückstich", "back stitch {n} mm": "Rückstich {n} mm",
    "blind stitch": "Blindstich", "blind stitch {n} mm": "Blindstich {n} mm", "overcast stitch": "Überwendlingsstich",
    "stretch stitch": "Stretchstich", "stretch stitch {n} mm": "Stretchstich {n} mm",
    "narrow zigzag": "schmaler Zickzack", "narrow zigzag {n} × {n} mm": "schmaler Zickzack {n} × {n} mm",
    "long straight stitch": "langer Geradstich", "long straight stitch {n} mm": "langer Geradstich {n} mm",
    "straight stitch": "Geradstich", "straight stitch {n} mm": "Geradstich {n} mm", "French seam": "Französische Naht",
    "French seam {n} mm": "Französische Naht {n} mm", "wide zigzag": "breiter Zickzack",
    "wide zigzag {n} × {n} mm": "breiter Zickzack {n} × {n} mm", "zigzag": "Zickzack", "zigzag {n} × {n} mm": "Zickzack {n} × {n} mm",
    "{n}-needle cover stitch": "{n}-Nadel-Coverstich", "{n}-needle cover stitch {n} × {n} mm": "{n}-Nadel-Coverstich {n} × {n} mm",
    "twin needle": "Zwillingsnadel", "twin needle {n} × {n} mm": "Zwillingsnadel {n} × {n} mm", "none": "keiner",
    "jersey/stretch needle {n}": "Jersey-/Stretchnadel {n}", "universal needle {n}": "Universalnadel {n}",
    "overlocker needles (ELx705 or as the manual says)": "Overlocknadeln (ELx705 oder laut Anleitung)",
    "overlocker needles": "Overlocknadeln", "coverstitch needles": "Coverlocknadeln",
    "stretch twin needle {n}/{n}": "Stretch-Zwillingsnadel {n}/{n}", "hand sewing needle, polyester thread":
        "Handnähnadel, Polyestergarn",
    "tacking stitch, {n} cm long": "Heftstich, {n} cm lang", "{n} rows of running stitch": "{n} Reihen Vorstich",
    "box of hand stitches": "Kästchen aus Handstichen", "hand bar tack": "Riegel von Hand", "ladder stitch": "Matratzenstich",
    "narrow zigzag {n} × {n} mm, {n} cm long": "schmaler Zickzack {n} × {n} mm, {n} cm lang",
    "steam": "Dampf", "steam, cotton setting": "Dampf, Stufe Baumwolle",
    "longest straight stitch, no backstitch": "längster Geradstich, nicht verriegeln",
    "{n} rows of the longest straight stitch, loose ends": "{n} Reihen längster Geradstich, Fäden lose lassen",
    "straight stitch {n} mm, stretching the elastic": "Geradstich {n} mm, Gummi dabei dehnen",
    "straight stitch {n} mm, zipper foot": "Geradstich {n} mm, Reißverschlussfuß",
    "{n}-thread overlock along the edge": "{n}-Faden-Overlock an der Kante",
    "wide zigzag {n} × {n} mm over the edge": "breiter Zickzack {n} × {n} mm über die Kante",
    "coverstitch, {n} needles": "Coverstich, {n} Nadeln", "coverstitch machine": "Coverlock",
    "twin needle {n} mm, stitch {n} mm": "Zwillingsnadel {n} mm, Stich {n} mm",
    "narrow zigzag {n} × {n} mm (or overlocker)": "schmaler Zickzack {n} × {n} mm (oder Overlock)",
    "overlocker, {n}-thread": "Overlock, {n}-Faden", "stretch stitch (lightning bolt)": "Stretchstich (Blitz)",
    "sewing machine: {s}": "Nähmaschine: {s}", "a straight stitch": "Geradstich",
    "a straight stitch, then finish the edges": "Geradstich, dann die Kanten versäubern",
    "a twin needle/coverstitch": "Zwillingsnadel/Coverlock",
    "an overlocker or a narrow zigzag/stretch stitch": "Overlock oder schmaler Zickzack-/Stretchstich",
    "the overlocker ({n}-thread overlock stitch, differential feed about {n} so the seam does not wave)":
        "Overlock ({n}-Faden-Overlockstich, Differential etwa {n}, damit die Naht nicht wellt)",

    # ------------------------------------------------------------------ booklet
    "Parts": "Teile", "Fabric and notions": "Stoff und Zubehör", "Machines and tools": "Maschinen und Werkzeug",
    "Polyester sewing thread to match": "Passendes Polyester-Nähgarn", "cut on fold": "im Bruch",
    "{n} parts · {n} steps": "{n} Teile · {n} Schritte",
    "Read the steps once before you start. Every picture is drawn from your pattern pieces.":
        "Lies die Schritte einmal durch, bevor du anfängst. Jedes Bild ist aus deinen Schnittteilen gezeichnet.",
    "right side": "rechte Stoffseite", "wrong side": "linke Stoffseite", "stitch": "nähen", "pin": "Stecknadel",
    "notch: match": "Knips: aufeinander", "Pins or clips": "Stecknadeln oder Clips", "Fabric scissors": "Stoffschere",
    "Tape measure": "Maßband", "Chalk or a fabric pen": "Kreide oder Markierstift", "Safety pin": "Sicherheitsnadel",
    "Steps are written for a sewing machine with zigzag. Have an overlocker or a coverstitch machine? Tell the "
    "generator which machines you own and the steps use them.":
        "Die Schritte sind für eine Nähmaschine mit Zickzack geschrieben. Du hast eine Overlock oder Coverlock? "
        "Sag dem Generator, welche Maschinen du hast, dann nutzen die Schritte sie.",
    "{s}: {n} at {n} width": "{s}: {n} bei {n} Breite", "{n} m at {n}\" width": "{n} m bei {n}\" Breite",

    # ------------------------------------------------------------------ diagrams
    "fold line": "Bruchlinie", "raw edges": "offene Kanten", "band folded,\nraw edges down": "Bündchen gefaltet,\noffene Kanten unten",
    "stretch": "dehnen", "pull": "ziehen", "grain": "Fadenlauf", "inside out": "links gewendet",
    "right side out": "rechts gewendet", "elastic, with a safety pin": "Gummi, mit Sicherheitsnadel",
    "ladder stitch: the stitches disappear": "Matratzenstich: die Stiche verschwinden", "pants top edge": "Hosenoberkante",
    "leg opening": "Beinsaum", "neckline": "Halsausschnitt", "skirt top edge": "Rockoberkante", "sleeve hem": "Ärmelsaum",
    "hem": "Saum", "shoulder": "Schulter", "from the neck point": "ab Halspunkt",

    # ------------------------------------------------------------------ steps: common
    "Prepare": "Vorbereiten", "Finish": "Fertigstellen", "Done!": "Fertig!",
    "Pre-wash the fabric": "Stoff vorwaschen",
    "Wash and dry it the way you will wash the garment later, so it shrinks now, not after sewing.":
        "So waschen und trocknen, wie du das Kleidungsstück später wäschst, damit er jetzt einläuft und nicht "
        "nach dem Nähen.",
    "Cut out all pieces": "Alle Teile zuschneiden",
    "Follow the cutting layout; grainline arrows parallel to the selvage.":
        "Nach dem Zuschnittplan; Fadenlaufpfeile parallel zur Webkante.",
    "Snip the notches": "Knipse einschneiden",
    "Cut {n}–{n} mm into the seam allowance at every notch.": "An jedem Knips {n}–{n} mm in die Nahtzugabe schneiden.",
    "Set up the machine": "Maschine einrichten", "Set up the overlocker": "Overlock einrichten",
    "Set up your machine": "Maschine einrichten",
    "Jersey/stretch needle {n}–{n}, polyester thread. Sew a test seam on a scrap first.":
        "Jersey-/Stretchnadel {n}–{n}, Polyestergarn. Zuerst eine Probenaht an einem Rest nähen.",
    "Universal needle {n}, polyester thread. Sew a test seam on a scrap first.":
        "Universalnadel {n}, Polyestergarn. Zuerst eine Probenaht an einem Rest nähen.",
    "Test seam on two layers of a scrap: differential {n}, stitch length {n}. Hand needle and polyester thread "
    "for the hand stitches.":
        "Probenaht an zwei Lagen eines Rests: Differential {n}, Stichlänge {n}. Handnadel und Polyestergarn für "
        "die Handstiche.",
    "Test seam on two layers of a scrap: differential {n} (knit {n}), stitch length {n}. Hand needle and "
    "polyester thread for the hand stitches.":
        "Probenaht an zwei Lagen eines Rests: Differential {n} (Jersey {n}), Stichlänge {n}. Handnadel und "
        "Polyestergarn für die Handstiche.",
    "Press all seams.": "Alle Nähte bügeln.", "Press all seams with steam.": "Alle Nähte mit Dampf bügeln.",
    "Press all seams with steam; do not press down hard on sweat.":
        "Alle Nähte mit Dampf bügeln; Sweat nicht fest andrücken.",
    "Press all seams from the wrong side on a terry towel; do not press down hard (the pile goes flat).":
        "Alle Nähte von links auf einem Frottiertuch bügeln; nicht fest andrücken (der Flor drückt sich platt).",
    "Press all seams: fleece only with a cool iron through a cloth, or not at all.":
        "Alle Nähte bügeln: Fleece nur mit kühlem Eisen durch ein Tuch, oder gar nicht.",
    "Pull the pins before they reach the knife.": "Stecknadeln herausziehen, bevor sie das Messer erreichen.",
    "Sew the curve slowly; pull the clips before they reach the knife.":
        "Die Rundung langsam nähen; Clips abnehmen, bevor sie das Messer erreichen.",
    "Sew the pieces together": "Teile zusammennähen",
    "Right sides together, matching the notches.": "Rechts auf rechts, Knipse aufeinander.",

    # ------------------------------------------------------------------ steps: pants
    "Side pockets": "Seitentaschen", "Legs": "Beine", "Crotch": "Schritt", "Waistband": "Bund",
    "Back pockets": "Gesäßtaschen", "Cargo pockets": "Cargotaschen",
    "Sew the pocket bag to the opening": "Taschenbeutel an den Eingriff nähen",
    "Inner pocket bag right sides together on the pocket opening of the front leg.":
        "Inneren Taschenbeutel rechts auf rechts auf den Tascheneingriff der Vorderhose legen.",
    "Clip and turn the bag inside": "Einschneiden und Beutel nach innen wenden",
    "Clip the curved allowance, turn the bag to the inside and press the edge.":
        "Die gerundete Zugabe einschneiden, den Beutel nach innen wenden und die Kante bügeln.",
    "Topstitch the pocket edge": "Eingriffkante absteppen",
    "Sew the pocket bag seam": "Taschenbeutelnaht nähen",
    "Side panel right sides together under the pocket bag; the \"pocket opening\" mark meets the opening edge.":
        "Seitenteil rechts auf rechts unter den Taschenbeutel; die Markierung „Tascheneingriff“ trifft die "
        "Eingriffkante.",
    "Baste the side panel to the leg": "Seitenteil an die Hose heften",
    "Top edge and side seam, inside the seam allowance.": "Oberkante und Seitennaht, innerhalb der Nahtzugabe.",
    "Hem the pocket top edge": "Taschenoberkante säumen",
    "Press {n} cm to the inside and topstitch.": "{n} cm nach innen bügeln und absteppen.",
    "Press the edges under": "Kanten umbügeln",
    "{n} cm on the other three sides.": "{n} cm an den anderen drei Seiten.",
    "{n} mm on the other three sides.": "{n} mm an den anderen drei Seiten.",
    "Stitch the pocket on": "Tasche aufnähen",
    "Stitch the pocket on (right back leg only)": "Tasche aufnähen (nur rechte Hinterhose)",
    "Stitch the pocket on (left back leg only)": "Tasche aufnähen (nur linke Hinterhose)",
    "Only ONE pocket: on the right back leg (as worn), on the marking; reinforce the top corners and leave the "
    "top open.":
        "Nur EINE Tasche: auf die rechte Hinterhose (getragen), auf die Markierung; die oberen Ecken sichern und "
        "oben offen lassen.",
    "Only ONE pocket: on the left back leg (as worn), on the marking; reinforce the top corners and leave the "
    "top open.":
        "Nur EINE Tasche: auf die linke Hinterhose (getragen), auf die Markierung; die oberen Ecken sichern und "
        "oben offen lassen.",
    "Edgestitch on the marking of the back leg; reinforce the top corners and leave the top open.":
        "Auf der Markierung der Hinterhose knappkantig aufnähen; die oberen Ecken sichern und oben offen lassen.",
    "Sew the side seams": "Seitennähte nähen",
    "Front and back leg right sides together; single notches = front, double = back.":
        "Vorder- und Hinterhose rechts auf rechts; einfache Knipse = vorne, doppelte = hinten.",
    "Finish the side seams": "Seitennähte versäubern", "Finish the inseams": "Innenbeinnähte versäubern",
    "Finish the crotch seam": "Schrittnaht versäubern",
    "Both allowances together, then press them towards the back.": "Beide Zugaben zusammen, dann nach hinten bügeln.",
    "Sew the inseams": "Innenbeinnähte nähen", "The notches on the inseam meet.": "Die Knipse am Innenbein treffen sich.",
    "Put one leg inside the other": "Ein Bein ins andere stecken",
    "Turn one leg right side out and slip it into the other (wrong side out): the legs lie right sides together.":
        "Ein Bein auf rechts wenden und in das andere (links gewendete) stecken: die Beine liegen rechts auf rechts.",
    "Sew the crotch seam": "Schrittnaht nähen",
    "In one go from the front to the back top edge; the inseams meet exactly.":
        "In einem Zug von der vorderen zur hinteren Oberkante; die Innenbeinnähte treffen sich genau.",
    "Sew the crotch curve a second time for strength.": "Die Schrittrundung zur Sicherheit ein zweites Mal nähen.",
    "Sew the curve slowly, clips off before the knife.": "Die Rundung langsam nähen, Clips vor dem Messer abnehmen.",
    "Topstitch the fake fly": "Fake-Hosenschlitz absteppen", "Topstitch the fake fly by hand": "Fake-Hosenschlitz von Hand absteppen",
    "Only on the left front leg (as worn), before the waistband: two rows {n} mm apart along the J line ({n} cm "
    "from centre front, {n} cm long), bar tack at the crotch seam.":
        "Nur auf der linken Vorderhose (getragen), vor dem Bund: zwei Reihen im Abstand von {n} mm entlang der "
        "J-Linie ({n} cm neben der vorderen Mitte, {n} cm lang), Riegel an der Schrittnaht.",
    "Only on the left front leg (as worn), before the waistband: two rows {n} mm apart along the J line ({n} cm "
    "from centre front, {n} cm long), hand bar tack at the crotch seam.":
        "Nur auf der linken Vorderhose (getragen), vor dem Bund: zwei Reihen im Abstand von {n} mm entlang der "
        "J-Linie ({n} cm neben der vorderen Mitte, {n} cm lang), Riegel von Hand an der Schrittnaht.",
    "Only on the right front leg (as worn), before the waistband: two rows {n} mm apart along the J line ({n} cm "
    "from centre front, {n} cm long), bar tack at the crotch seam.":
        "Nur auf der rechten Vorderhose (getragen), vor dem Bund: zwei Reihen im Abstand von {n} mm entlang der "
        "J-Linie ({n} cm neben der vorderen Mitte, {n} cm lang), Riegel an der Schrittnaht.",
    "Only on the right front leg (as worn), before the waistband: two rows {n} mm apart along the J line ({n} cm "
    "from centre front, {n} cm long), hand bar tack at the crotch seam.":
        "Nur auf der rechten Vorderhose (getragen), vor dem Bund: zwei Reihen im Abstand von {n} mm entlang der "
        "J-Linie ({n} cm neben der vorderen Mitte, {n} cm lang), Riegel von Hand an der Schrittnaht.",
    "The stitching does not catch the crotch seam allowance: pin a strip of fabric (about {n} × {n} cm) "
    "underneath for strength.":
        "Die Steppnaht erfasst die Schrittnahtzugabe nicht: einen Stoffstreifen (etwa {n} × {n} cm) zur "
        "Verstärkung darunter stecken.",
    "The stitching catches the crotch seam allowance.": "Die Steppnaht erfasst die Schrittnahtzugabe.",
    "Close the waistband into a ring": "Bund zum Ring schließen",
    "Right sides together across the short ends (centre back).": "Rechts auf rechts an den kurzen Enden (hintere Mitte).",
    "Right sides together across the short ends (centre back); leave {n} cm open for the elastic.":
        "Rechts auf rechts an den kurzen Enden (hintere Mitte); {n} cm für das Gummi offen lassen.",
    "Right sides together across the short ends (centre back); leave {n} mm open for the elastic.":
        "Rechts auf rechts an den kurzen Enden (hintere Mitte); {n} mm für das Gummi offen lassen.",
    "Fold the waistband in half": "Bund längs falten", "Lengthwise, wrong sides together.": "Längs, links auf links.",
    "Lengthwise, wrong sides together, along the fold line.": "Längs, links auf links, an der Bruchlinie.",
    "Mark quarters": "Viertel markieren",
    "On waistband and pants top edge: centre front, centre back, sides.":
        "An Bund und Hosenoberkante: vordere Mitte, hintere Mitte, Seiten.",
    "Sew the waistband on": "Bund annähen", "Right sides together, cross seam at centre back.":
        "Rechts auf rechts, Quernaht in der hinteren Mitte.",
    "Stretch only the waistband, not the pants.": "Nur den Bund dehnen, nicht die Hose.",
    "Raw edges together, opening at the back on the inside; quarter marks meet.":
        "Offene Kanten aufeinander, Öffnung hinten innen; Viertelmarkierungen treffen sich.",
    "Thread the elastic": "Gummi einziehen",
    "With a safety pin through the opening; overlap the ends by {n} cm and sew them together.":
        "Mit einer Sicherheitsnadel durch die Öffnung; die Enden {n} cm überlappen und zusammennähen.",
    "With a safety pin through the opening; overlap the ends by {n} mm and sew them together.":
        "Mit einer Sicherheitsnadel durch die Öffnung; die Enden {n} mm überlappen und zusammennähen.",
    "Close the opening": "Öffnung schließen",
    "Spread the gathers evenly, close the opening and stitch in the ditch at the side seams so the elastic cannot "
    "twist.":
        "Die Kräuselung gleichmäßig verteilen, die Öffnung schließen und an den Seitennähten in der Naht "
        "steppen, damit sich das Gummi nicht verdreht.",
    "Press the top edge under": "Oberkante umbügeln", "{n} mm to the wrong side.": "{n} mm nach links.",
    "{n} cm to the wrong side.": "{n} cm nach links.",
    "Sew the elastic casing": "Gummitunnel nähen",
    "Fold along the \"fold casing\" line and edgestitch; leave {n} cm open.":
        "An der Linie „Tunnel umschlagen“ falten und knappkantig steppen; {n} cm offen lassen.",
    "With a safety pin; sew the ends together with an overlap and close the opening.":
        "Mit einer Sicherheitsnadel; die Enden überlappend zusammennähen und die Öffnung schließen.",
    "Close the cuffs into rings": "Bündchen zu Ringen schließen",
    "Right sides together across the short ends.": "Rechts auf rechts an den kurzen Enden.",
    "Fold the cuffs in half": "Bündchen längs falten", "On cuff and leg opening.": "An Bündchen und Beinsaum.",
    "Sew the cuffs on": "Bündchen annähen",
    "Slip the cuff over the right-side-out leg, cuff seam at the inseam.":
        "Das Bündchen über das rechts gewendete Bein ziehen, Bündchennaht an der Innenbeinnaht.",
    "Press the allowance up": "Zugabe nach oben bügeln", "Seam allowance towards the pants.": "Nahtzugabe zur Hose.",
    "Sew the hem": "Saum nähen", "Press {n} cm to the inside.": "{n} cm nach innen bügeln.",
    "Press {n} cm under and sew it down.": "{n} cm einschlagen und festnähen.",
    "Fold the turn-up": "Aufschlag falten",
    "Fold the leg to the inside along the \"Hem edge\", then fold the turn-up back out along the \"Turn-up fold\"; "
    "tack it at the side seam and inseam.":
        "Das Bein an der „Saumkante“ nach innen falten, dann den Aufschlag an der Linie „Aufschlag-Bruch“ "
        "wieder nach außen falten; an Seiten- und Innenbeinnaht festheften.",
    "Sew the hem casing": "Saumtunnel nähen",
    "Press {n} mm under, then {n} cm to the inside; sew close to the inner fold; leave {n} cm open at the inseam.":
        "{n} mm einschlagen, dann {n} cm nach innen; knapp an der inneren Bruchkante nähen; an der "
        "Innenbeinnaht {n} cm offen lassen.",
    "Finish the raw edge with the overlocker, fold {n} cm to the inside once and sew along the finished edge; "
    "leave {n} cm open at the inseam.":
        "Die offene Kante mit der Overlock versäubern, {n} cm einmal nach innen falten und entlang der "
        "versäuberten Kante nähen; an der Innenbeinnaht {n} cm offen lassen.",
    "Keep the casing free: do not catch the elastic channel.": "Tunnel frei halten: den Gummikanal nicht mitfassen.",
    "{n} cm per leg + {n} cm overlap (fit it on the child): thread it with a safety pin, overlap the ends {n} cm "
    "and sew them together, then close the opening.":
        "{n} cm pro Bein + {n} cm Überlappung (am Kind anpassen): mit einer Sicherheitsnadel einziehen, die "
        "Enden {n} cm überlappen und zusammennähen, dann die Öffnung schließen.",
    "Do not twist the elastic.": "Das Gummi nicht verdrehen.",
    "Bring both \"pleat fold\" lines to the pleat centre on the wrong side, press, baste across top and bottom.":
        "Beide Linien „Faltenbruch“ auf der linken Seite zur Faltenmitte legen, bügeln, oben und unten quer heften.",
    "Fold the box pleat": "Kellerfalte legen",
    "Edgestitch on the \"Cargo pocket\" marking; reinforce the top corners.":
        "Auf der Markierung „Cargotasche“ knappkantig aufnähen; die oberen Ecken sichern.",
    "Sew, turn and topstitch the flap": "Klappe nähen, wenden und absteppen",
    "Outer flap and facing right sides together along sides and flap edge, trim, turn, press.":
        "Klappe und Beleg rechts auf rechts an Seiten und Klappenkante nähen, zurückschneiden, wenden, bügeln.",
    "Sew the flap on": "Klappe annähen",
    "Open edge on the \"Flap\" line, upside down; fold it down and topstitch {n} mm from the fold.":
        "Offene Kante an der Linie „Klappe“, kopfüber; nach unten klappen und {n} mm vom Bruch absteppen.",
    "Press {n} cm to the inside and topstitch": "{n} cm nach innen bügeln und absteppen",
}

# T-shirt, hoodie, skirt, dress, beanie, loop, doll clothes
TABLE.update({
    "sizes {n} · {n}": "Größen {n} · {n}",
    "sizes {n} · {n} · {n}": "Größen {n} · {n} · {n}",
    "sizes {n} · {n} · {n} · {n}": "Größen {n} · {n} · {n} · {n}",
    "sizes {n} · {n} · {n} · {n} · {n}": "Größen {n} · {n} · {n} · {n} · {n}",
    "{n} % of chest_width + {n} cm": "{n} % von chest_width + {n} cm",
    "{n} % of chest_width + {n} cm + {n} %": "{n} % von chest_width + {n} cm + {n} %",
    "{n} % of chest_width + {n} cm + {n} %, limited to option armhole_depth_max":
        "{n} % von chest_width + {n} cm + {n} %, begrenzt durch Option armhole_depth_max",
    "{n}× main fabric + {n}× lining (jersey)": "{n}× Oberstoff + {n}× Futter (Jersey)",
    "{n} außen + {n} Beleg": "{n} außen + {n} Beleg",
    "Armhole": "Armloch",
    "Armhole ↔ sleeve cap (ease)": "Armloch ↔ Ärmelkugel (Mehrweite)",
    "Back": "Rückenteil",
    "Back opening": "Rückenschlitz",
    "Back opening (turn under)": "Rückenschlitz (einschlagen)",
    "Back skirt": "Rockteil hinten",
    "Band: cross seam = centre back. Neckline: centre front, centre back, shoulders.":
        "Bündchen: Quernaht = hintere Mitte. Halsausschnitt: vordere Mitte, hintere Mitte, Schultern.",
    "Band: cross seam at a side seam.": "Bündchen: Quernaht an einer Seitennaht.",
    "Beanie": "Beanie",
    "Beanie height": "Mützenhöhe",
    "Beanie fits over the head": "Mütze passt über den Kopf",
    "Beanie stays on (not too loose)": "Mütze hält (nicht zu weit)",
    "Beanie width (relaxed)": "Mützenweite (ungedehnt)",
    "Body length plausible": "Körperlänge plausibel",
    "Both allowances together; press them towards the back.": "Beide Zugaben zusammen; zum Rückenteil bügeln.",
    "Both centre back edges.": "Beide Kanten der hinteren Mitte.",
    "Both pieces right sides together; in one go.": "Beide Teile rechts auf rechts; in einem Zug.",
    "Bottom edge ↔ side": "Unterkante ↔ Seite",
    "Bottom end": "Unteres Ende",
    "Bottom right corner": "Ecke unten rechts",
    "Brim": "Umschlag",
    "Brim seam": "Umschlagnaht",
    "Brim seam at the back seam; quarter both with pins.": "Umschlagnaht an der hinteren Naht; beide mit Nadeln vierteln.",
    "Brim ↔ beanie edge (stretched)": "Umschlag ↔ Mützenkante (gedehnt)",
    "Centre": "Mitte",
    "Centre (fold)": "Mitte (Bruch)",
    "Centre back seam": "Naht hintere Mitte",
    "Centre front (zip)": "Vordere Mitte (Reißverschluss)",
    "Centre front, centre back, sides.": "Vordere Mitte, hintere Mitte, Seiten.",
    "Chest circumference pattern = body + ease": "Brustumfang Schnitt = Körper + Mehrweite",
    "Chest width": "Brustbreite",
    "Circle skirt": "Tellerrock",
    "Circle skirt back": "Tellerrock hinten",
    "Circle skirt front": "Tellerrock vorne",
    "Circumference": "Umfang",
    "Close the brim into a ring": "Umschlag zum Ring schließen",
    "Close the hem band into a ring": "Saumbündchen zum Ring schließen",
    "Close the neckband into a ring": "Halsbündchen zum Ring schließen",
    "Close the opening by hand": "Wendeöffnung von Hand schließen",
    "Cover the seam allowance with jersey binding or finish it.": "Nahtzugabe mit Jerseyschrägband einfassen oder versäubern.",
    "Cross seam (right ↔ left)": "Quernaht (rechts ↔ links)",
    "Crown seam": "Scheitelnaht",
    "Crown seam front ↔ back": "Scheitelnaht vorne ↔ hinten",
    "Cuff seam at the sleeve seam; quarter cuff and sleeve hem with pins.":
        "Bündchennaht an der Ärmelnaht; Bündchen und Ärmelsaum mit Nadeln vierteln.",
    "Cuffs": "Bündchen",
    "Doll clothes: narrow seam allowances ({n} mm). Sew with a short stitch ({n}–{n} mm) and finish woven edges "
    "with pinking shears, a narrow zigzag or a little fray stop.":
        "Puppenkleidung: schmale Nahtzugaben ({n} mm). Mit kurzer Stichlänge ({n}–{n} mm) nähen und Webstoffkanten "
        "mit der Zackenschere, einem schmalen Zickzack oder etwas Fransenstopp versäubern.",
    "Dress fits over the hip": "Kleid passt über die Hüfte",
    "Dress goes on through the back opening": "Kleid geht durch den Rückenschlitz an",
    "Dress length from neck point": "Kleidlänge ab Halspunkt",
    "Dress length plausible": "Kleidlänge plausibel",
    "Dress with gathered skirt": "Kleid mit gekräuseltem Rock",
    "Elastic {n} cm, joined into a ring, onto the waist seam allowance, stretching it evenly; press the seam up.":
        "Gummiband {n} cm, zum Ring geschlossen, gleichmäßig gedehnt auf die Nahtzugabe der Taillennaht nähen; "
        "Naht nach oben bügeln.",
    "Elastic for the waist seam: {n} mm wide, {n} cm ({n} cm overlap).":
        "Gummiband für die Taillennaht: {n} mm breit, {n} cm ({n} cm Überlappung).",
    "End": "Ende",
    "Finish the armhole seams": "Armlochnähte versäubern",
    "Finish the neck seam": "Halsnaht versäubern",
    "Finish the opening edges": "Schlitzkanten versäubern",
    "Finish the shoulder seams": "Schulternähte versäubern",
    "Finish the skirt side seams": "Seitennähte des Rocks versäubern",
    "Fold along the \"fold casing\" line and edgestitch; leave {n} mm open.":
        "An der Linie „Tunnel falten“ umlegen und knappkantig absteppen; {n} mm offen lassen.",
    "Fold lengthwise right sides together; sew into a tube.": "Längs rechts auf rechts falten; zum Schlauch nähen.",
    "Fold the binding in half": "Schrägband zur Hälfte falten",
    "Fold the brim in half": "Umschlag zur Hälfte falten",
    "Fold the ends in, turn the binding to the inside over the allowance and stitch close to the fold.":
        "Enden einschlagen, das Schrägband über die Zugabe nach innen legen und knapp an der Bruchkante steppen.",
    "Fold the hem band in half": "Saumbündchen zur Hälfte falten",
    "Fold the neckband in half": "Halsbündchen zur Hälfte falten",
    "From the hem up to the notch; above the notch it stays open (continues the back opening).":
        "Vom Saum bis zum Knipser; oberhalb bleibt sie offen (setzt den Rückenschlitz fort).",
    "Front": "Vorderteil",
    "Front (left and right)": "Vorderteil (links und rechts)",
    "Front and back right sides together.": "Vorder- und Rückenteil rechts auf rechts.",
    "Front and back skirt right sides together.": "Vorderes und hinteres Rockteil rechts auf rechts.",
    "Front edge (casing/facing)": "Vorderkante (Tunnel/Beleg)",
    "Front edge (towards the zip)": "Vorderkante (zum Reißverschluss)",
    "Front edge fold line": "Bruchlinie Vorderkante",
    "Front edge on the centre front edge; stitch top edge and side. Bottom and front edge are caught in the hem "
    "band and zip seams.":
        "Vorderkante an der Kante der vorderen Mitte; Oberkante und Seite absteppen. Unter- und Vorderkante werden "
        "in den Nähten von Saumbündchen und Reißverschluss mitgefasst.",
    "Front end (zip)": "Vorderes Ende (Reißverschluss)",
    "Front opening (zip)": "Vorderer Verschluss (Reißverschluss)",
    "Front pocket": "Vordertasche",
    "Front skirt": "Rockteil vorne",
    "Gather the skirt top edge": "Rockoberkante einkräuseln",
    "Gather the top edge": "Oberkante einkräuseln",
    "Gathered skirt": "Kräuselrock",
    "Hand fits through the sleeve cuff": "Hand passt durch das Ärmelbündchen",
    "Head fits through the back opening": "Kopf passt durch den Rückenschlitz",
    "Height (double layer)": "Höhe (doppellagig)",
    "Hem (narrow)": "Saum (schmal)",
    "Hem at centre front": "Saum an der vorderen Mitte",
    "Hem band": "Saumbündchen",
    "Hem band ↔ hem (stretched)": "Saumbündchen ↔ Saum (gedehnt)",
    "Hem seam": "Saumnaht",
    "Hem the hood front edge": "Vorderkante der Kapuze säumen",
    "Hem the pocket openings": "Tascheneingriffe säumen",
    "Hem the sleeves": "Ärmel säumen",
    "Hem width": "Saumweite",
    "Hem ↔ side seam": "Saum ↔ Seitennaht",
    "Hood": "Kapuze",
    "Hood centre seam": "Kapuzenmittelnaht",
    "Hood centre seam (left ↔ right)": "Kapuzenmittelnaht (links ↔ rechts)",
    "Hood height": "Kapuzenhöhe",
    "Hood pieces right sides together.": "Kapuzenteile rechts auf rechts.",
    "Hood right sides together to the neckline: centre seam at centre back, front edges end exactly at the centre "
    "front edges.":
        "Kapuze rechts auf rechts an den Halsausschnitt: Mittelnaht an der hinteren Mitte, die Vorderkanten enden "
        "genau an den Kanten der vorderen Mitte.",
    "Hood right sides together to the neckline: centre seam at centre back, front edges meet at centre front "
    "(overlap {n} cm if needed).":
        "Kapuze rechts auf rechts an den Halsausschnitt: Mittelnaht an der hinteren Mitte, die Vorderkanten treffen "
        "sich an der vorderen Mitte (bei Bedarf {n} cm überlappen).",
    "Hood tall enough": "Kapuze hoch genug",
    "Hood ↔ neckline (each side)": "Kapuze ↔ Halsausschnitt (je Seite)",
    "Hood: front edge ↔ neck seam": "Kapuze: Vorderkante ↔ Halsnaht",
    "Hoodie": "Hoodie",
    "In one go from the hem over the underarm to the sleeve hem; the underarm seams meet exactly.":
        "In einem Zug vom Saum über die Achsel bis zum Ärmelsaum; die Achselnähte treffen genau aufeinander.",
    "Jersey: {n}–{n} mm": "Jersey: {n}–{n} mm",
    "Join hood and lining": "Kapuze und Futter verbinden",
    "Kangaroo pocket": "Kängurutasche",
    "Length from neck point": "Länge ab Halspunkt",
    "Lengthwise, wrong sides together; press.": "Längs, links auf links; bügeln.",
    "Let the skirt hang for {n} h": "Rock {n} Std. hängen lassen",
    "Lining inside, press the front edge.": "Futter nach innen, Vorderkante bügeln.",
    "Long edge": "Lange Kante",
    "Long edges together": "Lange Kanten aufeinander",
    "Loop": "Loop",
    "Loop fits over the head": "Loop passt über den Kopf",
    "Neck binding (bias)": "Halsschrägband",
    "Neck binding ↔ neckline": "Halsschrägband ↔ Halsausschnitt",
    "Neck seam": "Halsnaht",
    "Neckband": "Halsbündchen",
    "Neckband ↔ neckline (stretched)": "Halsbündchen ↔ Halsausschnitt (gedehnt)",
    "Neckline": "Halsausschnitt",
    "Neckline (fabric edge) fits over the head": "Halsausschnitt (Stoffkante) passt über den Kopf",
    "Neckline at centre back": "Halsausschnitt an der hinteren Mitte",
    "Neckline at centre front": "Halsausschnitt an der vorderen Mitte",
    "Neckline circumference": "Halsausschnittumfang",
    "Neckline fits over the head": "Halsausschnitt passt über den Kopf",
    "On the marking; stitch top edge and sides. The bottom edge is caught by the hem band.":
        "Auf die Markierung; Oberkante und Seiten absteppen. Die Unterkante fasst das Saumbündchen mit.",
    "Opening (hem it)": "Öffnung (säumen)",
    "Optional, gives a flat, professional neckline.": "Optional, ergibt einen flachen, sauberen Halsausschnitt.",
    "Pin the zip": "Reißverschluss feststecken",
    "Pocket": "Tasche",
    "Press {n} cm to the inside and stitch it down.": "{n} cm nach innen bügeln und feststeppen.",
    "Press {n} cm under and topstitch.": "{n} cm einschlagen und absteppen.",
    "Press {n} mm to the inside.": "{n} mm nach innen bügeln.",
    "Press {n} cm to the inside; ease a curved hem in with steam.": "{n} cm nach innen bügeln; einen runden Saum mit Dampf einhalten.",
    "Press the allowance down and topstitch": "Zugabe nach unten bügeln und absteppen",
    "Press the allowance under twice and stitch.": "Zugabe doppelt einschlagen und steppen.",
    "Press the allowances away from the zip.": "Zugaben vom Reißverschluss weg bügeln.",
    "Press to the inside along the fold line and topstitch (room for a drawstring).":
        "An der Bruchlinie nach innen bügeln und absteppen (Platz für eine Kordel).",
    "Press under twice by {n} cm.": "Zweimal {n} cm einschlagen und bügeln.",
    "Pull the elastic through with a small safety pin; for very small dolls a thin elastic cord also works.":
        "Das Gummi mit einer kleinen Sicherheitsnadel einziehen; bei sehr kleinen Puppen geht auch Gummikordel.",
    "Raglan seam": "Raglannaht",
    "Raglan seam back": "Raglannaht hinten",
    "Raglan seam back: back ↔ sleeve": "Raglannaht hinten: Rückenteil ↔ Ärmel",
    "Raglan seam front": "Raglannaht vorne",
    "Raglan seam front: front ↔ sleeve": "Raglannaht vorne: Vorderteil ↔ Ärmel",
    "Raglan sleeve": "Raglanärmel",
    "Raw edges": "Offene Kanten",
    "Raw edges (into the zip seam)": "Offene Kanten (in die Reißverschlussnaht)",
    "Raw edges to the neckline, right sides together; let each end stick out past the opening edge by the allowance.":
        "Offene Kanten rechts auf rechts an den Halsausschnitt; jedes Ende um die Zugabe über die Schlitzkante "
        "hinausstehen lassen.",
    "Right side out.": "Rechte Seite nach außen.",
    "Right sides together across the short ends (centre back); leave {n} cm open.":
        "Rechts auf rechts an den kurzen Enden (hintere Mitte); {n} cm offen lassen.",
    "Right sides together along the front edge; sew, then turn the lining inside.":
        "Rechts auf rechts entlang der Vorderkante nähen, dann das Futter nach innen wenden.",
    "Right sides together, raw edges meet, opening on the inside.": "Rechts auf rechts, offene Kanten aufeinander, Öffnung innen.",
    "Right sides together, raw edges meet.": "Rechts auf rechts, offene Kanten aufeinander.",
    "Right sides together, raw edges meet; band ends flush with the front edges.":
        "Rechts auf rechts, offene Kanten aufeinander; die Bündchenenden bündig mit den Vorderkanten.",
    "Right sides together, raw edges meet; stretch the band, not the neckline.":
        "Rechts auf rechts, offene Kanten aufeinander; das Bündchen dehnen, nicht den Ausschnitt.",
    "Separate the {n} cm zip; each half right sides together on a centre front edge, teeth towards the body, top "
    "stop just below the neck seam, bottom flush with the hem band.":
        "Den {n}-cm-Reißverschluss teilen; jede Hälfte rechts auf rechts an eine Kante der vorderen Mitte, Zähnchen "
        "zum Körper, oberer Stopper knapp unter der Halsnaht, unten bündig mit dem Saumbündchen.",
    "Separating (jacket) zip, {n} cm long (front opening {n} cm incl. hem band).":
        "Teilbarer (Jacken-)Reißverschluss, {n} cm lang (vordere Öffnung {n} cm inkl. Saumbündchen).",
    "Set in the sleeves": "Ärmel einsetzen",
    "Sew a narrow hem": "Schmalen Saum nähen",
    "Sew in the elastic": "Gummiband einnähen",
    "Sew on the Velcro": "Klettband aufnähen",
    "Sew side and crown seams": "Seiten- und Scheitelnähte nähen",
    "Sew side and sleeve seams": "Seiten- und Ärmelnähte nähen",
    "Sew skirt and bodice together": "Rock und Oberteil zusammennähen",
    "Sew the brim on": "Umschlag annähen",
    "Sew the cross seam": "Quernaht nähen",
    "Sew the hem band on": "Saumbündchen annähen",
    "Sew the hood centre seam": "Kapuzenmittelnaht nähen",
    "Sew the hood on": "Kapuze annähen",
    "Sew the long seam": "Lange Naht nähen",
    "Sew the neck binding on": "Halsschrägband annähen",
    "Sew the neckband on": "Halsbündchen annähen",
    "Sew the shoulder seams": "Schulternähte nähen",
    "Sew the skirt centre back seam": "Hintere Mittelnaht des Rocks nähen",
    "Sew the skirt side seams": "Seitennähte des Rocks nähen",
    "Sew the zip in": "Reißverschluss einnähen",
    "Shoulder": "Schulter",
    "Shoulder seam front ↔ back": "Schulternaht vorne ↔ hinten",
    "Shoulder ↔ armhole (front + back)": "Schulter ↔ Armloch (vorne + hinten)",
    "Shoulder ↔ neckline (front + back)": "Schulter ↔ Halsausschnitt (vorne + hinten)",
    "Shoulders": "Schultern",
    "Side seam ↔ waist": "Seitennaht ↔ Taille",
    "Side seams": "Seitennähte",
    "Side ↔ crown (smooth)": "Seite ↔ Scheitel (glatt)",
    "Size": "Größe",
    "Skirt": "Rock",
    "Skirt back": "Rockteil hinten",
    "Skirt centre back seam (left ↔ right)": "Hintere Rockmittelnaht (links ↔ rechts)",
    "Skirt front": "Rockteil vorne",
    "Skirt front and back right sides together.": "Vorderes und hinteres Rockteil rechts auf rechts.",
    "Skirt hem ↔ side seam": "Rocksaum ↔ Seitennaht",
    "Skirt length": "Rocklänge",
    "Skirt length incl. waistband": "Rocklänge inkl. Bund",
    "Skirt right sides together to the bodice: side seams meet, centre front/back meet.":
        "Rock rechts auf rechts an das Oberteil: Seitennähte und vordere/hintere Mitte treffen aufeinander.",
    "Skirt side seam front ↔ back": "Seitennaht Rock vorne ↔ hinten",
    "Skirt side seam ↔ waist": "Seitennaht Rock ↔ Taille",
    "Skirt top edge (ungathered)": "Rockoberkante (ungekräuselt)",
    "Skirt waist ↔ centre": "Rocktaille ↔ Mitte",
    "Skirt width at top (ungathered)": "Rockweite oben (ungekräuselt)",
    "Sleeve": "Ärmel",
    "Sleeve cap back": "Ärmelkugel hinten",
    "Sleeve cap front": "Ärmelkugel vorne",
    "Sleeve cap top (smooth)": "Ärmelkugel oben (glatt)",
    "Sleeve cuff": "Ärmelbündchen",
    "Sleeve cuff ↔ sleeve hem (stretched)": "Ärmelbündchen ↔ Ärmelsaum (gedehnt)",
    "Sleeve hem": "Ärmelsaum",
    "Sleeve hems": "Ärmelsäume",
    "Sleeve length": "Ärmellänge",
    "Sleeve length plausible": "Ärmellänge plausibel",
    "Sleeve on the bottom: the machine eases the cap in.": "Ärmel unten: die Maschine hält die Kugel ein.",
    "Sleeve opening": "Ärmelöffnung",
    "Sleeve seam": "Ärmelnaht",
    "Sleeve seam (front ↔ back)": "Ärmelnaht (vorne ↔ hinten)",
    "Sleeve underarm ↔ cap front": "Ärmel Achsel ↔ Kugel vorne",
    "Sleeves": "Ärmel",
    "Slip one end into the other (right sides together); sew around, leaving {n} cm open.":
        "Ein Ende in das andere schieben (rechts auf rechts); rundherum nähen, {n} cm offen lassen.",
    "Stitch the binding down": "Schrägband feststeppen",
    "Stitch the opening closed.": "Öffnung zusteppen.",
    "Stretch direction: crosswise": "Dehnrichtung: quer",
    "Sweat / French Terry: {n}–{n} mm": "Sweat / French Terry: {n}–{n} mm",
    "T-Shirt": "T-Shirt",
    "T-shirt dress": "T-Shirt-Kleid",
    "The back opens completely: close it with narrow Velcro ({n} cm) or {n}–{n} small snaps.":
        "Der Rücken öffnet sich ganz: mit schmalem Klettband ({n} cm) oder {n}–{n} kleinen Druckknöpfen schließen.",
    "The edges overlap at the centre back: soft side on the left back, hook side on the right back (or {n}–{n} snaps).":
        "Die Kanten überlappen an der hinteren Mitte: Flauschseite auf dem linken Rückenteil, Hakenseite auf dem "
        "rechten (oder {n}–{n} Druckknöpfe).",
    "The garment opens completely: easy dressing.": "Das Kleidungsstück öffnet sich ganz: leichtes Anziehen.",
    "The hood front edges end exactly at the zip (no overlap at centre front).":
        "Die Vorderkanten der Kapuze enden genau am Reißverschluss (keine Überlappung an der vorderen Mitte).",
    "Then level the hem: the bias stretches.": "Danach den Saum begradigen: der schräge Fadenlauf dehnt sich.",
    "Thin, soft fabrics work best (cotton poplin, batiste, old T-shirts); thick fabric makes the tiny seams bulky.":
        "Dünne, weiche Stoffe eignen sich am besten (Baumwollpopeline, Batist, alte T-Shirts); dicker Stoff macht "
        "die winzigen Nähte klobig.",
    "Top edge (press under)": "Oberkante (einschlagen)",
    "Top end": "Oberes Ende",
    "Top notch of the sleeve cap on the shoulder seam, front/back notches meet; sew the sleeve in flat.":
        "Oberer Knipser der Ärmelkugel auf die Schulternaht, vordere/hintere Knipser treffen aufeinander; den "
        "Ärmel flach einnähen.",
    "Topstitch beside the zip": "Neben dem Reißverschluss absteppen",
    "Turn and close with a ladder stitch.": "Wenden und mit dem Matratzenstich schließen.",
    "Turn in the opening edges": "Schlitzkanten einschlagen",
    "Turn right side out": "Auf rechts wenden",
    "Turn the hood": "Kapuze wenden",
    "Turn the tube": "Schlauch wenden",
    "Two rows of long stitches; pull them up to the bodice waist (gather ratio {n}), spread the gathers evenly.":
        "Zwei Reihen lange Stiche; auf die Taillenweite des Oberteils zusammenziehen (Kräuselfaktor {n}), die "
        "Kräusel gleichmäßig verteilen.",
    "Two rows of the longest stitch; pull them up to the waistband length, spread the gathers evenly.":
        "Zwei Reihen mit der längsten Stichlänge; auf die Bundlänge zusammenziehen, die Kräusel gleichmäßig verteilen.",
    "Underarm: side seam ↔ armhole back": "Achsel: Seitennaht ↔ Armloch hinten",
    "Underarm: side seam ↔ armhole front": "Achsel: Seitennaht ↔ Armloch vorne",
    "Underarm: side seam ↔ raglan (body)": "Achsel: Seitennaht ↔ Raglan (Rumpf)",
    "Underarm: sleeve seam ↔ raglan (sleeve front)": "Achsel: Ärmelnaht ↔ Raglan (Ärmel vorne)",
    "Upper-arm width": "Oberarmweite",
    "V point (intended angle)": "V-Spitze (gewollter Winkel)",
    "Waist (gather)": "Taille (kräuseln)",
    "Waist seam": "Taillennaht",
    "Waist seam (bodice)": "Taillennaht (Oberteil)",
    "Waist seam (gather)": "Taillennaht (kräuseln)",
    "Waist seam bodice ↔ skirt (gathered)": "Taillennaht Oberteil ↔ Rock (gekräuselt)",
    "Waist seam fits over the shoulders/chest": "Taillennaht passt über Schultern/Brust",
    "Waist ↔ centre": "Taille ↔ Mitte",
    "Waistband fits over the hip": "Bund passt über die Hüfte",
    "Waistband ↔ skirt top edge": "Bund ↔ Rockoberkante",
    "Waistband ↔ skirt top edge (gathered)": "Bund ↔ Rockoberkante (gekräuselt)",
    "Width at the hip": "Weite an der Hüfte",
    "With a safety pin; join the ends with an overlap.": "Mit einer Sicherheitsnadel; die Enden überlappend verbinden.",
    "With the zipper foot. Lay the folded zip guard on the inside of the left front over the zip tape and catch it "
    "in the same seam.":
        "Mit dem Reißverschlussfuß. Den gefalteten Untertritt innen am linken Vorderteil über das "
        "Reißverschlussband legen und in derselben Naht mitfassen.",
    "Woven: {n}–{n} mm": "Webware: {n}–{n} mm",
    "Zip": "Reißverschluss",
    "Zip guard": "Reißverschluss-Untertritt",
    "Zip length": "Reißverschlusslänge",
    "Zip length fits the front opening": "Reißverschlusslänge passt zur vorderen Öffnung",
    "Zip: left ↔ right front edge": "Reißverschluss: linke ↔ rechte Vorderkante",
    "arm length {n} cm": "Armlänge {n} cm",
    "back length + {n} % of height": "Rückenlänge + {n} % der Körpergröße",
    "beanie edge": "Mützenkante",
    "chest × ({n} + {n} % ease)": "Brust × ({n} + {n} % Mehrweite)",
    "circumference incl. stretch": "Umfang inkl. Dehnung",
    "cut on the bias ({n}°)": "schräg zum Fadenlauf zuschneiden ({n}°)",
    "derived": "abgeleitet",
    "doll {n} cm (made to measure)": "Puppe {n} cm (nach Maß)",
    "ease {n}–{n} mm": "Mehrweite {n}–{n} mm",
    "ends at the zip: not sewn into a ring": "endet am Reißverschluss: nicht zum Ring geschlossen",
    "front opening {n} cm, standard zip rounded down": "vordere Öffnung {n} cm, Standard-Reißverschluss abgerundet",
    "gather ratio {n} (allowed {n}–{n})": "Kräuselfaktor {n} (erlaubt {n}–{n})",
    "hand circumference ≈ {n} × wrist": "Handumfang ≈ {n} × Handgelenk",
    "hood height ≥ {n} × head circumference": "Kapuzenhöhe ≥ {n} × Kopfumfang",
    "left front only (covers the zip inside)": "nur linkes Vorderteil (deckt den Reißverschluss innen ab)",
    "neck / {n} + {n} cm": "Hals / {n} + {n} cm",
    "neck_width_half + {n} cm + {n} cm (V-neck)": "neck_width_half + {n} cm + {n} cm (V-Ausschnitt)",
    "neckband length incl. usable stretch ≥ head circumference": "Halsbündchenlänge inkl. nutzbarer Dehnung ≥ Kopfumfang",
    "neckline + both edges of the back opening ≥ head circumference + {n} %":
        "Halsausschnitt + beide Kanten des Rückenschlitzes ≥ Kopfumfang + {n} %",
    "neckline incl. stretch ≥ head circumference": "Halsausschnitt inkl. Dehnung ≥ Kopfumfang",
    "negative ease for jersey": "negative Mehrweite für Jersey",
    "normal": "normal",
    "slim": "schmal",
    "wide": "weit",
    "open for the top {n} cm (notch)": "oben {n} cm offen (Knipser)",
    "pull-on dress without closure: waist seam incl. usable stretch ≥ chest":
        "Kleid ohne Verschluss: Taillennaht inkl. nutzbarer Dehnung ≥ Brust",
    "shoulder + allowance for fit 'normal'": "Schulter + Zugabe für Passform „normal“",
    "shoulder + allowance for fit 'wide'": "Schulter + Zugabe für Passform „weit“",
    "shoulder + allowance for fit 'slim'": "Schulter + Zugabe für Passform „schmal“",
    "the skirt is gathered (intended extra length)": "der Rock ist gekräuselt (gewollte Mehrlänge)",
    "waist seam + both edges of the skirt opening ≥ hip + {n} %": "Taillennaht + beide Kanten des Rockschlitzes ≥ Hüfte + {n} %",
    "waistband unstretched ≥ hip (the elastic gathers it)": "Bund ungedehnt ≥ Hüfte (das Gummi rafft ihn)",
    "width at hip level ≥ hip + {n} %": "Weite auf Hüfthöhe ≥ Hüfte + {n} %",
    "width incl. stretch": "Weite inkl. Dehnung",
    "with the overlocker ({n}-thread overlock stitch, differential feed about {n}), stretching only the band":
        "mit der Overlock ({n}-Faden-Overlockstich, Differentialtransport etwa {n}), nur das Bündchen dehnen",
})

# Booklet v2
TABLE.update({
    "{n}–{n} stitches on top of each other, then wrapped closely with buttonhole stitches.":
        "{n}–{n} Stiche übereinander, dann eng mit Knopflochstichen umwickeln.",
    "A piece of cardboard in the finished pocket size makes pressing the edges easy.":
        "Ein Stück Karton in der fertigen Taschengröße macht das Bügeln der Kanten leicht.",
    "A strip of stay tape ironed onto the opening keeps it in shape.":
        "Ein Streifen Formband, auf den Eingriff gebügelt, hält ihn in Form.",
    "After the test garment": "Nach dem Probeteil",
    "Always the front and back of the SAME leg (FL + BL, FR + BR).":
        "Immer Vorder- und Hinterteil DESSELBEN Beins (VL + HL, VR + HR).",
    "At the end sew a {n} cm thread chain off the fabric; thread it back under the stitches with a darning needle.":
        "Am Ende {n} cm Fadenkette über den Stoff hinaus nähen; mit einer Stopfnadel unter die Stiche zurückziehen.",
    "Back stitch": "Rückstich",
    "Back view": "Rückansicht",
    "Front view": "Vorderansicht",
    "Basics: hand stitches": "Grundlagen: Handstiche",
    "Basics: the overlocker": "Grundlagen: die Overlock",
    "Basics: the sewing machine": "Grundlagen: die Nähmaschine",
    "Baste {n} mm from the edge, inside the seam allowance.": "{n} mm von der Kante heften, innerhalb der Nahtzugabe.",
    "Blind stitch": "Blindstich",
    "Chalk": "Kreide",
    "Clips": "Clips",
    "Pins": "Stecknadeln",
    "Pin": "Stecknadel",
    "Scissors": "Schere",
    "Terry towel": "Frottiertuch",
    "Clips are safer at the overlocker: pins must come out before the knife.":
        "An der Overlock sind Clips sicherer: Stecknadeln müssen vor dem Messer heraus.",
    "Closes an opening invisibly: the stitches run inside the folds.":
        "Schließt eine Öffnung unsichtbar: die Stiche laufen in den Bruchkanten.",
    "Colours and lines": "Farben und Linien",
    "Cross-section of the edge": "Querschnitt der Kante",
    "Cross-section of the hem": "Querschnitt des Saums",
    "Cross-section: pressed edge": "Querschnitt: gebügelte Kante",
    "Crotch curve on the left, waist up: that is FL and BR. Left/right always means as worn, seen from the child.":
        "Schrittrundung links, Taille oben: das sind VL und HR. Links/rechts heißt immer getragen, vom Kind aus gesehen.",
    "Curves (crotch, pocket bag): sew slowly and steer the fabric, do not pull it.":
        "Rundungen (Schritt, Taschenbeutel): langsam nähen und den Stoff führen, nicht ziehen.",
    "Cut both layers at once with long strokes; keep the fabric flat on the table.":
        "Beide Lagen auf einmal mit langen Schnitten zuschneiden; der Stoff bleibt flach auf dem Tisch.",
    "Each stitch goes back to the end of the last one: strong like a machine seam; for topstitching and seams.":
        "Jeder Stich geht zurück zum Ende des letzten: fest wie eine Maschinennaht; zum Absteppen und für Nähte.",
    "Elastic": "Gummiband", "Zip": "Reißverschluss", "Velcro": "Klettband", "Snaps": "Druckknöpfe",
    "Buttons": "Knöpfe", "Drawstring": "Kordel", "Cord": "Kordel", "Binding": "Schrägband",
    "Fold the front leg out of the way: sew only the two pocket bag layers.":
        "Die Vorderhose wegklappen: nur die beiden Lagen Taschenbeutel nähen.",
    "For hems and casings: catch only {n}–{n} threads of the outer fabric, then {n} mm in the fold.":
        "Für Säume und Tunnel: nur {n}–{n} Fäden vom Oberstoff fassen, dann {n} mm in der Bruchkante.",
    "Important": "Wichtig",
    "Tip": "Tipp",
    "In the colour of the fabric.": "In der Farbe des Stoffs.",
    "In the colour of the fabric; overlocker: {n} cones.": "In der Farbe des Stoffs; Overlock: {n} Konen.",
    "Knit seams (narrow) and finishing the edges (wide).": "Jerseynähte (schmal) und Kanten versäubern (breit).",
    "Label the pieces": "Teile beschriften",
    "Ladder stitch": "Matratzenstich",
    "Lay the four leg pieces right side up, waist up. Stick a strip of tape on each: FL, FR (front left/right) and "
    "BL, BR (back left/right), as worn.":
        "Die vier Beinteile mit der rechten Seite nach oben legen, Taille oben. Auf jedes einen Streifen Klebeband: "
        "VL, VR (vorne links/rechts) und HL, HR (hinten links/rechts), getragen.",
    "FL": "VL", "FR": "VR", "BL": "HL", "BR": "HR",
    "Machines and basics": "Maschinen und Grundlagen",
    "Mark the {n} cm opening at the inseam with two pins before you start.":
        "Die {n}-cm-Öffnung an der Innenbeinnaht vorher mit zwei Nadeln markieren.",
    "Marking (chalk)": "Markierung (Kreide)",
    "Nap: no piece turned round, all with the waist up. Stroke the fabric to check the direction.":
        "Strich: kein Teil gedreht, alle mit der Taille nach oben. Mit der Hand über den Stoff streichen, um die "
        "Richtung zu prüfen.",
    "Never deeper than half the seam allowance.": "Nie tiefer als die halbe Nahtzugabe.",
    "Only ONE pocket. The top edge stays open.": "Nur EINE Tasche. Die Oberkante bleibt offen.",
    "The top edge stays open.": "Die Oberkante bleibt offen.",
    "Parts and material": "Teile und Material",
    "Pierce the pocket corners with a pin and mark them with chalk on the right side.":
        "Die Taschenecken mit einer Nadel durchstechen und auf der rechten Seite mit Kreide markieren.",
    "Pin across the seam line.": "Quer zur Nahtlinie stecken.",
    "Pin the far end to the leg so it cannot slip into the casing.":
        "Das hintere Ende am Bein feststecken, damit es nicht in den Tunnel rutscht.",
    "Pin the notches first, then the ends.": "Erst die Knipse stecken, dann die Enden.",
    "Print at {n} % and measure the control square. Cut the template out along the grey outline, lay it on the "
    "piece (right side up) with the edges on the edges, and trace the line with chalk.":
        "Mit {n} % drucken und das Kontrollquadrat messen. Die Schablone an der grauen Kontur ausschneiden, Kante "
        "auf Kante auf das Teil legen (rechte Seite oben) und die Linie mit Kreide nachzeichnen.",
    "Pull it over the child's hip to test it.": "Zur Probe über die Hüfte des Kindes ziehen.",
    "Pull the pins or clips out before they reach the knife: a pin in the knife breaks it.":
        "Nadeln oder Clips herausziehen, bevor sie das Messer erreichen: eine Nadel im Messer zerbricht es.",
    "Read the steps once before you start. Every picture is drawn from your pattern pieces. Sew a test garment "
    "from cheap fabric first and adjust before you cut the good fabric.":
        "Lies die Schritte einmal durch, bevor du anfängst. Jedes Bild ist aus deinen Schnittteilen gezeichnet. "
        "Nähe zuerst ein Probeteil aus günstigem Stoff und passe an, bevor du den guten Stoff zuschneidest.",
    "Right side up, with the same distance to the edge all the way; use the edge of the presser foot as a guide.":
        "Rechte Seite oben, überall im gleichen Abstand zur Kante; die Kante des Nähfußes dient als Führung.",
    "Right/wrong side of the fabric = the side of the fabric. Left/right (as worn) = seen from the child wearing "
    "it: the left front leg is on the right when you look at the child.":
        "Rechte/linke Stoffseite = die Seite des Stoffs. Links/rechts (getragen) = vom Kind aus gesehen, das die "
        "Hose trägt: das linke Vorderbein ist rechts, wenn du das Kind ansiehst.",
    "Roll the edge {n}–{n} mm to the inside: no pocket bag may show from the outside.":
        "Die Kante {n}–{n} mm nach innen rollen: von außen darf kein Taschenbeutel zu sehen sein.",
    "Seam allowance {n} mm: the needle runs on the seam line, the knife trims only a sliver.":
        "Nahtzugabe {n} mm: die Nadel läuft auf der Nahtlinie, das Messer schneidet nur einen schmalen Streifen ab.",
    "Seam allowance {n} cm: the needle runs on the seam line, the knife trims only a sliver.":
        "Nahtzugabe {n} cm: die Nadel läuft auf der Nahtlinie, das Messer schneidet nur einen schmalen Streifen ab.",
    "Seams in woven fabric, {n} mm; backstitch at the start and the end.":
        "Nähte in Webware, {n} mm; am Anfang und Ende verriegeln.",
    "See the basics page at the front of the booklet.": "Siehe die Grundlagen-Seite vorne im Heft.",
    "Sew by hand": "Von Hand nähen",
    "Sew now (machine)": "Jetzt nähen (Maschine)",
    "Fold / press line": "Bruch-/Bügellinie",
    "Notch: match them": "Knips: aufeinanderlegen",
    "Sewn with": "Genäht mit",
    "Start exactly at the crotch point and sew towards the hem.": "Genau am Schrittpunkt beginnen und zum Saum nähen.",
    "Straight stitch": "Geradstich",
    "Zigzag": "Zickzack",
    "Topstitching": "Absteppen",
    "Tacking stitch": "Heftstich",
    "Bar tack": "Riegel",
    "Template": "Schablone",
    "Templates 1:1": "Schablonen 1:1",
    "Test seam on two layers of a scrap: differential {n} (knit {n}), stitch length {n}.":
        "Probenaht an zwei Lagen eines Rests: Differential {n} (Jersey {n}), Stichlänge {n}.",
    "Test seam on two layers of a scrap: differential {n}, stitch length {n}.":
        "Probenaht an zwei Lagen eines Rests: Differential {n}, Stichlänge {n}.",
    "The inseams lie exactly on top of each other; press their allowances in opposite directions. Pull the inner "
    "leg out afterwards.":
        "Die Innenbeinnähte liegen genau aufeinander; ihre Zugaben in entgegengesetzte Richtungen legen. Danach das "
        "innere Bein herausziehen.",
    "The legs now lie right sides together, the hems point the same way.":
        "Die Beine liegen jetzt rechts auf rechts, die Säume zeigen in dieselbe Richtung.",
    "The opening is on the bias: do not stretch it.": "Der Eingriff liegt schräg zum Fadenlauf: nicht dehnen.",
    "The pocket opening lies flat, not pulled.": "Der Tascheneingriff liegt flach, nicht gezogen.",
    "Trace the J line with the 1:1 template at the end of the booklet.":
        "Die J-Linie mit der 1:1-Schablone hinten im Heft übertragen.",
    "Trace the J line with chalk now, using the 1:1 template at the end.":
        "Die J-Linie jetzt mit Kreide übertragen, mit der 1:1-Schablone hinten im Heft.",
    "Try the test garment on the child: length, width at the hip and the waistband. Adjust the measurements or "
    "options and print the pattern again before you cut the good fabric.":
        "Probiere das Probeteil am Kind an: Länge, Weite an der Hüfte und Bund. Passe Maße oder Optionen an und "
        "drucke den Schnitt neu, bevor du den guten Stoff zuschneidest.",
    "Turn it over afterwards and check from the outside that the opening lies flat.":
        "Danach umdrehen und von außen prüfen, dass der Eingriff flach liegt.",
    "Two rows {n} mm apart, {n} cm from centre front, {n} cm long, curve radius {n} cm; bar tack at the crotch seam.":
        "Zwei Reihen im Abstand von {n} mm, {n} cm neben der vorderen Mitte, {n} cm lang, Rundung {n} cm; Riegel "
        "an der Schrittnaht.",
    "both legs": "beide Beine", "both sides": "beide Seiten", "both sleeves": "beide Ärmel",
    "knife": "Messer", "needle": "Nadel", "seam allowance": "Nahtzugabe", "waist ↑": "Taille ↑",
    "right side up: the pile goes flat": "rechte Seite oben: der Flor wird platt",
    "wrong side up on a towel": "linke Seite oben auf einem Tuch",
    "right side · wrong side": "rechte · linke Seite",
    "Main fabric": "Oberstoff", "Corduroy": "Cord", "Velvet": "Samt", "Rib knit": "Bündchen",
    "Polyester sewing thread": "Polyester-Nähgarn",
    "Pins or clips": "Stecknadeln oder Clips",
    "Done!": "Fertig!",

    "Notions": "Zubehör", "Seam allowance": "Nahtzugabe", "included": "enthalten", "hem": "Saum",
    "Parts and steps": "Teile und Schritte", "Difficulty": "Schwierigkeit", "easy": "leicht", "medium": "mittel",
    "advanced": "anspruchsvoll", "about {n} h": "etwa {n} Std.", "Size": "Größe",
    "Long running stitches ({n} cm), they come out again later.": "Lange Vorstiche ({n} cm), sie kommen später wieder heraus.",
    "Fold the corners in first, then the sides: the corners stay flat.":
        "Erst die Ecken einschlagen, dann die Seiten: so bleiben die Ecken flach.",
    "Press the cross seam allowance open first: the fold lies flatter.":
        "Die Zugabe der Quernaht vorher auseinanderbügeln: der Bruch liegt flacher.",
    "The waistband is shorter than the top edge: the quarter marks meet, the lengths do not.":
        "Der Bund ist kürzer als die Oberkante: die Viertelmarken treffen sich, die Längen nicht.",
})
