// Energy Research Warehouse (ERW) site, session 1175 (chain 078): the 3D network's code is loaded only when its shape is
// drawn. A source scan of the import graph of the Grid page (app/grid/page.tsx and the root layout), following every
// relative and "@/" import with the site's own TypeScript parser: no module the page loads statically imports three.js
// or 3d-force-graph (nor any package that depends on them), and the only imports of the two are the dynamic ones in
// app/network/Network.tsx, inside the effect that returns at once unless the shape shown is the network, the browser
// draws WebGL and the frame is near the screen (sessions 180 and 428). The default tab (Mix) draws no NetworkView.
// The 3D frame keeps its box, the WebGL fallback its words, and the loading line is the box's sibling (session 1175).
// Needs site/node_modules (typescript); no build, no network.
//
//   node scripts/test-network-split.mjs
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const SITE = path.resolve(here, "..");
const NM = path.join(SITE, "node_modules");
const ts = createRequire(path.join(SITE, "package.json"))("typescript");
const rel = (f) => path.relative(SITE, f).split(path.sep).join("/");
const read = (r) => fs.readFileSync(path.join(SITE, r), "utf-8");
let n = 0;
const test = (name, f) => { f(); n += 1; console.log(`ok   ${name}`); };

// what the 3D shape alone needs: three.js and the packages built on it
const HEAVY = /^(three|3d-force-graph|3d-force-graph-vr|three-[\w.-]+|@react-three\/[\w.-]+|react-force-graph(-[\w]+)?|globe\.gl|deck\.gl|@deck\.gl\/[\w.-]+)(\/.*)?$/;
const CODE = /\.(tsx?|mjs|jsx?)$/;

/** The imports of a module: static (type-only left out: they are erased), and dynamic import() calls with their node. */
function parse(file) {
  const text = fs.readFileSync(file, "utf-8");
  const sf = ts.createSourceFile(file, text, ts.ScriptTarget.Latest, true, file.endsWith("x") ? ts.ScriptKind.TSX : ts.ScriptKind.TS);
  const out = { text, sf, statics: [], dynamics: [] };
  const visit = (node) => {
    if (ts.isImportDeclaration(node)) { if (!node.importClause?.isTypeOnly) out.statics.push(node.moduleSpecifier.text); }
    else if (ts.isExportDeclaration(node) && node.moduleSpecifier) { if (!node.isTypeOnly) out.statics.push(node.moduleSpecifier.text); }
    else if (ts.isCallExpression(node) && node.expression.kind === ts.SyntaxKind.ImportKeyword && node.arguments[0] && ts.isStringLiteralLike(node.arguments[0])) out.dynamics.push({ spec: node.arguments[0].text, node });
    else if (ts.isCallExpression(node) && ts.isIdentifier(node.expression) && node.expression.text === "require" && node.arguments[0] && ts.isStringLiteralLike(node.arguments[0])) out.statics.push(node.arguments[0].text);
    ts.forEachChild(node, visit);
  };
  visit(sf);
  return out;
}

/** A relative or "@/" import to its file in the site; a package's name otherwise. */
function resolve(spec, from) {
  if (!spec.startsWith(".") && !spec.startsWith("@/")) return { pkg: spec.startsWith("@") ? spec.split("/").slice(0, 2).join("/") : spec.split("/")[0] };
  const base = spec.startsWith("@/") ? path.join(SITE, spec.slice(2)) : path.resolve(path.dirname(from), spec);
  for (const c of [base, ...[".ts", ".tsx", ".js", ".mjs", ".jsx"].map((x) => base + x), ...["index.ts", "index.tsx", "index.js"].map((x) => path.join(base, x))]) {
    if (fs.existsSync(c) && fs.statSync(c).isFile()) return { file: c };
  }
  // a data file written by `npm run content` (content/*.json) holds no import: a leaf, there or not
  if (/\.(json|css|md)$/.test(base)) return { file: base };
  throw new Error(`${spec} from ${rel(from)}: no such file`);
}

