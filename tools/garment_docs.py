#!/usr/bin/env python3
"""One example folder per garment: examples/garments/<garment>/README.md (German), README.en.md
(English) and cover.png (the finished garment from the booklet's title page), plus the garment
tables of README.md / README.en.md (between the GARMENTS markers).

  python tools/garment_docs.py            # READMEs and cover pictures
  python tools/garment_docs.py text       # only the READMEs (no drafting)
"""
from __future__ import annotations

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

# garment: (group, title de, title en, size, description de, description en,
#           [(option = values, prompt de, prompt en), ...])
GROUPS = [("Hosen und Overalls", "Pants and overalls"), ("Oberteile", "Tops"), ("Jacken und Mäntel", "Jackets and coats"),
          ("Röcke und Kleider", "Skirts and dresses"), ("Bodys, Bade- und Unterwäsche", "Bodysuits, swimwear and underwear"),
          ("Baby und Schlafen", "Baby and sleepwear"), ("Accessoires", "Accessories"), ("Taschen", "Bags")]

DOCS = {
    "pants_basic": (0, "Hose (Jogger, Pumphose, Leggings, Schlupfhose)", "Pants (joggers, harem pants, leggings, pull-on trousers)", "122",
                    "Der Hosengrundschnitt: Gummibund, Bündchen oder Saum, Taschen, Längen von kurz bis lang.",
                    "The pants block: elastic waistband, cuffs or hem, pockets, lengths from shorts to long.",
                    [("style = jogger, harem, leggings, trousers", "Eine Pumphose in Größe 122 aus Sweat.", "Harem pants in size 122 from sweat fabric."),
                     ("fit = slim, normal, wide, oversized, harem", "Joggpants in 140, weit geschnitten.", "Wide-fit joggers in 140."),
                     ("length = long, 7/8, knee, short", "Kurze Hose (Shorts) in 116 aus Jersey.", "Shorts in 116 from jersey."),
                     ("waistband = casing, rib, yoga, tunnel", "Leggings mit breitem Yoga-Bund für mich, Größe 38.", "Leggings with a wide yoga waistband for me, size 38."),
                     ("cuffs", "Jogger ohne Bündchen, mit normalem Saum.", "Joggers without cuffs, plain hem."),
                     ("pockets = side, back_patch, cargo", "Schlupfhose mit Eingrifftaschen und Cargotaschen.", "Pull-on trousers with slanted pockets and cargo pockets."),
                     ("leg_shape = straight, tapered, bootcut, flare", "Eine Schlaghose aus Jersey mit Elasthan, Größe 36.", "Flared trousers from jersey with elastane, size 36."),
                     ("fake_fly", "Jogger mit angedeutetem Hosenschlitz (Ziernaht).", "Joggers with a fake fly (topstitched J)."),
                     ("hem_finish = plain, elastic_casing", "Hose mit Gummizug im Saum statt Bündchen.", "Pants with an elastic casing at the hem instead of cuffs.")]),
    "jeans": (0, "Jeans", "Jeans", "w38",
              "Fünf-Taschen-Jeans: Reißverschluss-Hosenschlitz, eingeschnittene Taschen, Passe hinten, aufgesetzte Gesäßtaschen, Uhrentasche, Bund mit Knopf, Gürtelschlaufen.",
              "Five-pocket jeans: zip fly, scoop pockets, back yoke, patch back pockets, coin pocket, waistband with button, belt loops.",
              [("fit = slim, normal, wide", "Eine Slim-Jeans für mich, Größe 38, Stretchdenim.", "Slim jeans for me, size 38, stretch denim."),
               ("leg_shape = straight, tapered, bootcut, flare", "Bootcut-Jeans in Herrengröße 52.", "Bootcut jeans in men's size 52."),
               ("length = long, 7/8, knee, short", "Jeansshorts in 140.", "Denim shorts in 140."),
               ("coin_pocket, belt_loops", "Jeans ohne Uhrentasche und ohne Gürtelschlaufen.", "Jeans without coin pocket and belt loops."),
               ("back_pockets = 0, 1, 2", "Jeans mit nur einer Gesäßtasche.", "Jeans with one back pocket only.")]),
    "dungarees": (0, "Latzhose", "Dungarees", "104",
                  "Hose mit Latz und gekreuzten Trägern, die am Latz geknöpft werden; Latztasche, Gummibund hinten.",
                  "Pants with a bib and crossed straps buttoned onto it; bib pocket, elastic waistband.",
                  [("style = trousers, jogger", "Eine Latzhose aus Cord für meinen Sohn, Größe 104.", "Corduroy dungarees for my son, size 104."),
                   ("length = long, 7/8, knee, short", "Kurze Latzhose (Latzshorts) in 92.", "Short dungarees in 92."),
                   ("bib_pocket", "Latzhose ohne Latztasche.", "Dungarees without the bib pocket."),
                   ("fabric = woven, corduroy, sweat …", "Latzhose aus Sweat mit Bündchen.", "Sweat dungarees with cuffs."),
                   ("pockets", "Latzhose mit Eingrifftaschen und Gesäßtaschen.", "Dungarees with slanted and back pockets.")]),
    "jumpsuit": (0, "Jumpsuit, Playsuit, Overall", "Jumpsuit, playsuit, boiler suit", "w38",
                 "Oberteil und Hose an der Taillennaht verbunden, Knopfleiste oder Reißverschluss, Gummi im Rückenteil, Bindegürtel.",
                 "Bodice and pants joined at the waist seam, buttons or zip, elastic in the back waist, tie belt.",
                 [("style = jumpsuit, boiler", "Einen Jumpsuit aus Viskose für mich, Größe 38.", "A viscose jumpsuit for me, size 38."),
                  ("style = boiler", "Einen Overall (Boiler Suit) mit Reißverschluss und Hemdkragen, Herrengröße 52.", "A boiler suit with zip and shirt collar, men's size 52."),
                  ("length = long, 7/8, short", "Einen kurzen Playsuit in 128.", "A short playsuit in 128."),
                  ("sleeve_length = short, long", "Jumpsuit mit langen Ärmeln.", "Jumpsuit with long sleeves."),
                  ("closure = buttons, zip", "Jumpsuit mit Reißverschluss vorne statt Knöpfen.", "Jumpsuit with a front zip instead of buttons."),
                  ("collar = none, stand, shirt", "Jumpsuit mit Stehkragen.", "Jumpsuit with a stand collar."),
                  ("belt, chest_pocket, pockets", "Jumpsuit ohne Gürtel, mit Brusttasche.", "Jumpsuit without belt, with a chest pocket.")]),
    "tshirt_basic": (1, "T-Shirt und Langarmshirt", "T-shirt and long-sleeve top", "128",
                     "Der Oberteil-Grundschnitt: eingesetzte oder Raglanärmel, Rundhals oder V-Ausschnitt, Bündchen.",
                     "The top block: set-in or raglan sleeves, round or V neck, bands.",
                     [("sleeve_style = set_in, raglan", "Ein Raglanshirt in 140.", "A raglan top in 140."),
                      ("sleeve_length = short, 3/4, long", "Ein Langarmshirt in 110.", "A long-sleeve top in 110."),
                      ("neckline = round, v", "T-Shirt mit V-Ausschnitt für mich, Herrengröße 50.", "V-neck T-shirt for me, men's 50."),
                      ("fit = slim, normal, wide, oversized, boxy", "Ein Oversize-Shirt in 152.", "An oversized tee in 152."),
                      ("length = normal, tunic", "Ein Tunika-Shirt in 122.", "A tunic top in 122."),
                      ("sleeve_cuffs, hem_band", "Langarmshirt mit Bündchen an Ärmeln und Saum.", "Long-sleeve top with cuffs and a hem band."),
                      ("style_lines = princess, yoke, color_block", "T-Shirt mit Colour-Blocking: oben eine andere Farbe.", "A colour-block tee: the top part in another colour.")]),
    "hoodie": (1, "Hoodie, Sweatshirt, Sweatjacke", "Hoodie, sweatshirt, zip jacket", "140",
               "Kapuze (auch gefüttert), Kängurutasche, Bündchen; geschlossen oder als Jacke mit Reißverschluss.",
               "Hood (optionally lined), kangaroo pocket, bands; pullover or zip-up jacket.",
               [("hood, hood_lining", "Ein Hoodie mit gefütterter Kapuze in 140.", "A hoodie with a lined hood in 140."),
                ("hood = false", "Ein Sweatshirt ohne Kapuze.", "A sweatshirt without hood."),
                ("kangaroo", "Hoodie ohne Kängurutasche.", "Hoodie without the kangaroo pocket."),
                ("front = closed, zip", "Eine Sweatjacke mit Reißverschluss, Größe 128.", "A zip-up sweat jacket, size 128."),
                ("sleeve_style = set_in, raglan", "Raglan-Hoodie in Größe 38.", "Raglan hoodie in size 38."),
                ("style_lines = princess, yoke, color_block", "Hoodie mit Passe vorne und hinten.", "Hoodie with a front and back yoke.")]),
    "shirt": (1, "Hemd und Bluse", "Shirt and blouse", "m52",
              "Gewebtes Hemd mit Knopfleiste, Kragen mit Steg, Passe, Manschetten mit Ärmelschlitz, Brusttasche; Bluse mit Brustabnäher.",
              "Woven shirt with button stand, collar and stand, yoke, cuffs with sleeve placket, chest pocket; blouse with bust dart.",
              [("style = shirt, blouse", "Eine Bluse für mich, Größe 40.", "A blouse for me, size 40."),
               ("collar = shirt, stand, peter_pan, none", "Eine Kinderbluse mit Bubikragen, Größe 110.", "A girl's blouse with a Peter Pan collar, size 110."),
               ("sleeve_length = short, long", "Kurzarmhemd in Herrengröße 52.", "Short-sleeve shirt in men's 52."),
               ("yoke, pocket, bust_dart, cuffs", "Hemd ohne Brusttasche und ohne Passe.", "Shirt without chest pocket and yoke."),
               ("buttons", "Bluse mit 7 Knöpfen.", "Blouse with 7 buttons.")]),
    "polo": (1, "Poloshirt", "Polo shirt", "m52",
             "Halbe Knopfleiste, Strickkragen aus Bündchen, Ärmelbündchen, optional Seitenschlitze.",
             "Half placket, rib-knit collar, sleeve bands, optional side vents.",
             [("sleeve_length = short, long", "Ein Poloshirt in Herrengröße 52.", "A polo shirt in men's 52."),
              ("collar_fabric = rib, main", "Polo mit Kragen aus dem Oberstoff.", "Polo with the collar from the main fabric."),
              ("side_vents", "Polo mit Seitenschlitzen.", "Polo with side vents."),
              ("buttons", "Polo mit 2 Knöpfen.", "Polo with 2 buttons.")]),
    "cardigan": (1, "Cardigan / Strickjacke", "Cardigan", "w38",
                 "Jacke aus Strick oder Sweat mit durchgehender Knopfleiste, V- oder Rundhals, Taschen.",
                 "Knit or sweat jacket with a continuous button band, V or round neck, pockets.",
                 [("neckline = v, round", "Ein Cardigan mit Rundhals in 128.", "A round-neck cardigan in 128."),
                  ("pockets", "Cardigan ohne Taschen.", "Cardigan without pockets."),
                  ("band_fabric = main, rib", "Cardigan mit Blende aus Bündchen.", "Cardigan with a rib band."),
                  ("hem_band, sleeve_cuffs", "Cardigan ohne Saumbündchen.", "Cardigan without the hem band.")]),
    "vest": (1, "Weste / Gilet", "Vest / gilet", "128",
             "Ärmellos, Reißverschluss, Druckknöpfe oder zum Überziehen; Kragen, Taschen, Armausschnitt mit Einfassung.",
             "Sleeveless, zip, snaps or pullover; collar, pockets, bound armholes.",
             [("closure = zip, snaps, none", "Eine Fleeceweste mit Druckknöpfen in 128.", "A fleece vest with snaps in 128."),
              ("collar", "Weste ohne Kragen.", "Vest without collar."),
              ("pockets", "Weste ohne Taschen.", "Vest without pockets."),
              ("binding_fabric = main, rib", "Weste mit Bündchen-Einfassung.", "Vest with rib binding.")]),
    "jacket": (2, "Jacke (gefüttert, gewebt)", "Jacket (lined, woven)", "w38",
               "Gefütterte Jacke mit Knopfleiste, Besätzen, Stehkragen und Paspel-, Leisten- oder Klappentaschen.",
               "Lined jacket with button front, facings, stand collar and welt, jetted or flap pockets.",
               [("pockets = welt, jetted, flap", "Eine gefütterte Jacke mit Paspeltaschen, Größe 38.", "A lined jacket with jetted pockets, size 38."),
                ("collar = stand, none", "Jacke ohne Kragen.", "Jacket without collar."),
                ("lining", "Jacke ohne Futter.", "Unlined jacket."),
                ("buttons", "Jacke mit 4 Knöpfen.", "Jacket with 4 buttons."),
                ("length", "Etwas längere Jacke (Hüftlänge).", "A longer jacket (hip length).")]),
    "coat": (2, "Mantel", "Coat", "w40",
             "Gefütterter Mantel in Knielänge mit Klappentaschen und Stehkragen.",
             "Lined knee-length coat with flap pockets and stand collar.",
             [("length = knee, midi", "Einen Wollmantel in Knielänge, Größe 40.", "A knee-length wool coat, size 40."),
              ("pockets = flap, welt, jetted", "Mantel mit Leistentaschen.", "Coat with welt pockets."),
              ("collar = stand, none", "Mantel ohne Kragen.", "Coat without collar.")]),
    "softshell": (2, "Softshelljacke / Outdoorjacke", "Softshell / outdoor jacket", "128",
                  "Reißverschluss, Kapuze, Reißverschlusstaschen, Klettriegel an den Ärmeln, Tunnelzug im Saum.",
                  "Zip, hood, zip pockets, Velcro sleeve tabs, drawcord hem.",
                  [("hood", "Softshelljacke ohne Kapuze, Größe 140.", "Softshell jacket without hood, size 140."),
                   ("pockets", "Softshelljacke ohne Taschen.", "Softshell jacket without pockets."),
                   ("cuff_tabs", "Ohne Klettriegel an den Ärmeln.", "Without the Velcro sleeve tabs."),
                   ("hem_drawcord", "Ohne Tunnelzug im Saum.", "Without the drawcord hem.")]),
    "skirt": (3, "Rock", "Skirt", "128",
              "Rock mit Gummibund: gezogen, A-Linie oder Tellerrock.",
              "Skirt with elastic waist: gathered, A-line or circle.",
              [("style = gathered, a_line, circle", "Einen Tellerrock in 128.", "A circle skirt in 128."),
               ("length = mini, knee, midi, maxi", "Einen Maxirock für mich, Größe 38.", "A maxi skirt for me, size 38."),
               ("gather", "Ein Stufenrock mit wenig Kräuselung (1,3).", "A gathered skirt with little fullness (1.3)."),
               ("flare_deg", "A-Linien-Rock mit mehr Weite.", "An A-line skirt with more flare.")]),
    "dress": (3, "Kleid", "Dress", "116",
              "T-Shirt-Oberteil mit Rock (gezogen, A-Linie, Teller) oder T-Shirt-Kleid; Taschen, Gummi in der Taille.",
              "T-shirt bodice with a skirt (gathered, A-line, circle) or a T-shirt dress; pockets, waist elastic.",
              [("style = waist_seam, shirt_dress", "Ein T-Shirt-Kleid in 116.", "A T-shirt dress in 116."),
               ("skirt = gathered, a_line, circle", "Kleid mit Tellerrock, Größe 128.", "A dress with a circle skirt, size 128."),
               ("length = mini, knee, midi, maxi", "Ein Midikleid für mich, Größe 40.", "A midi dress for me, size 40."),
               ("pockets, waist_elastic", "Kleid mit Nahttaschen.", "Dress with in-seam pockets."),
               ("sleeve_length", "Langarmkleid.", "Long-sleeve dress."),
               ("style_lines = princess, yoke, color_block", "Kleid mit Prinzessnähten.", "A dress with princess seams.")]),
    "fitted_dress": (3, "Tailliertes Kleid (gewebt)", "Fitted woven dress", "w38",
                     "Gewebtes Kleid mit Brust- und Taillenabnähern, nahtverdecktem Reißverschluss und Schrägband am Ausschnitt.",
                     "Woven dress with bust and waist darts, invisible zip and a bias-bound neckline.",
                     [("skirt = a_line, gathered", "Ein tailliertes Kleid mit gezogenem Rock, Größe 38.", "A fitted dress with a gathered skirt, size 38."),
                      ("sleeve_length = none, short, long", "Ärmelloses Etuikleid.", "A sleeveless fitted dress."),
                      ("length = knee, midi", "Tailliertes Midikleid.", "A fitted midi dress."),
                      ("pockets", "Mit Nahttaschen.", "With in-seam pockets.")]),
    "wrap": (3, "Wickeltop und Wickelkleid", "Wrap top and wrap dress", "w38",
             "Jersey, die Vorderteile kreuzen sich, Blende entlang der Wickelkante, Bindebänder.",
             "Knit, crossed fronts, band along the wrap edge, ties.",
             [("style = top, dress", "Ein Wickelkleid aus Jersey, Größe 38.", "A jersey wrap dress, size 38."),
              ("sleeve_length = short, long", "Wickeltop mit langen Ärmeln.", "Wrap top with long sleeves."),
              ("overlap", "Wickeltop mit weniger Überlappung (0,7).", "Wrap top with less overlap (0.7).")]),
    "pinafore": (3, "Trägerkleid", "Pinafore dress", "116",
                 "Gefüttertes Latz-Oberteil, gekreuzte Träger mit Knöpfen, gezogener Rock.",
                 "Lined bib bodice, crossed straps with buttons, gathered skirt.",
                 [("skirt = gathered, a_line", "Ein Trägerkleid aus Cord, Größe 116, A-Linie.", "A corduroy pinafore, size 116, A-line skirt."),
                  ("length = mini, knee, midi", "Kurzes Trägerkleid.", "A short pinafore."),
                  ("pockets", "Mit Taschen.", "With pockets.")]),
    "bodysuit": (4, "Body, Badeanzug, Wickelbody", "Bodysuit, swimsuit, wrap bodysuit", "74",
                 "Jersey mit Elasthan: Druckknöpfe im Schritt, Beinbündchen; Badeanzug mit Futter und Gummi; Baby-Wickelbody.",
                 "Knit with elastane: snap crotch, leg bands; swimsuit with lining and elastic; baby wrap bodysuit.",
                 [("style = body, swimsuit, wrap", "Einen Badeanzug für mich, Größe 38.", "A swimsuit for me, size 38."),
                  ("style = wrap", "Einen Wickelbody für ein Neugeborenes, Größe 56.", "A wrap bodysuit for a newborn, size 56."),
                  ("sleeve_length = none, short, long", "Langarmbody in 80.", "Long-sleeve bodysuit in 80."),
                  ("leg_cut = normal, high, low", "Badeanzug mit hohem Beinausschnitt.", "Swimsuit with a high leg cut.")]),
    "underwear": (4, "Unterwäsche: Slip und Boxershorts", "Underwear: briefs and boxers", "w38",
                  "Slip mit gefüttertem Zwickel (Burrito-Methode) und Gummi an Bund und Bein, oder Boxershorts.",
                  "Briefs with a lined gusset (burrito method) and elastic at waist and legs, or boxer briefs.",
                  [("style = briefs, boxers", "Boxershorts für meinen Mann, Größe 52.", "Boxer briefs for my husband, size 52."),
                   ("leg_cut = normal, high, low", "Slip mit hohem Beinausschnitt.", "Briefs with a high leg cut."),
                   ("rise = mid, low", "Hüftslip (tiefe Leibhöhe).", "Low-rise briefs."),
                   ("leg_length", "Boxershorts mit 15 cm Beinlänge.", "Boxers with 15 cm leg length.")]),
    "swim_trunks": (4, "Badeshorts", "Swim trunks", "m52",
                    "Schnell trocknender Stoff, Gummibund mit Kordel durch Ösen, Taschen mit Netzbeutel, Netz-Innenslip.",
                    "Quick-dry fabric, elastic waistband with a drawcord through eyelets, mesh pocket bags, mesh brief liner.",
                    [("length = short, knee", "Knielange Badeshorts, Größe 52.", "Knee-length swim trunks, size 52."),
                     ("liner", "Badeshorts ohne Innenslip für mein Kind, 128.", "Swim trunks without liner for my child, 128."),
                     ("pockets", "Badeshorts mit Gesäßtasche.", "Swim trunks with a back pocket.")]),
    "romper": (5, "Baby-Strampler", "Baby romper", "68",
               "Strampler (Gr. 50–92) mit Druckknöpfen an den Beininnenseiten, Bündchen oder Füßen.",
               "Romper (sizes 50–92) with snaps along the inner legs, cuffs or feet.",
               [("feet", "Einen Strampler mit Füßen, Größe 68.", "A footed romper, size 68."),
                ("sleeve_length = short, long", "Kurzarm-Strampler für den Sommer, Größe 62.", "A short-sleeve romper for summer, size 62."),
                ("fabric = jersey, interlock, fleece", "Strampler aus Interlock.", "Romper from interlock.")]),
    "sleeping_bag": (5, "Baby-Schlafsack und Pucksack", "Baby sleeping bag and swaddle sack", "74",
                     "Gefüttert, Zwei-Wege-Reißverschluss; Wärme nach TOG (Wattierung); Pucksack mit Flügeln und Klett.",
                     "Lined, two-way zip; warmth by TOG (wadding); swaddle sack with wings and Velcro.",
                     [("style = sleeping_bag, swaddle", "Einen Pucksack für ein Neugeborenes (Größe 56).", "A swaddle sack for a newborn (size 56)."),
                      ("tog = 0.5, 1.0, 2.5", "Einen Winterschlafsack (2,5 TOG) in 86.", "A winter sleeping bag (2.5 TOG) in 86."),
                      ("fabric", "Schlafsack aus Musselin (Webware) für den Sommer.", "A muslin (woven) sleeping bag for summer.")]),
    "pyjama": (5, "Schlafanzug", "Pyjamas", "128",
               "Oberteil und Hose in einem Auftrag: ein Zuschnittplan und ein Heft für beide Teile.",
               "Top and pants in one order: one cutting layout and one booklet for both.",
               [("top = tshirt, shirt", "Einen Schlafanzug mit geknöpftem Oberteil für mich, Herrengröße 52.", "Pyjamas with a button-up top for me, men's 52."),
                ("length = long, short", "Einen Shorty in 140.", "A shorty pyjama set in 140."),
                ("cuffs", "Schlafanzug mit Bündchen an Armen und Beinen.", "Pyjamas with cuffs on sleeves and legs."),
                ("collar = none, stand, shirt", "Geknöpftes Oberteil mit Hemdkragen.", "Button-up top with a shirt collar.")]),
    "bib": (5, "Lätzchen", "Baby bib", "74",
            "Klassisch mit Druckknopf oder als Halstuch-Lätzchen, saugfähige Rückseite.",
            "Classic with a snap or bandana style, absorbent back.",
            [("style = classic, bandana", "Ein Halstuch-Lätzchen in 74.", "A bandana bib in 74."),
             ("absorbent", "Lätzchen ohne saugfähige Lage.", "Bib without the absorbent layer."),
             ("length_cm", "Ein längeres Lätzchen (25 cm).", "A longer bib (25 cm).")]),
    "beanie": (6, "Beanie / Mütze", "Beanie", "128",
               "Jerseymütze mit oder ohne Umschlag, auch als Slouch.",
               "Knit hat with or without brim, also slouchy.",
               [("brim", "Beanie ohne Umschlag.", "Beanie without brim."),
                ("slouch", "Eine Slouchy-Beanie für mich.", "A slouchy beanie for me.")]),
    "loop": (6, "Loopschal", "Loop scarf", "128",
             "Schlauchschal, einfach oder doppelt gelegt.",
             "Tube scarf, worn single or doubled.",
             [("wraps = 1, 2", "Ein Loop zum zweimal Herumlegen.", "A loop scarf to wear doubled."),
              ("height", "Ein schmaler Loop (20 cm hoch).", "A narrow loop (20 cm high).")]),
    "scarf": (6, "Schal", "Scarf", "w38",
              "Schlauchschal oder flacher Schal, optional mit Fransen.",
              "Tube or flat scarf, optional fringe.",
              [("style = tube, flat", "Einen flachen Schal mit Fransen.", "A flat scarf with fringe."),
               ("length_cm, width_cm", "Einen Schal 180 × 30 cm.", "A scarf 180 × 30 cm.")]),
    "headband": (6, "Stirnband", "Headband", "w38",
                 "Glatt oder mit Twist-Knoten vorne.",
                 "Plain or with a twist at the front.",
                 [("style = plain, twist", "Ein Twist-Stirnband für mich.", "A twist headband for me."),
                  ("height_cm", "Ein breites Stirnband (12 cm).", "A wide headband (12 cm).")]),
    "neckwear": (6, "Halstuch und Schlauchschal", "Neck gaiter and neckerchief", "116",
                 "Schlauchschal (Neck Gaiter) oder Dreieckstuch.",
                 "Neck gaiter or triangle neckerchief.",
                 [("style = gaiter, neckerchief", "Ein Dreieckstuch für mein Kind, 116.", "A neckerchief for my child, 116."),
                  ("height_cm", "Ein hoher Schlauchschal (25 cm).", "A tall neck gaiter (25 cm).")]),
    "mittens": (6, "Fäustlinge", "Mittens", "116",
                "Daumen im Profil, optional mit Bündchen und Verbindungsschnur; für Babys ohne Daumen.",
                "Thumb in profile, optional rib cuff and string; thumbless for babies.",
                [("thumb", "Babyfäustlinge ohne Daumen, Größe 74.", "Thumbless baby mittens, size 74."),
                 ("cuff", "Fäustlinge ohne Bündchen.", "Mittens without cuff."),
                 ("string", "Fäustlinge mit Verbindungsschnur.", "Mittens with a string.")]),
    "gloves": (6, "Fingerhandschuhe", "Gloves", "w38",
               "Als Umriss-Handschuh oder mit Schichteln (Fourchettes) und eingesetztem Daumen.",
               "Outline gloves, or with fourchettes and a set-in thumb.",
               [("style = outline, fourchette", "Handschuhe mit Schichteln aus Fleece.", "Fleece gloves with fourchettes."),
                ("hand_circ, hand_length", "Handschuhe für Handumfang 19 cm, Handlänge 18 cm.", "Gloves for hand circumference 19 cm, length 18 cm.")]),
    "socks": (6, "Socken und Hausschuhsocken", "Socks and house socks", "128",
              "Socken mit geformter Ferse oder Hausschuhsocken mit Sohle.",
              "Socks with a shaped heel, or house socks with a sole.",
              [("style = profile, sole", "Hausschuhsocken mit ABS-Sohle in 128.", "House socks with an anti-slip sole in 128."),
               ("length = ankle, crew, knee", "Kniestrümpfe.", "Knee socks."),
               ("cuff", "Socken mit Bündchen.", "Socks with a rib cuff.")]),
    "earflap_hat": (6, "Mütze mit Ohrenklappen", "Earflap hat", "104",
                    "Gefüttert, optional mit Bindebändern.",
                    "Lined, optional ties.",
                    [("ties", "Ohrenklappenmütze ohne Bänder.", "Earflap hat without ties."),
                     ("flap_cm", "Längere Ohrenklappen (8 cm).", "Longer earflaps (8 cm).")]),
    "bucket_hat": (6, "Fischerhut / Sonnenhut", "Bucket hat / sun hat", "116",
                   "Gefüttert oder zum Wenden.",
                   "Lined or reversible.",
                   [("reversible", "Ein Wendehut.", "A reversible bucket hat."),
                    ("brim_cm", "Sonnenhut mit breiter Krempe (8 cm).", "Sun hat with a wide brim (8 cm).")]),
    "cap": (6, "Baseballcap", "Baseball cap", "w38",
            "Sechs Segmente, versteifter Schirm, verstellbarer Riegel.",
            "Six panels, stiffened peak, adjustable strap.",
            [("peak_cm", "Cap mit längerem Schirm (8 cm).", "A cap with a longer peak (8 cm)."),
             ("ease_cm", "Cap etwas lockerer (2 cm Zugabe).", "A slightly looser cap (2 cm ease).")]),
    "bag": (7, "Taschen: Shopper und Turnbeutel", "Bags: tote and drawstring bag", "-",
            "Shopper mit Futter, Boden und Innentasche, oder Turnbeutel; ohne Körpermaße.",
            "Lined tote with boxed corners and inner pocket, or drawstring bag; no body measurements.",
            [("style = tote, drawstring", "Einen Turnbeutel.", "A drawstring bag."),
             ("bag_size = small, medium, large", "Einen großen Shopper.", "A large tote."),
             ("width_cm, height_cm, depth_cm", "Einen Shopper 40 × 35 × 10 cm.", "A tote 40 × 35 × 10 cm."),
             ("lining, pocket", "Shopper ohne Futter.", "Unlined tote.")]),
}

