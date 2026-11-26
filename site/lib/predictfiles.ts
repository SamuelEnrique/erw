// Energy Research Warehouse (ERW) site, session 10401 (chain 720, part C): the reader of the ERW forecast's page files
// (site/data/predict/, written by the data machine's forecast build; contract docs/state/page_files_predict.md). A file
// is read when a request names it, in the manner of lib/countryfiles.ts: a file the data machine has not written yet is
// null and the page draws its blanks, so the real files land with no change of code. A file that says it is a test's
// fixture is read only from a test's own folder, never from the site's.
import fs from "node:fs";
import path from "node:path";
import type { IndexPlace, PlaceFile, PredictIndex, ScoresFile } from "@/lib/predict";

/** The folder of the page files. ERW_PREDICT_DIR stands in for it in a test, and only there. */
export function predictDir(): string {
  return process.env.ERW_PREDICT_DIR ?? path.join(process.cwd(), "data", "predict");
}

/** The text of a file of the site's own folder, or null. The path is written out from the site's root so that the build
 *  sees which folder is read and carries that folder with the route, and no more (a path it cannot follow has it carry
 *  the whole project); next.config.ts names the files for it as well (outputFileTracingIncludes, "/forecast"). */
function siteText(name: string): string | null {
  const at = path.join(process.cwd(), "data", "predict", name);
  return fs.existsSync(at) ? fs.readFileSync(at, "utf8") : null;
}
/** The text of a file of a test's folder (ERW_PREDICT_DIR), or null. The build is told not to follow these reads. */
function testText(dir: string, name: string): string | null {
  const at = path.join(/*turbopackIgnore: true*/ dir, name);
  return fs.existsSync(/*turbopackIgnore: true*/ at) ? fs.readFileSync(/*turbopackIgnore: true*/ at, "utf8") : null;
}

/** One page file, or null while it is not on the site or cannot be read as JSON. Only a plain file name is read. */
export function readPredict<T>(name: string): T | null {
  if (!/^[a-z0-9][a-z0-9_-]*\.json$/.test(name)) return null;
  try {
    const text = process.env.ERW_PREDICT_DIR ? testText(process.env.ERW_PREDICT_DIR, name) : siteText(name);
    if (text === null) return null;
    const v = JSON.parse(text) as T & { fixture?: string };
    if (v && typeof v === "object" && "fixture" in v && v.fixture && !process.env.ERW_PREDICT_DIR) return null;
    return v;
  } catch {
    return null;
  }
}

export const predictIndex = () => readPredict<PredictIndex>("index.json");
export const predictScores = () => readPredict<ScoresFile>("scores.json");
/** A place's file, by the name the index gives it. */
export const predictPlace = (p: Pick<IndexPlace, "file"> | null | undefined) => (p ? readPredict<PlaceFile>(p.file) : null);
