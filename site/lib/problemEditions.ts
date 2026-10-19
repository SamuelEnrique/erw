// Session 293 (Samuel's ruling 8a of 14 October 2026): the dated editions of the problem sets. Each edition is every
// set as lib/problems.ts built it on its date, frozen in data/problem_editions/<date>.json by
// scripts/build-problem-edition.mjs, with each question's rows in public/problems/<date>/<slug>-<id>.csv. The live sets
// move as the tables update; an edition does not, so a class can answer what its teacher prepared.
import fs from "node:fs";
import path from "node:path";
import type { ProblemSet, Question } from "@/lib/problems";

export type EditionQuestion = Question & { rows: number; csv: string };
export type EditionSet = Omit<ProblemSet, "questions"> & { questions: EditionQuestion[] };
export type Edition = { date: string; built_at: string; note: string; sets: EditionSet[] };

const DIR = () => path.join(process.cwd(), "data", "problem_editions");

/** The editions held, newest first. */
export function editions(): string[] {
  return (JSON.parse(fs.readFileSync(path.join(DIR(), "index.json"), "utf-8")) as { editions: string[] }).editions;
}
export function edition(date: string): Edition | null {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(date) || !editions().includes(date)) return null;
  return JSON.parse(fs.readFileSync(path.join(DIR(), `${date}.json`), "utf-8")) as Edition;
}
export const editionPath = (slug: string, date: string) => `/learn/problems/${slug}/${date}`;
export const teacherPath = (slug: string, date: string) => `/learn/problems/${slug}/${date}/teacher`;
/** "15 October 2026" for 2026-10-15. */
export const longDate = (d: string) => new Date(`${d}T12:00:00Z`).toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric", timeZone: "UTC" });
