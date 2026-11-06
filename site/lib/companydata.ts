// Energy Research Warehouse (ERW) site, session 3304 (chain 200): the company database's files, read on the server when
// a request first asks for them and kept (next.config.ts lists the folder for the pages' server traces). Nothing is read
// from the database. The files: site/data/companies/ (warehouse/derived/companies_page.py).
import "server-only";
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import type { Company, CompanyIndex } from "@/lib/companydb";

const DIR = path.join(process.cwd(), "data", "companies");
let index: CompanyIndex | null = null;
const shards = new Map<string, Record<string, Company>>();

/** The index (every listed company). Throws when the file cannot be read: the page says so. */
export function companyIndex(): CompanyIndex {
  if (!index) index = JSON.parse(fs.readFileSync(path.join(DIR, "index.json"), "utf8")) as CompanyIndex;
  return index;
}

/** One company by its address part ("eia-6452"), or null when no listed company has it. */
export function company(id: string): Company | null {
  if (!/^[a-z0-9-]{1,80}$/.test(id)) return null;
  const key = crypto.createHash("sha1").update(`company:${id}`, "utf8").digest("hex").slice(0, 2);
  let s = shards.get(key);
  if (!s) {
    const p = path.join(DIR, "c", `${key}.json`);
    if (!fs.existsSync(p)) return null;
    s = JSON.parse(fs.readFileSync(p, "utf8")) as Record<string, Company>;
    shards.set(key, s);
  }
  return s[id] ?? null;
}
