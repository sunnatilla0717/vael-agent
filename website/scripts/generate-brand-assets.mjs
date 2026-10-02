#!/usr/bin/env node
/**
 * Generate the VAEL brand assets shipped in website/static/img.
 *
 * The upstream repo shipped raster assets painted with the Hermes wordmark and
 * mascot. Rather than hand-editing binaries (or adding an image dependency),
 * this script draws the placeholder marks from the CyberAI palette and writes
 * them with Node's stdlib only (node:zlib for PNG deflate).
 *
 * Palette (docs/design-system.md): primary #D97757, accent #CC785C,
 * canvas #191410, paper #FBF7F1, ink #1F1B16.
 *
 * Regenerate with:
 *   node website/scripts/generate-brand-assets.mjs
 *
 * Outputs
 *   static/img/vael-mark.svg           navbar logo, light mode
 *   static/img/vael-mark-dark.svg      navbar logo, dark mode
 *   static/img/favicon.svg             modern browsers
 *   static/img/favicon-16x16.png
 *   static/img/favicon-32x32.png
 *   static/img/favicon.ico             legacy browsers
 *   static/img/apple-touch-icon.png    iOS home screen
 *   static/img/vael-agent-banner.png   1200x630 Open Graph / Twitter card
 *
 * The upstream mascot (logo.png / logo-dark.png) and the old
 * hermes-agent-banner.png are intentionally left on disk: they are upstream
 * marketing assets, and REBRANDING.md keeps upstream content until the merge
 * path is reviewed (see docs/open-items.md).
 */

import { deflateSync } from "node:zlib";
import { mkdirSync, writeFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const OUT = resolve(dirname(fileURLToPath(import.meta.url)), "..", "static", "img");

const PRIMARY = [0xd9, 0x77, 0x57];
const ACCENT = [0xcc, 0x78, 0x5c];
const CANVAS = [0x19, 0x14, 0x10];
const PAPER = [0xfb, 0xf7, 0xf1];
const INK = [0x1f, 0x1b, 0x16];
const WHITE = [0xff, 0xff, 0xff];

// ---------------------------------------------------------------------------
// Minimal PNG encoder (8-bit RGBA, no interlacing)
// ---------------------------------------------------------------------------

const CRC_TABLE = (() => {
  const table = new Int32Array(256);
  for (let n = 0; n < 256; n += 1) {
    let c = n;
    for (let k = 0; k < 8; k += 1) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    table[n] = c;
  }
  return table;
})();

function crc32(buf) {
  let c = 0xffffffff;
  for (const byte of buf) c = CRC_TABLE[(c ^ byte) & 0xff] ^ (c >>> 8);
  return (c ^ 0xffffffff) >>> 0;
}

function chunk(type, data) {
  const length = Buffer.alloc(4);
  length.writeUInt32BE(data.length, 0);
  const body = Buffer.concat([Buffer.from(type, "ascii"), data]);
  const crc = Buffer.alloc(4);
  crc.writeUInt32BE(crc32(body), 0);
  return Buffer.concat([length, body, crc]);
}

/** @param {Uint8Array} rgba length = width*height*4 */
function encodePng(width, height, rgba) {
  const raw = Buffer.alloc(height * (width * 4 + 1));
  for (let y = 0; y < height; y += 1) {
    raw[y * (width * 4 + 1)] = 0; // filter: none
    Buffer.from(rgba.buffer, rgba.byteOffset + y * width * 4, width * 4).copy(
      raw,
      y * (width * 4 + 1) + 1,
    );
  }
  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(width, 0);
  ihdr.writeUInt32BE(height, 4);
  ihdr[8] = 8; // bit depth
  ihdr[9] = 6; // color type: RGBA
  return Buffer.concat([
    Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]),
    chunk("IHDR", ihdr),
    chunk("IDAT", deflateSync(raw, { level: 9 })),
    chunk("IEND", Buffer.alloc(0)),
  ]);
}

