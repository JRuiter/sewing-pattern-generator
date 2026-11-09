"""German texts of the garment modules added in 1.7 (accessories, tops, jackets, dresses, body,
baby and detail components). Merged into i18n_de.TABLE; same key rules (``{n}``, ``{s}``)."""
from __future__ import annotations

TABLE: dict[str, str] = {
    # ------------------------------------------------------------------ shared
    "{s}: {s} Adjust the measurements or options and print the pattern again if needed.":
        "{s}: {s} Passe Maße oder Optionen an und drucke den Schnitt neu, falls nötig.",
    "Try the test garment on the child": "Probiere das Probeteil am Kind an",
    "Try the test garment on": "Probiere das Probeteil an",
    "Corner": "Ecke", "Length": "Länge", "Width": "Breite", "Height": "Höhe",
    "Circumference": "Umfang", "Circumference (relaxed)": "Umfang (ungedehnt)",
    "Short edge": "Schmale Kante", "Side edge": "Seitenkante", "Long seam": "Längsnaht",
    "Snap": "Druckknopf", "Turn right side out": "Wenden",
    "negative ease for knits": "negative Mehrweite bei Strickstoffen",
    "about the body height": "etwa die Körpergröße",

    # ------------------------------------------------------------------ scarf
    "Scarf": "Schal", "Scarf end": "Schalende", "Scarf ends": "Schalenden",
    "Lange Kante, Scarf end": "Lange Kante, Schalende",
    "Scarf length plausible": "Schallänge plausibel",
    "Stretch direction: across the scarf": "Dehnrichtung: quer zum Schal",
    "Fringe: fray 6 cm at both ends": "Fransen: an beiden Enden 6 cm ausfransen",
    "Close one end": "Ein Ende schließen",
    "Close the other end by hand": "Das andere Ende von Hand schließen",
    "Fold the scarf lengthwise right sides together, long edges level, and pin. Sew with {n} mm seam allowance "
    "along the whole length: you get a tube.":
        "Falte den Schal der Länge nach rechts auf rechts, die langen Kanten liegen bündig, und stecke sie. "
        "Nähe mit {n} mm Nahtzugabe über die ganze Länge: so entsteht ein Schlauch.",
    "Fold the scarf lengthwise right sides together, long edges level, and pin. Sew with {n} cm seam allowance "
    "along the whole length: you get a tube.":
        "Falte den Schal der Länge nach rechts auf rechts, die langen Kanten liegen bündig, und stecke sie. "
        "Nähe mit {n} cm Nahtzugabe über die ganze Länge: so entsteht ein Schlauch.",
    "Sew one end closed with {n} mm seam allowance, the long seam in the middle or at the side.":
        "Nähe ein Ende mit {n} mm Nahtzugabe zu; die Längsnaht liegt in der Mitte oder an der Seite.",
    "Sew one end closed with {n} cm seam allowance, the long seam in the middle or at the side.":
        "Nähe ein Ende mit {n} cm Nahtzugabe zu; die Längsnaht liegt in der Mitte oder an der Seite.",
    "Push the closed end through the tube with a long ruler or a wooden spoon.":
        "Schiebe das geschlossene Ende mit einem langen Lineal oder einem Kochlöffel durch den Schlauch.",
    "Fold the allowances of the open end inwards and close it with a ladder stitch.":
        "Schlage die Nahtzugaben am offenen Ende nach innen ein und schließe es mit dem Matratzenstich.",
    "Round the corners": "Ecken abrunden",
    "Fleece does not fray: round the four corners slightly with scissors. Nothing to sew.":
        "Fleece franst nicht aus: runde die vier Ecken mit der Schere leicht ab. Nähen ist nicht nötig.",
    "Hem the long edges": "Lange Kanten säumen", "Hem the ends": "Enden säumen",
    "Fold each long edge {n} mm to the wrong side and press, then again by the same amount. Sew it down close to "
    "the inner fold.":
        "Bügle jede lange Kante {n} mm nach links um und dann noch einmal genauso breit. Steppe sie dicht an der "
        "inneren Bruchkante fest.",
    "Fold each end {n} mm to the wrong side and press, then again by the same amount. Sew it down close to the "
    "inner fold.":
        "Bügle jedes Ende {n} mm nach links um und dann noch einmal genauso breit. Steppe es dicht an der inneren "
        "Bruchkante fest.",
    "Fray the fringe": "Fransen ausziehen",
    "At both ends pull out the crosswise threads one by one, 6 cm deep. Secure the fringe with a straight stitch "
    "6 cm from the end.":
        "Ziehe an beiden Enden die Querfäden einzeln heraus, 6 cm tief. Sichere die Fransen mit einem Geradstich "
        "6 cm vor dem Ende.",
    "is the length right when it is wrapped once round the neck?":
        "Stimmt die Länge, wenn der Schal einmal um den Hals gelegt ist?",

    # ------------------------------------------------------------------ headband
    "Headband": "Stirnband", "Twist headband": "Twist-Stirnband", "Twist": "Twist",
    "Twist loop": "Twist-Schlaufe", "Twist loop long seam": "Längsnaht Twist-Schlaufe",
    "Headband goes over the head": "Stirnband geht über den Kopf",
    "Headband stays on (snug)": "Stirnband hält (liegt eng an)",
    "Stretch direction: along the band": "Dehnrichtung: entlang des Bandes",
    "does it sit snugly over the ears without slipping or pressing?":
        "Liegt es eng über den Ohren, ohne zu rutschen oder zu drücken?",
    "Fold the band lengthwise right sides together, long edges level, and pin. Sew with {n} mm seam allowance "
    "along the whole length: you get a tube.":
        "Falte das Band der Länge nach rechts auf rechts, die langen Kanten liegen bündig, und stecke sie. Nähe "
        "mit {n} mm Nahtzugabe über die ganze Länge: so entsteht ein Schlauch.",
    "Fold the band lengthwise right sides together, long edges level, and pin. Sew with {n} cm seam allowance "
    "along the whole length: you get a tube.":
        "Falte das Band der Länge nach rechts auf rechts, die langen Kanten liegen bündig, und stecke sie. Nähe "
        "mit {n} cm Nahtzugabe über die ganze Länge: so entsteht ein Schlauch.",
    "Turn half of the tube": "Eine Hälfte des Schlauchs wenden",
    "Reach into the tube and turn one half right side out over the other half. Now both ends lie on top of each "
    "other, right sides together.":
        "Greife in den Schlauch und stülpe eine Hälfte rechts herum über die andere. Jetzt liegen beide Enden "
        "rechts auf rechts aufeinander.",
    "The long seams lie on top of each other: pin there first.":
        "Die Längsnähte liegen aufeinander: stecke dort zuerst.",
    "Sew the twist loop": "Twist-Schlaufe nähen",
    "Fold the twist loop lengthwise right sides together and sew the long edge with {n} mm seam allowance. Turn it "
    "right side out.":
        "Falte die Twist-Schlaufe der Länge nach rechts auf rechts und nähe die lange Kante mit {n} mm Nahtzugabe. "
        "Wende sie.",
    "Sew the cross seam": "Quernaht nähen",
    "Pin the two ends together all round, long seams on top of each other. Sew round with {n} mm seam allowance, "
    "leaving 4 cm open.":
        "Stecke die beiden Enden ringsum aufeinander, die Längsnähte übereinander. Nähe mit {n} mm Nahtzugabe "
        "rundherum und lass 4 cm offen.",
    "Close the opening by hand": "Wendeöffnung von Hand schließen",
    "Turn the band right side out through the opening. Fold the allowances in and close the opening with a ladder "
    "stitch.":
        "Wende das Band durch die Öffnung. Schlage die Nahtzugaben ein und schließe die Öffnung mit dem "
        "Matratzenstich.",
    "Wrap the twist loop round": "Twist-Schlaufe herumlegen",
    "Gather the band at the cross seam, wrap the twist loop tightly round it and sew the loop ends together by "
    "hand on the inside.":
        "Raffe das Band an der Quernaht, lege die Twist-Schlaufe fest darum und nähe die Schlaufenenden innen von "
        "Hand zusammen.",
    "Long edges together": "Lange Kanten zusammen", "Cross seam (right ↔ left)": "Quernaht (rechts ↔ links)",

    # ------------------------------------------------------------------ neckwear
    "Neck gaiter": "Schlauchschal", "Neckerchief": "Dreieckstuch", "Gaiter": "Schlauchschal",
    "Gaiter goes over the head": "Schlauchschal geht über den Kopf",
    "circumference incl. half the stretch": "Umfang inkl. halber Dehnung",
    "Stretch direction: round the neck": "Dehnrichtung: rund um den Hals",
    "does it go over the head easily and lie flat round the neck?":
        "Geht es leicht über den Kopf und liegt es glatt um den Hals?",
    "Fold the piece crosswise right sides together, short edges level, and pin. Sew with {n} mm seam allowance: "
    "you get a wide ring.":
        "Falte das Teil quer rechts auf rechts, die schmalen Kanten liegen bündig, und stecke sie. Nähe mit {n} mm "
        "Nahtzugabe: so entsteht ein breiter Ring.",
    "Fold the ring in half": "Ring zur Hälfte falten",
    "Sew the raw edges together": "Offene Kanten zusammennähen",
    "Pin the raw edges together all round and sew them with {n} mm seam allowance, stretching slightly. Leave {n} cm "
    "open if you sew right sides together and turn; with the overlocker sew round in one go.":
        "Stecke die offenen Kanten ringsum aufeinander und nähe sie mit {n} mm Nahtzugabe, leicht gedehnt. Lass "
        "{n} cm offen, wenn du rechts auf rechts nähst und wendest; mit der Overlock einmal rundherum nähen.",
    "Neckerchief overlaps round the neck": "Dreieckstuch überlappt um den Hals",
    "neck + overlap for the snap": "Hals + Überlappung für den Druckknopf",
    "Outer edges": "Außenkanten", "Long edge": "Lange Kante",
    "Sew the side edges": "Seitenkanten nähen", "Sew the long edge": "Lange Kante nähen",
    "Lay both triangles right sides together, edges level, and pin. Sew the two short edges with {n} mm seam "
    "allowance, pivoting at the point.":
        "Lege beide Dreiecke rechts auf rechts, Kanten bündig, und stecke sie. Nähe die beiden kurzen Kanten mit "
        "{n} mm Nahtzugabe; an der Spitze mit versenkter Nadel drehen.",
    "Sew the long edge with {n} mm seam allowance, leaving {n} cm open in the middle.":
        "Nähe die lange Kante mit {n} mm Nahtzugabe und lass in der Mitte {n} cm offen.",
    "Clip the point diagonally so it turns out sharp.":
        "Schneide die Spitze schräg ab, damit sie beim Wenden spitz wird.",
    "Turn through the opening, push the points out with a blunt tool and press.":
        "Wende durch die Öffnung, forme die Spitzen mit einem stumpfen Werkzeug aus und bügle.",
    "Topstitch all round": "Rundherum absteppen",
    "Topstitch 3 mm from the edge all round; this also closes the opening.":
        "Steppe ringsum 3 mm von der Kante ab; so schließt sich auch die Wendeöffnung.",
    "Attach the snap": "Druckknopf anbringen",
    "Try it on, mark the overlap and attach a snap (or sew on two ties).":
        "Probiere an, markiere die Überlappung und bringe einen Druckknopf an (oder nähe zwei Bänder an).",
}

# ---------------------------------------------------------------------- bib
TABLE.update({
    "Bib": "Lätzchen", "Bandana bib": "Halstuch-Lätzchen", "Bib top": "Lätzchen oben",
    "Bib underside": "Lätzchen unten", "Absorbent layer": "Saugeinlage",
    "Absorbent layer (terry, bamboo fleece)": "Saugeinlage (Frottee, Bambusfleece)",
    "Terry or fleece": "Frottee oder Fleece", "Bib round": "Lätzchen rundherum",
    "Outer edge": "Außenkante", "Neck edge": "Halskante",
    "Neck opening incl. overlap": "Halsöffnung inkl. Überlappung", "neck + a finger of room": "Hals + ein Finger Luft",
    "No seam allowance: lies loose inside, caught by the topstitching":
        "Ohne Nahtzugabe: liegt lose dazwischen und wird beim Absteppen mitgefasst",
    "Lay the absorbent layer in": "Saugeinlage einlegen",
    "Lay the absorbent layer centred on the wrong side of the underside and pin it; it is caught later by the "
    "topstitching.":
        "Lege die Saugeinlage mittig auf die linke Seite des Unterteils und stecke sie fest; sie wird später beim "
        "Absteppen mitgefasst.",
    "Sew round the bib": "Lätzchen rundherum nähen",
    "Lay top and underside right sides together, edges level, and pin. Sew all round with {n} mm seam allowance; "
    "leave {n} cm open on the lower edge.":
        "Lege Ober- und Unterteil rechts auf rechts, Kanten bündig, und stecke sie. Nähe mit {n} mm Nahtzugabe "
        "rundherum; lass an der unteren Kante {n} cm offen.",
    "Clip the allowances in the neck curve every 1 cm, close to the seam.":
        "Schneide die Nahtzugaben in der Halsrundung alle 1 cm bis knapp an die Naht ein.",
    "Turn through the opening, shape the tabs and press. Fold the allowances of the opening in.":
        "Wende durch die Öffnung, forme die Laschen aus und bügle. Schlage die Nahtzugaben an der Öffnung ein.",
    "Topstitch {n} mm from the edge all round; this also closes the opening.":
        "Steppe ringsum {n} mm von der Kante ab; so schließt sich auch die Wendeöffnung.",
    "Attach a plastic snap to the marked tab ends: the cap on the top tab, the socket on the other.":
        "Bringe an den markierten Laschenenden einen Kam-Snap an: das Oberteil auf die obere Lasche, das Unterteil "
        "auf die andere.",
    "does the neck opening close with a little room (one finger) and cover the chest?":
        "Schließt die Halsöffnung mit etwas Luft (ein Finger) und bedeckt das Lätzchen die Brust?",
})

# ---------------------------------------------------------------------- accessories: shared
TABLE.update({
    "1 per hand": "1 pro Hand", "2 per hand": "2 pro Hand", "2 mirrored pairs": "2 gegengleiche Paare",
    "2 mirrored pairs (back and palm of each hand)": "2 gegengleiche Paare (Handrücken und Handfläche je Hand)",
    "2 mirrored pairs (palm and back of each hand)": "2 gegengleiche Paare (Handfläche und Handrücken je Hand)",
    "Cuff": "Bündchen", "Cuff goes over the hand": "Bündchen geht über die Hand",
    "cuff incl. stretch ≥ hand": "Bündchen inkl. Dehnung ≥ Hand",
    "Cuff ↔ mitten (stretched)": "Bündchen ↔ Fäustling (gedehnt)", "Cuff ↔ sock (stretched)": "Bündchen ↔ Socke (gedehnt)",
    "Fold each cuff crosswise right sides together and sew the short edges with {n} mm seam allowance.":
        "Falte jedes Bündchen quer rechts auf rechts und nähe die schmalen Kanten mit {n} mm Nahtzugabe.",
    "Fold each ring lengthwise wrong sides together, raw edges level.":
        "Falte jeden Ring der Länge nach links auf links, die offenen Kanten liegen bündig.",
    "Stretch direction: across the hand": "Dehnrichtung: quer über die Hand",
    "Stretch direction: round the wrist": "Dehnrichtung: rund ums Handgelenk",
    "Stretch direction: round the foot (across)": "Dehnrichtung: rund um den Fuß (quer)",
    "Width (flat)": "Breite (flach)", "wrist opening": "Handgelenköffnung", "top edge": "obere Kante",
    "Interfacing": "Bügeleinlage", "Optional: iron-on interfacing": "Optional: Bügeleinlage",
    "glue side on the wrong side, press without steam": "Klebeseite auf die linke Stoffseite, ohne Dampf bügeln",
    "snap: cap and socket on the marks": "Druckknopf: Ober- und Unterteil auf die Markierungen",
    "cord, with a safety pin": "Kordel, mit einer Sicherheitsnadel",
    "buttonholes": "Knopflöcher", "buttons": "Knöpfe",
    "opening incl. half the stretch": "Öffnung inkl. halber Dehnung",
    "opening incl. half the stretch ≥ hand": "Öffnung inkl. halber Dehnung ≥ Hand",
    "Hem the wrist": "Handgelenk säumen", "Hem the top edge": "Obere Kante säumen",
    "Fold the wrist edge {n} cm to the wrong side and sew it down, stretching slightly.":
        "Bügle die Kante am Handgelenk {n} cm nach links um und steppe sie leicht gedehnt fest.",
    "Fold the top edge {n} cm to the wrong side and sew it down, stretching slightly.":
        "Bügle die obere Kante {n} cm nach links um und steppe sie leicht gedehnt fest.",
    "Schablone: {s}": "Schablone: {s}",
    "Buckles": "Schnallen", "Wadding": "Volumenvlies",
})

