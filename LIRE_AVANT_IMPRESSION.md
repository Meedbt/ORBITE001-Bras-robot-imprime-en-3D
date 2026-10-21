# ORBITE V0 — ton bras robot personnel

Conception originale inspirée du style de ta référence : coques claires arrondies, bagues sombres, moteurs intégrés et petite pince. Prévue pour une **Bambu Lab A1 mini**, trois MG996R et trois MG90S. Le plateau utile est de 180 × 180 × 180 mm ; les pièces sont fournies séparément à leur taille réelle.

**Statut : prototype de conception.** La géométrie a été générée et contrôlée numériquement. Aucun exemplaire n’a été imprimé, assemblé ou motorisé. Les dimensions réelles des servos, les palonniers, les jeux d’assemblage, les longueurs de vis, le passage des câbles, les butées et la tenue en charge restent à valider. Les six moteurs correspondent à cinq articulations du bras et un moteur de pince.

## Ce que tu peux faire maintenant

1. Ouvrir `apercu_3d.html` dans ton navigateur. Tu peux tourner autour du bras, masquer les coques, afficher les moteurs et déplacer les six commandes d’aperçu. Ce fichier fonctionne sans téléchargement supplémentaire. Les commandes ne pilotent aucun moteur et leurs plages ne représentent pas des limites mécaniques validées.
2. Dans Bambu Studio, importer **`gabarits_depart_A1_mini.3mf`**. Ce fichier contient uniquement deux gabarits de montage ; il ne contient ni réglages de tranchage certifiés ni programme d’impression.
3. Choisir ton imprimante **A1 mini**, ta buse réelle et ton PLA, puis imprimer à **100 % de l’échelle**. Point de départ pour une buse de 0,4 mm : couches de 0,20 mm, quatre parois, sans supports. Vérifier l’aperçu de tranchage avant l’impression.
4. Essayer un MG996R dans son grand gabarit et un MG90S dans le petit. Le corps doit passer sans forcer ; les oreilles doivent prendre appui et leurs trous doivent correspondre aux lumières. Vérifier aussi l’accès aux vis. Les corps nominaux utilisés sont 40,7 × 19,7 mm et 22,8 × 12,2 mm ; cela ne remplace pas la mesure des moteurs achetés.
5. Si le montage serre, essayer le gabarit `jeu_0p5`. S’il flotte trop, essayer `jeu_0p2`. Les valeurs indiquent un **jeu par côté**, donc le gabarit 0,35 mm ajoute 0,70 mm aux dimensions du corps. Ne pas agrandir tout le bras pour corriger un logement.

**À ce stade, imprimer les gabarits seulement.** Leurs résultats permettront d’ajuster les logements et les fixations avant une impression complète.

## Organisation du pack

| Élément | Utilisation |
|---|---|
| `stl/gabarits/` | Six gabarits de servos, avec trois jeux différents, et un gabarit de logements de roulements |
| `stl/structure/` | Dix pièces d’armature et de pince, nommées S01 à S10 |
| `stl/coques/` | Dix-huit pièces de carrosserie démontable, caches et bagues |
| `sources/orbite_v0.scad` | Source CAO modifiable dans OpenSCAD ; choix d’une pièce avec la variable `piece` |
| `sources/parametres.json` | Dimensions nominales et hypothèses de conception |
| `liste_pieces.csv` | Liste des pièces et de leurs dimensions d’impression |
| `assemblage_visuel.glb` | Assemblage coloré pour un logiciel de visualisation 3D |
| `assemblage_visuel_NE_PAS_IMPRIMER.stl` | Vue d’ensemble figée, avec références des moteurs ; ce fichier n’est pas un plateau d’impression |
| `verification_export.json` | Contrôle des fichiers STL relus après export |
| `calcul_statique_preliminaire.json` | Estimation de l’effort gravitaire, avec ses limites |

La vue éclatée aide à identifier les sous-ensembles ; l’écartement des pièces est illustratif. Les couleurs sont indicatives. Il n’est pas nécessaire d’avoir un AMS : chaque pièce peut être imprimée dans une seule couleur.

## Architecture et ordre de montage envisagé

| Sous-ensemble | Pièces principales | Moteur / support |
|---|---|---|
| Socle et rotation | S01, S02, S03, S04 | M1 MG996R, roulement 608ZZ et liaison centrale M4 |
| Épaule | S04 → S05 | M2 MG996R ; appui opposé par 624ZZ et axe M4 |
| Coude | S05 → S06 | M3 MG996R ; appui opposé par 624ZZ et axe M4 |
| Inclinaison du poignet | S06 → S07 | M4 MG90S ; appui opposé par 623ZZ et axe M3 |
| Rotation du poignet | S07 → S08 | M5 MG90S et palonnier fourni |
| Pince | S08, S09, S10 | M6 MG90S ; doigt entraîné sur 623ZZ et axe M3 |

Les axes moteurs restent ceux des servos. Les pièces imprimées se fixent sur les **palonniers d’origine** ; aucune cannelure de servo n’est imprimée. Les trous des adaptations sont oblongs pour permettre un ajustement, mais la compatibilité des palonniers reste à confirmer avec la référence exacte achetée.

