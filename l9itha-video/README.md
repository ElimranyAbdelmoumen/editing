# L9ITHA.Club : vidéo promotionnelle (90 s, 16:9 Full HD)

Animatique v0 : rythme, animations, transitions, typographie, effets sonores et
sous-titres sont en place. Les captures de la plateforme, les plans tournés, le
logo et la voix off sont remplacés par des **emplacements de montage
identifiés** (`C…` = capture réelle, `V…` = plan vidéo).

## Fichiers

| Fichier | Rôle |
|---|---|
| `render/cues.js` | Timings des scènes + texte de la voix off et sous-titres FR/EN (source unique) |
| `render/stage.html` | Toute l'animation (une timeline déterministe, 1920×1080) |
| `render/render.mjs` | Rendu image par image → `out/animatique_sans_son.mp4` |
| `render/thumbnail.html` | Miniature 1280×720 |
| `audio/make_audio.py` | Musique provisoire + effets sonores synchronisés |
| `subtitles/` | `fr.srt`, `en.srt`, `fr.ass`, `en.ass` (générés) |
| `build.sh` | Assemblage final : mixage (ducking sous la voix), sous-titres incrustés |

```bash
npm install && ./build.sh
```

## Livrables générés (`out/`, non versionnés)

- `L9ITHA_Club_90s.mp4` : version principale, sans sous-titres
- `L9ITHA_Club_90s_soustitres_fr.mp4` : sous-titres français incrustés
- `L9ITHA_Club_90s_soustitres_en.mp4` : sous-titres anglais incrustés
- `miniature.png` : « Apprendre Python, créer ses premières idées »

## Éléments à fournir

### Logo
- `assets/logo/` : logo officiel en **SVG ou PNG transparent** (version claire + version sur fond sombre). Il sera intégré tel quel, sans être redessiné.

### Captures réelles de la plateforme (comptes et noms fictifs)
Une image `assets/captures/<ID>.png` remplace automatiquement l'emplacement
correspondant (recadrée aux proportions de l'emplacement, remplissage en bas
avec la couleur de la page). **Déjà intégrées** : C2-01, C2-02 (nom d'élève
remplacé par « Yassine Alami »), C6-01, C6-02, C6-04, C6-05.
Format conseillé pour les autres : capture 1920×1080, navigateur plein écran,
noms d'élèves fictifs.

| ID | Moment | Contenu |
|---|---|---|
| C2-01 | 11,4 s | Accueil élève (thème clair) |
| C2-02 | 14,8 s | L'élève ouvre une séance |
| C3-01 | 18,4 s | Activités Junior : frappe, quiz, réflexes |
| C3-02 | 19,4 s | Activités Pro : programmes à compléter ou à réparer |
| C4-01 | 30,0 s | Consigne d'un exercice |
| C4-02 | 32,0 s | Saisie de `print("Bonjour !")` |
| C4-03 | 33,4 s | Clic sur Exécuter : la console affiche `Bonjour !` |
| C4-04 | 34,6 s | Vrai message d'erreur et indice en français |
| C4-05 | 37,2 s | Correction du code |
| C4-06 | 39,6 s | Soumettre : résultats des tests et points |
| C4-07 | 42,2 s | Dessin Turtle |
| C4-08 | 44,6 s | Reprise du travail sauvegardé |
| C6-01 | 60,0 s | Prof : choix du groupe et de la séance |
| C6-02 | 62,4 s | Prof : cartes des séances |
| C6-03 | 64,4 s | Prof : présentation d'un support |
| C6-04 | 67,4 s | Prof : déblocage des exercices, code de présence |
| C6-05 | 70,0 s | Prof : tableau de suivi (présences, progression, résultats, détail des essais) |
| C6-06 | 73,8 s | Admin (bref) : import Excel, tickets de connexion |
| C7-01 | 76,2 s | Quiz terminé |
| C7-02 | 76,6 s | Programme qui fonctionne |

### Plans tournés en salle informatique
| ID | Moment | Contenu |
|---|---|---|
| V1-01 | 0–8 s | Un élève tape du Python, un dessin coloré apparaît ; un camarade observe ; échange avec le professeur |
| V5-01 | 48–53,5 s | Le professeur échange avec un élève devant l'écran |
| V5-02 | 53,5–60 s | L'élève explique son programme à un parent |
| V7-01 | 77,3 s | Échange entre élèves et professeur |

Filles et garçons de 11 à 17 ans, établissement marocain. **Autorisations
parentales de droit à l'image indispensables** pour les mineurs filmés.

