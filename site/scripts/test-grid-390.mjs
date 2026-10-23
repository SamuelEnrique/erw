// Energy Research Warehouse (ERW) site, session 1158 (chain 077): the Grid tool at 390 pixels, its drawings read by a
// keyboard and a finger. lib/networkMap.ts cardWidth (the widest a hover card of the map or the gravity shape may be, so
// that it stays inside its frame, which clips it), and the markup of the two drawings and the panels session 1158
// mended: no image or group role on a drawing that holds what a keyboard reaches (AccessLint
// aria/presentational-children-focusable, aria/aria-allowed-role), a tap on a line shows its card and a finger lifting
// does not take it away, the energy mix panel's tables in a frame a keyboard reaches (keyboard-accessible/
// scrollable-region), a stored answer's long filter wrapping. Needs no build, no network and no node_modules.
//
//   node scripts/test-grid-390.mjs
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import * as M from "../lib/networkMap.ts";

const here = path.dirname(fileURLToPath(import.meta.url));
const read = (...p) => fs.readFileSync(path.join(here, "..", ...p), "utf-8");
let n = 0;
const test = (name, f) => { f(); n += 1; console.log(`ok   ${name}`); };
const map = read("app", "network", "NetworkMap.tsx");
const grav = read("app", "network", "NetworkGravity.tsx");

test("a hover card is never wider than the room the frame leaves it, nor than 20rem", () => {
  assert.equal(M.cardWidth(-1, false), "min(20rem, calc(100% - 16px))");
  assert.equal(M.cardWidth(100, false), "min(20rem, calc(100% - 120px))");
  assert.equal(M.cardWidth(250, true), "min(20rem, 230px)");
  assert.equal(M.cardWidth(10, true), "min(20rem, 0px)");
  // at a phone's 324 px drawing, a card from the middle has the half the frame leaves it, not 320 px
  assert.equal(M.cardWidth(161, false), "min(20rem, calc(100% - 181px))");
  for (const s of [map, grav]) {
    assert.ok(s.includes("maxWidth: cardWidth(hover.x, hover.right)"), "the card takes the width");
    assert.ok(!s.includes("max-w-xs"), "no fixed card width is left");
  }
});

test("neither drawing is an image or a group: each svg keeps its name and its own role", () => {
  for (const s of [map, grav]) {
    assert.ok(s.includes('className="h-full w-full" preserveAspectRatio="xMidYMid meet"'), "the drawing takes no role");
    assert.ok(!/<svg[^>]*role="(img|group)"[^>]*preserveAspectRatio="xMidYMid meet"/.test(s), "no img or group role on the drawing");
  }
  assert.ok(map.includes("aria-label={`A map of the US balancing authorities"), "the map keeps its name");
  assert.ok(grav.includes('aria-label="The seven ISO grids around the Lower 48'), "the gravity shape keeps its name");
});

test("a tap on a line shows its card, and a finger lifting does not take it away", () => {
  for (const s of [map, grav]) {
    assert.ok(s.includes('const leave = (e: PointerEvent<SVGElement>) => { if (e.pointerType !== "touch") setHover(null); };'), "touch leave");
    assert.ok(!s.includes("onPointerLeave={() => setHover(null)}"), "every leave is the touch-aware one");
    assert.ok(s.includes("onPointerDown={(e) => { if (e.target === e.currentTarget) setHover(null); }}"), "a tap on the empty drawing clears the card");
  }
  assert.ok(map.includes('onPointerDown={hoverAt(`${f.a}-${f.b}`, "edge")}'), "the map's lines");
  assert.ok(grav.includes('onPointerDown={hoverAt(p.id, "edge")}') && grav.includes("onPointerDown={hoverAt(p.id)}"), "the gravity lines and circles");
  // the mouse's hover is as it was
  assert.ok(map.includes('onPointerMove={hoverAt(`${f.a}-${f.b}`, "edge")}') && grav.includes('onPointerMove={hoverAt(p.id, "edge")}'));
});

test("the energy mix panel's tables scroll in a frame a keyboard reaches, the fuel the row's header", () => {
  const m = read("components", "grid", "MixFigures.tsx");
  assert.equal((m.match(/overflow-x-auto" \{\.\.\.scrollRegion\(/g) ?? []).length, 2);
  assert.equal((m.match(/<th scope="row" className="py-1 pr-3 text-left font-normal"><span aria-hidden="true"/g) ?? []).length, 2);
  assert.ok(!m.includes('<td className="py-1 pr-3"><span className="mr-1'));
});

test("a stored answer's filter written without a space wraps in the Ask column", () => {
  assert.ok(read("components", "grid", "AskExamples.tsx").includes('className="border-b border-rule py-2 text-sm break-words"'));
});

console.log(`${n} tests passed`);