/** Every module reached from the roots by static imports; the packages they name; the dynamic imports met on the way. */
function closure(roots) {
  const files = new Map(), pkgs = new Map(), dynamics = [];
  const walk = (file) => {
    if (files.has(file)) return;
    if (!CODE.test(file)) { files.set(file, null); return; }
    const p = parse(file);
    files.set(file, p);
    for (const spec of p.statics) {
      const r = resolve(spec, file);
      if (r.pkg) { if (!pkgs.has(spec)) pkgs.set(spec, rel(file)); }
      else walk(r.file);
    }
    for (const d of p.dynamics) dynamics.push({ from: file, spec: d.spec, node: d.node, sf: p.sf });
  };
  roots.forEach(walk);
  return { files, pkgs, dynamics };
}

const ROOTS = [path.join(SITE, "app", "grid", "page.tsx"), path.join(SITE, "app", "layout.tsx")];
const page = closure(ROOTS);
const NETWORK = path.join(SITE, "app", "network", "Network.tsx");

test("the walk reaches the network component and the panels the Grid page draws", () => {
  for (const r of ["components/grid/NetworkView.tsx", "app/network/Network.tsx", "components/grid/NetworkFigures.tsx", "lib/networkMap.ts", "lib/networkGravity.ts", "components/grid/MixView.tsx"]) {
    assert.ok(page.files.has(path.join(SITE, ...r.split("/"))), `${r} is reached`);
  }
  assert.ok(page.files.size > 60, `${page.files.size} modules`);
});

test("no module the Grid page loads statically imports three.js or 3d-force-graph", () => {
  for (const [spec, from] of page.pkgs) assert.ok(!HEAVY.test(spec), `${from} imports ${spec} statically`);
  // and none names them in a require, or in an import kept for its effect
  for (const [file, p] of page.files) if (p) for (const s of p.statics) assert.ok(!HEAVY.test(s), `${rel(file)}: ${s}`);
});

test("no package the page imports statically depends on three.js, however deep", () => {
  if (!fs.existsSync(NM)) { console.log("     (site/node_modules is not here: the packages' own dependencies were not read)"); return; }
  const seen = new Set(), path0 = new Map();
  const visit = (name, via) => {
    if (seen.has(name)) return;
    seen.add(name);
    path0.set(name, via);
    const pj = path.join(NM, ...name.split("/"), "package.json");
    if (!fs.existsSync(pj)) return;   // an optional peer not installed
    const j = JSON.parse(fs.readFileSync(pj, "utf-8"));
    for (const d of Object.keys({ ...(j.dependencies ?? {}), ...(j.peerDependencies ?? {}), ...(j.optionalDependencies ?? {}) })) {
      assert.ok(!HEAVY.test(d), `${[...via, name].join(" > ")} depends on ${d}`);
      visit(d, [...via, name]);
    }
  };
  for (const spec of page.pkgs.keys()) { const name = spec.startsWith("@") ? spec.split("/").slice(0, 2).join("/") : spec.split("/")[0]; assert.ok(!HEAVY.test(name), name); visit(name, []); }
  assert.ok(seen.has("next") && seen.has("react") && seen.size > 5, "the page's packages were read");
});

// the lazy modules: every dynamic import met from the page (next/dynamic's targets, the scene's chunk), followed in turn
const lazy = [];
{
  const met = new Set();
  const queue = [...page.dynamics];
  while (queue.length) {
    const d = queue.shift();
    const key = `${rel(d.from)}>${d.spec}`;
    if (met.has(key)) continue;
    met.add(key);
    lazy.push(d);
    const r = resolve(d.spec, d.from);
    if (r.file) { const c = closure([r.file]); for (const [spec, from] of c.pkgs) lazy.push({ from: path.join(SITE, from), spec, node: null, statik: true }); queue.push(...c.dynamics); }
  }
}

test("three.js and 3d-force-graph are imported in one place only: two import() calls in the network component", () => {
  const heavy = lazy.filter((d) => HEAVY.test(d.spec));
  assert.deepEqual(heavy.map((d) => [rel(d.from), d.spec, !!d.statik]), [["app/network/Network.tsx", "3d-force-graph", false], ["app/network/Network.tsx", "three", false]]);
  // the map and the gravity shape are next/dynamic modules of their own, and import neither
  const targets = lazy.filter((d) => d.from === NETWORK && d.spec.startsWith("./")).map((d) => d.spec).sort();
  assert.deepEqual(targets, ["./NetworkGravity", "./NetworkMap"]);
  for (const t of ["NetworkMap", "NetworkGravity"]) {
    const c = closure([path.join(SITE, "app", "network", `${t}.tsx`)]);
    for (const spec of c.pkgs.keys()) assert.ok(!HEAVY.test(spec), `${t}: ${spec}`);
    assert.ok(!c.dynamics.some((d) => HEAVY.test(d.spec)), t);
  }
});

