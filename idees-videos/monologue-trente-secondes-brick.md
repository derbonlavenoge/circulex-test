# Monologue « Trente secondes » (voix Brick, ElevenLabs)

**Usage :** ouverture de la vidéo sur la présélection (on enchaîne ensuite sur l'accroche « Ce matin, j'ai découvert que plein de gens vont à Crissier… »), ou format court autonome.

**Voix :** Brick – Voix professionnelle, calme (ElevenLabs), modèle eleven_v4. Les mots entre crochets sont des indications de jeu pour ElevenLabs : ils ne sont pas prononcés.

**Durée :** environ 2 min (deux prises générées : 1 min 58 et 2 min 01).

---

## Texte (tel qu'envoyé à ElevenLabs)

```text
[softly] 6 h 30. Il pleut.
Une pluie d'automne, fine, patiente. Comme moi.

Le café fume dans le porte-gobelet. La radio parle doucement. Les essuie-glaces vont et viennent… gauche, droite. Gauche, droite.

J'arrive à l'entrée de l'autoroute. Ma voie est pleine : une longue file de feux arrière qui brillent sous la pluie. Je me mets au bout. J'ai le temps. Le matin, j'ai toujours un peu de temps. C'est mon luxe.

Sur la voie de droite, celle qui va à Crissier, ça roule.

[pause] Une voiture remonte la file, par la droite. Elle avance, elle avance… et au dernier moment, clignoteur. Elle se glisse devant moi.
[sighs] Bon. Il ne connaît peut-être pas le coin. Ça arrive.

[pause] Une deuxième. Même trajectoire. Même clignoteur de dernière seconde.
[frustrated sigh] Une troisième.

Le feu passe au vert. Trois voitures passent. Deux d'entre elles n'étaient même pas dans la file il y a une minute.
Rouge.

[nervous] Une quatrième.
Mes mains se serrent sur le volant. Les essuie-glaces battent toujours la mesure… mais mon cœur, lui, est passé en vitesse rapide.

[angry] Je pourrais klaxonner. Il ne m'entendra pas. Ou il rira.
Je pourrais coller la voiture de devant, ne laisser aucune place… et finir dans sa portière, pour avoir eu raison.
Je pourrais lui parler. À travers deux vitres… et la pluie.

[long pause] [softly] Imaginez la caisse du supermarché, un samedi matin.
Vous avez votre panier. Vous avez pris votre place. Et quelqu'un arrive par l'allée d'à côté… et pose ses courses sur le tapis, juste devant les vôtres.
[sarcastic] « Oh, pardon… je ne vous avais pas vu. »
[softly] Ça n'arrive presque jamais. Parce que toute la file se retournerait. Parce que quelqu'un dirait : « Monsieur, la file commence là-bas. » Et il irait au bout, les joues rouges.

[pause] Mais ici, il y a une vitre. De la pluie. Un clignoteur.
Pas de regard. Pas de honte.
Juste des feux arrière qui s'éloignent.

[exhales] Alors je reste dans ma file. Pas parce que je suis naïf. Parce qu'une file, ça ne tient que si chacun y reste.

[softly] Les essuie-glaces ont repris leur rythme. Gauche, droite.
Le feu passe au vert. C'est mon tour.
Ce matin, mon tour m'a coûté huit minutes… et un peu de ma bonne humeur.
Eux, ils ont gagné trente secondes.

[long pause] Je me demande ce qu'ils en font.
```

---

## La métaphore : la caisse du supermarché

Au supermarché, presque personne ne double la file : tout le monde se voit, et la honte suffit à faire respecter la règle. Au volant, la vitre, la pluie et l'anonymat suppriment le regard des autres. La métaphore explique donc à la fois pourquoi certains osent le faire en voiture et pourquoi celui qui attend se sent impuissant : il n'a ni regard ni parole pour réagir.

## Images suggérées

- **6 h 30** : tableau de bord dans le noir, café dans le porte-gobelet, pluie sur le pare-brise, essuie-glaces.
- **La file** : longue rangée de feux arrière rouges sous la pluie, à l'entrée de l'autoroute.
- **Les resquilleurs** : une voiture qui remonte par la droite, clignoteur au dernier moment.
- **La tension** : mains serrées sur le volant, essuie-glaces en vitesse rapide.
- **Le supermarché** : file à la caisse, quelqu'un qui pose ses courses sur le tapis devant les autres, regards qui se tournent.
- **Retour en voiture** : feux arrière qui s'éloignent, feu qui passe au vert.
- **Son** : deux boucles générées dans le même projet ElevenLabs que la voix. « Pluie sur la voiture » (15 s) et « Essuie-glaces lents » (10 s), quatre variations chacune, à répéter sous la voix au montage.

## Mixage

- **Fichier :** `trente-secondes-mix.mp3`, 2 min 04, MP3 320 kbit/s (envoyé dans la conversation).
- **Éléments :** voix Brick prise 1, pluie variation 1, essuie-glaces variation 1.
- **Réglages :** 2 s d'ambiance seule avant la voix et 4 s après. Pluie 12 dB et essuie-glaces 16 dB sous la voix, avec atténuation automatique : l'ambiance baisse quand la voix parle et remonte dans les silences. Fondus d'entrée et de sortie. Niveau final −16 LUFS, crête −1,7 dBFS.

## Vidéo

- **Fichier :** `trente-secondes.mp4`, 2 min 04, 16:9 en 1080p à 30 images/s, sous-titres incrustés (envoyé dans la conversation).
- **Images :** 12 images générées par IA (ElevenLabs, GPT Image 2.5, 4 variantes par plan, 9 120 crédits), animées par des mouvements de caméra lents. Version 2 : plans A, D, E et H refaits avec un décor suisse (Léman, Alpes, banlieue lausannoise), 3 040 crédits.
- **Montage :** fondus enchaînés calés sur la narration, coupe sèche sur « Rouge. », fondu au noir pour entrer dans la scène du supermarché et en sortir, fondu au noir final.
- **Sous-titres :** calés au mot près sur la voix, grâce à une transcription horodatée.
- **Fichiers de travail :** les scripts de mixage, de sous-titres et de montage sont dans `outils/`. Le minutage, les identifiants ElevenLabs des images retenues et les sous-titres (`.ass` et `.srt`) sont dans `outils/trente-secondes/`.

| Temps | Image | Moment |
|---|---|---|
| 0:00 | A – Habitacle sous la pluie | 6 h 30, il pleut, le café |
| 0:11 | B – Essuie-glaces | Gauche, droite |
| 0:16 | C – File de feux arrière | Ma voie est pleine |
| 0:26 | D – Voiture sur la voie de droite | Elle se glisse devant moi |
| 0:37 | A | Bon. Ça arrive. |
| 0:41 | D | Une deuxième, une troisième |
| 0:47 | E – Feu vert | Le feu passe au vert |
| 0:52 | F – Mains crispées | Rouge. (coupe sèche) |
| 0:59 | G – Conducteur tendu | Je pourrais klaxonner… |
| 1:08 | H – Deux vitres | À travers deux vitres… et la pluie |
| 1:12 | I – File à la caisse | Imaginez la caisse du supermarché |
| 1:17 | J – Celui qui passe devant | « Oh, pardon… » |
| 1:24 | J | Toute la file se retournerait |
| 1:32 | K – Feux arrière qui s'éloignent | Pas de regard. Pas de honte. |
| 1:40 | A | Je reste dans ma file |
| 1:46 | B | Les essuie-glaces ont repris leur rythme |
| 1:50 | E | C'est mon tour |
| 1:52 | L – Autoroute à l'aube | Trente secondes |