/** Wrap a PNG payload in an ICO container (PNG-in-ICO, supported since Vista). */
function encodeIco(png, size) {
  const header = Buffer.alloc(6);
  header.writeUInt16LE(0, 0); // reserved
  header.writeUInt16LE(1, 2); // type: icon
  header.writeUInt16LE(1, 4); // image count
  const entry = Buffer.alloc(16);
  entry[0] = size >= 256 ? 0 : size;
  entry[1] = size >= 256 ? 0 : size;
  entry.writeUInt16LE(1, 4); // color planes
  entry.writeUInt16LE(32, 6); // bits per pixel
  entry.writeUInt32LE(png.length, 8);
  entry.writeUInt32LE(6 + 16, 12);
  return Buffer.concat([header, entry, png]);
}

// ---------------------------------------------------------------------------
// Drawing helpers (supersampled coverage -> anti-aliased RGBA canvas)
// ---------------------------------------------------------------------------

class Canvas {
  constructor(width, height) {
    this.width = width;
    this.height = height;
    this.pixels = new Uint8Array(width * height * 4);
  }

  /** Composite a color over one pixel with coverage 0..1. */
  blend(x, y, color, coverage, alpha = 1) {
    if (x < 0 || y < 0 || x >= this.width || y >= this.height) return;
    const a = Math.max(0, Math.min(1, coverage)) * alpha;
    if (a <= 0) return;
    const i = (y * this.width + x) * 4;
    const dstA = this.pixels[i + 3] / 255;
    const outA = a + dstA * (1 - a);
    for (let c = 0; c < 3; c += 1) {
      const src = color[c];
      const dst = this.pixels[i + c];
      this.pixels[i + c] = outA
        ? Math.round((src * a + dst * dstA * (1 - a)) / outA)
        : 0;
    }
    this.pixels[i + 3] = Math.round(outA * 255);
  }

  /** Signed distance of a rounded rectangle outline (negative inside). */
  roundedRectSdf(x, y, cx, cy, halfW, halfH, radius) {
    const dx = Math.abs(x - cx) - (halfW - radius);
    const dy = Math.abs(y - cy) - (halfH - radius);
    const outside = Math.hypot(Math.max(dx, 0), Math.max(dy, 0));
    return outside + Math.min(Math.max(dx, dy), 0) - radius;
  }

  /** Distance from a point to a line segment. */
  static segmentDistance(px, py, x1, y1, x2, y2) {
    const dx = x2 - x1;
    const dy = y2 - y1;
    const lenSq = dx * dx + dy * dy;
    const t = lenSq ? Math.max(0, Math.min(1, ((px - x1) * dx + (py - y1) * dy) / lenSq)) : 0;
    return Math.hypot(px - (x1 + t * dx), py - (y1 + t * dy));
  }

  fillRoundedRect(cx, cy, halfW, halfH, radius, color) {
    for (let y = 0; y < this.height; y += 1) {
      for (let x = 0; x < this.width; x += 1) {
        const d = this.roundedRectSdf(x + 0.5, y + 0.5, cx, cy, halfW, halfH, radius);
        this.blend(x, y, color, 0.5 - d);
      }
    }
  }

  /** Draw a V glyph as two tapered strokes. */
  drawV(cx, cy, halfW, halfH, thickness, color) {
    const top = cy - halfH;
    const bottom = cy + halfH;
    for (let y = 0; y < this.height; y += 1) {
      for (let x = 0; x < this.width; x += 1) {
        const px = x + 0.5;
        const py = y + 0.5;
        const d = Math.min(
          Canvas.segmentDistance(px, py, cx - halfW, top, cx, bottom),
          Canvas.segmentDistance(px, py, cx + halfW, top, cx, bottom),
        );
        this.blend(x, y, color, 0.5 + thickness / 2 - d);
      }
    }
  }

  fill(color) {
    for (let y = 0; y < this.height; y += 1) {
      for (let x = 0; x < this.width; x += 1) {
        this.blend(x, y, color, 1);
      }
    }
  }