test("the scene's import() runs only in the network's own effect, after the shape, WebGL and the frame are checked", () => {
  const scene = page.dynamics.filter((d) => d.from === NETWORK && HEAVY.test(d.spec));
  assert.equal(scene.length, 2);
  for (const d of scene) {
    // its function is `load`, declared in the body of a useEffect callback
    let at = d.node, load = null, effect = null;
    while (at) {
      if (!load && ts.isVariableDeclaration(at) && ts.isIdentifier(at.name) && at.name.text === "load") load = at;
      if (ts.isCallExpression(at) && ts.isIdentifier(at.expression) && at.expression.text === "useEffect") { effect = at; break; }
      at = at.parent;
    }
    assert.ok(load, `${d.spec}: inside load`);
    assert.ok(effect, `${d.spec}: inside a useEffect`);
    const body = effect.arguments[0].getText(d.sf);
    const guard = body.indexOf('if (shape !== "network" || (v3 && (ownShape ?? parseShape(window.location.search)) !== "network")) return;');
    const gl = body.indexOf('if (!(c.getContext("webgl2") || c.getContext("webgl"))) { fail(); return; }');
    const imp = body.indexOf(`import("${d.spec}")`);
    assert.ok(guard >= 0 && gl > guard && imp > gl, `${d.spec}: the shape, then WebGL, then the import`);
    // load runs from the observer once the frame is within 200 px of the screen, or at once without an observer
    assert.ok(body.includes('if (typeof IntersectionObserver === "undefined") load();'));
    assert.ok(body.includes('{ rootMargin: "200px 0px" }'));
    // the effect runs again only when the shape changes
    assert.equal(effect.arguments[1].getText(d.sf), "[shape]");
  }
});

test("the Grid page's default tab, Mix, draws no network component", () => {
  assert.ok(read("lib/gridtool.ts").includes('export const DEFAULT_VIEW: GridView = "mix";'));
  const p = read("app/grid/page.tsx");
  const uses = [...p.matchAll(/<NetworkView /g)].length;
  assert.equal(uses, 2);
  assert.ok(p.includes('{view === "network" ? <NetworkView keep={keep} node={p.node} grid={grid} day={p.day} /> : null}'));
  assert.ok(/\{view === "gravity" \? \(\s*<>[\s\S]*?<NetworkView keep=\{keep\} node=\{p\.node\} shape="gravity"/.test(p) || p.includes('<NetworkView keep={keep} node={p.node} shape="gravity" grid={grid} day={p.day} />'));
  // on the Gravity tab the component opens in the gravity shape, so the scene's effect returns before any import
  assert.ok(read("app/network/Network.tsx").includes("const [ownShape, setOwnShape] = useState<Shape | null>(page?.shape ?? null);"));
});

test("the 3D frame keeps its box and its fallback; the loading line is its sibling and goes once the scene is built", () => {
  const s = read("app/network/Network.tsx");
  assert.equal(s.split('style={{ height: "min(72vh, 620px)", minHeight: 420 }}').length, 2, "the box's size, once");
  assert.ok(s.includes('aria-label="A 3D network of the US balancing authorities and their interchange; drag to rotate, scroll to zoom, click a grid for its panel" role="img" />'), "the box has no child: the library empties it");
  assert.ok(s.includes('<div className="relative min-w-0" data-scene={sceneReady ? "ready" : "loading"}>'));
  assert.ok(s.includes('<p className="pointer-events-none absolute inset-0 flex items-center justify-center p-4 text-center text-sm text-muted" data-scene-wait="1">'));
  assert.ok(s.includes("graph.current = g;\n      setSceneReady(true);"), "ready once the graph is built");
  assert.ok(s.includes("graph.current = null; setSceneReady(false); };"), "loading again when the scene is taken down");
  assert.ok(s.includes("This browser cannot draw 3D (WebGL is not available), so the network is not shown. The table of balancing authorities below, and"));
  assert.ok(s.includes('"Drag to rotate, scroll to zoom, click a grid; it turns slowly until touched."'));
});

console.log(`${n} tests passed`);