# ---------------------------------------------------------------------- mittens, gloves
TABLE.update({
    "Mittens": "Fäustlinge", "Baby mittens": "Baby-Fäustlinge", "Mitten": "Fäustling",
    "Outline seam": "Umrissnaht", "Hand slips through the wrist opening": "Hand passt durch die Handgelenköffnung",
    "Hand slips through the wrist": "Hand passt durchs Handgelenk", "Room at the fingertips": "Luft an den Fingerspitzen",
    "do the hands slip in easily, with 1–1.5 cm room at the fingertips and the thumb?":
        "Schlüpfen die Hände leicht hinein, mit 1–1,5 cm Luft an den Fingerspitzen und am Daumen?",
    "Cord: {n} piece of {n} cm (mitten string)": "Kordel: {n} Stück à {n} cm (Fäustlingsband)",
    "Sew round the mittens": "Fäustlinge rundherum nähen",
    "Lay each mirrored pair right sides together, edges level, and pin. Sew round with {n} mm seam allowance from "
    "wrist to wrist, slowly round the thumb.":
        "Lege jedes gegengleiche Paar rechts auf rechts, Kanten bündig, und stecke es. Nähe mit {n} mm Nahtzugabe "
        "von Handgelenk zu Handgelenk rundherum, langsam um den Daumen.",
    "Lay each mirrored pair right sides together, edges level, and pin. Sew round with {n} mm seam allowance from "
    "wrist to wrist.":
        "Lege jedes gegengleiche Paar rechts auf rechts, Kanten bündig, und stecke es. Nähe mit {n} mm Nahtzugabe "
        "von Handgelenk zu Handgelenk rundherum.",
    "Clip into the thumb crotch close to the seam.": "Schneide den Daumenwinkel bis knapp an die Naht ein.",
    "Shorten the stitch a little round the fingertips.": "Verkürze die Stichlänge um die Fingerspitzen etwas.",
    "Turn both mittens.": "Wende beide Fäustlinge.",
    "Turn both mittens; push the thumb out with a blunt pencil.":
        "Wende beide Fäustlinge; schiebe den Daumen mit einem stumpfen Stift aus.",
    "Fold the wrist edge {n} cm to the wrong side and sew it down; thread a narrow elastic through if the mitten "
    "should hold better.":
        "Bügle die Kante am Handgelenk {n} cm nach links um und steppe sie fest; ziehe ein schmales Gummi ein, wenn "
        "der Fäustling besser halten soll.",
    "Sew on the mitten string": "Fäustlingsband annähen",
    "Sew the ends of the cord firmly to the inside of the cuffs. The cord runs through both sleeves of the jacket.":
        "Nähe die Enden der Kordel fest innen an die Bündchen. Die Kordel läuft durch beide Jackenärmel.",
    "Slide the cuff over the mitten, raw edges level, cuff seam on the side seam. Pin at the quarters and sew with "
    "{n} mm seam allowance, stretching only the cuff.":
        "Schiebe das Bündchen über den Fäustling, offene Kanten bündig, Bündchennaht auf der Seitennaht. Stecke an "
        "den Vierteln und nähe mit {n} mm Nahtzugabe; dehne dabei nur das Bündchen.",
    "Gloves": "Handschuhe", "Glove": "Handschuh", "Fingertip": "Fingerspitze", "Fingertips": "Fingerspitzen",
    "Between the fingers": "Zwischen den Fingern", "Outer seam": "Außennaht", "Outer seams": "Außennähte",
    "Fourchette {n}": "Schichtel {n}", "Fourchette {n} ↔ back": "Schichtel {n} ↔ Handrücken",
    "Fourchette {n} ↔ palm": "Schichtel {n} ↔ Handfläche", "Gusset side": "Schichtelkante",
    "Gusset tip": "Schichtelspitze", "Thumb": "Daumen", "Thumb base": "Daumenansatz", "Thumb seam": "Daumennaht",
    "Thumb base fits the opening": "Daumenansatz passt in die Öffnung", "opening is cut after tracing":
        "die Öffnung wird nach dem Übertragen ausgeschnitten",
    "Thumb opening (palm only): cut out on the line": "Daumenöffnung (nur Handfläche): auf der Linie ausschneiden",
    "Middle finger length incl. room": "Länge Mittelfinger inkl. Luft", "finger length + 3–5 mm room":
        "Fingerlänge + 3–5 mm Luft",
    "do all fingers reach the tips with a few millimetres to spare, and does the hand slip in easily?":
        "Reichen alle Finger mit ein paar Millimetern Luft bis in die Spitzen, und schlüpft die Hand leicht hinein?",
    "Sew round the gloves": "Handschuhe rundherum nähen",
    "Lay each mirrored pair right sides together, edges level, and pin between the fingers. Sew round with {n} mm "
    "seam allowance and a short stitch ({n} mm), from wrist to wrist.":
        "Lege jedes gegengleiche Paar rechts auf rechts, Kanten bündig, und stecke zwischen den Fingern. Nähe mit "
        "{n} mm Nahtzugabe und kurzem Stich ({n} mm) von Handgelenk zu Handgelenk rundherum.",
    "Pivot at each finger crotch with the needle down, then clip into the crotch close to the seam.":
        "Drehe in jedem Fingerzwischenraum mit versenkter Nadel und schneide den Zwischenraum danach bis knapp an "
        "die Naht ein.",
    "Turn the gloves; push every finger out with a blunt pencil or a chopstick.":
        "Wende die Handschuhe; schiebe jeden Finger mit einem stumpfen Stift oder einem Essstäbchen aus.",
    "Cut the thumb openings": "Daumenöffnungen ausschneiden",
    "Trace the oval thumb opening onto the two palm pieces (not the back pieces) and cut it out on the line.":
        "Übertrage die ovale Daumenöffnung auf die beiden Handflächen (nicht auf die Handrücken) und schneide sie auf "
        "der Linie aus.",
    "Sew the thumbs": "Daumen nähen",
    "Lay each thumb pair right sides together and sew the curved edge with {n} mm seam allowance.":
        "Lege jedes Daumenpaar rechts auf rechts und nähe die runde Kante mit {n} mm Nahtzugabe.",
    "Set in the thumbs": "Daumen einsetzen",
    "Thumb wrong side out, palm right side up: push the thumb through the opening from the right side and sew its "
    "base to the opening with {n} mm seam allowance, the thumb seam towards the index finger.":
        "Daumen links herum, Handfläche mit der rechten Seite nach oben: schiebe den Daumen von rechts durch die "
        "Öffnung und nähe den Ansatz mit {n} mm Nahtzugabe an die Öffnung, die Daumennaht zum Zeigefinger.",
    "Sew the fourchettes to the back": "Schichtel an den Handrücken nähen",
    "Pin one long edge of each fourchette right sides together to the sides between two fingers of the back piece, "
    "the tip in the crotch. Sew with {n} mm seam allowance.":
        "Stecke eine lange Kante jedes Schichtels rechts auf rechts an die Seiten zwischen zwei Fingern des "
        "Handrückens, die Spitze im Fingerzwischenraum. Nähe mit {n} mm Nahtzugabe.",
    "Sew each side from the crotch towards the fingertip.": "Nähe jede Seite vom Zwischenraum zur Fingerspitze.",
    "Sew the palm on": "Handfläche annähen",
    "Lay the palm right sides together onto the back. Sew the other edges of the fourchettes to the palm, then round "
    "the fingertips and the outer seams, all with {n} mm seam allowance.":
        "Lege die Handfläche rechts auf rechts auf den Handrücken. Nähe die anderen Kanten der Schichtel an die "
        "Handfläche, dann um die Fingerspitzen und die Außennähte, alles mit {n} mm Nahtzugabe.",
})

# ---------------------------------------------------------------------- socks
TABLE.update({
    "Socks": "Socken", "House socks": "Hausschuhsocken", "Sock": "Socke", "Upper": "Oberteil", "Sole": "Sohle",
    "Sole fabric (anti-slip)": "Sohlenstoff (Antirutsch)", "Sole seam": "Sohlennaht", "Front seam": "Vordere Naht",
    "Back seam": "Hintere Naht", "Back and sole seam": "Hintere Naht und Sohle",
    "Foot length": "Fußlänge", "Leg height": "Schafthöhe", "Foot passes the heel": "Fuß kommt über die Ferse",
    "leg width incl. stretch ≥ heel–instep circumference": "Schaftweite inkl. Dehnung ≥ Fersen-Rist-Umfang",
    "Sock length vs. foot": "Sockenlänge zum Fuß", "knits slightly shorter than the foot":
        "Strickstoffe etwas kürzer als der Fuß",
    "does the heel sit on the heel, and is there no fold over the instep?":
        "Sitzt die Ferse an der Ferse, und wirft es keine Falte über dem Rist?",
    "Sew the front seam": "Vordere Naht nähen",
    "Lay each mirrored pair right sides together. Sew the front seam from the top edge over the instep to the toe "
    "with {n} mm seam allowance, stretching slightly.":
        "Lege jedes gegengleiche Paar rechts auf rechts. Nähe die vordere Naht von der oberen Kante über den Rist "
        "bis zur Spitze mit {n} mm Nahtzugabe, leicht gedehnt.",
    "Sew the back and sole seam": "Hintere Naht und Sohle nähen",
    "Sew from the top edge down the back, round the heel and along the sole to the toe, with {n} mm seam "
    "allowance.":
        "Nähe von der oberen Kante hinten hinunter, um die Ferse und entlang der Sohle bis zur Spitze, mit {n} mm "
        "Nahtzugabe.",
    "Sew the heel curve slowly; stretch the fabric a little.": "Nähe die Fersenrundung langsam; dehne den Stoff etwas.",
    "Sew front and back seams": "Vordere und hintere Naht nähen",
    "Lay each mirrored pair of uppers right sides together and sew the front seam and the back seam with {n} mm "
    "seam allowance.":
        "Lege jedes gegengleiche Paar Oberteile rechts auf rechts und nähe die vordere und die hintere Naht mit "
        "{n} mm Nahtzugabe.",
    "Sew the sole in": "Sohle einnähen",
    "Upper wrong side out: pin the sole right sides together into the lower edge, the back seam at the heel and the "
    "front seam at the toe. Sew round with {n} mm seam allowance.":
        "Oberteil links herum: stecke die Sohle rechts auf rechts an die untere Kante, die hintere Naht an der "
        "Ferse, die vordere Naht an der Spitze. Nähe mit {n} mm Nahtzugabe rundherum.",
    "Clip the allowance of the upper at the toe and heel curves.":
        "Schneide die Nahtzugabe des Oberteils an Spitze und Ferse ein.",
    "Slide the cuff over the sock, raw edges level, cuff seam on the back seam. Pin at the quarters and sew with "
    "{n} mm seam allowance, stretching only the cuff.":
        "Schiebe das Bündchen über die Socke, offene Kanten bündig, Bündchennaht auf der hinteren Naht. Stecke an "
        "den Vierteln und nähe mit {n} mm Nahtzugabe; dehne dabei nur das Bündchen.",
})

# ---------------------------------------------------------------------- hats and cap
TABLE.update({
    "Bucket hat": "Fischerhut", "Crown": "Kopfteil", "Crown (inside)": "Kopfteil (innen)", "Side band": "Seitenteil",
    "Side band (inside)": "Seitenteil (innen)", "Under brim": "Krempe unten", "Brim edge": "Krempenkante",
    "Brim side seam": "Seitennaht Krempe", "Brim side seams": "Seitennähte Krempe",
    "Under brim side seams": "Seitennähte untere Krempe", "Brim outer edge": "Krempe Außenkante",
    "Brim ↔ side band": "Krempe ↔ Seitenteil", "Brim width": "Krempenbreite", "Side band height": "Höhe Seitenteil",
    "Head opening": "Kopföffnung", "head + 0.5–2.5 cm": "Kopf + 0,5–2,5 cm",
    "Side band seams (outside)": "Nähte Seitenteil (außen)", "Side band seams (inside)": "Nähte Seitenteil (innen)",
    "Crown ↔ side band (outside)": "Kopfteil ↔ Seitenteil (außen)",
    "Crown ↔ side band (inside)": "Kopfteil ↔ Seitenteil (innen)",
    "Optional: iron-on interfacing on the outer side band": "Optional: Bügeleinlage auf dem äußeren Seitenteil",
    "does it sit on the head without pressing, the brim slightly sloping down?":
        "Sitzt er ohne zu drücken auf dem Kopf, die Krempe leicht nach unten geneigt?",
    "Interface the outer side band": "Äußeres Seitenteil verstärken",
    "Optional, for a firmer hat: iron interfacing onto the wrong side of the outer side band pieces.":
        "Optional, für einen festeren Hut: Bügle Einlage auf die linke Seite der äußeren Seitenteile.",
    "Close the side band": "Seitenteil schließen",
    "Lay both side band halves right sides together and sew both short ends with {n} mm seam allowance: a ring. "
    "Press the allowances open.":
        "Lege beide Seitenteilhälften rechts auf rechts und nähe beide schmalen Enden mit {n} mm Nahtzugabe: ein "
        "Ring. Bügle die Nahtzugaben auseinander.",
    "Sew the crown in": "Kopfteil einnähen",
    "Pin the crown right sides together into the narrow edge of the band: the long axis of the oval front and back, "
    "the side seams at the sides. Sew with {n} mm seam allowance.":
        "Stecke das Kopfteil rechts auf rechts in die schmale Kante des Seitenteils: die lange Achse des Ovals vorne "
        "und hinten, die Seitennähte an den Seiten. Nähe mit {n} mm Nahtzugabe.",
    "Clip the band allowance every 1.5 cm so it follows the curve.":
        "Schneide die Nahtzugabe des Seitenteils alle 1,5 cm ein, damit sie der Rundung folgt.",
    "Close the brims": "Krempen schließen",
    "Sew the two halves of each brim together at the short ends with {n} mm seam allowance: two rings. Press the "
    "allowances open.":
        "Nähe die zwei Hälften jeder Krempe an den schmalen Enden mit {n} mm Nahtzugabe zusammen: zwei Ringe. Bügle "
        "die Nahtzugaben auseinander.",
    "Sew the brim edge": "Krempenkante nähen",
    "Lay the two brim rings right sides together and sew round the outer edge with {n} mm seam allowance. Turn, "
    "press and baste the inner edges together.":
        "Lege die beiden Krempenringe rechts auf rechts und nähe die Außenkante mit {n} mm Nahtzugabe rundherum. "
        "Wende, bügle und hefte die inneren Kanten zusammen.",
    "Clip the allowance of the outer edge in small notches before turning.":
        "Schneide die Nahtzugabe der Außenkante vor dem Wenden in kleinen Keilen ein.",
    "Topstitch the brim": "Krempe absteppen",
    "Topstitch rows {n} mm apart all round the brim, starting {n} mm from the outer edge.":
        "Steppe die Krempe in Reihen mit {n} mm Abstand rundherum ab, beginnend {n} mm von der Außenkante.",
    "Sew the brim on": "Krempe annähen",
    "Pin the brim to the lower edge of the outer hat (right side of the brim to the right side of the hat), side "
    "seams matching. Sew with {n} mm seam allowance.":
        "Stecke die Krempe an die untere Kante des äußeren Huts (rechte Seite der Krempe auf die rechte Seite des "
        "Huts), Seitennähte aufeinander. Nähe mit {n} mm Nahtzugabe.",
    "Sew the inner hat": "Inneren Hut nähen",
    "Sew band and crown of the lining the same way.": "Nähe Seitenteil und Kopfteil des Futters genauso.",
    "Sew band and crown of the second hat the same way.": "Nähe Seitenteil und Kopfteil des zweiten Huts genauso.",
    "Join outer and inner hat": "Äußeren und inneren Hut verbinden",
    "Fold the lower allowance of the inner hat to the wrong side. Slip it into the outer hat, wrong sides together, "
    "so the fold covers the brim seam. Pin and topstitch close to the fold from the outside, through all layers.":
        "Bügle die untere Nahtzugabe des inneren Huts nach links. Schiebe ihn links auf links in den äußeren Hut, so "
        "dass der Bruch die Krempennaht verdeckt. Stecke und steppe von außen knapp an der Bruchkante durch alle "
        "Lagen.",
    "Press the brim over a rolled towel.": "Bügle die Krempe über einem gerollten Handtuch.",
    "Second fabric": "Zweiter Stoff",
    "Ear flap hat": "Ohrenmütze", "Hat": "Mütze", "Hat lining": "Mützenfutter", "Ear flap": "Ohrenklappe",
    "Ear flap lining": "Futter Ohrenklappe", "Flap top": "Obere Kante Klappe", "Flap edge": "Klappenkante",
    "Tie": "Bindeband", "Tie end": "Bandende", "Tie edge": "Bandkante", "Ties": "Bindebänder",
    "Hat height": "Mützenhöhe", "Ear flap length": "Länge Ohrenklappe", "Lower edge": "Untere Kante",
    "Side and crown seams": "Seiten- und Scheitelnaht", "Lining side and crown seams": "Futter: Seiten- und Scheitelnaht",
    "Ear flaps round": "Ohrenklappen rundherum", "Lower edge (hat ↔ lining)": "Untere Kante (Mütze ↔ Futter)",
    "Hat goes over the head": "Mütze geht über den Kopf", "Flap covers the ear": "Klappe bedeckt das Ohr",
    "≥ {n} % of the head": "≥ {n} % des Kopfumfangs",
    "does it sit firmly without pressing, and do the flaps cover the ears completely?":
        "Sitzt sie fest, ohne zu drücken, und bedecken die Klappen die Ohren ganz?",
    "Sew the ties": "Bindebänder nähen",
    "Fold each tie lengthwise right sides together and sew the long edge and one end with {n} mm seam allowance. "
    "Turn with a safety pin.":
        "Falte jedes Band der Länge nach rechts auf rechts und nähe die lange Kante und ein Ende mit {n} mm "
        "Nahtzugabe. Wende es mit einer Sicherheitsnadel.",
    "Sew the ear flaps": "Ohrenklappen nähen",
    "Lay each flap right sides together onto its lining, the tie between them at the bottom, pointing inwards. Sew "
    "round the curved edge with {n} mm seam allowance; the top stays open.":
        "Lege jede Klappe rechts auf rechts auf ihr Futter, das Band unten dazwischen, nach innen zeigend. Nähe die "
        "runde Kante mit {n} mm Nahtzugabe; oben bleibt offen.",
    "Lay each flap right sides together onto its lining. Sew round the curved edge with {n} mm seam allowance; the "
    "top stays open.":
        "Lege jede Klappe rechts auf rechts auf ihr Futter. Nähe die runde Kante mit {n} mm Nahtzugabe; oben bleibt "
        "offen.",
    "Turn the flaps": "Klappen wenden", "Clip the curve, turn the flaps and press them flat.":
        "Schneide die Rundung ein, wende die Klappen und bügle sie flach.",
    "Sew the hat": "Mütze nähen",
    "Lay both hat halves right sides together and sew from one lower edge over the crown to the other with {n} mm "
    "seam allowance.":
        "Lege beide Mützenhälften rechts auf rechts und nähe von einer unteren Kante über den Scheitel zur anderen "
        "mit {n} mm Nahtzugabe.",
    "Sew the lining": "Futter nähen",
    "Sew the lining the same way, but leave {n} cm open in one side seam for turning.":
        "Nähe das Futter genauso, lass aber in einer Seitennaht {n} cm zum Wenden offen.",
    "Baste the flaps on": "Klappen anheften",
    "Hat right side out: pin each flap onto the right side of the hat, centred over a side seam, raw edges level, "
    "the flap pointing up. Baste close to the edge.":
        "Mütze rechts herum: stecke jede Klappe auf die rechte Seite der Mütze, mittig über eine Seitennaht, "
        "offene Kanten bündig, die Klappe zeigt nach oben. Hefte sie knapp an der Kante fest.",
    "Sew hat and lining together": "Mütze und Futter verbinden",
    "Put the hat into the lining, right sides together; the flaps lie between the layers. Match the side seams and "
    "sew round the lower edge with {n} mm seam allowance.":
        "Stecke die Mütze rechts auf rechts in das Futter; die Klappen liegen dazwischen. Lege die Seitennähte "
        "aufeinander und nähe die untere Kante mit {n} mm Nahtzugabe rundherum.",
    "Turn and close the opening": "Wenden und Öffnung schließen",
    "Turn the hat through the opening in the lining. Close the opening with a ladder stitch and push the lining into "
    "the hat.":
        "Wende die Mütze durch die Öffnung im Futter. Schließe die Öffnung mit dem Matratzenstich und schiebe das "
        "Futter in die Mütze.",
    "Topstitch the lower edge": "Untere Kante absteppen",
    "Optional: topstitch {n} mm from the lower edge and round the flaps.":
        "Optional: steppe {n} mm von der unteren Kante und um die Klappen ab.",
    "Baseball cap": "Basecap", "Crown panel": "Kopfteil-Segment", "Back panel": "Hinteres Segment",
    "Strap opening": "Riemenöffnung", "Centre back seam": "Hintere Mittelnaht", "Crown seam": "Scheitelnaht",
    "Peak": "Schirm", "Peak insert": "Schirmeinlage", "Peak seam": "Schirmnaht", "Peak edge": "Schirmkante",
    "Peak insert (plastic, 0,5–0,8 mm)": "Schirmeinlage (Kunststoff, 0,5–0,8 mm)",
    "Peak insert (plastic, 0.5–0.8 mm)": "Schirmeinlage (Kunststoff, 0,5–0,8 mm)",
    "Top and under peak": "Schirm oben und unten", "No seam allowance; trim 3 mm all round":
        "Ohne Nahtzugabe; ringsum 3 mm kürzen",
    "Strap": "Riemen", "Strap end": "Riemenende", "Strap edge": "Riemenkante", "Eyelet (optional)": "Öse (optional)",
    "2 front panels (with interfacing) and 2 side panels": "2 vordere Segmente (mit Einlage) und 2 seitliche",
    "Crown seams (front and sides)": "Scheitelnähte (vorne und seitlich)", "Crown seams (back)": "Scheitelnähte (hinten)",
    "Peak ↔ front panels": "Schirm ↔ vordere Segmente", "peak eased in": "Schirm eingehalten",
    "Head opening (strap closed in the middle)": "Kopföffnung (Riemen in der Mitte geschlossen)",
    "Head opening incl. strap": "Kopföffnung inkl. Riemen", "strap closed in the middle position":
        "Riemen in mittlerer Stellung", "Peak depth": "Schirmtiefe", "Crown height": "Höhe Kopfteil",
    "Button: {n} cover button {n}–{n} mm for the top": "Knopf: {n} Überziehknopf {n}–{n} mm für oben",
    "Velcro: {n} cm × {n} cm for the strap": "Klett: {n} cm × {n} cm für den Riemen",
    "Interfacing: firm iron-on for the two front panels": "Bügeleinlage: fest, für die beiden vorderen Segmente",
    "Binding: {n} cm bias binding, {n} mm wide (folded), for the inside lower edge":
        "Schrägband: {n} cm, {n} mm breit (gefalzt), für die untere Kante innen",
    "does it sit on the head with the strap in the middle position, the peak straight to the front?":
        "Sitzt sie mit dem Riemen in mittlerer Stellung auf dem Kopf, der Schirm gerade nach vorne?",
    "Interface the front panels": "Vordere Segmente verstärken",
    "Iron firm interfacing onto the wrong side of two of the four crown panels: they become the front.":
        "Bügle feste Einlage auf die linke Seite von zwei der vier Kopfteil-Segmente: sie werden die vorderen.",
    "Sew the front and the sides": "Vorderteil und Seiten nähen",
    "Sew the two front panels together along one long edge, then a side panel to each, all with {n} mm seam "
    "allowance.":
        "Nähe die beiden vorderen Segmente an einer langen Kante zusammen, dann an jedes ein seitliches, alles mit "
        "{n} mm Nahtzugabe.",
    "Sew the back": "Hinterteil nähen",
    "Sew the two back panels together along the centre-back edge above the arch, {n} mm seam allowance.":
        "Nähe die beiden hinteren Segmente an der hinteren Mittelkante oberhalb des Bogens zusammen, {n} mm "
        "Nahtzugabe.",
    "Close the crown": "Kopfteil schließen",
    "Pin the back to the front part and sew the two remaining seams with {n} mm seam allowance, over the top.":
        "Stecke das Hinterteil an das Vorderteil und nähe die beiden übrigen Nähte mit {n} mm Nahtzugabe über den "
        "Scheitel.",
    "Press every seam open over a ham or a rolled towel.":
        "Bügle jede Naht über einem Bügelei oder gerollten Handtuch auseinander.",
    "Topstitch the crown seams": "Scheitelnähte absteppen",
    "Topstitch {n} mm on both sides of every crown seam.": "Steppe jede Scheitelnaht beidseitig {n} mm breit ab.",
    "Sew the peak": "Schirm nähen",
    "Lay the two peak pieces right sides together and sew the outer curve with {n} mm seam allowance. Trim to {n} mm "
    "and turn.":
        "Lege die beiden Schirmteile rechts auf rechts und nähe die äußere Rundung mit {n} mm Nahtzugabe. Kürze auf "
        "{n} mm und wende.",
    "Slide the insert in": "Einlage einschieben",
    "Push the plastic insert into the peak up to the outer edge. Sew close along the insert's inner edge with a "
    "zipper foot so it cannot move.":
        "Schiebe die Kunststoffeinlage bis an die Außenkante in den Schirm. Nähe mit dem Reißverschlussfuß knapp an "
        "der inneren Kante der Einlage entlang, damit sie nicht verrutscht.",
    "Topstitch the peak": "Schirm absteppen",
    "Topstitch rows {n} mm apart, parallel to the outer edge, with a long stitch.":
        "Steppe mit langem Stich Reihen mit {n} mm Abstand parallel zur Außenkante.",
    "Sew the peak on": "Schirm annähen",
    "Pin the peak right sides together to the lower edge of the front panels, centres matching, and sew with {n} mm "
    "seam allowance.":
        "Stecke den Schirm rechts auf rechts an die untere Kante der vorderen Segmente, Mitte auf Mitte, und nähe mit "
        "{n} mm Nahtzugabe.",
    "Bind the lower edge": "Untere Kante einfassen",
    "Unfold one edge of the bias binding and sew it right sides together round the whole lower edge and the arch in "
    "the crease. Fold it inside over the allowances and topstitch it down.":
        "Klappe eine Kante des Schrägbands auf und nähe es rechts auf rechts im Falz um die ganze untere Kante und "
        "den Bogen. Schlage es nach innen über die Nahtzugaben und steppe es fest.",
    "Sew on the strap": "Riemen annähen",
    "Sew the straps with velcro (or snaps) to the inside of the arch, one on each side.":
        "Nähe die Riemen mit Klett (oder Druckknöpfen) innen an den Bogen, je einen auf jeder Seite.",
    "Cover the button": "Knopf beziehen",
    "Cover the button with a scrap of fabric and sew it on the top where the six seams meet.":
        "Beziehe den Knopf mit einem Stoffrest und nähe ihn oben an, wo die sechs Nähte zusammentreffen.",
    "Press the crown over a ball or a rolled towel.": "Bügle das Kopfteil über einem Ball oder gerollten Handtuch.",
})

