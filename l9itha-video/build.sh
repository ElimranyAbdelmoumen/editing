#!/usr/bin/env bash
# Assemble la vidéo : image + musique + effets (+ voix off si présente) + sous-titres.
# Prérequis : npm install ; python3 avec numpy ; ffmpeg.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p out

# Récupère les voix et plans générés sur Higgsfield qui manquent encore.
grep -v '^#' assets/higgsfield.tsv | while IFS=$'\t' read -r DEST URL; do
  [ -z "$DEST" ] || [ -f "$DEST" ] || { mkdir -p "$(dirname "$DEST")"; curl -fsSL -o "$DEST.part" "$URL" && mv "$DEST.part" "$DEST" \
    || { rm -f "$DEST.part"; echo "⚠ Téléchargement impossible : $DEST (domaine autorisé dans le réseau ?)" >&2; }; }
done

# Plans tournés ou générés : assets/plans/<ID>.mp4 → images 1920×1080 à 30 i/s (frames/<ID>/).
for P in assets/plans/*.mp4; do
  [ -e "$P" ] || continue
  ID=$(basename "$P" .mp4); D=frames/$ID
  if [ ! -f "$D/index.json" ] || [ "$P" -nt "$D/index.json" ]; then
    rm -rf "$D"; mkdir -p "$D"
    ffmpeg -y -loglevel error -i "$P" -an -vf "fps=30,scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080" -q:v 3 "$D/%04d.jpg"
    echo "{\"n\": $(ls "$D" | wc -l), \"fps\": 30}" > "$D/index.json"
  fi
done
A=out/animatique_sans_son.mp4
if [ ! -f $A ] || [ -n "$(find render/stage.html render/cues.js frames assets/captures assets/logo -newer $A -type f 2>/dev/null | head -1)" ]; then
  node render/render.mjs $A 30
fi
python3 audio/make_audio.py
# Voix off : uniquement la voix clonée (prises par scène). Pas de voix de synthèse de remplacement.
if compgen -G "assets/voix/scenes/scene_*" > /dev/null; then python3 audio/place_voice.py
else rm -f assets/voix/voix_off.wav; echo "⚠ Prises de la voix clonée absentes : vidéo sans voix off." >&2; fi
node subtitles/make_subs.mjs

VO=assets/voix/voix_off.wav   # voix off calée sur la timeline (90 s)
if [ -f "$VO" ]; then
  # La musique baisse automatiquement quand la voix parle (sidechain).
  ffmpeg -y -loglevel error -i audio/music.wav -i audio/sfx.wav -i "$VO" -filter_complex \
    "[2:a]aresample=44100,highpass=f=70,equalizer=f=180:t=q:w=1:g=2,equalizer=f=3500:t=q:w=1.2:g=2.5,acompressor=threshold=0.1:ratio=3:attack=10:release=150,aecho=0.8:0.5:40:0.08,aformat=channel_layouts=stereo,loudnorm=I=-16:TP=-1.5,asplit[vo][key];\
     [0:a]volume=0.55[m];[m][key]sidechaincompress=threshold=0.03:ratio=8:attack=30:release=400[md];\
     [1:a]volume=0.8[fx];[md][fx][vo]amix=inputs=3:normalize=0,alimiter=limit=0.95[a]" \
    -map "[a]" -c:a pcm_s16le out/mix.wav
else
  ffmpeg -y -loglevel error -i audio/music.wav -i audio/sfx.wav -filter_complex \
    "[0:a]volume=0.8[m];[1:a]volume=0.8[fx];[m][fx]amix=inputs=2:normalize=0,alimiter=limit=0.95[a]" \
    -map "[a]" -c:a pcm_s16le out/mix.wav
fi

ffmpeg -y -loglevel error -i out/animatique_sans_son.mp4 -i out/mix.wav -map 0:v -map 1:a \
  -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart out/L9ITHA_Club_90s.mp4
for L in fr en; do
  ffmpeg -y -loglevel error -i out/L9ITHA_Club_90s.mp4 -vf "ass=subtitles/$L.ass" \
    -c:v libx264 -crf 18 -preset medium -pix_fmt yuv420p -c:a copy -movflags +faststart out/L9ITHA_Club_90s_soustitres_$L.mp4
done
echo "Vidéos prêtes dans out/"