COMMON_DE = [("fabric, stretch", "… aus Jersey mit 40 % Dehnung."), ("Größe oder Maße", "… für mich: Brust 96, Taille 80, Hüfte 102, Größe 168."),
             ("Druck", "… auf A4 zum Kleben / auf der 24\"-Rolle / als A0."), ("Maschinen", "… ich nähe nur mit der Overlock."),
             ("Sprache", "… Anleitung auf Deutsch.")]
COMMON_EN = [("fabric, stretch", "… from jersey with 40 % stretch."), ("size or measurements", "… for me: chest 96, waist 80, hip 102, height 168."),
             ("printing", "… as A4 pages / on the 24\" roll / as A0."), ("machines", "… I only sew with an overlocker."),
             ("language", "… instructions in English.")]


def size_label(size: str, de: bool) -> str:
    if size == "-":
        return "ohne Größe" if de else "no size"
    if size.startswith("w"):
        return ("Damengröße " if de else "women's size ") + size[1:]
    if size.startswith("m"):
        return ("Herrengröße " if de else "men's size ") + size[1:]
    return ("Größe " if de else "size ") + size


def readme(garment: str, de: bool) -> str:
    grp, tde, ten, size, dde, den, opts = DOCS[garment]
    title, desc = (tde, dde) if de else (ten, den)
    other = "README.en.md" if de else "README.md"
    lines = [f"# {title}", "", f"*{'English version' if de else 'Deutsche Version'}: [{other}]({other})*", "",
             desc, "", f'<img src="cover.png" alt="{title}" width="560">', "",
             ("Modul" if de else "Module") + f": `{garment}` · " + ("Beispielbild" if de else "Picture") + f": {size_label(size, de)}", "",
             "## " + ("Beispiel-Prompts für alle Optionen" if de else "Example prompts for every option"), "",
             "| " + ("Option" if de else "Option") + " | Prompt |", "|---|---|"]
    for name, pde, pen in opts:
        lines.append(f"| `{name}` | *„{pde}“* |" if de else f'| `{name}` | *"{pen}"* |')
    lines += ["", "## " + ("Geht bei jedem Kleidungsstück" if de else "Works for every garment"), "",
              "| " + ("Angabe" if de else "What") + " | Prompt |", "|---|---|"]
    for name, p in (COMMON_DE if de else COMMON_EN):
        lines.append(f"| {name} | *{p}* |")
    lines += ["", ("Alle Optionen mit Werten: [references/options.md](../../../references/options.md)." if de else
                   "All options with their values: [references/options.md](../../../references/options.md)."), ""]
    return "\n".join(lines)