# ---------------------------------------------------------------------- bags
TABLE.update({
    "Tote bag": "Tragetasche", "Drawstring bag": "Turnbeutel", "Bag": "Tasche", "Depth": "Tiefe",
    "Bottom": "Boden", "Bottom fold": "Bruch am Boden", "Bottom seam": "Bodennaht", "Boxed corner": "Bodenecke",
    "Boxed corners": "Bodenecken", "Top edge": "Obere Kante", "Top edge (bag ↔ lining)": "Obere Kante (Tasche ↔ Futter)",
    "Lining side seams": "Seitennähte Futter", "Lining bottom seam": "Bodennaht Futter",
    "Lining boxed corners": "Bodenecken Futter", "Handle": "Henkel", "Handle end": "Henkelende",
    "Folded edge": "Umgelegte Kante", "Inner pocket": "Innentasche", "Pocket edge": "Taschenkante",
    "Pocket placement": "Taschenposition", "Casing": "Tunnel", "Leave open": "Offen lassen", "Corner loop": "Eckschlaufe",
    "Loop edge": "Schlaufenkante", "Loop end": "Schlaufenende", "Side seams (left)": "Seitennähte (links)",
    "Cord: {n} pieces of {n} cm ({n}–{n} mm thick)": "Kordel: {n} Stück à {n} cm ({n}–{n} mm dick)",
    "is the size right, and do the handles sit comfortably on the shoulder?":
        "Stimmt die Größe, und liegen die Henkel angenehm auf der Schulter?",
    "Press the corner loops": "Eckschlaufen bügeln",
    "Press each loop in half lengthwise, then fold both long edges into the middle and press again.":
        "Bügle jede Schlaufe der Länge nach zur Hälfte, schlage dann beide langen Kanten zur Mitte ein und bügle "
        "noch einmal.",
    "Topstitch the loops": "Schlaufen absteppen",
    "Topstitch along the open long edge. Fold each loop in half crosswise.":
        "Steppe entlang der offenen langen Kante ab. Lege jede Schlaufe quer zur Hälfte.",
    "Baste the loops on": "Schlaufen anheften",
    "Pin the folded loops at the marks of the lower corners onto the right side, loop pointing inwards, raw ends "
    "level with the side edge, and baste them.":
        "Stecke die gefalteten Schlaufen an den Markierungen der unteren Ecken auf die rechte Seite, Schlaufe nach "
        "innen, offene Enden bündig mit der Seitenkante, und hefte sie fest.",
    "Fold the bag right sides together at the bottom fold. Sew both side seams with {n} mm seam allowance, from the "
    "bottom up to the 'leave open' mark; the top {n} cm stay open.":
        "Falte die Tasche am Bruch rechts auf rechts. Nähe beide Seitennähte mit {n} mm Nahtzugabe vom Boden bis "
        "zur Markierung „offen lassen“; die oberen {n} cm bleiben offen.",
    "Backstitch well at the mark and over the loops.": "Verriegle gut an der Markierung und über den Schlaufen.",
    "Press the allowances open": "Nahtzugaben auseinanderbügeln",
    "Press the allowances open, also along the open part; topstitch them down there in a U shape.":
        "Bügle die Nahtzugaben auseinander, auch im offenen Teil; steppe sie dort in U-Form fest.",
    "Sew the casing": "Tunnel nähen",
    "Fold the upper edge {n} cm, then {n} cm to the wrong side and press. Sew close to the lower fold all round; "
    "front and back stay separate tunnels.":
        "Bügle die obere Kante {n} cm und dann {n} cm nach links um. Steppe rundherum knapp an der unteren "
        "Bruchkante; vorne und hinten bleiben getrennte Tunnel.",
    "Thread the cords": "Kordeln einziehen",
    "Thread one cord with a safety pin through the front tunnel and back through the back tunnel, the second cord "
    "the other way round, starting at the other side. Pull each pair of ends through the loop of its corner and "
    "knot it.":
        "Ziehe eine Kordel mit der Sicherheitsnadel durch den vorderen Tunnel und durch den hinteren zurück, die "
        "zweite Kordel genauso, aber von der anderen Seite. Ziehe jedes Endenpaar durch die Schlaufe seiner Ecke und "
        "verknote es.",
    "Press the handles": "Henkel bügeln",
    "Press each handle in half lengthwise, open it, fold both long edges into the middle and press, then fold in "
    "half again: {n} layers.":
        "Bügle jeden Henkel der Länge nach zur Hälfte, öffne ihn, schlage beide langen Kanten zur Mitte ein und "
        "bügle, dann wieder zur Hälfte legen: {n} Lagen.",
    "Topstitch the handles": "Henkel absteppen",
    "Topstitch {n} mm from both long edges.": "Steppe {n} mm neben beiden langen Kanten ab.",
    "Hem the pocket opening": "Tascheneingriff säumen",
    "Fold the upper pocket edge {n} cm, then {n} cm to the wrong side and sew it down close to the lower fold.":
        "Bügle die obere Taschenkante {n} cm und dann {n} cm nach links um und steppe sie knapp an der unteren "
        "Bruchkante fest.",
    "Press the pocket edges": "Taschenkanten bügeln",
    "Press the other three edges {n} cm to the wrong side.": "Bügle die anderen drei Kanten {n} cm nach links um.",
    "Sew the pocket onto the lining": "Tasche aufs Futter nähen",
    "Pin the pocket onto the marked spot of one lining piece and topstitch sides and bottom {n} mm from the edge.":
        "Stecke die Tasche auf die markierte Stelle eines Futterteils und steppe Seiten und Boden {n} mm von der "
        "Kante ab.",
    "Sew side and bottom seams": "Seiten- und Bodennaht nähen",
    "Lay both bag pieces right sides together. Sew the side seams and the bottom seam with {n} mm seam allowance; "
    "the cut-out corners stay open.":
        "Lege beide Taschenteile rechts auf rechts. Nähe die Seitennähte und die Bodennaht mit {n} mm Nahtzugabe; "
        "die ausgeschnittenen Ecken bleiben offen.",
    "Sew the boxed corners": "Bodenecken nähen",
    "Pull each open corner apart so that side seam and bottom seam lie on top of each other. Sew the raw edge "
    "straight across with {n} mm seam allowance.":
        "Ziehe jede offene Ecke auseinander, so dass Seitennaht und Bodennaht aufeinanderliegen. Nähe die offene "
        "Kante gerade quer mit {n} mm Nahtzugabe.",
    "Press the side seam and the bottom seam allowances in opposite directions so they nest.":
        "Bügle die Nahtzugaben von Seiten- und Bodennaht in entgegengesetzte Richtungen, dann liegen sie flach "
        "ineinander.",
    "Sew the lining the same way with {n} mm seam allowance, but leave {n} cm open in the bottom seam for turning.":
        "Nähe das Futter genauso mit {n} mm Nahtzugabe, lass aber in der Bodennaht {n} cm zum Wenden offen.",
    "Box the lining corners": "Bodenecken des Futters nähen",
    "Sew the corners of the lining like those of the bag, with {n} mm seam allowance.":
        "Nähe die Ecken des Futters wie die der Tasche, mit {n} mm Nahtzugabe.",
    "Baste the handles on": "Henkel anheften",
    "Bag right side out: pin the handle ends at the marks, raw ends level with the top edge, the handle hanging down "
    "(not twisted). Baste {n} mm from the edge.":
        "Tasche rechts herum: stecke die Henkelenden an den Markierungen fest, offene Enden bündig mit der oberen "
        "Kante, der Henkel hängt nach unten (nicht verdreht). Hefte {n} mm von der Kante.",
    "Sew the top edge": "Obere Kante nähen",
    "Put the bag (right side out) into the lining (wrong side out), right sides together. Match the side seams and "
    "sew round the top edge with {n} mm seam allowance.":
        "Stecke die Tasche (rechts herum) in das Futter (links herum), rechts auf rechts. Lege die Seitennähte "
        "aufeinander und nähe die obere Kante mit {n} mm Nahtzugabe rundherum.",
    "Turn and close the lining": "Wenden und Futter schließen",
    "Turn the bag through the opening in the lining. Fold the allowances of the opening in and topstitch it closed "
    "close to the edge.":
        "Wende die Tasche durch die Öffnung im Futter. Schlage die Nahtzugaben der Öffnung ein und steppe sie knapp "
        "an der Kante zu.",
    "Topstitch the top edge": "Obere Kante absteppen",
    "Push the lining into the bag, press the top edge and topstitch {n} mm from it.":
        "Schiebe das Futter in die Tasche, bügle die obere Kante und steppe {n} mm daneben ab.",
    "Fold the top edge {n} cm, then {n} cm to the wrong side. Slip the handle ends under the fold at the marks and "
    "sew close to the lower fold.":
        "Bügle die obere Kante {n} cm und dann {n} cm nach links um. Schiebe die Henkelenden an den Markierungen "
        "unter den Umschlag und steppe knapp an der unteren Bruchkante.",
    "Secure the handles": "Henkel sichern",
    "Fold the handles up and topstitch close to the top edge, catching them.":
        "Klappe die Henkel nach oben und steppe knapp an der oberen Kante ab, dabei die Henkel mitfassen.",
    "Press the bag; press the boxed corners into shape.": "Bügle die Tasche; bügle die Bodenecken in Form.",

    # ------------------------------------------------------------------ new garments (bodysuit … sleeping bag, style lines)
    'Arm length {n} cm looks unusual for a body height of {n} cm':
        'Armlänge {n} cm wirkt ungewöhnlich für eine Körpergröße von {n} cm',
    'Armhole (binding)': 'Armloch (Einfassung)',
    'Armhole (elastic, turned)': 'Armloch (Gummi, umgeschlagen)',
    'Armhole (lined)': 'Armloch (gefüttert)',
    'Armhole binding': 'Armlochblende',
    'Armhole binding (bias)': 'Armlochblende (schräg)',
    'Armhole binding ↔ armhole': 'Armlochblende ↔ Armloch',
    'Baby romper': 'Baby-Strampler',
    'Baby sleeping bag': 'Baby-Schlafsack',
    'Back bodice': 'Rückenteil Oberteil',
    'Back bodice lining': 'Futter Rückenteil Oberteil',
    'Back centre panel': 'Rückenmittelteil',
    'Back lining': 'Rückenteil Futter',
    'Back lower part': 'Rückenteil unten',
    'Back neck facing': 'Rückwärtiger Halsbeleg',
    'Back side panel': 'Rückenseitenteil',
    'Back upper part (contrast)': 'Rückenteil oben (Kontrast)',
    'Back wadding': 'Rückenteil Volumenvlies',
    'Back yoke': 'Rückenpasse',
    'Bag bottom': 'Taschenboden',
    'Bag length (shoulder to bottom)': 'Schlafsacklänge (Schulter bis Boden)',
    'Bag side': 'Schlafsackseite',
    'Band edge': 'Bündchenkante',
    'Band end (hem)': 'Blendenende (Saum)',
    'Baste the liner in': 'Innenslip einheften',
    'Baste the lining': 'Futter heften',
    'Baste the straps on': 'Träger anheften',
    'Baste the wadding on': 'Volumenvlies anheften',
    'Belt edge': 'Gürtelkante',
    'Belt end': 'Gürtelende',
    'Belt end (centre back seam)': 'Gürtelende (hintere Mittelnaht)',
    'Belt loop strip': 'Streifen für Gürtelschlaufen',
    'Bib edge': 'Latzkante',
    'Bib height': 'Latzhöhe',
    'Bib pocket': 'Latztasche',
    'Bib round (outer ↔ facing)': 'Latz rundum (außen ↔ Beleg)',
    'Bib sits on the front waistband': 'Latz sitzt auf dem vorderen Bund',
    'Bib top edge': 'Latz-Oberkante',
    'Bind the armholes': 'Armlöcher einfassen',
    'Bind the leg openings': 'Beinausschnitte einfassen',
    'Bind the sleeve placket': 'Ärmelschlitz einfassen',
    'Bind the wrap edges': 'Wickelkanten einfassen',
    'Binding edge': 'Einfasskante',
    'Blouse (short sleeves)': 'Bluse (kurze Ärmel)',
    'Bodysuit': 'Body',
    'Boiler suit': 'Arbeitsoverall',
    'Bottom seam front ↔ back': 'Bodennaht vorne ↔ hinten',
    'Bottom width (flat × {n})': 'Weite unten (flach × {n})',
    'Boxer briefs': 'Retroshorts',
    'Briefs': 'Slip',
    'Bust dart': 'Brustabnäher',
    'Bust dart: {n} cm at the side seam': 'Brustabnäher: {n} cm an der Seitennaht',
    'Button': 'Knopf',
    'Button band': 'Knopfleiste',
    'Button band width': 'Breite der Knopfleiste',
    'Button band ↔ front edges and neckline (slightly stretched)':
        'Knopfleiste ↔ Vorderkanten und Halsausschnitt (leicht gedehnt)',
    'Buttonhole': 'Knopfloch',
    'Buttonhole and button': 'Knopfloch und Knopf',
    'Buttonholes and buttons': 'Knopflöcher und Knöpfe',
    'Buttons: {n} buttons, {n} mm': 'Knöpfe: {n} Knöpfe, {n} mm',
    'Buttons: {n} buttons, {n} mm (+ {n} smaller ones for the cuffs)':
        'Knöpfe: {n} Knöpfe, {n} mm (+ {n} kleinere für die Manschetten)',
    'Buttons: {n} buttons, {n} mm (or dungaree buckles)':
        'Knöpfe: {n} Knöpfe, {n} mm (oder Latzhosenschnallen)',
    'Cardigan': 'Cardigan',
    'Centre back': 'Hintere Mitte',
    'Centre back (fold)': 'Hintere Mitte (Stoffbruch)',
    'Centre back (zip)': 'Hintere Mitte (Reißverschluss)',
    'Centre front (fold)': 'Vordere Mitte (Stoffbruch)',
    'Centre ↔ top edge (back)': 'Mitte ↔ Oberkante (hinten)',
    'Centre ↔ top edge (front)': 'Mitte ↔ Oberkante (vorne)',
    'Chest pocket': 'Brusttasche',
    'Clip the neckline allowance every {n} cm so it follows the collar.':
        'Schneide die Nahtzugabe am Halsausschnitt alle {n} cm ein, damit sie dem Kragen folgt.',
    'Close the lining at the waist': 'Futter an der Taille schließen',
    'Close the placket': 'Schlitzleiste schließen',
    'Close the pocket bags': 'Taschenbeutel schließen',
    'Close the top edge': 'Oberkante schließen',
    'Coat': 'Mantel',
    'Coin pocket': 'Münztasche',
    'Coin pocket (right side panel only)': 'Münztasche (nur rechtes Seitenteil)',
    'Collar': 'Kragen',
    'Collar edge': 'Kragenkante',
    'Collar point': 'Kragenspitze',
    'Collar round (upper ↔ under collar)': 'Kragen rundum (Ober- ↔ Unterkragen)',
    'Collar seam': 'Kragennaht',
    'Collar stand': 'Kragensteg',
    'Collar ↔ collar stand': 'Kragen ↔ Kragensteg',
    'Collar ↔ neckline': 'Kragen ↔ Halsausschnitt',
    'Collar ↔ neckline (slightly stretched)': 'Kragen ↔ Halsausschnitt (leicht gedehnt)',
    'Contrast fabric': 'Kontraststoff',
    'Cotton jersey': 'Baumwolljersey',
    'Crotch (snap facing)': 'Schritt (Druckknopfbeleg)',
    'Crotch (snap facing, overlaps the front)': 'Schritt (Druckknopfbeleg, über dem Vorderteil)',
    'Crotch gusset (lining)': 'Schrittzwickel (Futter)',
    'Crotch length': 'Schrittlänge',
    'Crotch length (front + gusset + back)': 'Schrittlänge (vorne + Zwickel + hinten)',
    'Crotch seam (zip at the top)': 'Schrittnaht (oben Reißverschluss)',
    'Crotch: front ↔ back': 'Schritt: vorne ↔ hinten',
    'Cuff (closed)': 'Manschette (geschlossen)',
    'Cuff end': 'Manschettenende',
    'Cuff ends': 'Manschettenenden',
    'Cuff seam (pleats)': 'Manschettennaht (Falten)',
    'Cuff ↔ sleeve (pleated)': 'Manschette ↔ Ärmel (mit Falten)',
    'Cut the opening': 'Öffnung einschneiden',
    'Do not backstitch at the point: tie the threads off by hand.':
        'An der Spitze nicht verriegeln: Verknote die Fäden von Hand.',
    'Drawcord: {n} cm flat cord; {n} eyelets {n} mm (or {n} buttonholes)':
        'Kordel: {n} cm Flachkordel; {n} Ösen {n} mm (oder {n} Knopflöcher)',
    'Dungarees': 'Latzhose',
    'Edge': 'Kante',
    'End (button)': 'Ende (Knopf)',
    'End (buttonhole)': 'Ende (Knopfloch)',
    'Eyelet (drawcord)': 'Öse (Kordel)',
    'Facing seam': 'Belegnaht',
    'Facing seam back (facing ↔ lining)': 'Belegnaht hinten (Beleg ↔ Futter)',
    'Facing seam front (facing ↔ lining)': 'Belegnaht vorne (Beleg ↔ Futter)',
    'Facing shoulders': 'Schulternähte Beleg',
    'Facing ↔ front edge': 'Beleg ↔ Vorderkante',
    'Fitted dress': 'Tailliertes Kleid',
    'Flap pocket opening': 'Eingriff Pattentasche',
    'Flap seam': 'Pattennaht',
    'Fly extension': 'Schlitzübertritt',
    'Fly shield': 'Schlitzuntertritt',
    'Fly topstitching (left front leg only)': 'Schlitzsteppung (nur linkes Vorderbein)',
    'Fly: left ↔ right extension': 'Schlitz: linker ↔ rechter Übertritt',
    'Fold line (stand)': 'Umbruchlinie (Leiste)',
    'Fold the band in half': 'Blende längs falten',
    'Fold the button band in half': 'Knopfleiste längs falten',
    'Fold the button stands': 'Knopfleisten umbügeln',
    'Fold the collar': 'Kragen falten',
    'Fold the crotch facings': 'Schrittbelege umbügeln',
    'Fold the front edges': 'Vorderkanten umbügeln',
    'Fold the hem {n} cm to the wrong side and stitch it down.':
        'Bügle den Saum {n} cm nach links um und steppe ihn fest.',
    'Fold the snap facings': 'Druckknopfbelege umbügeln',
    'Fold the top edge twice and topstitch it with topstitching thread.':
        'Schlage die Oberkante doppelt ein und steppe sie mit Steppgarn ab.',
    'Fold the top edge twice and topstitch it.': 'Schlage die Oberkante doppelt ein und steppe sie ab.',
    'Fold the top edge {n} cm to the wrong side and stitch it down.':
        'Bügle die Oberkante {n} cm nach links um und steppe sie fest.',
    'Foot seam (sole)': 'Fußnaht (Sohle)',
    'Footed romper': 'Strampler mit Füßen',
    'Front (outer and inner)': 'Vorderteil (außen und innen)',
    'Front bib': 'Vorderer Latz',
    'Front bib lining': 'Futter vorderer Latz',
    'Front centre panel': 'Vorderes Mittelteil',
    'Front edge (band)': 'Vorderkante (Blende)',
    'Front edge (button stand)': 'Vorderkante (Knopfleiste)',
    'Front edge (button stand), Saum': 'Vorderkante (Knopfleiste), Saum',
    'Front edge (facing seam)': 'Vorderkante (Belegnaht)',
    'Front edge (hem)': 'Vorderkante (Saum)',
    'Front edge (hem), Saum': 'Vorderkante (Saum), Saum',
    'Front end': 'Vorderes Ende',
    'Front end (band)': 'Vorderes Ende (Blende)',
    'Front facing': 'Vorderer Beleg',
    'Front lining': 'Vorderteil Futter',
    'Front lower part': 'Vorderteil unten',
    'Front side panel': 'Vorderes Seitenteil',
    'Front upper part (contrast)': 'Vorderteil oben (Kontrast)',
    'Front wadding': 'Vorderteil Volumenvlies',
    'Front yoke': 'Vordere Passe',
    'Grundlagen: Nähmaschine': 'Grundlagen: Nähmaschine',
    'Gusset': 'Zwickel',
    'Gusset back end': 'Zwickelende hinten',
    'Gusset edge (turned under)': 'Zwickelkante (eingeschlagen)',
    'Gusset edge (turned under), Gusset end': 'Zwickelkante (eingeschlagen), Zwickelende',
    'Gusset end': 'Zwickelende',
    'Gusset front end': 'Zwickelende vorne',
    'Gusset lining: cotton jersey (breathable)': 'Zwickelfutter: Baumwolljersey (atmungsaktiv)',
    'Gusset seam': 'Zwickelnaht',
    'Gusset ↔ back': 'Zwickel ↔ Rückenteil',
    'Gusset ↔ front': 'Zwickel ↔ Vorderteil',
    'Head cannot slip through the neckline': 'Kopf kann nicht durch den Halsausschnitt rutschen',
    'Head fits through the open placket': 'Kopf passt durch die offene Leiste',
    'Hem (lining, sewn to the hem allowance)': 'Saum (Futter, an die Saumzugabe genäht)',
    'Hem (lining, sewn to the sleeve hem allowance)': 'Saum (Futter, an die Ärmelsaumzugabe genäht)',
    'Hem casing (drawcord)': 'Saumtunnel (Kordel)',
    'Hem the bib pocket': 'Latztasche säumen',
    'Hem the coin pocket': 'Münztasche säumen',
    'Hem the front edges': 'Vorderkanten säumen',
    'Hem the jacket': 'Jacke säumen',
    'Hem ↔ front edge': 'Saum ↔ Vorderkante',
    'Hip (unstretched)': 'Hüfte (ungedehnt)',
    'Hip passes the opened fly': 'Hüfte passt durch den geöffneten Schlitz',
    'Hip with negative ease': 'Hüfte mit negativer Mehrweite',
    'Inner collar ↔ facing neckline': 'Innerer Kragen ↔ Halsausschnitt Beleg',
    'Inner neckline seam': 'Innere Halsnaht',
    'Inseam (snap facing, turned)': 'Innere Beinnaht (Druckknopfbeleg, umgeschlagen)',
    'Interface': 'Einlage aufbügeln',
    'Interface the button band': 'Einlage auf die Knopfleiste bügeln',
    'Interface the facings': 'Einlage auf die Belege bügeln',
    'Interface the placket': 'Einlage auf die Leiste bügeln',
    'Interface the pocket opening': 'Einlage auf den Tascheneingriff bügeln',
    'Interface the pocket openings': 'Einlage auf die Tascheneingriffe bügeln',
    'Interface the waistband': 'Einlage auf den Bund bügeln',
    'Interface the zip edges': 'Einlage auf die Reißverschlusskanten bügeln',
    'Interfacing: light iron-on for the button stands': 'Einlage: leichte Bügeleinlage für die Knopfleisten',
    'Interfacing: light iron-on for the zip edges and the collar':
        'Einlage: leichte Bügeleinlage für die Reißverschlusskanten und den Kragen',
    'Invisible zip, {n} cm long (opening {n} cm).':
        'Nahtverdeckter Reißverschluss, {n} cm lang (Öffnung {n} cm).',
    'Iron a strip of interfacing behind each zip pocket marking.':
        'Bügle hinter jede Markierung einer Reißverschlusstasche einen Streifen Einlage.',
    'Iron interfacing onto the waistband.': 'Bügle Einlage auf den Bund.',
    'Iron light interfacing onto one half of each placket strip.':
        'Bügle leichte Einlage auf eine Hälfte jedes Leistenstreifens.',
    'Jeans': 'Jeans',
    'Jersey with elastane: {n}–{n} mm': 'Jersey mit Elasthan: {n}–{n} mm',
    'Jetted pocket opening': 'Eingriff Paspeltasche',
    'Jumpsuit': 'Jumpsuit',
    'Leg band': 'Beinblende',
    'Leg band ↔ leg opening (stretched)': 'Beinblende ↔ Beinausschnitt (gedehnt)',
    'Leg elastic': 'Beingummi',
    'Leg elastic (each)': 'Beingummi (je Bein)',
    'Leg opening (elastic)': 'Beinausschnitt (Gummi)',
    'Leg opening (elastic), Top edge (elastic)': 'Beinausschnitt (Gummi), Oberkante (Gummi)',
    'Leg opening (elastic, turned)': 'Beinausschnitt (Gummi, umgeschlagen)',
    'Leg opening (elastic, turned), Neckline (elastic, turned)':
        'Beinausschnitt (Gummi, umgeschlagen), Halsausschnitt (Gummi, umgeschlagen)',
    'Lined jacket': 'Gefütterte Jacke',
    'Liner back': 'Innenslip hinten',
    'Liner front': 'Innenslip vorne',
    'Liner gusset': 'Innenslip Zwickel',
    'Liner gusset ↔ back': 'Innenslip-Zwickel ↔ hinten',
    'Liner gusset ↔ front': 'Innenslip-Zwickel ↔ vorne',
    'Liner side seams': 'Seitennähte Innenslip',
    'Lining armhole ↔ sleeve lining': 'Futter-Armloch ↔ Ärmelfutter',
    'Lining or main fabric': 'Futter oder Oberstoff',
    'Lining shoulders': 'Schulternähte Futter',
    'Lining sleeve seams': 'Ärmelnähte Futter',
    'Lining: jersey': 'Futter: Jersey',
    'Lip edge': 'Paspelkante',
    'Lip end': 'Paspelende',
    'Lower edge (turned under)': 'Unterkante (eingeschlagen)',
    'Main fabric + cotton jersey': 'Oberstoff + Baumwolljersey',
    'Make the belt loops': 'Gürtelschlaufen nähen',
    'Mesh': 'Netzstoff',
    'Neck point to crotch': 'Halspunkt bis Schritt',
    'Neckline (elastic, turned)': 'Halsausschnitt (Gummi, umgeschlagen)',
    'Neckline (lined)': 'Halsausschnitt (gefüttert)',
    'Neckline end': 'Ende Halsausschnitt',
    'Neckline seam': 'Halsnaht',
    'Opening edge': 'Öffnungskante',
    'Patch pocket': 'Aufgesetzte Tasche',
    'Peter Pan collar': 'Bubikragen',
    'Pinafore dress': 'Trägerkleid',
    'Placket binding': 'Schlitzeinfassung',
    'Placket length': 'Leistenlänge',
    'Placket opening': 'Leistenöffnung',
    'Placket seam': 'Leistennaht',
    'Placket strip': 'Leistenstreifen',
    'Placket strips ↔ placket opening': 'Leistenstreifen ↔ Leistenöffnung',
    'Pocket bag': 'Taschenbeutel',
    'Pocket bag round': 'Taschenbeutel rundum',
    'Pocket flap': 'Taschenpatte',
    'Pocket flap round': 'Taschenpatte rundum',
    'Pocket lining': 'Taschenfutter',
    'Pocket lips': 'Paspeln',
    'Pocket opening (hem)': 'Tascheneingriff (Saum)',
    'Pocket welt': 'Taschenleiste',
    'Pocket zip facing': 'Reißverschlussbeleg Tasche',
    'Pocket zips: {n} × {n} cm (not separating)': 'Taschenreißverschlüsse: {n} × {n} cm (nicht teilbar)',
    'Polo collar': 'Polokragen',
    'Polo shirt': 'Poloshirt',
    'Press lightly with steam (no heat on the elastic).':
        'Bügle leicht mit Dampf (keine Hitze auf das Gummi).',
    'Press the jacket over a ham, with a pressing cloth.':
        'Bügle die Jacke über einem Bügelkissen, mit einem Bügeltuch.',
    'Pyjamas': 'Schlafanzug',
    'Quick-dry swim fabric (polyester)': 'Schnelltrocknender Badestoff (Polyester)',
    'Raw edge (folded in)': 'Offene Kante (eingeschlagen)',
    'Raw edge (folded inside)': 'Offene Kante (nach innen eingeschlagen)',
    'Raw edges (zip seam)': 'Offene Kanten (Reißverschlussnaht)',
    'Roll the pieces tightly so they fit inside the gusset.':
        'Rolle die Teile fest auf, damit sie in den Zwickel passen.',
    'Room for the legs (hip-healthy)': 'Platz für die Beine (hüftgesund)',
    'Seam edge (turned in)': 'Nahtkante (eingeschlagen)',
    'Separating (jacket) zip, {n} cm long (front opening {n} cm).':
        'Teilbarer Reißverschluss (Jacke), {n} cm lang (vordere Öffnung {n} cm).',
    'Set in the lining sleeves': 'Futterärmel einsetzen',
    'Set the eyelets': 'Ösen einschlagen',
    'Set the snaps': 'Druckknöpfe anbringen',
    'Sew bib and straps on': 'Latz und Träger annähen',
    'Sew bodice and legs together': 'Oberteil und Beine zusammennähen',
    'Sew bodice and lining together': 'Oberteil und Futter zusammennähen',
    'Sew bodice and pants together': 'Oberteil und Hose zusammennähen',
    'Sew buttonholes and buttons': 'Knopflöcher und Knöpfe nähen',
    'Sew facing and jacket together': 'Beleg und Jacke zusammennähen',
    'Sew facings and lining together': 'Belege und Futter zusammennähen',
    'Sew front and back together at the sides with {n} mm seam allowance.':
        'Nähe Vorder- und Rückenteil an den Seiten mit {n} mm Nahtzugabe zusammen.',
    'Sew in the back elastic': 'Gummi im Rücken einnähen',
    'Sew in the invisible zip': 'Nahtverdeckten Reißverschluss einnähen',
    'Sew in the soles': 'Sohlen einnähen',
    'Sew in the zip': 'Reißverschluss einnähen',
    'Sew on the buttons': 'Knöpfe annähen',
    'Sew on the leg elastic': 'Beingummi annähen',
    'Sew on the second tie': 'Zweites Bindeband annähen',
    'Sew on the waist elastic': 'Taillengummi annähen',
    'Sew the Velcro onto the sleeves': 'Klettband auf die Ärmel nähen',
    'Sew the back crotch seam': 'Hintere Schrittnaht nähen',
    'Sew the back yokes on': 'Rückenpassen annähen',
    'Sew the band on': 'Blende annähen',
    'Sew the bib': 'Latz nähen',
    'Sew the bottom edges of front and back together; clip the curves.':
        'Nähe die Unterkanten von Vorder- und Rückenteil zusammen; schneide die Rundungen ein.',
    'Sew the bottom seam': 'Bodennaht nähen',
    'Sew the button band on': 'Knopfleiste annähen',
    'Sew the collar': 'Kragen nähen',
    'Sew the collar into the stand': 'Kragen in den Steg nähen',
    'Sew the collar on': 'Kragen annähen',
    'Sew the cuff ends': 'Manschettenenden nähen',
    'Sew the darts': 'Abnäher nähen',
    'Sew the fly': 'Schlitz nähen',
    'Sew the front crotch seam': 'Vordere Schrittnaht nähen',
    'Sew the gusset to the back (burrito)': 'Zwickel ans Rückenteil nähen (Burrito)',
    'Sew the gusset to the front': 'Zwickel ans Vorderteil nähen',
    'Sew the inner collar on': 'Inneren Kragen annähen',
    'Sew the leg cuffs on': 'Beinbündchen annähen',
    'Sew the leg side seams': 'Seitennähte der Beine nähen',
    'Sew the lining shoulders': 'Schulternähte des Futters nähen',
    'Sew the lining side seams': 'Seitennähte des Futters nähen',
    'Sew the lining the same way, shoulders included.': 'Nähe das Futter genauso, Schultern eingeschlossen.',
    'Sew the lining the same way.': 'Nähe das Futter genauso.',
    'Sew the mesh gusset to the liner front with {n} mm seam allowance.':
        'Nähe den Netzzwickel mit {n} mm Nahtzugabe an das Vorderteil des Innenslips.',
    'Sew the neckline and armholes': 'Halsausschnitt und Armlöcher nähen',
    'Sew the other end of the gusset to the liner back.':
        'Nähe das andere Ende des Zwickels an das Rückenteil des Innenslips.',
    'Sew the outer side seams with {n} mm seam allowance.':
        'Nähe die äußeren Seitennähte mit {n} mm Nahtzugabe.',
    'Sew the placket strips on': 'Leistenstreifen annähen',
    'Sew the pocket flaps': 'Taschenpatten nähen',
    'Sew the pocket zips in': 'Taschenreißverschlüsse einnähen',
    'Sew the shoulder seams of facings and lining.': 'Nähe die Schulternähte von Belegen und Futter.',
    'Sew the side seams of the bodice with {n} mm seam allowance.':
        'Nähe die Seitennähte des Oberteils mit {n} mm Nahtzugabe.',
    'Sew the side seams of the liner.': 'Nähe die Seitennähte des Innenslips.',
    'Sew the side seams of the lining the same way.': 'Nähe die Seitennähte des Futters genauso.',
    'Sew the sleeve tabs': 'Ärmelriegel nähen',
    'Sew the stand collar': 'Stehkragen nähen',
    'Sew the straps': 'Träger nähen',
    'Sew the style seams (back)': 'Teilungsnähte nähen (hinten)',
    'Sew the style seams (front)': 'Teilungsnähte nähen (vorne)',
    'Sew the tie belt': 'Bindegürtel nähen',
    'Sew the two back legs together at the centre back the same way.':
        'Nähe die beiden hinteren Beine genauso in der hinteren Mitte zusammen.',
    'Sew the welt on': 'Leiste annähen',
    'Sew the wings': 'Flügel nähen',
    'Sew the yoke on': 'Passe annähen',
    'Shirt': 'Hemd',
    'Side seam (other side)': 'Seitennaht (andere Seite)',
    'Side ↔ top (front)': 'Seite ↔ oben (vorne)',
    'Side ↔ top edge (back)': 'Seite ↔ Oberkante (hinten)',
    'Side ↔ top edge (front)': 'Seite ↔ Oberkante (vorne)',
    'Skirt dart': 'Rockabnäher',
    'Sleeve lining': 'Ärmelfutter',
    'Sleeve placket (slit)': 'Ärmelschlitz',
    'Sleeve tab': 'Ärmelriegel',
    'Sleeve tabs': 'Ärmelriegel',
    'Snaps: {n} snaps (plastic or metal) for the crotch':
        'Druckknöpfe: {n} Druckknöpfe (Kunststoff oder Metall) für den Schritt',
    'Snaps: {n} snaps ({n}–{n} mm)': 'Druckknöpfe: {n} Druckknöpfe ({n}–{n} mm)',
    'Softshell': 'Softshell',
    'Softshell jacket': 'Softshelljacke',
    'Softshell: {n}–{n} mm': 'Softshell: {n}–{n} mm',
    'Sole edge': 'Sohlenkante',
    'Sole length': 'Sohlenlänge',
    'Sole ↔ leg end': 'Sohle ↔ Beinende',
    'Soles: non-slip sole fabric or a double layer of the main fabric':
        'Sohlen: rutschfester Sohlenstoff oder doppelt gelegter Oberstoff',
    'Stand collar': 'Stehkragen',
    'Stand collar round': 'Stehkragen rundum',
    'Stitch the bib pocket on': 'Latztasche aufsteppen',
    'Stitch the coin pocket on': 'Münztasche aufsteppen',
    'Stitch the gusset in': 'Zwickel einsteppen',
    'Stitch the pockets on': 'Taschen aufsteppen',
    'Strap (crossed)': 'Träger (gekreuzt)',
    'Strap end (buttonhole)': 'Trägerende (Knopfloch)',
    'Strap end (buttonholes)': 'Trägerende (Knopflöcher)',
    'Strap end (into the back seam)': 'Trägerende (in die hintere Naht)',
    'Strap end (into the back waistband)': 'Trägerende (in den hinteren Bund)',
    'Strap length': 'Trägerlänge',
    'Straps': 'Träger',
    'Stretch direction: across (around the body)': 'Dehnrichtung: quer (um den Körper)',
    'Style lines: colour blocking (upper part in a contrast fabric)':
        'Teilungsnähte: Colour Blocking (oberes Teil aus Kontraststoff)',
    'Style lines: front and back yoke': 'Teilungsnähte: Passe vorne und hinten',
    'Style lines: princess seams': 'Teilungsnähte: Prinzessnähte',
    'Style seam': 'Teilungsnaht',
    'Style seam back': 'Teilungsnaht hinten',
    'Style seam front': 'Teilungsnaht vorne',
    'Swaddle sack': 'Pucksack',
    'Swim lining': 'Badefutter',
    'Swim trunks': 'Badeshorts',
    'Swimsuit': 'Badeanzug',
    'Tab edge': 'Riegelkante',
    'Tab end': 'Riegelende',
    'Tab end (into the seam)': 'Riegelende (in die Naht)',
    'The same on the back.': 'Genauso am Rückenteil.',
    'Thread the drawcords': 'Kordeln einziehen',
    'Tie belt': 'Bindegürtel',
    'Tie end (into the seam)': 'Bindebandende (in die Naht)',
    'Tie slot (one side only)': 'Schlitz für das Bindeband (nur eine Seite)',
    'Top edge (bodice ↔ lining)': 'Oberkante (Oberteil ↔ Futter)',
    'Top edge (elastic)': 'Oberkante (Gummi)',
    'Top edge (into the waistband seam)': 'Oberkante (in die Bundnaht)',
    'Top edge (lined)': 'Oberkante (gefüttert)',
    'Top ↔ centre (front)': 'Oben ↔ Mitte (vorne)',
    'Turn the welt through': 'Leiste durchwenden',
    'Understitch the facing close to the seam so it rolls inside.':
        'Steppe den Beleg knapp neben der Naht unter, damit er nach innen rollt.',
    'Velcro: {n} × {n} cm (soft side on the inner wing)':
        'Klettband: {n} × {n} cm (weiche Seite auf dem inneren Flügel)',
    'Vest': 'Weste',
    'Wadding: thin ({n} g/m²)': 'Volumenvlies: dünn ({n} g/m²)',
    'Waist (darts closed)': 'Taille (Abnäher geschlossen)',
    'Waist (wrapped)': 'Taille (gewickelt)',
    'Waist dart': 'Taillenabnäher',
    'Waist elastic': 'Taillengummi',
    'Waist end': 'Taillenende',
    'Waist seam bodice ↔ legs': 'Taillennaht Oberteil ↔ Beine',
    'Waist seam bodice ↔ pants': 'Taillennaht Oberteil ↔ Hose',
    'Waist seam bodice ↔ skirt': 'Taillennaht Oberteil ↔ Rock',
    'Waist seam goes over the hips': 'Taillennaht passt über die Hüfte',
    'Waist with the darts closed': 'Taille mit geschlossenen Abnähern',
    'Waistband fits the mid-rise waistline': 'Bund passt zur mittleren Leibhöhe',
    'Waistband ↔ jeans top edge': 'Bund ↔ Oberkante Jeans',
    'Welt end': 'Leistenende',
    'Welt pocket opening': 'Eingriff Leistentasche',
    'Welt seam': 'Leistennaht',
    'Welt seam (fold)': 'Leistennaht (Bruch)',
    'Wing edge': 'Flügelkante',
    'Wing end (Velcro)': 'Flügelende (Klettband)',
    'Wing end (into the side seam)': 'Flügelende (in die Seitennaht)',
    'Wings (outer ↔ lining)': 'Flügel (außen ↔ Futter)',
    'With the collar the zip may run up to its top: about {n} cm.':
        'Mit Kragen darf der Reißverschluss bis zu dessen Oberkante reichen: etwa {n} cm.',
    'Wrap band': 'Wickelblende',
    'Wrap band ↔ wrap edges and back neck': 'Wickelblende ↔ Wickelkanten und hinterer Halsausschnitt',
    'Wrap bodysuit': 'Wickelbody',
    'Wrap dress': 'Wickelkleid',
    'Wrap edge (band)': 'Wickelkante (Blende)',
    'Wrap top': 'Wickelshirt',
    'Wrap wing': 'Wickelflügel',
    'Yoke': 'Passe',
    'Yoke seam': 'Passennaht',
    'Yoke seam (back leg ↔ yoke)': 'Passennaht (hinteres Bein ↔ Passe)',
    'Yoke seam (back ↔ yoke)': 'Passennaht (Rückenteil ↔ Passe)',
    'Zip (centre back bodice ↔ bodice)': 'Reißverschluss (hintere Mitte Oberteil ↔ Oberteil)',
    'Zip pocket opening': 'Eingriff Reißverschlusstasche',
    'Zip: {n} cm (closed end; front neck to below the waist)':
        'Reißverschluss: {n} cm (nicht teilbar; vom vorderen Halsausschnitt bis unter die Taille)',
    'bib width at the waist': 'Latzbreite an der Taille',
    'binding ends overlap at the side seam': 'Enden der Einfassung überlappen an der Seitennaht',
    'cut on the bias ({n}°); press both long edges to the middle':
        'schräg zuschneiden ({n}°); beide Längskanten zur Mitte bügeln',
    'cut on the seam line, no allowance': 'auf der Nahtlinie zuschneiden, ohne Zugabe',
    'drawcord, with a safety pin': 'Kordel, mit einer Sicherheitsnadel',
    'ease the wider part in': 'den weiteren Teil einhalten',
    'ends at the button band: not sewn into a ring': 'endet an der Knopfleiste: nicht zum Ring genäht',
    'eyelets on the marks, cord through them': 'Ösen auf die Markierungen, Kordel hindurch',
    'fold both edges to the middle, topstitch, cut {n} loops':
        'beide Kanten zur Mitte falten, absteppen, {n} Schlaufen abschneiden',
    'fold lengthwise; Velcro on the tab and on the sleeve': 'längs falten; Klettband auf Riegel und Ärmel',
    'fold on the centre line, sew from the edge to the point':
        'an der Mittellinie falten, von der Kante zur Spitze nähen',
    'from placket centre to placket centre': 'von Leistenmitte zu Leistenmitte',
    'front + back, vertical stretch included': 'vorne + hinten, Längsdehnung eingerechnet',
    'inseam': 'innere Beinnaht',
    'interface it': 'mit Einlage bebügeln',
    'interface it completely': 'ganz mit Einlage bebügeln',
    'interface one half': 'eine Hälfte mit Einlage bebügeln',
    'interface one half; buttonholes in the right strip':
        'eine Hälfte mit Einlage bebügeln; Knopflöcher in den rechten Streifen',
    'interface the front part of one half (buttons and buttonholes)':
        'den vorderen Teil einer Hälfte mit Einlage bebügeln (Knöpfe und Knopflöcher)',
    'knit with elastane stretches to the body': 'Strickstoff mit Elasthan dehnt sich an den Körper',
    'leave {n} cm open in one sleeve seam for turning': 'in einer Ärmelnaht {n} cm Wendeöffnung lassen',
    'mid rise: between waist and hip; the waistband closes with a button':
        'mittlere Leibhöhe: zwischen Taille und Hüfte; der Bund schließt mit einem Knopf',
    'neckline + both placket edges ≥ head + {n} %': 'Halsausschnitt + beide Leistenkanten ≥ Kopf + {n} %',
    'one or two pleats at the back of the sleeve': 'eine oder zwei Falten hinten am Ärmel',
    'one strip per pocket (both lips); interface it':
        'ein Streifen je Tasche (beide Paspeln); mit Einlage bebügeln',
    'outer and inner piece; interface the outer one': 'Außen- und Innenteil; das äußere mit Einlage bebügeln',
    'outer and inner yoke, both on the fold': 'äußere und innere Passe, beide im Stoffbruch',
    'outer and lining (cotton jersey)': 'außen und Futter (Baumwolljersey)',
    'outer bib and facing': 'äußerer Latz und Beleg',
    'outseam': 'äußere Seitennaht',
    'plus the button overlap': 'plus der Knopfübertritt',
    'plus the ends of the hem band': 'plus die Enden des Saumbündchens',
    'press both long edges to the middle, then fold (binding)':
        'beide Längskanten zur Mitte bügeln, dann falten (Einfassband)',
    'press both long edges {n} mm in, then fold in half':
        'beide Längskanten {n} mm einbügeln, dann längs halbieren',
    'sewn onto both edges of the slit': 'an beide Kanten des Schlitzes genäht',
    'sleeve-cap ease': 'Mehrweite der Armkugel',
    'stand to the front edge': 'Leiste bis zur Vorderkante',
    'stretched slightly onto the leg opening': 'leicht gedehnt an den Beinausschnitt',
    'the back elastic gathers the difference': 'das Gummi im Rücken rafft den Unterschied',
    'the collar ends at centre front': 'der Kragen endet in der vorderen Mitte',
    'the collar ends where the stand runs onto the button stand':
        'der Kragen endet dort, wo der Steg auf die Knopfleiste läuft',
    'the ends are folded in at the front edges': 'die Enden werden an den Vorderkanten eingeschlagen',
    'the front includes the bust dart': 'das Vorderteil enthält den Brustabnäher',
    'the full-width front against both back halves': 'das ganze Vorderteil gegen beide Rückenhälften',
    'the jumpsuit is stepped into: the waist seam must pass the hips':
        'in den Jumpsuit steigt man hinein: die Taillennaht muss über die Hüfte gehen',
    'the legs must be able to bend up and out (M position)':
        'die Beine müssen sich nach oben und außen beugen können (M-Stellung)',
    'toe at the front leg, heel at the back leg': 'Zehen am vorderen Bein, Ferse am hinteren Bein',
    'upper and under collar; interface the upper one':
        'Ober- und Unterkragen; den Oberkragen mit Einlage bebügeln',
    'waist + the opened fly ≥ hip': 'Taille + geöffneter Schlitz ≥ Hüfte',
    'waist + {n}–{n} % ease': 'Taille + {n}–{n} % Mehrweite',
    '{n} outer + {n} lining': '{n} außen + {n} Futter',
    '{n} per pocket': '{n} je Tasche',
    '{n} per pocket (outer flap + facing); interface the outer one':
        '{n} je Tasche (äußere Patte + Beleg); die äußere mit Einlage bebügeln',
    'Armhole (elastic, turned), Leg opening (elastic, turned), Neckline (elastic, turned)':
        'Armloch (Gummi, umgeschlagen), Beinausschnitt (Gummi, umgeschlagen), Halsausschnitt (Gummi, umgeschlagen)',
    'At least one piece is wider than {n} cm: an open width ≥ {n} cm is needed, or cut the piece in two with a cross seam.':
        'Mindestens ein Teil ist breiter als {n} cm: Du brauchst eine offene Stoffbreite ≥ {n} cm, oder teile das Teil mit einer Quernaht.',
    'Belt loops: {n} thread loops or fabric loops at the side seams, on the waist seam':
        'Gürtelschlaufen: {n} Faden- oder Stoffschlaufen an den Seitennähten, auf der Taillennaht',
    'Bind the wrap edges and the back neck in one go with the band, stretching it slightly.':
        'Fasse die Wickelkanten und den hinteren Halsausschnitt in einem Zug mit der Blende ein und dehne sie dabei leicht.',
    'Buttons: {n} buttons, {n} mm; light interfacing for the placket strips':
        'Knöpfe: {n} Knöpfe, {n} mm; leichte Einlage für die Leistenstreifen',
    'Buttons: {n} buttons, {n} mm; light iron-on interfacing strip for the button band':
        'Knöpfe: {n} Knöpfe, {n} mm; leichter Bügeleinlagestreifen für die Knopfleiste',
    'Close the elastic into a ring, quarter it and the top edge, and sew it on the same way, stretching it to fit.':
        'Schließe das Gummi zum Ring, teile es und die Oberkante in Viertel und nähe es genauso an, passend gedehnt.',
    'Cross the straps and baste their open ends onto the right side of the back top edge on the markings, pointing down.':
        'Kreuze die Träger und hefte ihre offenen Enden auf den Markierungen an die rechte Seite der hinteren Oberkante, nach unten zeigend.',
    'Crotch gusset: cotton jersey, stitched over the crotch seam on the inside':
        'Schrittzwickel: Baumwolljersey, innen über die Schrittnaht gesteppt',
    'Cut along the middle between the two lines, through the garment only, and into the corners in a Y, up to the last stitch.':
        'Schneide in der Mitte zwischen den beiden Linien nur durch das Kleidungsstück und an den Enden Y-förmig in die Ecken, bis zum letzten Stich.',
    'Cut the front on the placket marking: down the middle and diagonally into the lower corners. Sew one strip right sides together onto each long edge of the opening with {n} mm seam allowance, up to the corner.':
        'Schneide das Vorderteil auf der Leistenmarkierung ein: in der Mitte nach unten und schräg in die unteren Ecken. Nähe je einen Streifen rechts auf rechts mit {n} mm Nahtzugabe an jede Längskante der Öffnung, bis zur Ecke.',
    'Cut the slit on the marking. Spread it open into a straight line and sew the binding strip right sides together onto it with {n} mm allowance; fold the binding over the allowance, press, topstitch. Fold the front half of the binding inside.':
        'Schneide den Schlitz auf der Markierung ein. Ziehe ihn zu einer geraden Linie auseinander und nähe den Einfassstreifen rechts auf rechts mit {n} mm Zugabe an; schlage die Einfassung über die Zugabe, bügle und steppe ab. Schlage die vordere Hälfte der Einfassung nach innen.',
    'Divide the leg opening and the elastic into quarters. Sew the elastic onto the wrong side with a zigzag, stretching it evenly (a little more at the back), turn it in and topstitch with a zigzag or twin needle.':
        'Teile Beinausschnitt und Gummi in Viertel. Nähe das Gummi mit Zickzack auf die linke Seite und dehne es dabei gleichmäßig (hinten etwas mehr), schlage es ein und steppe mit Zickzack oder Zwillingsnadel ab.',
    'Drawcord: {n} cm for the hem and {n} cm for the hood, {n}–{n} cord stoppers, {n} small eyelets':
        'Kordel: {n} cm für den Saum und {n} cm für die Kapuze, {n}–{n} Kordelstopper, {n} kleine Ösen',
    'Elastic for the back waist: {n} mm wide, {n} cm (side seam to side seam)':
        'Gummi für die hintere Taille: {n} mm breit, {n} cm (Seitennaht bis Seitennaht)',
    'Elastic: waist {n} cm ({n}–{n} mm plush or waistband elastic), legs {n} × {n} cm ({n}–{n} mm, picot or lingerie elastic)':
        'Gummi: Taille {n} cm ({n}–{n} mm Plüsch- oder Bundgummi), Beine {n} × {n} cm ({n}–{n} mm, Picot- oder Wäschegummi)',
    'Finish the fly extensions. Sew the {n} cm zip onto the right fly extension, with the folded fly shield underneath. Sew the front crotch seam from the inseam up to the notch. Lay the left front over the zip, centre fronts matching, and sew the zip onto the left extension from the inside; topstitch the J line from the right side and bar-tack its lower end.':
        'Versäubere die Schlitzübertritte. Nähe den {n}-cm-Reißverschluss auf den rechten Übertritt, den gefalteten Untertritt darunter. Nähe die vordere Schrittnaht von der inneren Beinnaht bis zum Knipps. Lege das linke Vorderteil über den Reißverschluss, die vorderen Mitten aufeinander, und nähe den Reißverschluss von innen an den linken Übertritt; steppe die J-Linie von rechts ab und riegle ihr unteres Ende.',
    'Fold both long edges of the lip strip to the middle and press. Lay it centred on the marked line, right side down. Lay a pocket bag piece on top, right sides together, and sew two parallel lines {n} mm above and below the marked line, exactly as long as the opening.':
        'Bügle beide Längskanten des Paspelstreifens zur Mitte. Lege ihn mittig auf die markierte Linie, rechte Seite nach unten. Lege ein Taschenbeutelteil rechts auf rechts darauf und nähe zwei parallele Linien {n} mm über und unter der markierten Linie, genau so lang wie der Eingriff.',
    'Fold both long edges of the strip to the middle, fold again and topstitch both edges. Cut {n} loops.':
        'Bügle beide Längskanten des Streifens zur Mitte, falte ihn noch einmal und steppe beide Kanten ab. Schneide {n} Schlaufen ab.',
    'Fold each cuff lengthwise wrong sides together and sew it flat onto the leg end, stretching it slightly; its ends stop at the inner leg edges.':
        'Falte jedes Bündchen längs links auf links und nähe es flach an das Beinende, leicht gedehnt; seine Enden hören an den inneren Beinkanten auf.',
    'Fold each cuff right sides together on the fold line and sew both ends with {n} mm seam allowance. Trim, turn and press.':
        'Falte jede Manschette rechts auf rechts an der Umbruchlinie und nähe beide Enden mit {n} mm Nahtzugabe. Zurückschneiden, wenden und bügeln.',
    'Fold each dart right sides together on its middle, the dart lines on top of each other. Sew from the wide end to the point and run off the fold. Press bust darts down and waist darts towards the centre.':
        'Falte jeden Abnäher in seiner Mitte rechts auf rechts, die Abnäherlinien aufeinander. Nähe vom breiten Ende zur Spitze und laufe am Bruch aus. Bügle Brustabnäher nach unten und Taillenabnäher zur Mitte.',
    'Fold each front edge twice to the wrong side on the fold line, press and stitch it down.':
        'Schlage jede Vorderkante an der Umbruchlinie doppelt nach links ein, bügle sie und steppe sie fest.',
    'Fold each front edge {n} cm to the wrong side and then again {n} cm (on the fold line), press and stitch close to the inner fold.':
        'Schlage jede Vorderkante {n} cm nach links und dann noch einmal {n} cm (an der Umbruchlinie) ein, bügle sie und steppe knapp an der inneren Bruchkante.',
    'Fold each front right sides together on the middle of the dart, the dart lines on top of each other. Sew from the side edge to the point and run off the fold. Press the dart down.':
        'Falte jedes Vorderteil in der Mitte des Abnähers rechts auf rechts, die Abnäherlinien aufeinander. Nähe von der Seitenkante zur Spitze und laufe am Bruch aus. Bügle den Abnäher nach unten.',
    'Fold each strap lengthwise right sides together and sew the long edge and the buttonhole end with {n} mm seam allowance. Turn, press and topstitch.':
        'Falte jeden Träger längs rechts auf rechts und nähe die Längskante und das Knopflochende mit {n} mm Nahtzugabe. Wenden, bügeln und absteppen.',
    'Fold each strip in half over its allowance and press. Lay the right strip over the left one, push the lower ends and the little triangle to the inside and sew across them. Topstitch the edges of the placket.':
        'Falte jeden Streifen über seiner Zugabe zur Hälfte und bügle ihn. Lege den rechten Streifen über den linken, schiebe die unteren Enden und das kleine Dreieck nach innen und nähe quer darüber. Steppe die Kanten der Leiste ab.',
    'Fold each tab lengthwise right sides together, sew the long edge and one end, turn and topstitch. Sew the soft Velcro onto the tab.':
        'Falte jeden Riegel längs rechts auf rechts, nähe die Längskante und ein Ende, wende ihn und steppe ab. Nähe das weiche Klettband auf den Riegel.',
    'Fold each tie lengthwise right sides together and sew the long edge and one end with {n} mm seam allowance. Turn with a safety pin and press.':
        'Falte jedes Bindeband längs rechts auf rechts und nähe die Längskante und ein Ende mit {n} mm Nahtzugabe. Wende es mit einer Sicherheitsnadel und bügle es.',
    'Fold the band crosswise right sides together and sew the short edges with {n} mm seam allowance.':
        'Falte die Blende quer rechts auf rechts und nähe die kurzen Kanten mit {n} mm Nahtzugabe.',
    'Fold the band lengthwise wrong sides together, raw edges level, and press.':
        'Falte die Blende längs links auf links, die offenen Kanten bündig, und bügle sie.',
    'Fold the band lengthwise, pin it at the quarters and sew it on, stretching the band.':
        'Falte die Blende längs, stecke sie an den Vierteln fest und nähe sie an, die Blende dabei dehnen.',
    'Fold the bias strip lengthwise wrong sides together and press; shape it into a curve with the iron.':
        'Falte den Schrägstreifen längs links auf links und bügle ihn; forme ihn mit dem Bügeleisen zur Rundung.',
    'Fold the collar lengthwise right sides together and sew both ends; turn and press, raw edges level.':
        'Falte den Kragen längs rechts auf rechts und nähe beide Enden; wende und bügle ihn, die offenen Kanten bündig.',
    'Fold the crotch edges of front and back to the inside and stitch them down; interface them with a strip of interfacing first.':
        'Schlage die Schrittkanten von Vorder- und Rückenteil nach innen und steppe sie fest; bügle vorher einen Streifen Einlage darauf.',
    'Fold the ends in, turn the binding to the inside and stitch it down close to the fold.':
        'Schlage die Enden ein, wende die Einfassung nach innen und steppe sie knapp an der Bruchkante fest.',
    'Fold the garment right sides together at the shoulders, the sleeves folded in half lengthwise. Pin side and sleeve seam so that the armhole seams meet exactly at the underarm. Sew in one go with {n} mm seam allowance, from the hem over the underarm to the sleeve hem. Press the allowances towards the back. Catch one tie in the left side seam at the waist marking, pointing inwards; leave a {n} cm slot open in the right side seam at the marking.':
        'Lege das Kleidungsstück an den Schultern rechts auf rechts, die Ärmel längs zur Hälfte gefaltet. Stecke Seiten- und Ärmelnaht so, dass sich die Armlochnähte unter dem Arm genau treffen. Nähe in einem Zug mit {n} mm Nahtzugabe vom Saum über die Achsel bis zum Ärmelsaum. Bügle die Zugaben nach hinten. Fasse an der Taillenmarkierung ein Bindeband in die linke Seitennaht, nach innen zeigend; lasse in der rechten Seitennaht an der Markierung einen {n} cm langen Schlitz offen.',
    'Fold the hems of body and sleeves up and press. Sew the lining hems right sides together onto the hem allowances (the lining forms a small fold over the hem: it needs that room).':
        'Schlage die Säume von Körper und Ärmeln hoch und bügle sie. Nähe die Futtersäume rechts auf rechts an die Saumzugaben (das Futter bildet über dem Saum eine kleine Falte: diesen Platz braucht es).',
    'Fold the straight front edge below the wrap {n} cm to the wrong side and stitch it down.':
        'Schlage die gerade Vorderkante unterhalb der Wickelung {n} cm nach links ein und steppe sie fest.',
    'Fold the top edge {n} cm and then {n} cm to the wrong side and stitch it down.':
        'Schlage die Oberkante {n} cm und dann {n} cm nach links ein und steppe sie fest.',
    'Fold the welt lengthwise, wrong sides together, and lay it below the marked line, raw edges on the line, the fold pointing down. Lay a pocket bag piece on top, right sides together, and sew two parallel lines {n} mm above and below the marked line, exactly as long as the opening.':
        'Falte die Leiste längs links auf links und lege sie unter die markierte Linie, die offenen Kanten auf der Linie, der Bruch zeigt nach unten. Lege ein Taschenbeutelteil rechts auf rechts darauf und nähe zwei parallele Linien {n} mm über und unter der markierten Linie, genau so lang wie der Eingriff.',
    'Interface the eyelet spots on the waistband (outer half, either side of centre front) and set two eyelets {n} mm, or sew two vertical buttonholes.':
        'Bügle Einlage auf die Ösenstellen am Bund (äußere Hälfte, beidseits der vorderen Mitte) und schlage zwei Ösen {n} mm ein, oder nähe zwei senkrechte Knopflöcher.',
    'Interfacing: a strip of light iron-on interfacing in the snap facings':
        'Einlage: ein Streifen leichte Bügeleinlage in den Druckknopfbelegen',
    'Interfacing: light iron-on for the button stand (strip {n} × the stand width)':
        'Einlage: leichte Bügeleinlage für die Knopfleiste (Streifen {n} × Leistenbreite)',
    'Interfacing: light iron-on for the collar, the stand, the button stand (strip {n} × the stand width)':
        'Einlage: leichte Bügeleinlage für Kragen, Steg und Knopfleiste (Streifen {n} × Leistenbreite)',
    'Interfacing: light iron-on for the collar, the stand, the cuffs, the button stand (strip {n} × the stand width)':
        'Einlage: leichte Bügeleinlage für Kragen, Steg, Manschetten und Knopfleiste (Streifen {n} × Leistenbreite)',
    'Interfacing: light iron-on for the cuffs, the button stand (strip {n} × the stand width)':
        'Einlage: leichte Bügeleinlage für Manschetten und Knopfleiste (Streifen {n} × Leistenbreite)',
    'Interfacing: medium iron-on for the facings, the collar, the hems (strip {n} cm) and the pocket openings':
        'Einlage: mittlere Bügeleinlage für Belege, Kragen, Säume (Streifen {n} cm) und Tascheneingriffe',
    'Iron a strip of interfacing ({n} cm wide) onto the wrong side of the front behind the marked opening.':
        'Bügle einen Streifen Einlage ({n} cm breit) hinter dem markierten Eingriff auf die linke Seite des Vorderteils.',
    'Iron a strip of interfacing onto the front parts of one half of the band.':
        'Bügle einen Streifen Einlage auf die vorderen Teile einer Hälfte der Leiste.',
    'Iron a strip of interfacing onto the inner leg edges, fold them {n} cm to the wrong side and stitch them down; fold the cuff ends in with them.':
        'Bügle einen Streifen Einlage auf die inneren Beinkanten, schlage sie {n} cm nach links ein und steppe sie fest; schlage die Bündchenenden mit ein.',
    'Iron a {n} cm strip of light interfacing along the centre front edges of the bodice and the top of the front crotch seam.':
        'Bügle einen {n} cm breiten Streifen leichte Einlage an die Kanten der vorderen Mitte des Oberteils und oben an die vordere Schrittnaht.',
    'Iron interfacing onto the facings, the outer collar, a {n} cm strip along the hems of body and sleeves and behind the pocket openings.':
        'Bügle Einlage auf die Belege, den Oberkragen, einen {n} cm breiten Streifen an den Säumen von Körper und Ärmeln und hinter die Tascheneingriffe.',
    'Iron light interfacing onto the wrong side of the outer collar pieces, one half of each cuff and a strip along the front edges (button stand).':
        'Bügle leichte Einlage auf die linke Seite der äußeren Kragenteile, auf eine Hälfte jeder Manschette und als Streifen an die Vorderkanten (Knopfleiste).',
    'Iron light interfacing onto one half of each cuff and a strip along the front edges (button stand).':
        'Bügle leichte Einlage auf eine Hälfte jeder Manschette und als Streifen an die Vorderkanten (Knopfleiste).',
    'Iron light interfacing onto a strip along the front edges (button stand).':
        'Bügle leichte Einlage als Streifen an die Vorderkanten (Knopfleiste).',
    'Iron light interfacing onto the wrong side of the outer collar pieces and a strip along the front edges (button stand).':
        'Bügle leichte Einlage auf die linke Seite der äußeren Kragenteile und als Streifen an die Vorderkanten (Knopfleiste).',
    'Iron light interfacing onto a strip along the front edges (button stand) and onto the outer collar pieces.':
        'Bügle leichte Einlage als Streifen an die Vorderkanten (Knopfleiste) und auf die äußeren Kragenteile.',
    'Jeans zip {n} cm, {n} jeans button {n} mm, {n} rivets (optional); interfacing for the waistband; topstitching thread':
        'Jeansreißverschluss {n} cm, {n} Jeansknopf {n} mm, {n} Nieten (optional); Einlage für den Bund; Steppgarn',
    'Join the two belt halves at the short ends (centre back). Fold the belt lengthwise right sides together and sew the long edge and the ends with {n} mm seam allowance, leaving a gap; turn, press and close the gap.':
        'Nähe die beiden Gürtelhälften an den kurzen Enden zusammen (hintere Mitte). Falte den Gürtel längs rechts auf rechts und nähe Längskante und Enden mit {n} mm Nahtzugabe, lasse eine Wendeöffnung; wende, bügle und schließe die Öffnung.',
    'Lay both stand pieces right sides together and sew the top edge and the ends. Trim, turn and press.':
        'Lege beide Stegteile rechts auf rechts und nähe die Oberkante und die Enden. Zurückschneiden, wenden und bügeln.',
    'Lay each flap right sides together onto its facing and sew round the outline; the top stays open. Trim, turn and press; topstitch {n} mm from the edge if you like.':
        'Lege jede Patte rechts auf rechts auf ihren Beleg und nähe rundum; oben bleibt offen. Zurückschneiden, wenden und bügeln; nach Wunsch {n} mm von der Kante absteppen.',
    'Lay each outer and lining wing right sides together and sew round with {n} mm seam allowance, leaving the end for the side seam open. Turn, press and sew the Velcro on: hook side on the outer of the left wing, soft side on the lining of the right wing.':
        'Lege je einen Außen- und Futterflügel rechts auf rechts und nähe rundum mit {n} mm Nahtzugabe, das Ende für die Seitennaht bleibt offen. Wenden, bügeln und das Klettband aufnähen: Hakenseite außen auf den linken Flügel, weiche Seite auf das Futter des rechten Flügels.',
    'Lay each side panel right sides together onto the centre panel, the notches matching, and sew the princess seam with {n} mm seam allowance; ease the curve in, do not stretch it. Press the allowances towards the side.':
        'Lege jedes Seitenteil rechts auf rechts auf das Mittelteil, die Knipse aufeinander, und nähe die Prinzessnaht mit {n} mm Nahtzugabe; halte die Rundung ein, dehne sie nicht. Bügle die Zugaben zur Seite.',
    'Lay each wadding piece onto the wrong side of its outer piece and baste or quilt them together within the seam allowance: from now on they are one layer.':
        'Lege jedes Vliesteil auf die linke Seite seines Außenteils und hefte oder steppe sie innerhalb der Nahtzugabe zusammen: ab jetzt sind sie eine Lage.',
    'Lay front and back legs right sides together and sew the outer leg seams with {n} mm seam allowance. The inner legs stay open.':
        'Lege vordere und hintere Beine rechts auf rechts und nähe die äußeren Beinnähte mit {n} mm Nahtzugabe. Die inneren Beinkanten bleiben offen.',
    'Lay front and back right sides together and sew the shoulders with {n} mm seam allowance.':
        'Lege Vorder- und Rückenteil rechts auf rechts und nähe die Schultern mit {n} mm Nahtzugabe.',
    'Lay front and back right sides together and sew the side seams from the hem to the armhole. Press the allowances open.':
        'Lege Vorder- und Rückenteil rechts auf rechts und nähe die Seitennähte vom Saum bis zum Armloch. Bügle die Zugaben auseinander.',
    'Lay front and back right sides together and sew the side seams with {n} mm seam allowance, across the binding ends.':
        'Lege Vorder- und Rückenteil rechts auf rechts und nähe die Seitennähte mit {n} mm Nahtzugabe, über die Enden der Einfassung.',
    'Lay front and back right sides together and sew the side seams with {n} mm seam allowance.':
        'Lege Vorder- und Rückenteil rechts auf rechts und nähe die Seitennähte mit {n} mm Nahtzugabe.',
    'Lay one or two pleats at the back of the sleeve hem (pointing to the placket) until it fits the cuff. Sew the outer cuff right sides together onto it with {n} mm seam allowance, fold the inner edge under over the allowance and topstitch all round the cuff.':
        'Lege hinten am Ärmelsaum eine oder zwei Falten (zum Schlitz zeigend), bis er zur Manschette passt. Nähe die äußere Manschette rechts auf rechts mit {n} mm Nahtzugabe an, schlage die innere Kante über die Zugabe ein und steppe die Manschette rundum ab.',
    'Lay outer bib and facing right sides together and sew the sides and the top with {n} mm seam allowance. Clip the corners, turn, press and topstitch.':
        'Lege äußeren Latz und Beleg rechts auf rechts und nähe die Seiten und die Oberkante mit {n} mm Nahtzugabe. Ecken abschrägen, wenden, bügeln und absteppen.',
    'Lay the back between the outer yoke (right sides together) and the inner yoke (right side on the wrong side of the back). Sew through all three layers and fold both yokes up. Topstitch {n} mm above the seam.':
        'Lege das Rückenteil zwischen die äußere Passe (rechts auf rechts) und die innere Passe (rechte Seite auf die linke Seite des Rückenteils). Nähe durch alle drei Lagen und klappe beide Passen hoch. Steppe {n} mm über der Naht ab.',
    'Lay the bib onto the outside of the front waistband, centre on centre front, its lower edge {n} cm over the band seam, and topstitch it on through all layers. Cross the straps at the back and sew their ends onto the inside of the back waistband, {n} cm from centre back each.':
        'Lege den Latz außen auf den vorderen Bund, Mitte auf vordere Mitte, seine Unterkante {n} cm über der Bundnaht, und steppe ihn durch alle Lagen fest. Kreuze die Träger hinten und nähe ihre Enden innen an den hinteren Bund, je {n} cm von der hinteren Mitte.',
    'Lay the binding on the right side of the neckline, raw edges level, from one front edge to the other; let the ends stick out {n} cm. Sew with {n} mm seam allowance, trim and clip the allowance.':
        'Lege die Einfassung auf die rechte Seite des Halsausschnitts, die offenen Kanten bündig, von einer Vorderkante zur anderen; lasse die Enden {n} cm überstehen. Nähe mit {n} mm Nahtzugabe, schneide die Zugabe zurück und ein.',
    'Lay the bodice and the legs right sides together at the waist, side seams and centres matching, and sew with {n} mm seam allowance. Press the allowance towards the bodice.':
        'Lege Oberteil und Beine an der Taille rechts auf rechts, Seitennähte und Mitten aufeinander, und nähe mit {n} mm Nahtzugabe. Bügle die Zugabe zum Oberteil.',
    'Lay the collar between the two stand pieces (right sides of the stands facing the collar), centres matching, and sew along the top edge round the stand ends. Turn.':
        'Lege den Kragen zwischen die beiden Stegteile (rechte Seiten der Stege zum Kragen), Mitten aufeinander, und nähe entlang der Oberkante um die Stegenden. Wenden.',
    'Lay the collar onto the right side of the neckline, its ends at the middle of the placket strips. Fold the placket strips back over it (right sides together) and sew with {n} mm seam allowance, stretching the collar slightly. Turn the placket ends and cover the allowance at the back with a strip of tape.':
        'Lege den Kragen auf die rechte Seite des Halsausschnitts, seine Enden in der Mitte der Leistenstreifen. Schlage die Leistenstreifen darüber zurück (rechts auf rechts) und nähe mit {n} mm Nahtzugabe, den Kragen leicht gedehnt. Wende die Leistenenden und decke die Zugabe hinten mit einem Nahtband ab.',
    'Lay the contrast upper part right sides together onto the lower part and sew with {n} mm seam allowance. Press the allowances down.':
        'Lege das obere Teil aus Kontraststoff rechts auf rechts auf das untere Teil und nähe mit {n} mm Nahtzugabe. Bügle die Zugaben nach unten.',
    'Lay the facing right sides together over the marking and sew a narrow rectangle round the opening line. Cut in the middle and into the corners, turn the facing through and press. Lay the zip behind the opening and topstitch round it close to the edge.':
        'Lege den Beleg rechts auf rechts über die Markierung und nähe ein schmales Rechteck um die Eingriffslinie. Schneide in der Mitte und in die Ecken ein, wende den Beleg durch und bügle. Lege den Reißverschluss hinter die Öffnung und steppe knappkantig rundum ab.',
    'Lay the flap above the marked line, raw edges on the line, pointing up, and the lip strip below it. Lay a pocket bag piece on top, right sides together, and sew two parallel lines {n} mm above and below the marked line, exactly as long as the opening.':
        'Lege die Patte über die markierte Linie, offene Kanten auf der Linie, nach oben zeigend, und den Paspelstreifen darunter. Lege ein Taschenbeutelteil rechts auf rechts darauf und nähe zwei parallele Linien {n} mm über und unter der markierten Linie, genau so lang wie der Eingriff.',
    'Lay the front lining wrong side onto the wrong side of the front and baste them together within the allowances: from now on they are one layer.':
        'Lege das vordere Futter links auf links auf das Vorderteil und hefte beide innerhalb der Zugaben zusammen: ab jetzt sind sie eine Lage.',
    'Lay the lining into the bodice right sides together, the straps between them, and sew round the top edge with {n} mm seam allowance. Clip the curves, turn and press; topstitch the top edge.':
        'Lege das Futter rechts auf rechts in das Oberteil, die Träger dazwischen, und nähe die Oberkante rundum mit {n} mm Nahtzugabe. Rundungen einschneiden, wenden und bügeln; die Oberkante absteppen.',
    'Lay the lining into the jacket right sides together. Sew from the hem up the front edge, round the collar (or along the neckline) and down the other front edge. Trim the corners, turn the facings and press.':
        'Lege das Futter rechts auf rechts in die Jacke. Nähe vom Saum die Vorderkante hoch, um den Kragen (oder am Halsausschnitt entlang) und die andere Vorderkante hinunter. Ecken zurückschneiden, Belege wenden und bügeln.',
    'Lay the outer gusset on the front right sides together and the gusset lining right side onto the wrong side of the front (front between them). Sew through all three layers with {n} mm seam allowance.':
        'Lege den äußeren Zwickel rechts auf rechts auf das Vorderteil und das Zwickelfutter mit der rechten Seite auf die linke Seite des Vorderteils (das Vorderteil dazwischen). Nähe durch alle drei Lagen mit {n} mm Nahtzugabe.',
    'Lay the skirt back pieces right sides together and sew the centre back seam from the hem up to the notch; above the notch the zip goes in.':
        'Lege die hinteren Rockteile rechts auf rechts und nähe die hintere Mittelnaht vom Saum bis zum Knipps; oberhalb des Knippses kommt der Reißverschluss hinein.',
    'Lay the two front legs right sides together and sew the centre front seam with {n} mm seam allowance, from the top edge down to the crotch point.':
        'Lege die beiden vorderen Beine rechts auf rechts und nähe die vordere Mittelnaht mit {n} mm Nahtzugabe von der Oberkante bis zum Schrittpunkt.',
    'Lay the yoke right sides together onto the lower part and sew with {n} mm seam allowance. Press the allowances up towards the yoke and topstitch them if you like.':
        'Lege die Passe rechts auf rechts auf das untere Teil und nähe mit {n} mm Nahtzugabe. Bügle die Zugaben nach oben zur Passe und steppe sie nach Wunsch ab.',
    'Lay upper and under collar right sides together and sew round the outer edge. Trim, clip the curve, turn and press.':
        'Lege Ober- und Unterkragen rechts auf rechts und nähe die Außenkante rundum. Zurückschneiden, die Rundung einschneiden, wenden und bügeln.',
    'Lay upper and under collar right sides together and sew the points and the outer edge. Trim the points, turn, press and topstitch {n} mm from the edge.':
        'Lege Ober- und Unterkragen rechts auf rechts und nähe die Spitzen und die Außenkante. Spitzen zurückschneiden, wenden, bügeln und {n} mm von der Kante absteppen.',
    'Open the {n} cm zip and press its coils flat. Pin each half right sides together onto a centre back edge, the coil on the seam line, the top stop just below the binding. Sew with the invisible-zip foot as close to the coil as possible, down to the notch. Close the seam below it.':
        'Öffne den {n}-cm-Reißverschluss und bügle die Spiralen flach. Stecke jede Hälfte rechts auf rechts an eine Kante der hinteren Mitte, die Spirale auf der Nahtlinie, den oberen Endstopp knapp unter der Einfassung. Nähe mit dem Fuß für nahtverdeckte Reißverschlüsse so nah wie möglich an der Spirale bis zum Knipps. Schließe die Naht darunter.',
    'Pin each half of the separating zip right sides together onto a front edge, the teeth towards the middle, up to the top of the collar. Sew with a zipper foot, {n} mm from the edge, fold the allowance inside and topstitch {n} mm from the teeth.':
        'Stecke jede Hälfte des teilbaren Reißverschlusses rechts auf rechts an eine Vorderkante, die Zähnchen zur Mitte, bis oben an den Kragen. Nähe mit dem Reißverschlussfuß {n} mm von der Kante, schlage die Zugabe nach innen und steppe {n} mm neben den Zähnchen ab.',
    'Pin one long edge of the collar right sides together onto the neckline, centre back on centre back, and sew with {n} mm seam allowance. Fold the collar on the fold line, turn the inner edge under and topstitch it down.':
        'Stecke eine Längskante des Kragens rechts auf rechts an den Halsausschnitt, hintere Mitte auf hintere Mitte, und nähe mit {n} mm Nahtzugabe. Falte den Kragen an der Umbruchlinie, schlage die innere Kante ein und steppe sie fest.',
    'Pin the band onto the right side of the front edges and the neckline, centre back on the back neck, the ends level with the hem. Sew from hem to hem with {n} mm seam allowance, stretching the band slightly round the neck. Press the allowance towards the body and topstitch it down.':
        'Stecke die Blende auf die rechte Seite der Vorderkanten und des Halsausschnitts, Mitte auf den hinteren Halsausschnitt, die Enden bündig mit dem Saum. Nähe von Saum zu Saum mit {n} mm Nahtzugabe und dehne die Blende um den Hals leicht. Bügle die Zugabe zum Körper und steppe sie fest.',
    'Pin the band onto the right side of the wrap edges and the back neck, from one waist point to the other, centre back on the back neck. Sew with {n} mm seam allowance, stretching the band slightly over the bust. Press the allowance towards the body and topstitch it.':
        'Stecke die Blende auf die rechte Seite der Wickelkanten und des hinteren Halsausschnitts, von einem Taillenpunkt zum anderen, Mitte auf den hinteren Halsausschnitt. Nähe mit {n} mm Nahtzugabe und dehne die Blende über der Brust leicht. Bügle die Zugabe zum Körper und steppe sie ab.',
    'Pin the crotch curves together, starting at the inseams: they lie exactly on top of each other. Sew with {n} mm seam allowance in one go from the zip notch on the front to the back top edge.':
        'Stecke die Schrittrundungen zusammen, angefangen an den inneren Beinnähten: Sie liegen genau aufeinander. Nähe mit {n} mm Nahtzugabe in einem Zug vom Reißverschluss-Knipps vorne bis zur hinteren Oberkante.',
    'Pin the elastic ({n} cm) onto the waist seam allowance from side seam to side seam and sew it on with a zigzag, stretching it. Stitch the ends down firmly at the side seams.':
        'Stecke das Gummi ({n} cm) von Seitennaht zu Seitennaht auf die Zugabe der Taillennaht und nähe es gedehnt mit Zickzack an. Nähe die Enden an den Seitennähten gut fest.',
    'Pin the outer collar right sides together onto the neckline of the jacket, from front edge to front edge, and sew with {n} mm seam allowance. Clip the neckline allowance.':
        'Stecke den Oberkragen rechts auf rechts an den Halsausschnitt der Jacke, von Vorderkante zu Vorderkante, und nähe mit {n} mm Nahtzugabe. Schneide die Zugabe am Halsausschnitt ein.',
    'Pin the outer gusset to the back right sides together. Roll front and back up, wrap the lining around them and pin it to the back too. Sew through all layers, then pull everything out through the opening: no seam shows on the inside.':
        'Stecke den äußeren Zwickel rechts auf rechts an das Rückenteil. Rolle Vorder- und Rückenteil auf, lege das Futter um sie herum und stecke es ebenfalls an das Rückenteil. Nähe durch alle Lagen und ziehe dann alles durch die Öffnung heraus: innen ist keine Naht zu sehen.',
    'Pin the outer layer of the collar right sides together onto the neckline, centre back and the ends matching, and sew with {n} mm seam allowance. Clip the neckline allowance, fold the inner layer over it, turn its edge under and topstitch close to the edge.':
        'Stecke die äußere Lage des Kragens rechts auf rechts an den Halsausschnitt, hintere Mitte und Enden aufeinander, und nähe mit {n} mm Nahtzugabe. Schneide die Zugabe am Halsausschnitt ein, lege die innere Lage darüber, schlage ihre Kante ein und steppe knappkantig ab.',
    'Press lightly (not on the wadding). Check that no thread ends or loose parts are left inside.':
        'Bügle leicht (nicht auf dem Vlies). Prüfe, dass innen keine Fadenenden oder losen Teile übrig sind.',
    'Press the band and the hems. Wrap the inner front, pull its tie through the slot, wrap the outer front over it and tie both at the side.':
        'Bügle die Blende und die Säume. Wickle das innere Vorderteil, ziehe sein Bindeband durch den Schlitz, wickle das äußere Vorderteil darüber und binde beide an der Seite.',
    'Press the centre front allowances under. Pin the zip under the edges from the neckline down to the end of the crotch seam opening, teeth centred, and topstitch it on with the zipper foot; fold the top tape ends in under the neck finish.':
        'Bügle die Zugaben der vorderen Mitte nach innen. Stecke den Reißverschluss vom Halsausschnitt bis zum Ende der Öffnung in der Schrittnaht unter die Kanten, Zähnchen mittig, und steppe ihn mit dem Reißverschlussfuß fest; schlage die oberen Bandenden unter der Halsverarbeitung ein.',
    'Press the gusset edges under, lay it on the inside over the crotch seam, centred, and stitch it on all round with a narrow zigzag.':
        'Bügle die Zwickelkanten ein, lege den Zwickel innen mittig über die Schrittnaht und steppe ihn rundum mit schmalem Zickzack fest.',
    'Press the other edges under and topstitch the pocket onto the outer bib.':
        'Bügle die übrigen Kanten ein und steppe die Tasche auf den äußeren Latz.',
    'Press the other edges under and topstitch the pocket onto the right side panel.':
        'Bügle die übrigen Kanten ein und steppe die Tasche auf das rechte Seitenteil.',
    'Press the other edges {n} cm under, pin each pocket on its marking and topstitch it close to the edge.':
        'Bügle die übrigen Kanten {n} cm ein, stecke jede Tasche auf ihre Markierung und steppe sie knappkantig fest.',
    'Press the other edges {n} cm under. Pin the pocket onto the left front on the marking and topstitch it close to the edge, reinforcing the top corners with a small triangle.':
        'Bügle die übrigen Kanten {n} cm ein. Stecke die Tasche auf die Markierung am linken Vorderteil und steppe sie knappkantig fest; verstärke die oberen Ecken mit einem kleinen Dreieck.',
    'Push the bag and the allowances through the opening to the inside. Press the welt (lips) into place and secure the little triangles at the ends with a few stitches across.':
        'Schiebe Beutel und Zugaben durch die Öffnung nach innen. Bügle die Leiste (Paspeln) in Form und sichere die kleinen Dreiecke an den Enden mit ein paar Querstichen.',
    'Put the liner into the trunks, wrong side of the liner to wrong side of the trunks, side seams and centres matching, and baste the top edges together; ease the trunks onto the liner.':
        'Stecke den Innenslip in die Shorts, linke Seite des Slips auf die linke Seite der Shorts, Seitennähte und Mitten aufeinander, und hefte die Oberkanten zusammen; halte die Shorts auf den Slip ein.',
    'Safe sleep: no hood, no loose ties; the baby sleeps on the back; dress lightly underneath':
        'Sicherer Schlaf: keine Kapuze, keine losen Bänder; das Baby schläft auf dem Rücken; darunter leicht anziehen',
    'Set the sleeve linings into the armholes of the lining like the sleeves.':
        'Setze die Ärmelfutter wie die Ärmel in die Armlöcher des Futters ein.',
    'Set the snaps on the marks, caps on the right front, sockets on the left one.':
        'Bringe die Druckknöpfe auf den Markierungen an, Oberteile auf dem rechten Vorderteil, Unterteile auf dem linken.',
    'Set two small eyelets (or sew buttonholes) on the inside of the hem casing near the zip and near the hood edge ends.':
        'Schlage zwei kleine Ösen ein (oder nähe Knopflöcher), innen am Saumtunnel nahe dem Reißverschluss und nahe den Enden der Kapuzenkante.',
    'Set {n} snaps on the marks: sockets on the back crotch (it overlaps), caps on the front.':
        'Bringe {n} Druckknöpfe auf den Markierungen an: Unterteile am hinteren Schritt (er liegt oben), Oberteile vorne.',
    'Set {n} snaps on the marks: the sockets on the back legs, the caps on the front legs (the back overlaps the front).':
        'Bringe {n} Druckknöpfe auf den Markierungen an: Unterteile an den hinteren Beinen, Oberteile an den vorderen (hinten liegt über vorne).',
    'Sew each yoke onto its back leg with {n} mm seam allowance. Finish, press up and topstitch twice.':
        'Nähe jede Passe mit {n} mm Nahtzugabe an ihr hinteres Bein. Versäubern, nach oben bügeln und doppelt absteppen.',
    'Sew front and back together at the crotch with {n} mm seam allowance.':
        'Nähe Vorder- und Rückenteil im Schritt mit {n} mm Nahtzugabe zusammen.',
    'Sew front and back together at the sides with {n} mm seam allowance, catching a wing in each side seam at the top (pointing inwards).':
        'Nähe Vorder- und Rückenteil an den Seiten mit {n} mm Nahtzugabe zusammen und fasse oben in jede Seitennaht einen Flügel mit ein (nach innen zeigend).',
    'Sew outer and lining together along the top edge, right sides together, folding the zip tape ends in (zip garage). Turn the bag right side out through the zip and press.':
        'Nähe Außenstoff und Futter rechts auf rechts an der Oberkante zusammen und schlage dabei die Enden des Reißverschlussbands ein (Reißverschlussgarage). Wende den Schlafsack durch den Reißverschluss und bügle ihn.',
    'Sew side and sleeve seams of the lining in one go; leave {n} cm open in one sleeve seam.':
        'Nähe Seiten- und Ärmelnähte des Futters in einem Zug; lasse in einer Ärmelnaht {n} cm offen.',
    'Sew the band onto each leg opening from the front crotch to the back crotch, stretching it. Fold it over the allowance and stitch it down.':
        'Nähe die Blende gedehnt an jeden Beinausschnitt, vom vorderen bis zum hinteren Schritt. Schlage sie über die Zugabe und steppe sie fest.',
    'Sew the buttonhole in the left end of the waistband and set the jeans button on the right end.':
        'Nähe das Knopfloch in das linke Bundende und schlage den Jeansknopf am rechten Ende ein.',
    'Sew the buttonholes in the straps and the buttons at the top corners of the bib.':
        'Nähe die Knopflöcher in die Träger und die Knöpfe an die oberen Ecken des Latzes.',
    'Sew the buttonholes on the marks of the right placket strip and the buttons on the left one.':
        'Nähe die Knopflöcher auf den Markierungen des rechten Leistenstreifens und die Knöpfe auf den linken.',
    'Sew the front facings to the front linings and the back neck facing to the back lining with {n} mm seam allowance; press towards the lining.':
        'Nähe die vorderen Belege an die vorderen Futterteile und den rückwärtigen Halsbeleg an das Rückenfutter, mit {n} mm Nahtzugabe; zum Futter bügeln.',
    'Sew the front shoulders onto the outer yoke, then the inner yoke over them by rolling the shirt up inside the yoke (burrito method).':
        'Nähe die vorderen Schultern an die äußere Passe, dann die innere Passe darüber, indem du das Hemd in der Passe aufrollst (Burrito-Methode).',
    'Sew the hook Velcro onto the right side of the sleeve hem, at the back. Baste the tab into the sleeve seam at the hem, pointing towards the front.':
        'Nähe das Hakenklettband hinten auf die rechte Seite des Ärmelsaums. Hefte den Riegel am Saum in die Ärmelnaht, nach vorne zeigend.',
    'Sew the inner collar onto the neckline of the facings in the same way.':
        'Nähe den inneren Kragen genauso an den Halsausschnitt der Belege.',
    'Sew the leg elastic onto the wrong side of the liner leg openings with a zigzag, stretching it evenly; turn it in and topstitch.':
        'Nähe das Beingummi gleichmäßig gedehnt mit Zickzack auf die linke Seite der Beinausschnitte des Innenslips; schlage es ein und steppe ab.',
    'Sew the outer front and back together at the shoulders with {n} mm seam allowance.':
        'Nähe das äußere Vorder- und Rückenteil an den Schultern mit {n} mm Nahtzugabe zusammen.',
    'Sew the pocket bag pieces onto the zip tapes and together round the edges.':
        'Nähe die Taschenbeutelteile an die Reißverschlussbänder und rundum zusammen.',
    'Sew the second bag piece onto the upper allowance and sew both bag pieces together round the sides and the bottom. Finish the edges.':
        'Nähe das zweite Beutelteil an die obere Zugabe und beide Beutelteile an den Seiten und unten zusammen. Versäubere die Kanten.',
    'Sew the second tie onto the end of the wrap edge of the outer front, at the waist point.':
        'Nähe das zweite Bindeband an das Ende der Wickelkante des äußeren Vorderteils, am Taillenpunkt.',
    'Sew the swim elastic with a zigzag onto the wrong side of the leg openings, armholes and neckline, stretching it slightly (more at the back of the leg). Turn it in and topstitch with a zigzag or twin needle.':
        'Nähe das Badegummi leicht gedehnt mit Zickzack auf die linke Seite von Beinausschnitten, Armlöchern und Halsausschnitt (hinten am Bein stärker). Schlage es ein und steppe mit Zickzack oder Zwillingsnadel ab.',
    'Sew the waistband right sides together onto the top edge, the ends extending past the fly by the seam allowance, with {n} mm seam allowance. Fold the ends right sides together and sew across them; turn. Turn the inner edge under over the allowance and topstitch all round the waistband, catching the belt loops (centre back, back yokes, front).':
        'Nähe den Bund rechts auf rechts mit {n} mm Nahtzugabe an die Oberkante, die Enden um die Nahtzugabe über den Schlitz hinaus. Falte die Enden rechts auf rechts und nähe quer darüber; wende sie. Schlage die innere Kante über die Zugabe ein und steppe den Bund rundum ab, dabei die Gürtelschlaufen mitfassen (hintere Mitte, Passen hinten, vorne).',
    'Sew the zip right sides together onto the centre front edges of the outer bag, the top stop {n} cm below the top edge. Lay the lining over it right sides together and sew the centre front edges again through all layers.':
        'Nähe den Reißverschluss rechts auf rechts an die Kanten der vorderen Mitte des Außensacks, den oberen Endstopp {n} cm unter der Oberkante. Lege das Futter rechts auf rechts darüber und nähe die Kanten der vorderen Mitte noch einmal durch alle Lagen.',
    'Sew {n} buttonholes on the marks of the right band (women) or the left band (men) and the buttons opposite them.':
        'Nähe {n} Knopflöcher auf den Markierungen der rechten Leiste (Damen) oder der linken Leiste (Herren) und die Knöpfe gegenüber.',
    'Sew {n} horizontal buttonholes on the marks of the right front (women) or the left front (men) and the buttons on the other front, centre fronts on top of each other.':
        'Nähe {n} waagerechte Knopflöcher auf den Markierungen des rechten Vorderteils (Damen) oder des linken (Herren) und die Knöpfe auf das andere Vorderteil, vordere Mitten aufeinander.',
    "Sew {n} vertical buttonholes on the marks of the right front and one horizontal one in the collar stand, and one in each cuff. Lay the fronts on top of each other, centre fronts matching, and sew the buttons on the left front through the buttonholes' marks.":
        'Nähe {n} senkrechte Knopflöcher auf den Markierungen des rechten Vorderteils, ein waagerechtes in den Kragensteg und eines in jede Manschette. Lege die Vorderteile aufeinander, vordere Mitten bündig, und nähe die Knöpfe auf das linke Vorderteil, durch die Knopflöcher markiert.',
    "Sew {n} vertical buttonholes on the marks of the right front and one horizontal one in the collar stand. Lay the fronts on top of each other, centre fronts matching, and sew the buttons on the left front through the buttonholes' marks.":
        'Nähe {n} senkrechte Knopflöcher auf den Markierungen des rechten Vorderteils und ein waagerechtes in den Kragensteg. Lege die Vorderteile aufeinander, vordere Mitten bündig, und nähe die Knöpfe auf das linke Vorderteil, durch die Knopflöcher markiert.',
    'Sew {n} vertical buttonholes on the marks of the right front and the buttons on the left front.':
        'Nähe {n} senkrechte Knopflöcher auf den Markierungen des rechten Vorderteils und die Knöpfe auf das linke Vorderteil.',
    "Sew {n} vertical buttonholes on the marks of the right front, and one in each cuff. Lay the fronts on top of each other, centre fronts matching, and sew the buttons on the left front through the buttonholes' marks.":
        'Nähe {n} senkrechte Knopflöcher auf den Markierungen des rechten Vorderteils und eines in jede Manschette. Lege die Vorderteile aufeinander, vordere Mitten bündig, und nähe die Knöpfe auf das linke Vorderteil, durch die Knopflöcher markiert.',
    "Sew {n} vertical buttonholes on the marks of the right front. Lay the fronts on top of each other, centre fronts matching, and sew the buttons on the left front through the buttonholes' marks.":
        'Nähe {n} senkrechte Knopflöcher auf den Markierungen des rechten Vorderteils. Lege die Vorderteile aufeinander, vordere Mitten bündig, und nähe die Knöpfe auf das linke Vorderteil, durch die Knopflöcher markiert.',
    'Slip the bodice into the pants right sides together, waist edges level: side seams, centre back and the front edges matching. Pin, easing in any extra width at the back. Sew with {n} mm seam allowance and press the allowances up towards the bodice.':
        'Stecke das Oberteil rechts auf rechts in die Hose, die Taillenkanten bündig: Seitennähte, hintere Mitte und Vorderkanten aufeinander. Stecke fest und halte überschüssige Weite hinten ein. Nähe mit {n} mm Nahtzugabe und bügle die Zugaben nach oben zum Oberteil.',
    'Snap the inner leg closed at the foot. Pin the sole right sides together into the leg end, toe to the front leg, heel to the back leg, and sew it in with {n} mm seam allowance.':
        'Schließe das innere Bein am Fuß mit den Druckknöpfen. Stecke die Sohle rechts auf rechts in das Beinende, Zehen zum vorderen Bein, Ferse zum hinteren, und nähe sie mit {n} mm Nahtzugabe ein.',
    'Snaps: {n} snaps (plastic or jersey snaps) along the inner legs, back over front':
        'Druckknöpfe: {n} Druckknöpfe (Kunststoff- oder Jerseydruckknöpfe) entlang der inneren Beine, hinten über vorne',
    'Snaps: {n} snaps (plastic or metal) for the crotch + {n} for the wrap':
        'Druckknöpfe: {n} Druckknöpfe (Kunststoff oder Metall) für den Schritt + {n} für die Wickelung',
    'Stretch the band a little more over the bust: the edge then lies flat against the body and does not gape.':
        'Dehne die Blende über der Brust etwas stärker: dann liegt die Kante flach am Körper und steht nicht ab.',
    'Swim elastic {n}–{n} mm: leg openings {n} × {n} cm, armholes and neckline about {n} % of their length':
        'Badegummi {n}–{n} mm: Beinausschnitte {n} × {n} cm, Armlöcher und Halsausschnitt etwa {n} % ihrer Länge',
    'The outer front closes with a snap at the opposite side seam, the inner front with a snap inside.':
        'Das äußere Vorderteil schließt mit einem Druckknopf an der gegenüberliegenden Seitennaht, das innere mit einem Druckknopf innen.',
    'Thread the drawcords through the hem casing and the hood casing with a safety pin; put on the cord stoppers.':
        'Ziehe die Kordeln mit einer Sicherheitsnadel durch Saum- und Kapuzentunnel; setze die Kordelstopper auf.',
    'Thread the elastic with a safety pin, overlap the ends {n} cm and sew them together. Then thread the drawcord in through one eyelet, round the casing on top of the elastic and out through the other; knot its ends.':
        'Ziehe das Gummi mit einer Sicherheitsnadel ein, lege die Enden {n} cm übereinander und nähe sie zusammen. Ziehe dann die Kordel durch eine Öse ein, über dem Gummi rund durch den Tunnel und durch die andere Öse heraus; verknote ihre Enden.',
    'Try the dress on, button the straps onto the bib and sew the buttons on.':
        'Probiere das Kleid an, knöpfe die Träger an den Latz und nähe die Knöpfe an.',
    'Turn the jacket through the opening in the sleeve lining and close it by machine close to the fold.':
        'Wende die Jacke durch die Öffnung im Ärmelfutter und schließe sie knappkantig mit der Maschine.',
    'Turn the lower edge of the lining under over the waist seam allowance and stitch it down close to the fold (or stitch in the ditch from the right side).':
        'Schlage die Unterkante des Futters über der Zugabe der Taillennaht ein und steppe sie knapp an der Bruchkante fest (oder von rechts im Nahtschatten).',
    'Unfold one edge of the binding and sew it right sides together onto the armhole with {n} cm allowance in the crease, the ends overlapping {n} cm at the side seam. Fold it over the allowance to the inside and stitch it down from the right side.':
        'Klappe eine Kante der Einfassung auf und nähe sie rechts auf rechts mit {n} cm Zugabe im Bruch an das Armloch, die Enden {n} cm überlappend an der Seitennaht. Schlage sie über die Zugabe nach innen und steppe sie von rechts fest.',
    'Unfold one edge of the binding and sew it right sides together onto the armhole, the ends overlapping at the side seam. Fold it to the inside over the allowance and stitch it down.':
        'Klappe eine Kante der Einfassung auf und nähe sie rechts auf rechts an das Armloch, die Enden überlappend an der Seitennaht. Schlage sie über die Zugabe nach innen und steppe sie fest.',
    'Use a jeans needle ({n}–{n}) and topstitching thread for the visible seams.':
        'Nimm eine Jeansnadel ({n}–{n}) und Steppgarn für die sichtbaren Nähte.',
    'Warmth {n} TOG: all year, {n}–{n} °C; layers: outer fabric + jersey lining + thin wadding (about {n} g/m²)':
        'Wärme {n} TOG: ganzjährig, {n}–{n} °C; Lagen: Außenstoff + Jerseyfutter + dünnes Volumenvlies (etwa {n} g/m²)',
    'With outer and lining right sides together, sew round the neckline (folding the zip tape ends in) and round both armholes, stopping {n} cm before the shoulder seams. Clip the curves, pull the bag through the shoulders to the right side and close the shoulder gaps by hand.':
        'Lege Außenstoff und Futter rechts auf rechts und nähe den Halsausschnitt (die Enden des Reißverschlussbands eingeschlagen) und beide Armlöcher rundum, jeweils {n} cm vor den Schulternähten aufhören. Rundungen einschneiden, den Schlafsack durch die Schultern auf rechts ziehen und die Öffnungen an den Schultern von Hand schließen.',
    'Zip: two-way, {n} cm (or the next longer one), with a zip garage at the top':
        'Reißverschluss: zwei Wege, {n} cm (oder der nächstlängere), oben mit Reißverschlussgarage',
    'can the baby kick and bend the knees freely, and do the snaps close without pulling over the nappy?':
        'kann das Baby frei strampeln und die Knie beugen, und schließen die Druckknöpfe über der Windel, ohne zu ziehen?',
    'can you sit and bend forward without the crotch pulling up, and does the waist seam sit at your waist?':
        'kannst du sitzen und dich vorbeugen, ohne dass der Schritt hochzieht, und sitzt die Taillennaht an deiner Taille?',
    'cut on the bias (woven) or across the stretch (knit); press both long edges to the middle':
        'schräg zuschneiden (Webware) oder quer zur Dehnung (Strickstoff); beide Längskanten zur Mitte bügeln',
    'do the buttons close over the chest without pulling, and can you lift your arms?':
        'schließen die Knöpfe über der Brust, ohne zu ziehen, und kannst du die Arme heben?',
    'do the darts point at the bust, does the waist seam sit at the waist, and does the zip close without pulling?':
        'zeigen die Abnäher auf die Brust, sitzt die Taillennaht an der Taille, und schließt der Reißverschluss, ohne zu ziehen?',
    'do the trunks stay up with the drawcord loose, and does the liner sit close without cutting in?':
        'bleiben die Shorts mit lockerer Kordel oben, und liegt der Innenslip an, ohne einzuschneiden?',
    'does it close over a fleece, can you raise your arms without the hem riding up, and does the hood turn with your head?':
        'lässt sie sich über einem Fleece schließen, kannst du die Arme heben, ohne dass der Saum hochrutscht, und dreht sich die Kapuze mit dem Kopf?',
    'does it close over a jacket or a thick sweater, and can you sit down without it pulling?':
        'lässt er sich über einer Jacke oder einem dicken Pullover schließen, und kannst du dich setzen, ohne dass er zieht?',
    'does it close over a sweater without pulling, and can you cross your arms in front?':
        'lässt sie sich über einem Pullover schließen, ohne zu ziehen, und kannst du die Arme vor dem Körper kreuzen?',
    'does it close over a sweater, and do the armholes leave room without gaping?':
        'lässt sie sich über einem Pullover schließen, und lassen die Armlöcher Platz, ohne abzustehen?',
    'does it close over the chest without the band gaping, and do the sleeves end at the wrist?':
        'schließt sie über der Brust, ohne dass die Leiste absteht, und enden die Ärmel am Handgelenk?',
    'does it reach the crotch without pulling on the shoulders when you bend, and do the leg openings lie flat?':
        'reicht er bis in den Schritt, ohne beim Bücken an den Schultern zu ziehen, und liegen die Beinausschnitte flach?',
    'does the bib reach the chest with the straps buttoned in the middle hole, and can the wearer squat?':
        'reicht der Latz bis zur Brust, wenn die Träger im mittleren Loch geknöpft sind, und kann man darin in die Hocke gehen?',
    'does the bib reach to just below the armpits, and do the straps stay on the shoulders when you move?':
        'reicht der Latz bis knapp unter die Achseln, und bleiben die Träger beim Bewegen auf den Schultern?',
    'does the head slip through the open placket, and does the collar lie flat round the neck?':
        'passt der Kopf durch die offene Leiste, und liegt der Kragen flach um den Hals?',
    'does the waist elastic sit flat without rolling, and do the leg openings neither cut in nor gape?':
        'liegt das Taillengummi flach, ohne sich zu rollen, und schneiden die Beinausschnitte weder ein noch stehen sie ab?',
    'does the waistband close without gaping at the back, can you sit and squat, and does the fly lie flat?':
        'schließt der Bund, ohne hinten abzustehen, kannst du sitzen und in die Hocke gehen, und liegt der Schlitz flach?',
    'does the wrap cover the chest without gaping when you bend forward, and do the ties sit at the waist?':
        'bedeckt die Wickelung die Brust, ohne beim Vorbeugen abzustehen, und sitzen die Bindebänder an der Taille?',
    'front + gusset + back against the body crotch length (low rise sits lower)':
        'vorne + Zwickel + hinten gegen die Schrittlänge des Körpers (niedrige Leibhöhe sitzt tiefer)',
    'is the top loose enough to sleep in, and does the pants waist stay up without pressing?':
        'ist das Oberteil weit genug zum Schlafen, und bleibt der Hosenbund oben, ohne zu drücken?',
    "is there a hand's width of room below the feet, and does the neckline sit close without the head slipping in?":
        'ist unter den Füßen eine Handbreit Platz, und liegt der Halsausschnitt an, ohne dass der Kopf hineinrutschen kann?',
    'the zip opens the neckline for dressing; closed it stays smaller than the head':
        'der Reißverschluss öffnet den Halsausschnitt zum Anziehen; geschlossen bleibt er kleiner als der Kopf',
    'Velcro: {n} × {n} cm (tabs) and {n} × {n} cm (sleeves), {n} cm wide':
        'Klettband: {n} × {n} cm (Riegel) und {n} × {n} cm (Ärmel), {n} cm breit',
    'Pants: {s}': 'Hose: {s}',
    'Legs: {s}': 'Beine: {s}',
    'Liner: {s}': 'Innenslip: {s}',
    'leg elastic': 'Beingummi',
    'sew the gusset to the back': 'Zwickel ans Rückenteil nähen',
    'sew the gusset to the front': 'Zwickel ans Vorderteil nähen',
    'sew the side seams': 'Seitennähte nähen',
    'swim mesh; leg elastic {n} × {n} cm, {n}–{n} mm': 'Badenetz; Beingummi {n} × {n} cm, {n}–{n} mm',
})
