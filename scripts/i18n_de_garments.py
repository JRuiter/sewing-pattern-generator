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
})
