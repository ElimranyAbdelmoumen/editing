// Source unique des timings : voix off, sous-titres FR/EN et emplacements de montage.
// Les temps sont en secondes depuis le début de la vidéo (90 s).

export const SCENES = [
  { id: 1, t0: 0, t1: 8, name: "Éveiller la curiosité" },
  { id: 2, t0: 8, t1: 18, name: "Présenter la plateforme" },
  { id: 3, t0: 18, t1: 30, name: "Les deux parcours" },
  { id: 4, t0: 30, t1: 48, name: "Montrer l'apprentissage" },
  { id: 5, t0: 48, t1: 60, name: "Parler aux parents" },
  { id: 6, t0: 60, t1: 76, name: "Parler aux écoles" },
  { id: 7, t0: 76, t1: 84, name: "Donner envie" },
  { id: 8, t0: 84, t1: 90, name: "Appel à l'action" },
];

// [début, fin, français, anglais] — "\n" = retour à la ligne du sous-titre.
export const SUBS = [
  [0.6, 3.6, "Et si quelques lignes de code", "What if a few lines of code"],
  [3.6, 7.4, "devenaient le début d'une nouvelle passion ?", "became the start of a new passion?"],

  [8.6, 11.6, "Avec L9ITHA.Club, les élèves découvrent\nla programmation Python", "With L9ITHA.Club, students discover\nPython programming"],
  [11.6, 14.6, "dans un club informatique structuré,\navec des activités progressives", "in a structured computer club,\nwith step-by-step activities"],
  [14.6, 17.6, "et l'accompagnement de leur professeur.", "and the support of their teacher."],

  [18.5, 21.8, "Deux parcours, Junior et Pro,", "Two tracks, Junior and Pro,"],
  [21.8, 24.8, "proposent une progression adaptée à l'âge.", "offer a progression suited to each age."],
  [24.8, 27.4, "On s'échauffe, on s'entraîne avec de l'aide,", "We warm up, practise with guidance,"],
  [27.4, 29.8, "on pratique, puis on relève un défi.", "practise on our own, then take on a challenge."],

  [30.5, 34.0, "L'élève écrit son code, l'exécute\net observe le résultat.", "Students write their code, run it\nand watch the result."],
  [34.0, 38.6, "Des indices et des messages en français\nl'aident à comprendre ses erreurs.", "Hints and messages in French\nhelp them understand their mistakes."],
  [38.6, 42.6, "Il corrige, recommence et avance.", "They fix it, try again and move forward."],
  [42.6, 47.4, "Son travail est sauvegardé\npour la prochaine séance.", "Their work is saved\nfor the next session."],

  [48.5, 52.0, "Pour les parents, c'est une activité encadrée", "For parents, it's a supervised activity"],
  [52.0, 55.6, "pour développer la logique,\nencourager la créativité", "to build logical thinking,\nencourage creativity"],
  [55.6, 59.6, "et apprendre à persévérer face à un problème.", "and learn to persevere when facing a problem."],

  [60.5, 64.4, "Pour les écoles, la plateforme rassemble\nl'organisation du club,", "For schools, the platform brings together\nthe club's organisation,"],
  [64.4, 67.4, "les supports et les exercices.", "the course materials and the exercises."],
  [67.4, 71.6, "Le professeur présente la séance,\nouvre les activités", "The teacher presents the session,\nopens the activities"],
  [71.6, 75.6, "et retrouve les présences, les progrès\net les résultats de ses élèves.", "and sees attendance, progress\nand results for every student."],

  [76.4, 79.6, "Des premiers essais aux défis de programmation,", "From first attempts to coding challenges,"],
  [79.6, 81.8, "chaque séance invite les élèves\nà comprendre le code", "every session invites students\nto understand code"],
  [81.8, 83.8, "et à donner forme à leurs idées.", "and to bring their ideas to life."],

  [84.4, 86.4, "Découvrez L9ITHA.Club.", "Discover L9ITHA.Club."],
  [86.4, 89.6, "Pour rejoindre le club ou demander\nune démonstration, contactez-nous.", "To join the club or request\na demo, get in touch."],
];
