// Rendu déterministe de stage.html → vidéo (image par image, 30 i/s).
// Usage : node render/render.mjs <sortie.mp4> [fps] [début] [fin]
import { chromium } from "playwright";
import { spawn } from "node:child_process";
import http from "node:http";
import fs from "node:fs";
import path from "node:path";

const root = path.dirname(new URL(import.meta.url).pathname);
const [out = "out/video.mp4", fpsArg = "30", fromArg, toArg] = process.argv.slice(2);
const fps = +fpsArg;

const types = { ".html": "text/html", ".js": "text/javascript", ".png": "image/png", ".jpg": "image/jpeg", ".svg": "image/svg+xml", ".mp4": "video/mp4", ".json": "application/json" };
const server = http.createServer((req, res) => {
  const p = path.join(root, "..", decodeURIComponent(req.url.split("?")[0]));
  fs.readFile(p, (e, b) => e ? (res.writeHead(404), res.end()) : (res.writeHead(200, { "content-type": types[path.extname(p)] || "application/octet-stream" }), res.end(b)));
}).listen(0);
const port = server.address().port;

const browser = await chromium.launch({ });
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
page.on("pageerror", e => console.error("pageerror", e));
await page.goto(`http://localhost:${port}/render/stage.html`);
await page.waitForFunction(() => window.READY === true);
await page.evaluate(() => document.fonts.ready);
const duration = await page.evaluate(() => window.DURATION);
const t0 = fromArg ? +fromArg : 0, t1 = toArg ? +toArg : duration;
const n = Math.round((t1 - t0) * fps);

const ff = spawn("ffmpeg", ["-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", String(fps), "-c:v", "mjpeg", "-i", "-",
  "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out], { stdio: ["pipe", "inherit", "inherit"] });

const cdp = await page.context().newCDPSession(page);
for (let i = 0; i < n; i++){
  await page.evaluate(t => { window.seek(t); return Promise.all([...document.querySelectorAll("img.plan")].map(im => im.decode().catch(() => {}))); }, t0 + i / fps);
  const { data } = await cdp.send("Page.captureScreenshot", { format: "jpeg", quality: 92 });
  if (!ff.stdin.write(Buffer.from(data, "base64"))) await new Promise(r => ff.stdin.once("drain", r));
  if (i % 150 === 0) console.log(`frame ${i}/${n}`);
}
ff.stdin.end();
await new Promise(r => ff.on("close", r));
await browser.close(); server.close();
console.log("ok", out);