Pour la base, le logement d’écrou M4 de S03 s’ouvre par dessous : monter d’abord le palonnier d’origine sur le servo, insérer l’écrou dans S03, puis fixer S03 au palonnier par ses lumières. Le roulement et le support supérieur se montent ensuite, avant la tourelle. Les deux méplats du petit arbre transmettent la rotation à la tourelle ; la vis centrale retient cet ensemble.

Pour les pivots opposés aux moteurs, les rondelles de calage doivent appuyer sur la **bague intérieure** du roulement. Le serrage ne doit pas immobiliser la bague extérieure ou la pièce mobile. Les longueurs de vis et les empilements de rondelles sont à mesurer au montage.

Les demi-coques comportent des oreilles de jonction pour des vis M2 et des logements d’écrous. Ces oreilles ferment les deux moitiés ; leur rétention autour de l’armature, les ajustements et l’accès aux câbles doivent être essayés avant de les serrer définitivement. Les caches ronds ont leurs propres petits perçages. Les bagues sombres sont décoratives.

## Quincaillerie à prévoir après validation des gabarits

- 1 roulement **608ZZ : 8 × 22 × 7 mm** pour la base.
- 2 roulements **624ZZ : 4 × 13 × 5 mm** pour l’épaule et le coude.
- 2 roulements **623ZZ : 3 × 10 × 4 mm** pour le poignet et le doigt entraîné.
- Vis, écrous et rondelles **M2** pour les petits servos, les adaptations et les demi-coques ; prévoir plusieurs longueurs, à confirmer sur le montage réel.
- Vis, écrous et rondelles **M3** pour les gros servos, le support supérieur et les petits pivots ; écrous frein aux endroits mobiles si l’empilement le permet.
- Vis, écrous et rondelles **M4** pour le couplage de base et les pivots principaux.
- Les palonniers, leurs vis centrales spécifiques et les accessoires fournis avec les six servos.
- Une planche pour fixer le socle et de petits colliers pour retenir les câbles sans gêner les articulations.

Ne pas commander un lot de vis basé sur des longueurs supposées : les palonniers réels et le montage des roulements peuvent modifier les empilements. Le gabarit de roulements permet de vérifier leurs logements nominaux avant d’imprimer l’armature.

## Impression des sous-ensembles après ajustement

Les STL individuels sont posés à Z = 0 et orientés pour proposer une face de départ. Certaines fourches et certains berceaux présentent néanmoins des porte-à-faux : leur orientation et leurs supports doivent être vérifiés dans Bambu Studio. La compatibilité dimensionnelle avec le plateau ne constitue pas une validation du tranchage.

Pour les premiers essais, un point de départ est : PLA, buse de 0,4 mm, couches de 0,20 mm, quatre à cinq parois et 30–40 % de remplissage pour l’armature. Les coques sont déjà creuses, avec environ 2,2 mm de paroi nominale et des renforcements locaux. Les dents de pince demandent une impression propre et un retrait soigneux des bavures. Imprimer et contrôler un sous-ensemble avant le suivant.

## Charge et mouvements : ce qui reste à vérifier

Une estimation gravitaire a été faite avec un objet théorique de **20 g**, la masse des servos, une marge pour la quincaillerie et les pièces imprimées supposées en PLA plein de densité 1,24 g/cm³. Cette hypothèse ne prédit pas la masse d’une impression à 40 % de remplissage.

L’effort estimé à l’épaule est d’environ **2,5 kgf·cm dans la pose de présentation**, et **4,75 kgf·cm dans une pose entièrement horizontale**. Ce ne sont pas des charges admissibles : le couple de blocage annoncé pour un servo ne définit pas son couple continu. L’accélération, l’échauffement, les frottements, la flexion, le fluage et les efforts de pince ne sont pas validés.

Deux points d’ancrage sont prévus pour étudier une compensation de l’épaule. Le ressort ou l’élastique, sa force et son débattement restent à dimensionner ; aucun ressort précis n’est prescrit. Les premiers essais motorisés devront se faire sans charge, avec le bras soutenu, progressivement. La pose horizontale doit être étudiée avant un maintien prolongé.

Le contrôle d’interférences porte uniquement sur la pose de présentation et sur les enveloppes nominales modélisées, sans toutes les vis, tous les palonniers ou les câbles. La trajectoire complète des articulations reste à vérifier et à limiter. L’objectif est d’obtenir un prototype ajustable, pas de considérer les réglages d’aperçu comme des consignes moteur prêtes à utiliser.

## Références dimensionnelles

- [A1 mini — guide Bambu Lab, volume 180 × 180 × 180 mm](https://cdn1.bambulab.com/documentation/quick-start-f507128172bdf/Quick%20start%20guide%20-%20A1%20mini-EN.pdf)
- [MG996R — fiche TowerPro](https://towerpro.com.tw/product/mg996R/)
- [MG90S — fiche Waveshare](https://www.waveshare.com/mg90s-servo.htm)

Les variantes et les produits génériques peuvent avoir des cotes différentes : les mesures des exemplaires reçus priment sur ces valeurs nominales.
