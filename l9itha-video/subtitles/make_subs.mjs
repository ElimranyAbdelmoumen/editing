// Génère subtitles/{fr,en}.srt et .ass à partir de render/cues.js
import { SUBS } from "../render/cues.js";
import fs from "node:fs";
const dir = new URL(".", import.meta.url).pathname;
// Si la voix off a été générée, on reprend ses timings réels.
const timedPath = dir + "../render/subs_timed.json";
if (fs.existsSync(timedPath)) JSON.parse(fs.readFileSync(timedPath, "utf8")).forEach((t, i) => { if (t) { SUBS[i] = [...SUBS[i]]; SUBS[i][0] = t[0]; SUBS[i][1] = t[1]; } });
const srtT = s => { const ms = Math.round(s * 1000), h = ms / 3600000 | 0, m = ms / 60000 % 60 | 0, sec = ms / 1000 % 60 | 0;
  return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}:${String(sec).padStart(2, "0")},${String(ms % 1000).padStart(3, "0")}`; };
const assT = s => { const cs = Math.round(s * 100); return `${cs / 360000 | 0}:${String(cs / 6000 % 60 | 0).padStart(2, "0")}:${String(cs / 100 % 60 | 0).padStart(2, "0")}.${String(cs % 100).padStart(2, "0")}`; };
const head = `[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Inter SemiBold,46,&H00FFFFFF,&H00FFFFFF,&H00000000,&H9A13224A,0,0,0,0,100,100,0,0,3,14,0,2,200,200,46,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
`;
for (const [lang, col] of [["fr", 2], ["en", 3]]) {
  fs.writeFileSync(dir + lang + ".srt", SUBS.map((c, i) => `${i + 1}\n${srtT(c[0])} --> ${srtT(c[1])}\n${c[col]}\n`).join("\n"));
  fs.writeFileSync(dir + lang + ".ass", head + SUBS.map(c => `Dialogue: 0,${assT(c[0])},${assT(c[1])},Sub,,0,0,0,,{\\fad(120,120)}${c[col].replace(/\n/g, "\\N")}`).join("\n") + "\n");
}
console.log("ok");