def table(de: bool) -> str:
    out = []
    for gi, (gde, gen) in enumerate(GROUPS):
        rows = [(g, d) for g, d in DOCS.items() if d[0] == gi]
        if not rows:
            continue
        out += [f"### {gde if de else gen}", "", "| | " + ("Kleidungsstück" if de else "Garment") + " | " +
                ("Beispiel-Prompt" if de else "Example prompt") + " |", "|---|---|---|"]
        for g, d in rows:
            link = f"examples/garments/{g}/" + ("README.md" if de else "README.en.md")
            prompt = d[6][0][1] if de else d[6][0][2]
            out.append(f'| <img src="examples/garments/{g}/cover.png" width="90"> | [{d[1] if de else d[2]}]({link}) | '
                       + (f"*„{prompt}“*" if de else f'*"{prompt}"*') + " |")
        out.append("")
    return "\n".join(out)


def write_readmes():
    for g in DOCS:
        d = os.path.join(ROOT, "examples", "garments", g)
        os.makedirs(d, exist_ok=True)
        for de, fn in ((True, "README.md"), (False, "README.en.md")):
            with open(os.path.join(d, fn), "w", encoding="utf-8") as f:
                f.write(readme(g, de))
    for de, fn in ((True, "README.md"), (False, "README.en.md")):
        p = os.path.join(ROOT, fn)
        if not os.path.exists(p):
            continue
        s = open(p, encoding="utf-8").read()
        tbl = table(de)
        s = re.sub(r"(<!-- GARMENTS -->\n).*?(<!-- /GARMENTS -->)", lambda m, t=tbl: m.group(1) + t + m.group(2), s,
                   flags=re.S)
        with open(p, "w", encoding="utf-8") as f:
            f.write(s)