**Version actuelle : plans générés par IA** (Kling 3.0 Pro, 1080p, sans son),
listés dans `assets/higgsfield.tsv` et téléchargés en `assets/plans/<ID>.mp4`.
Les personnes sont fictives. Pour passer aux vrais plans tournés, remplacer le
fichier `assets/plans/<ID>.mp4` correspondant : `./build.sh` le découpe en
images (`frames/<ID>/`) et l'intègre à l'emplacement, sous les titres animés.

### Voix off
**Voix off : « Julian »** (voix masculine professionnelle ElevenLabs, via
Higgsfield), choisie parmi trois essais. Aucune autre voix de remplacement. `audio/make_voice.py` (voix « tom » de Piper) ne sert plus
qu'aux essais manuels. Le nom se prononce « Lqitha
Club ». Les sous-titres sont recalés automatiquement sur les pauses de la voix
(`render/subs_timed.json`).

**Voix « Julian »** : une prise par scène du texte ci-dessous. Les liens sont dans
`assets/higgsfield.tsv` ; `./build.sh` télécharge les fichiers manquants dans
`assets/voix/scenes/`, puis `audio/place_voice.py` retire les silences, garde
pour chaque scène la prise la plus posée qui tient dans sa fenêtre (×1,15 max,
sans changer la hauteur), la cale et recale les sous-titres FR/EN sur les
pauses réelles. Prérequis : autoriser `d8j0ntlcm91z4.cloudfront.net` dans le
réseau de l'environnement.

Une prise libre enregistrée soi-même fonctionne aussi : la découper par scène
et la déposer de la même façon.

Texte de lecture :
Lire chaque ligne dans sa fenêtre de temps (une prise libre fonctionne aussi :
elle sera découpée et calée) :

| Fenêtre | Texte |
|---|---|
| 0,6 – 7,4 | Et si quelques lignes de code devenaient le début d'une nouvelle passion ? |
| 8,6 – 17,6 | Avec L9ITHA.Club, les élèves découvrent la programmation Python dans un club informatique structuré, avec des activités progressives et l'accompagnement de leur professeur. |
| 18,5 – 29,8 | Deux parcours, Junior et Pro, proposent une progression adaptée à l'âge. On s'échauffe, on s'entraîne avec de l'aide, on pratique, puis on relève un défi. |
| 30,5 – 47,4 | L'élève écrit son code, l'exécute et observe le résultat. Des indices et des messages en français l'aident à comprendre ses erreurs. Il corrige, recommence et avance. Son travail est sauvegardé pour la prochaine séance. |
| 48,5 – 59,6 | Pour les parents, c'est une activité encadrée pour développer la logique, encourager la créativité et apprendre à persévérer face à un problème. |
| 60,5 – 75,6 | Pour les écoles, la plateforme rassemble l'organisation du club, les supports et les exercices. Le professeur présente la séance, ouvre les activités et retrouve les présences, les progrès et les résultats de ses élèves. |
| 76,4 – 83,8 | Des premiers essais aux défis de programmation, chaque séance invite les élèves à comprendre le code et à donner forme à leurs idées. |
| 84,4 – 89,6 | Découvrez L9ITHA.Club. Pour rejoindre le club ou demander une démonstration, contactez-nous. |

Conseils d'enregistrement : pièce calme et meublée (pas de salle de bain ni de
pièce vide), téléphone à 20 cm, légèrement de côté, débit posé et souriant.

### Musique
La piste actuelle est une maquette synthétisée. Pour la version finale, il
faut une piste instrumentale libre de droits (Artlist, Epidemic Sound ou
YouTube Audio Library), positive, autour de 100 BPM.

## Cohérence vérifiée
- Le code affiché à 0–4 s produit exactement le dessin animé ensuite (36
  segments de 220 px, rotation de 170°, couleurs nommées de Turtle : indigo,
  green, royalblue, orange).
- Code tapé à l'écran (habillage animé, distinct de l'interface réelle) :
  - Junior : `print("Salut !")` → `Salut !`
  - Pro : `def carre(n): return n * n` puis `print(carre(7))` → `49`
  - Atelier : `print("Bonjour !")` → `Bonjour !`
  - Correction : `for i in range(3)` sans « : » (cadre rouge, sans message
    inventé), ajout du « : », puis 3 × `Je progresse !`
- Aucun témoignage, aucune statistique, aucun partenaire extérieur (le logo et le nom de Madariss Ibn Mashish, l'école du club, apparaissent dans les captures avec son accord), aucun espace parent,
  aucun terme technique (Docker, API, Judge0, Pyodide).
