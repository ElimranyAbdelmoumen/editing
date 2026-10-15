#!/usr/bin/env bash
# Version « story » 9:16 : timeline + audio, rendu image par image, assemblage.
# Prérequis : ceux de ../build.sh (npm install, python3 + numpy, ffmpeg) ;
# faster-whisper seulement si story/words.json est absent.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p story/out
python3 story/make_story.py
STAGE=story/stage.html node render/render.mjs story/out/story_sans_son.mp4 30
ffmpeg -y -loglevel error -i story/out/story_sans_son.mp4 -i story/out/mix.wav -map 0:v -map 1:a \
  -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart story/out/L9ITHA_Club_story_9x16.mp4
echo "Story prête : story/out/L9ITHA_Club_story_9x16.mp4"
