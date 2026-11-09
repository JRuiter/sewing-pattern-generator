# sewing-pattern-generator

*English version: [README.en.md](README.en.md)*

Ein [Claude-Skill](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview), der
**nähbare, maßstabsgetreue Schnittmuster** aus Körpermaßen, einer Beschreibung oder Fotos eines
Kleidungsstücks erstellt: parametrische Konstruktion, Prüfung aller Nähte und druckfertige 1:1-PDFs
für Plotterrollen, A0/A1 oder A4 zum Kleben.

Alle erzeugten Dateien (Beschriftung der Schnittteile, Nähanleitung, Prüfbericht) gibt es auf
Deutsch (*„Anleitung auf Deutsch“*) oder Englisch. Claude antwortet in der Sprache, in der du
schreibst.

## Beispiel-Prompts

Beschreib einfach, was du möchtest:

- *„Eine Pumphose für meine Tochter, Größe 122, aus Sweat, Druck auf der 24"-Rolle.“*
- *„Ein Raglanshirt in Größe 140 als A4-Seiten zum Zusammenkleben.“*
- *„Ein Hoodie mit Kängurutasche für mich, Brust 96 cm, Hüfte 102 cm, Größe 168 cm.“*
- *„Hier ist ein Foto der Lieblingsjogger meines Sohnes neben der Referenzkarte, mach mir ein Schnittmuster daraus.“*
- *„Eine Bluse mit Bubikragen für meine Tochter, Größe 110, nur mit der Overlock genäht.“*
- *„Ein Kleid für die 45-cm-Stoffpuppe meiner Tochter.“*

## Installation in claude.ai (2 Minuten)

