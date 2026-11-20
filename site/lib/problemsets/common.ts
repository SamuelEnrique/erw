// Energy Research Warehouse (ERW) site, session 8901 (chain 507, part C): what the four problem sets of the whole country
// share. Every figure is read from a committed page file under site/data with lib/pagefile.ts and carries its pf| key;
// a derived figure is a calc| of two such keys, in the form lib/problems.ts writes (calc|<op>|<A>|<B>, "~" for "|"),
// which scripts/check-values.mjs recomputes from the file. No figure is typed: a path that does not lead to a number
// throws, and the page says the set could not be computed.
import type { Question, V } from "@/lib/problems";
import { fileHead, pfKey, pfValue, readPageFile, type Segment } from "@/lib/pagefile";
import { notePageFile, type SetGuide } from "@/lib/problemkit";

export type Built = { example: Question | null; questions: Question[] };
export type Meta = { slug: string; title: string; line: string; teacher: string; pages: { href: string; label: string }[] };
export type { SetGuide };

/** A page file read, its header's tables noted for the hover and the CSV (lib/problemkit.ts notePageFile). */
export function open<T = unknown>(file: string): T {
  const doc = readPageFile(file) as T;
  notePageFile(file, fileHead(file).tables);
  return doc;
}

/** The figure at a path of a page file, with its key; throws when the path leads to no finite number. */
export function fig(file: string, segments: Segment[], u?: string): V {
  open(file);
  const k = pfKey(file, segments);
  const v = pfValue(k);
  if (v === undefined) throw new Error(`no figure at ${k}`);
  return { v, k, u };
}

const tildes = (k: string) => k.replaceAll("|", "~");
/** A derived figure of two keyed figures, as lib/problems.ts's calc writes it. */
export function calc(op: "ratio" | "diff" | "pct", a: V, b: V, u?: string): V {
  const v = op === "ratio" ? a.v / b.v : op === "diff" ? a.v - b.v : (a.v / b.v) * 100;
  return { v, k: `calc|${op}|${tildes(a.k)}|${tildes(b.k)}`, u };
}

/** A month in words: "October 2026" for "2026-10". */
const MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
export const monthWords = (m: string) => `${MONTHS[Number(m.slice(5, 7)) - 1] ?? m.slice(5, 7)} ${m.slice(0, 4)}`;

/** The start of hour i of an event file's window, as UTC words ("2022-12-24 01:00 UTC"). */
export function hourAt(start: string, stepHours: number, i: number): string {
  return new Date(Date.parse(start) + i * stepHours * 3_600_000).toISOString().slice(0, 16).replace("T", " ") + " UTC";
}

/** The position of the largest finite value of an array (the first when two are equal), or -1. */
export function argmax(arr: (number | null | undefined)[]): number {
  let best = -1;
  arr.forEach((v, i) => { if (typeof v === "number" && Number.isFinite(v) && (best < 0 || v > (arr[best] as number))) best = i; });
  return best;
}
