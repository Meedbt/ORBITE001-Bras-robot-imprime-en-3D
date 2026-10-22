# ORBITE — Bras robot imprimé en 3D

Projet personnel réalisé en complément d’un projet universitaire pour apprendre à concevoir, fabriquer et programmer un bras robot.

L’objectif est de construire un petit bras de bureau capable de saisir et déplacer des objets légers. Il possède **cinq articulations et une pince motorisée**, soit **six servomoteurs**, avec une armature et des coques démontables imprimées en 3D.

![Aperçu du prototype ORBITE](apercu.png)

## Matériel prévu

- **3 MG996R** : rotation de la base, épaule et coude.
- **3 MG90S** : inclinaison du poignet, rotation du poignet et pince.
- Carte compatible **Arduino Uno R3**, logée dans le socle avec la distribution d’alimentation et le fusible.
- Alimentation externe adaptée aux servos ; l’adaptateur secteur reste hors du robot.
- Pièces en PLA imprimées sur une **Bambu Lab A1 mini**, roulements et visserie.

Le projet sert aussi à travailler la logique en organigrammes, utilisée à l’université avec **VBuilder**. Le programme Arduino et la manière de transférer cette logique restent à développer.

## État du projet

La révision **V0.2** ajoute un compartiment électronique fixe sous le bras, avec fond démontable, accès USB arrière et platine de passage des câbles. Le pack contient **38 STL** : 7 gabarits, 13 pièces de structure et 18 coques.

Les fichiers font l’objet de contrôles numériques ; le prototype n’a encore été ni imprimé ni assemblé. Les ajustements, le câblage et le fonctionnement restent à valider sur les composants réels.

## Fichiers

- [`stl/`](stl/) : pièces de structure, coques et gabarits.
- [`sources/`](sources/) : source CAO OpenSCAD et paramètres de conception.
- [`apercu_3d.html`](apercu_3d.html) : vue 3D interactive, avec un bouton **Socle ouvert** qui isole le fond et les références électroniques pour voir leur implantation.
- [`socle_electronique.png`](socle_electronique.png) : aperçu du compartiment inférieur.
- [`LIRE_AVANT_IMPRESSION.md`](LIRE_AVANT_IMPRESSION.md) : guide d’impression et de montage envisagé.

**Première étape :** imprimer les deux gabarits du fichier [`gabarits_depart_A1_mini.3mf`](gabarits_depart_A1_mini.3mf) et vérifier l’ajustement des servos avant d’imprimer le bras complet.