1. Lade die neueste `sewing-pattern-generator-x.y.z.zip` unter
   [**Releases → Latest**](https://github.com/JRuiter/sewing-pattern-generator/releases/latest)
   herunter. Nicht entpacken.
2. Öffne [claude.ai](https://claude.ai) im **Browser** (die App kann keine Skills hochladen; am Handy
   den Browser auf Desktop-Ansicht stellen).
3. Unter **Einstellungen → Fähigkeiten** *Codeausführung und Dateierstellung* einschalten, dann
   unter **Skills** auf **Skill hochladen** klicken und die Zip-Datei wählen.
4. Einen neuen Chat starten und einen der Prompts oben ausprobieren.

**Aktualisieren:** unter *Einstellungen → Fähigkeiten → Skills* den alten
`sewing-pattern-generator` löschen und die neue Zip-Datei wie in Schritt 3 hochladen.

## Was du bekommen kannst

- **Kleidung:** 37 Module, von Hosen, Jeans, Latzhosen und Jumpsuits über T-Shirts, Hoodies, Hemden,
  Blusen, Cardigans, Westen, Jacken und Mäntel bis zu Röcken und Kleidern, Bodys, Bade- und
  Unterwäsche, Schlafanzügen, Baby-Stramplern, Schlafsäcken, Mützen, Handschuhen, Socken und Taschen,
  dazu Puppenkleidung (20–100 cm). **[Alle Kleidungsstücke mit Beispiel-Prompts](#alle-kleidungsstücke)**.
- **Details:** Taschen, Bündchen, Bünde, Ärmelformen, Ausschnitte, Kragen, Knopfleisten,
  Reißverschlüsse, Teilungsnähte (Prinzessnähte, Passen, Colour-Blocking), Kapuzenfutter, Beinformen …
  sag einfach, was du möchtest; Claude sagt ehrlich, wenn etwas nicht geht, und bietet das Nächstbeste an.
- **Größen:** Baby und Kind 50–176, Damen 34–56, Herren 44–60, US/UK-Größen oder deine eigenen Maße
  (cm oder Zoll). Mehrere Größen auf einem Bogen gehen auch: *„Größen 98, 110 und 122 auf einem Schnitt“*.
- **Druck:** Plotterrolle (z. B. 24" / 610 mm), A0/A1, A4 oder US Letter zum Kleben, eine
  Beamer-Datei oder DXF für Schneidemaschinen. Jede Seite hat ein 5-cm- und ein 1-Zoll-Kontrollquadrat.
- **Was du bekommst:** das Schnittmuster als PDF (maßstabsgetreu) und SVG, einen Zuschnittplan mit dem
  Stoffverbrauch und ein bebildertes Nähheft mit einem Bild für jeden Schritt.
- **Vom Foto:** zeig ein Inspirationsfoto, und Claude überträgt es auf einen Schnitt; oder leg dein
  Lieblingsteil flach neben die druckbare [Referenzkarte](assets/reference-card.pdf), fotografier es
  von oben, und Claude baut den Schnitt daraus nach.
- **Anpassen:** nach dem Probeteil sagen, was nicht passt (*„Hüfte 2 cm zu eng, Schritt 1,5 cm zu
  tief“*), und einen korrigierten Schnitt bekommen.
- **Deine Ausstattung:** sag Claude einmal, welche Maschinen du hast (Nähmaschine, Overlock,
  Coverlock) und wessen Maße es sich merken soll; Nahtzugaben und Anleitung richten sich danach.

Jedes Schnittmuster wird vor dem Druck geprüft: Nähte, die zusammengenäht werden, müssen gleich lang
sein, Bündchen und Blenden müssen passen, der Kopf muss durch den Ausschnitt gehen. Ein Schnitt, der
die Prüfung nicht besteht, wird nicht gedruckt.

## Alle Kleidungsstücke

Jedes Kleidungsstück hat eine eigene Seite mit Bild und einem Beispiel-Prompt für jede Option.

<!-- GARMENTS -->
### Hosen und Overalls

| | Kleidungsstück | Beispiel-Prompt |
|---|---|---|
| <img src="examples/garments/pants_basic/cover.png" width="90"> | [Hose (Jogger, Pumphose, Leggings, Schlupfhose)](examples/garments/pants_basic/README.md) | *„Eine Pumphose in Größe 122 aus Sweat.“* |
| <img src="examples/garments/jeans/cover.png" width="90"> | [Jeans](examples/garments/jeans/README.md) | *„Eine Slim-Jeans für mich, Größe 38, Stretchdenim.“* |
| <img src="examples/garments/dungarees/cover.png" width="90"> | [Latzhose](examples/garments/dungarees/README.md) | *„Eine Latzhose aus Cord für meinen Sohn, Größe 104.“* |
| <img src="examples/garments/jumpsuit/cover.png" width="90"> | [Jumpsuit, Playsuit, Overall](examples/garments/jumpsuit/README.md) | *„Einen Jumpsuit aus Viskose für mich, Größe 38.“* |

### Oberteile

| | Kleidungsstück | Beispiel-Prompt |
|---|---|---|
| <img src="examples/garments/tshirt_basic/cover.png" width="90"> | [T-Shirt und Langarmshirt](examples/garments/tshirt_basic/README.md) | *„Ein Raglanshirt in 140.“* |
| <img src="examples/garments/hoodie/cover.png" width="90"> | [Hoodie, Sweatshirt, Sweatjacke](examples/garments/hoodie/README.md) | *„Ein Hoodie mit gefütterter Kapuze in 140.“* |
| <img src="examples/garments/shirt/cover.png" width="90"> | [Hemd und Bluse](examples/garments/shirt/README.md) | *„Eine Bluse für mich, Größe 40.“* |
| <img src="examples/garments/polo/cover.png" width="90"> | [Poloshirt](examples/garments/polo/README.md) | *„Ein Poloshirt in Herrengröße 52.“* |
| <img src="examples/garments/cardigan/cover.png" width="90"> | [Cardigan / Strickjacke](examples/garments/cardigan/README.md) | *„Ein Cardigan mit Rundhals in 128.“* |
| <img src="examples/garments/vest/cover.png" width="90"> | [Weste / Gilet](examples/garments/vest/README.md) | *„Eine Fleeceweste mit Druckknöpfen in 128.“* |

### Jacken und Mäntel

| | Kleidungsstück | Beispiel-Prompt |
|---|---|---|
| <img src="examples/garments/jacket/cover.png" width="90"> | [Jacke (gefüttert, gewebt)](examples/garments/jacket/README.md) | *„Eine gefütterte Jacke mit Paspeltaschen, Größe 38.“* |
| <img src="examples/garments/coat/cover.png" width="90"> | [Mantel](examples/garments/coat/README.md) | *„Einen Wollmantel in Knielänge, Größe 40.“* |
| <img src="examples/garments/softshell/cover.png" width="90"> | [Softshelljacke / Outdoorjacke](examples/garments/softshell/README.md) | *„Softshelljacke ohne Kapuze, Größe 140.“* |

### Röcke und Kleider

| | Kleidungsstück | Beispiel-Prompt |
|---|---|---|
| <img src="examples/garments/skirt/cover.png" width="90"> | [Rock](examples/garments/skirt/README.md) | *„Einen Tellerrock in 128.“* |
| <img src="examples/garments/dress/cover.png" width="90"> | [Kleid](examples/garments/dress/README.md) | *„Ein T-Shirt-Kleid in 116.“* |
| <img src="examples/garments/fitted_dress/cover.png" width="90"> | [Tailliertes Kleid (gewebt)](examples/garments/fitted_dress/README.md) | *„Ein tailliertes Kleid mit gezogenem Rock, Größe 38.“* |
| <img src="examples/garments/wrap/cover.png" width="90"> | [Wickeltop und Wickelkleid](examples/garments/wrap/README.md) | *„Ein Wickelkleid aus Jersey, Größe 38.“* |
| <img src="examples/garments/pinafore/cover.png" width="90"> | [Trägerkleid](examples/garments/pinafore/README.md) | *„Ein Trägerkleid aus Cord, Größe 116, A-Linie.“* |

### Bodys, Bade- und Unterwäsche

| | Kleidungsstück | Beispiel-Prompt |
|---|---|---|
| <img src="examples/garments/bodysuit/cover.png" width="90"> | [Body, Badeanzug, Wickelbody](examples/garments/bodysuit/README.md) | *„Einen Badeanzug für mich, Größe 38.“* |
| <img src="examples/garments/underwear/cover.png" width="90"> | [Unterwäsche: Slip und Boxershorts](examples/garments/underwear/README.md) | *„Boxershorts für meinen Mann, Größe 52.“* |
| <img src="examples/garments/swim_trunks/cover.png" width="90"> | [Badeshorts](examples/garments/swim_trunks/README.md) | *„Knielange Badeshorts, Größe 52.“* |

### Baby und Schlafen

| | Kleidungsstück | Beispiel-Prompt |
|---|---|---|
| <img src="examples/garments/romper/cover.png" width="90"> | [Baby-Strampler](examples/garments/romper/README.md) | *„Einen Strampler mit Füßen, Größe 68.“* |
| <img src="examples/garments/sleeping_bag/cover.png" width="90"> | [Baby-Schlafsack und Pucksack](examples/garments/sleeping_bag/README.md) | *„Einen Pucksack für ein Neugeborenes (Größe 56).“* |
| <img src="examples/garments/pyjama/cover.png" width="90"> | [Schlafanzug](examples/garments/pyjama/README.md) | *„Einen Schlafanzug mit geknöpftem Oberteil für mich, Herrengröße 52.“* |
| <img src="examples/garments/bib/cover.png" width="90"> | [Lätzchen](examples/garments/bib/README.md) | *„Ein Halstuch-Lätzchen in 74.“* |

### Accessoires

| | Kleidungsstück | Beispiel-Prompt |
|---|---|---|
| <img src="examples/garments/beanie/cover.png" width="90"> | [Beanie / Mütze](examples/garments/beanie/README.md) | *„Beanie ohne Umschlag.“* |
| <img src="examples/garments/loop/cover.png" width="90"> | [Loopschal](examples/garments/loop/README.md) | *„Ein Loop zum zweimal Herumlegen.“* |
| <img src="examples/garments/scarf/cover.png" width="90"> | [Schal](examples/garments/scarf/README.md) | *„Einen flachen Schal mit Fransen.“* |
| <img src="examples/garments/headband/cover.png" width="90"> | [Stirnband](examples/garments/headband/README.md) | *„Ein Twist-Stirnband für mich.“* |
| <img src="examples/garments/neckwear/cover.png" width="90"> | [Halstuch und Schlauchschal](examples/garments/neckwear/README.md) | *„Ein Dreieckstuch für mein Kind, 116.“* |
| <img src="examples/garments/mittens/cover.png" width="90"> | [Fäustlinge](examples/garments/mittens/README.md) | *„Babyfäustlinge ohne Daumen, Größe 74.“* |
| <img src="examples/garments/gloves/cover.png" width="90"> | [Fingerhandschuhe](examples/garments/gloves/README.md) | *„Handschuhe mit Schichteln aus Fleece.“* |
| <img src="examples/garments/socks/cover.png" width="90"> | [Socken und Hausschuhsocken](examples/garments/socks/README.md) | *„Hausschuhsocken mit ABS-Sohle in 128.“* |
| <img src="examples/garments/earflap_hat/cover.png" width="90"> | [Mütze mit Ohrenklappen](examples/garments/earflap_hat/README.md) | *„Ohrenklappenmütze ohne Bänder.“* |
| <img src="examples/garments/bucket_hat/cover.png" width="90"> | [Fischerhut / Sonnenhut](examples/garments/bucket_hat/README.md) | *„Ein Wendehut.“* |
| <img src="examples/garments/cap/cover.png" width="90"> | [Baseballcap](examples/garments/cap/README.md) | *„Cap mit längerem Schirm (8 cm).“* |

### Taschen

| | Kleidungsstück | Beispiel-Prompt |
|---|---|---|
| <img src="examples/garments/bag/cover.png" width="90"> | [Taschen: Shopper und Turnbeutel](examples/garments/bag/README.md) | *„Einen Turnbeutel.“* |
<!-- /GARMENTS -->

## In Bildern

Alle Bilder stammen aus den [Beispielen](#beispiele) unten und wurden mit diesem Skill erzeugt.

### Ein maßstabsgetreues Schnittmuster, fertig zum Drucken

> *„Eine Pumphose für meine Tochter, Größe 122, aus Sweat, Druck auf der 24"-Rolle.“*

Nahtzugabe, Fadenlauf, Knipse, Stoffbruch und Beschriftung an jedem Teil. Auf der Plotterrolle liegen
die Teile auf einer langen Seite; auf A4 oder Letter bekommst du nummerierte Seiten mit Klebeflächen
und eine Übersichtsseite.

<table><tr>
<td width="60%"><img src="docs/images/pattern_roll.png" alt="Pumphose Gr. 122 auf der 610-mm-Rolle"></td>
<td width="40%"><img src="docs/images/pattern_a4_tiles.png" alt="Derselbe Schnitt auf A4-Seiten"></td>
</tr><tr><td>610-mm-Plotterrolle</td><td>A4-Seiten zum Kleben</td></tr></table>

### Ein bebildertes Nähheft

> *„Ein Hoodie mit Kängurutasche, Größe 140.“*

Ein Titelblatt mit dem fertigen Kleidungsstück von vorne und hinten und womit es genäht wird; alle
Teile groß und im selben Maßstab mit ihrer Anzahl, das Material mit Stoffverbrauch, Kurzwaren und
Werkzeug; die Grundlagen für deine Maschinen; dann zwei Schritte pro Seite mit nummerierten
Handgriffen, Tipps, Warnungen und Alternativen. Jedes Bild wird aus deinen echten Schnittteilen
gezeichnet: rechte Seite farbig, linke Seite schraffiert, Stecknadeln, Nahtlinie, Nährichtung und die
Stichart für deine Maschine.

<table><tr>
<td><img src="docs/images/booklet_cover.png" alt="Titelblatt des Nähhefts"></td>
<td><img src="docs/images/booklet_parts.png" alt="Teile, Stoff und Werkzeug"></td>
<td><img src="docs/images/booklet_steps.png" alt="Nähschritte mit Bildern"></td>
</tr><tr><td>Titelblatt</td><td>Teile und Material</td><td>Schritte</td></tr></table>

### Zuschnittplan und Stoffverbrauch

Jedes Teil auf deiner Stoffbreite (im Stoffbruch oder einlagig, was weniger Stoff braucht), mit der
Menge Oberstoff und Bündchen, die du kaufen musst.

<img src="docs/images/cutting_layout.png" alt="Zuschnittplan für den Hoodie" width="700">

### Mehrere Größen auf einem Bogen

> *„Jogger in den Größen 98, 110 und 122 auf einem Schnitt.“*

Jede Größe hat eine eigene Farbe, Linienart und PDF-Ebene; nicht benötigte Größen blendest du vor dem
Drucken aus.

<img src="docs/images/nested_sizes.png" alt="Jogger in den Größen 98, 110 und 122 ineinander" width="500">

### Ein Lieblingsteil vom Foto kopieren

> *„Hier ist ein Foto der Lieblingsjogger meines Sohnes neben der Referenzkarte, mach mir ein Schnittmuster daraus.“*

Leg das Kleidungsstück flach neben die druckbare [Referenzkarte](assets/reference-card.pdf) und
fotografier es von oben. Claude richtet das Foto gerade, misst nach, zeigt dir die Messwerte und baut
einen Schnitt, den du auch in andere Größen umrechnen lassen kannst.

<table><tr>
<td><img src="docs/images/photo_input.jpg" alt="Foto mit Referenzkarte"></td>
<td><img src="docs/images/photo_overlay.jpg" alt="Gemessene Kontur und Werte"></td>
</tr><tr><td>Dein Foto</td><td>Was Claude gemessen hat</td></tr></table>

### Puppenkleidung

> *„Ein Kleid für die 45-cm-Stoffpuppe meiner Tochter.“*

Kleider, Röcke, Hosen und T-Shirts für Stoffpuppen und Kuscheltiere von 20 bis 100 cm, mit schmalen
Nahtzugaben und einem Rückenverschluss mit Klett statt eines Ausschnitts, durch den der Puppenkopf
nicht passt.

<img src="docs/images/doll_dress.png" alt="Puppenkleid für eine 45-cm-Puppe auf A4-Seiten" width="300">

## Beispiele

Vollständige Ausgabeordner, jeder mit eigener README (Prompt, Bilder, was jede Datei ist):

1. [Pumphose, Größe 122, Sweat, 610-mm-Rolle](examples/1_harem_pants_122_roll610)
2. [Dieselbe als A4-Seiten zum Kleben](examples/2_harem_pants_122_a4)
3. [Vom Foto kopiert](examples/3_photo_mode_b): Foto mit Referenzkarte → nachgebaute Jogger
4. [Puppenkleid](examples/4_doll_dress_45cm_a4) für eine 45-cm-Stoffpuppe, A4-Seiten
5. [Hoodie mit Kängurutasche, Größe 140](examples/5_hoodie_140_a4), A4-Seiten
6. [Jogger in den Größen 98, 110 und 122](examples/6_joggers_nested_98_110_122_roll610) auf einer 610-mm-Rolle

## Claude Code und Kommandozeile

Für Claude Code das Repository in den Skills-Ordner klonen:

```bash
git clone https://github.com/JRuiter/sewing-pattern-generator ~/.claude/skills/sewing-pattern-generator
pip install -r ~/.claude/skills/sewing-pattern-generator/requirements.txt
```

Alles Weitere (Generator aus Python aufrufen, alle Optionen, wie die Prüfungen funktionieren, Tests,
Aufbau des Repositorys) steht im **[Deep Dive](docs/DEEP_DIVE.md)** (Englisch).

## Deine Schnittmuster gehören dir

Mit diesem Werkzeug erzeugte Schnittmuster gehören **dir**. Nutzen, drucken, nähen, die fertigen
Stücke verkaufen oder die Schnittdateien weitergeben, wie du möchtest; keine Namensnennung nötig. Die
MIT-Lizenz unten gilt für die *Software* und schränkt nicht ein, was du damit erstellst.

Die Konstruktionen sind eigene parametrische Schnitte nach allgemein bekannten Konstruktionsregeln;
es wurden keine kommerziellen oder geschützten Schnittmuster kopiert. Bei einem Foto eines
Designerstücks erstellt der Skill eine eigene Konstruktion im ähnlichen Stil, keine Kopie.

**Näh immer zuerst ein Probeteil** aus günstigem Stoff mit ähnlicher Dehnung, wenn du einen neuen
Schnitt zum ersten Mal verwendest.

## Lizenz

[MIT](LICENSE) © JRuiter. Die mitgelieferten DejaVu-Schriften stehen unter ihrer eigenen freien Lizenz
([assets/fonts/DejaVu-LICENSE.txt](assets/fonts/DejaVu-LICENSE.txt)).
