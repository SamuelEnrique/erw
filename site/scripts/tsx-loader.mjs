// Energy Research Warehouse (ERW) site, session 1160: a Node module hook so a script can import the site's server
// components (.tsx) as they are, without building the site, and call them to learn which reads a page makes.
//
//   node --import ./scripts/alias-register.mjs --import ./scripts/tsx-register.mjs scripts/time-grid-reads.mjs
//
// It runs before scripts/alias-loader.mjs (session 66: the "@/..." paths, .json, "server-only", "next/server",
// "next/cache"), which it leaves as they are, and adds:
//   - .ts and .tsx files transpiled by the site's own TypeScript (JSX as react-jsx), so a component file loads;
//   - a module whose first statement is "use client" replaced by stubs: each export a function that draws nothing,
//     marked __erwClient, so a caller can walk the props a server component handed it (its children) without
//     running browser code or importing what the browser needs (charts, d3, maps). The browser never reads Supabase:
//     every read of the page is made on the server, so nothing is lost;
//   - .css imports as empty modules, and stand-ins for next/link, next/navigation, next/dynamic, next/headers and
//     next/font/google, the Next modules the site's components import.
// Nothing here sends a request.
import fs from "node:fs";
import { fileURLToPath } from "node:url";
import ts from "typescript";

const STUBS = {
  "next/link": "export default function Link(p) { return p.children ?? null; } Link.__erwClient = 'next/link';",
  "next/navigation": [
    "export function notFound() { throw new Error('notFound() called'); }",
    "export function redirect(to) { throw new Error('redirect(' + to + ') called'); }",
    "export function usePathname() { return '/'; } export function useRouter() { return {}; } export function useSearchParams() { return new URLSearchParams(); }",
  ].join("\n"),
  "next/dynamic": "export default function dynamic() { const f = () => null; f.__erwClient = 'next/dynamic'; return f; }",
  "next/headers": "export async function cookies() { return { get: () => undefined, has: () => false, getAll: () => [] }; } export async function headers() { return new Headers(); }",
  "next/font/google": ["Inter", "IBM_Plex_Mono", "IBM_Plex_Sans", "Source_Serif_4"].map((n) => `export function ${n}() { return { variable: "", className: "", style: {} }; }`).join("\n"),
};

/** Whether a module's source opens with the "use client" directive (comments and blank lines before it allowed). */
export function isClientModule(src) {
  const body = src.replace(/^﻿/, "").replace(/^(\s|\/\/[^\n]*\n|\/\*[\s\S]*?\*\/)*/, "");
  return /^["']use client["']/.test(body);
}

/** The names a module exports, read from its transpiled JavaScript (no type is left there). "default" included. */
export function exportNames(js) {
  const names = new Set();
  for (const m of js.matchAll(/^export\s+(?:async\s+)?(?:function\*?|class)\s+([A-Za-z_$][\w$]*)/gm)) names.add(m[1]);
  for (const m of js.matchAll(/^export\s+(?:const|let|var)\s+([^\n]*)/gm)) {
    const line = m[1];
    if (/^[{[]/.test(line)) {
      // a destructuring: the names bound inside the braces
      for (const part of line.slice(1, line.search(/[}\]]/)).split(",")) {
        const n = part.split(":").pop().split("=")[0].trim();
        if (/^[A-Za-z_$][\w$]*$/.test(n)) names.add(n);
      }
      continue;
    }
    // "A = 1, B = 2": the first name, and each name after a comma outside brackets
    let depth = 0, start = 0;
    for (let i = 0; i <= line.length; i++) {
      const c = line[i];
      if (c === "(" || c === "[" || c === "{") depth++;
      else if (c === ")" || c === "]" || c === "}") depth--;
      if (i === line.length || (c === "," && depth === 0)) {
        const n = /^\s*([A-Za-z_$][\w$]*)\s*=/.exec(line.slice(start, i));
        if (n) names.add(n[1]);
        start = i + 1;
      }
    }
  }
  for (const m of js.matchAll(/^export\s*\{([^}]*)\}/gm)) {
    for (const part of m[1].split(",")) {
      const n = part.trim().split(/\s+as\s+/).pop()?.trim();
      if (n) names.add(n);
    }
  }
  if (/^export\s+default\b/m.test(js)) names.add("default");
  return [...names];
}

/** The stand-in for a client module: every export a function that draws nothing, marked with its module and name. */
export function clientStub(names, url) {
  const lines = ["const __erw = (n) => { const f = () => null; f.__erwClient = " + JSON.stringify(url) + " + '#' + n; return f; };"];
  for (const n of names) lines.push(n === "default" ? "export default __erw('default');" : `export const ${n} = __erw(${JSON.stringify(n)});`);
  return lines.join("\n");
}

export function transpile(src, file) {
  return ts.transpileModule(src, {
    fileName: file,
    compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2022, jsx: ts.JsxEmit.ReactJSX, esModuleInterop: true, isolatedModules: true },
  }).outputText;
}

export async function resolve(specifier, context, next) {
  if (specifier in STUBS) return { url: `erw-tsx-stub:${specifier}`, shortCircuit: true };
  return next(specifier, context);
}

export async function load(url, context, next) {
  if (url.startsWith("erw-tsx-stub:")) return { format: "module", source: STUBS[url.slice("erw-tsx-stub:".length)], shortCircuit: true };
  if (url.startsWith("file:") && /\.css$/.test(url)) return { format: "module", source: "export default {};", shortCircuit: true };
  if (url.startsWith("file:") && /\.tsx?$/.test(url) && !url.includes("/node_modules/")) {
    const file = fileURLToPath(url);
    const src = fs.readFileSync(file, "utf-8");
    const js = transpile(src, file);
    if (isClientModule(src)) return { format: "module", source: clientStub(exportNames(js), url.slice(url.indexOf("/site/") + 6)), shortCircuit: true };
    return { format: "module", source: js, shortCircuit: true };
  }
  return next(url, context);
}
