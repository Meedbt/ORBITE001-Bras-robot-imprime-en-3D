# ORBITE001 — Bras robot imprimé en 3D

Projet personnel réalisé en complément d’un projet universitaire pour apprendre à fabriquer et programmer un bras robot.

La version **V0.3 MICRO TEST** utilise **six MG90S** : cinq articulations et une pince motorisée. L’armature est raccourcie, avec deux maillons de **60 et 50 mm entre axes**, et se monte sans coques décoratives pour les premiers essais **sans charge**.

![Aperçu du prototype ORBITE001](apercu.png)

## Matériel prévu

- **6 servomoteurs MG90S positionnels**, avec leurs palonniers et vis centrales.
- Carte compatible **Arduino Uno R3**, distribution d’alimentation et fusible dans le socle.
- Alimentation externe adaptée aux servos ; adaptateur secteur à l’extérieur du robot.
- Pièces imprimées sur une **Bambu Lab A1 mini**, un roulement 608ZZ, quatre 623ZZ et visserie.

Le projet permet de travailler la logique en organigrammes utilisée à l’université avec **VBuilder**. Le programme Arduino et la transposition de cette logique restent à développer.

## État du projet

Cette version est un **prototype CAO à tester**, encore non imprimé et non assemblé physiquement. Le fonctionnement avec les six MG90S, les mouvements et la tenue en charge restent à valider ; un ajustement ou un rééquilibrage peut être nécessaire.

Le pack contient **18 STL : 5 gabarits et 13 pièces de structure**, dont le compartiment électronique à fond démontable. L’ancienne V0.2 reste une autre conception : ses pièces ne doivent pas être mélangées avec celles de la version micro.

## Fichiers

- [`stl/`](stl/) : armature, pince, socle électronique et gabarits.
- [`sources/`](sources/) : source CAO OpenSCAD et paramètres.
- [`apercu_3d.html`](apercu_3d.html) : aperçu interactif ; le bouton **Socle ouvert** montre l’implantation électronique.
- [`LIRE_AVANT_IMPRESSION.md`](LIRE_AVANT_IMPRESSION.md) : guide d’impression, de montage et de premiers essais.


