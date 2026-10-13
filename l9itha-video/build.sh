#!/usr/bin/env bash
# Assemble la vidéo : image + musique + effets (+ voix off si présente) + sous-titres.
# Prérequis : npm install ; python3 avec numpy ; ffmpeg.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p out

[ -f out/animatique_sans_son.mp4 ] || node render/render.mjs out/animatique_sans_son.mp4 30
python3 audio/make_audio.py
[ -f assets/voix/voix_off.wav ] || python3 audio/make_voice.py
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