  fillRect(x0, y0, x1, y1, color) {
    for (let y = Math.round(y0); y < Math.round(y1); y += 1) {
      for (let x = Math.round(x0); x < Math.round(x1); x += 1) {
        this.blend(x, y, color, 1);
      }
    }
  }

  toPng() {
    return encodePng(this.width, this.height, this.pixels);
  }
}

/** Monogram: rounded orange square with a white V, transparent outside. */
function monogram(size) {
  const canvas = new Canvas(size, size);
  const c = size / 2;
  canvas.fillRoundedRect(c, c, size / 2, size / 2, size * 0.22, PRIMARY);
  canvas.drawV(c, c * 1.06, size * 0.24, size * 0.26, size * 0.15, WHITE);
  return canvas;
}

// 5x7 pixel font — block letters keep the banner dependency-free.
const FONT = {
  V: ["10001", "10001", "10001", "10001", "01010", "01010", "00100"],
  A: ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
  E: ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
  L: ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
  G: ["01110", "10001", "10000", "10111", "10001", "10001", "01110"],
  N: ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
  T: ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
};

function drawWord(canvas, word, originX, originY, scale, color) {
  let x = originX;
  for (const letter of word) {
    const glyph = FONT[letter];
    glyph.forEach((row, gy) => {
      [...row].forEach((cell, gx) => {
        if (cell === "1") {
          canvas.fillRect(
            x + gx * scale,
            originY + gy * scale,
            x + (gx + 1) * scale,
            originY + (gy + 1) * scale,
            color,
          );
        }
      });
    });
    x += (glyph[0].length + 1) * scale;
  }
  return x - scale; // right edge
}

/** 1200x630 Open Graph card: VAEL wordmark on warm charcoal. */
function banner() {
  const canvas = new Canvas(1200, 630);
  canvas.fill(CANVAS);
  // 2px accent frame inset from the edges.
  canvas.fillRect(24, 24, 1176, 30, ACCENT);
  canvas.fillRect(24, 600, 1176, 606, ACCENT);
  const scale = 26;
  const wordWidth = (5 * 4 + 3) * scale;
  drawWord(canvas, "VAEL", (1200 - wordWidth) / 2, 232, scale, PRIMARY);
  const capsuleScale = 14;
  const capsuleWidth = (5 * 5 + 4) * capsuleScale;
  drawWord(canvas, "AGENT", (1200 - capsuleWidth) / 2, 486, capsuleScale, ACCENT);
  return canvas;
}

// ---------------------------------------------------------------------------
// SVG marks (text-free geometry, so they render identically everywhere)
// ---------------------------------------------------------------------------

function markSvg(bg, fg) {
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-label="VAEL">
  <rect width="64" height="64" rx="14" fill="#${bg}" />
  <path d="M17 18 L32 46 L47 18" fill="none" stroke="#${fg}" stroke-width="9"
        stroke-linecap="round" stroke-linejoin="round" />
</svg>
`;
}

function faviconSvg() {
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-label="VAEL">
  <rect width="64" height="64" rx="14" fill="#D97757" />
  <path d="M17 18 L32 46 L47 18" fill="none" stroke="#FFFFFF" stroke-width="9"
        stroke-linecap="round" stroke-linejoin="round" />
</svg>
`;
}

const hex = (rgb) => rgb.map((c) => c.toString(16).padStart(2, "0")).join("");

function main() {
  mkdirSync(OUT, { recursive: true });
  const write = (name, data) => {
    writeFileSync(join(OUT, name), data);
    console.log(`wrote static/img/${name} (${data.length} bytes)`);
  };

  write("vael-mark.svg", markSvg(hex(PRIMARY), "FFFFFF"));
  write("vael-mark-dark.svg", markSvg(hex(PRIMARY), "FFFFFF"));
  write("favicon.svg", faviconSvg());

  write("favicon-16x16.png", monogram(16).toPng());
  write("favicon-32x32.png", monogram(32).toPng());
  write("apple-touch-icon.png", monogram(180).toPng());
  write("favicon.ico", encodeIco(monogram(32).toPng(), 32));
  write("vael-agent-banner.png", banner().toPng());
}

main();
