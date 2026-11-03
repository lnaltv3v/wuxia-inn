#!/bin/bash
# 將 _work/wav_* 轉到 sfx/ bgm/（需已跑 gen_audio.py）
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
for f in "$ROOT/_work/wav_sfx"/*.wav; do
  [ -f "$f" ] || continue
  base=$(basename "$f" .wav)
  ffmpeg -y -i "$f" -c:a libvorbis -q:a 3 -ac 1 "$ROOT/sfx/${base}.ogg"
done
for f in "$ROOT/_work/wav_bgm"/*.wav; do
  [ -f "$f" ] || continue
  base=$(basename "$f" .wav)
  ffmpeg -y -i "$f" -c:a libvorbis -q:a 4 -ac 1 "$ROOT/bgm/${base}.ogg"
done
cp -f "$ROOT/bgm/bgm_inn_day.ogg" "$ROOT/bgm/bgm_inn.ogg"
echo "convert done"
