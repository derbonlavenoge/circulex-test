# Vidéo 120 s – « L'alcool dans ton corps » : script de la voix off

Public : ado de 16 ans. Tutoiement, ton factuel, sans morale.
Voix : **Enrick** (narrateur, ElevenLabs, modèle eleven_v4) et **Alicia** (questions d'ado).
Les fichiers audio sont débarrassés des silences de début et de fin, puis accélérés de 5 % (narrateur) ou 10 % (ado).

## Contraintes
- Narrateur : voix **Enrick**. Jamais de voix à accent africain.
- Français de Suisse : **septante** (70), **huitante** (80), **nonante** (90) et leurs composés (septante-cinq…), jamais « soixante-dix », « quatre-vingts », « quatre-vingt-dix ».

Minutages réels : voir `timeline.js` (début et durée de chaque réplique après traitement).

| #  | Scène | Début (s) | Voix | Texte |
|----|-------|-----------|------|-------|
| 1  | Intro : le même verre | 1,6 | Ado | Pourquoi le même verre ne fait pas le même effet à tout le monde ? |
| 2  | C'est une concentration | 4,3 | Narr. | L'alcool se répartit dans toute l'eau de ton corps. Le taux, c'est une concentration : même dose dans moins d'eau, taux plus haut. |
| 3  | L'eau vs la graisse | 11,5 | Narr. | Un muscle, c'est environ 75 % d'eau. La graisse, seulement 10 à 20 %. Et l'alcool va dans l'eau, pas dans la graisse. |
| 4  | Homme / femme à poids égal | 19,5 | Narr. | Deux personnes de 70 kilos. En moyenne, l'homme a plus de muscles : environ 60 % d'eau. La femme, plus de graisse : environ 50 %. Même verre, moins d'eau : taux plus haut. |
| 5  | | 30,9 | Ado | Attends… donc les filles tiennent moins l'alcool ? |
| 6  | | 33,4 | Narr. | Non. Ça n'a rien à voir avec « tenir l'alcool ». C'est une moyenne, pas une règle : juste une question d'eau dans le corps. |
| 7  | Ce qui fait monter le taux | 39,7 | Narr. | Le taux monte aussi plus haut si tu pèses moins, as moins de muscles, bois à jeun ou bois vite. À 16 ans, on pèse souvent moins qu'un adulte : même verre, taux plus haut. |
| 8  | Le trajet | 49,2 | Narr. | De l'estomac et de l'intestin, l'alcool passe dans le sang, qui l'emmène partout, jusqu'au cerveau. À 16 ans, ton cerveau se développe encore, jusqu'à 25 ans environ : il est plus sensible. |
| 9  | | 59,4 | Narr. | Ensuite, le foie en élimine plus de 90 %. Le reste sort par le souffle, l'urine et la sueur. |
| 10 | Le foie en 3 étapes | 65,9 | Narr. | Dans le foie, deux enzymes, des petits outils, font le travail. L'ADH change l'alcool en acétaldéhyde, toxique. L'ALDH le change en acétate, qui finit en eau et en gaz carbonique. |
| 11 | Vitesse fixe | 77,7 | Narr. | Le foie va à vitesse fixe : −0,1 à 0,15 ‰ par heure. De 0,5 ‰ à zéro : environ 3 à 5 heures. |
| 12 | Rien n'accélère | 87,2 | Ado | Et un café, ça n'aide pas ? |
| 13 | | 88,8 | Narr. | Non. Ni café, ni douche froide, ni eau, ni air frais, ni sport. Rien n'accélère le foie. Seul le temps. |
| 14 | Le pic | 96,5 | Narr. | Et le taux monte encore après le dernier verre : le pic arrive 30 à 60 minutes plus tard. Te sentir bien juste après ne veut pas dire qu'il a fini de monter. |
| 15 | À retenir | 105,3 | Narr. | À retenir : c'est une concentration. Moins d'eau, taux plus haut. Le pic vient après. Le foie va à vitesse fixe. Seul le temps fait baisser le taux. |
| 16 | Fin | 114,8 | Narr. | Maintenant, tu sais comment ça marche. |

Pour la synthèse, les nombres ont été écrits en toutes lettres (ex. « zéro virgule quinze pour mille »)
« septante », « nonante » en toutes lettres, et les sigles épelés (« A.D.H. ») ; le texte exact envoyé est dans `video.html` (champ `sp` de `LINES`).

## Fabrication

```bash
# 1. voix : l01.wav … l16.wav (mono 44,1 kHz) dans un dossier vo/
# 2. images (3600 PNG) + liste des bruitages sfx.json
NODE_PATH=$(npm root -g) node render_frames.js frames 5
# 3. bande son (musique 120 BPM + bruitages + voix, ducking)
python3 audio.py vo frames/sfx.json mix.wav
# 4. assemblage
ffmpeg -framerate 30 -i frames/f%04d.png -i mix.wav -c:v libx264 -pix_fmt yuv420p -crf 18 \
       -c:a aac -b:a 192k -shortest alcool-120s.mp4
```

Le dossier `voix/` contient les fichiers MP3 bruts sortis d'ElevenLabs (avant découpe des silences et accélération).