def write_covers():
    """The title-page views (front and back) of every garment as cover.png."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    from PIL import Image

    import allowance as A
    import booklet as B
    import diagrams as DG
    import measurements as M
    import views as V
    from garments import get
    for g, d in DOCS.items():
        size = d[3]
        mm = {} if size == "-" else M.complete_measures({}, size)[0]
        pat = A.draft(get(g), mm, {})
        DG._CTX["pattern"] = pat
        views = V.garment_views(pat)
        if views:
            fig, axes = plt.subplots(1, len(views), figsize=(4.2 * len(views), 5.2))
            axes = list(axes) if len(views) > 1 else [axes]
            for ax, (name, view) in zip(axes, views.items()):
                V.draw_view(ax, pat, view, back=name == "back")
            sx = max(np.ptp(a.get_xlim()) for a in axes)
            sy = max(np.ptp(a.get_ylim()) for a in axes)
            for a in axes:
                cx, y0 = float(np.mean(a.get_xlim())), a.get_ylim()[0]
                a.set_xlim(cx - sx / 2, cx + sx / 2)
                a.set_ylim(y0, y0 + sy)
                a.set_aspect("equal")
        else:
            fig = plt.figure(figsize=(B.PAGE[0], B.PAGE[0] * 0.55))
            B._views(fig, pat, (0.05, 0.05, 0.9, 0.9), captions=False)
        out = os.path.join(ROOT, "examples", "garments", g, "cover.png")
        fig.savefig(out, dpi=90, facecolor="white")
        plt.close(fig)
        im = Image.open(out).convert("RGB")
        bbox = Image.eval(im, lambda v: 255 - v).getbbox()
        if bbox:
            im = im.crop((max(0, bbox[0] - 10), max(0, bbox[1] - 10), min(im.width, bbox[2] + 10),
                          min(im.height, bbox[3] + 10)))
        im.thumbnail((700, 420))
        im.save(out, optimize=True)
        print(g, "ok")


if __name__ == "__main__":
    write_readmes()
    if "text" not in sys.argv[1:]:
        write_covers()
