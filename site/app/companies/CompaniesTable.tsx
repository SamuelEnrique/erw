"use client";
// Session 26: the /companies table: filters by sector, niche tag, stage, state and confidence; each row expands to the
// description, founders, raised, sources and the confidence clause. A row's anchor (#co-<name>) opens it, so /deals can link here.
import { Fragment, useEffect, useMemo, useState } from "react";
import type { Company } from "@/lib/data";
import { companyAnchor } from "@/lib/companies";

const STATES: Record<string, string> = {
  Alabama: "AL", Alaska: "AK", Arizona: "AZ", Arkansas: "AR", California: "CA", Colorado: "CO", Connecticut: "CT", Delaware: "DE",
  Florida: "FL", Georgia: "GA", Hawaii: "HI", Idaho: "ID", Illinois: "IL", Indiana: "IN", Iowa: "IA", Kansas: "KS", Kentucky: "KY",
  Louisiana: "LA", Maine: "ME", Maryland: "MD", Massachusetts: "MA", Michigan: "MI", Minnesota: "MN", Mississippi: "MS", Missouri: "MO",
  Montana: "MT", Nebraska: "NE", Nevada: "NV", "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
  "North Carolina": "NC", "North Dakota": "ND", Ohio: "OH", Oklahoma: "OK", Oregon: "OR", Pennsylvania: "PA", "Rhode Island": "RI",
  "South Carolina": "SC", "South Dakota": "SD", Tennessee: "TN", Texas: "TX", Utah: "UT", Vermont: "VT", Virginia: "VA", Washington: "WA",
  "West Virginia": "WV", Wisconsin: "WI", Wyoming: "WY",
};
const CODES = new Set(Object.values(STATES));

/** The US state a location names, by name or postal code; "" when none (a location outside the US, or not stated). */
function stateOf(location: string): string {
  for (const [name, code] of Object.entries(STATES).sort((a, b) => b[0].length - a[0].length)) {
    if (new RegExp(`\\b${name}\\b`).test(location)) return code;
  }
  const m = location.match(/\b([A-Z]{2})\b/g);
  return m?.find((c) => CODES.has(c)) ?? "";
}
const stageOf = (s: string) => (/public|nasdaq|nyse/i.test(s) ? "public" : s.replace(/\s*\(.*$/, "").trim() || "not disclosed");
const split = (s: string) => (s ? s.split(";").map((x) => x.trim()).filter(Boolean) : []);

export function CompaniesTable({ rows }: { rows: Company[] }) {
  const [sector, setSector] = useState("");
  const [niche, setNiche] = useState("");
  const [stage, setStage] = useState("");
  const [state, setState] = useState("");
  const [minConf, setMinConf] = useState("0");
  const [open, setOpen] = useState<string | null>(null);
  useEffect(() => {
    const h = decodeURIComponent(window.location.hash.slice(1));
    if (h) {
      const r = rows.find((x) => companyAnchor(x.name) === h);
      if (r) {
        setOpen(r.entity_id);
        document.getElementById(h)?.scrollIntoView();
      }
    }
  }, [rows]);
  const uniq = (xs: string[]) => Array.from(new Set(xs.filter(Boolean))).sort();
  const opts = useMemo(
    () => ({
      sector: uniq(rows.map((r) => r.sector)),
      niche: uniq(rows.flatMap((r) => split(r.niche_tags))),
      stage: uniq(rows.map((r) => stageOf(r.stage))),
      state: uniq(rows.map((r) => stateOf(r.location))),
    }),
    [rows],
  );
  const shown = rows.filter(
    (r) =>
      (!sector || r.sector === sector) &&
      (!niche || split(r.niche_tags).includes(niche)) &&
      (!stage || stageOf(r.stage) === stage) &&
      (!state || stateOf(r.location) === state) &&
      Number(r.confidence || 0) >= Number(minConf),
  );
  const sel = (label: string, v: string, set: (x: string) => void, options: [string, string][]) => (
    <label className="flex flex-col text-xs text-muted">
      {label}
      <select value={v} onChange={(e) => set(e.target.value)} className="mt-1 border border-rule bg-panel px-2 py-1 text-sm text-ink">
        {options.map(([k, l]) => (
          <option key={k} value={k}>
            {l}
          </option>
        ))}
      </select>
    </label>
  );
  const all = (xs: string[]): [string, string][] => [["", "All"], ...xs.map((x) => [x, x] as [string, string])];
  return (
    <div>
      <div className="mb-3 flex flex-wrap items-end gap-3">
        {sel("Sector", sector, setSector, all(opts.sector))}
        {sel("Niche", niche, setNiche, all(opts.niche))}
        {sel("Stage", stage, setStage, all(opts.stage))}
        {sel("State", state, setState, all(opts.state))}
        {sel("Confidence", minConf, setMinConf, [["0", "Any"], ["50", "50 or more"], ["80", "80 or more"]])}
        <span className="text-xs text-muted">
          {shown.length} of {rows.length} companies
        </span>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-rule text-left text-xs text-muted">
              <th className="py-1 pr-3">Company</th>
              <th className="py-1 pr-3">Niche</th>
              <th className="py-1 pr-3">Stage</th>
              <th className="py-1 pr-3">Location</th>
              <th className="py-1 text-right">Confidence</th>
            </tr>
          </thead>
          <tbody>
            {shown.map((r) => {
              const isOpen = open === r.entity_id;
              const srcs = split(r.sources);
              return (
                <Fragment key={r.entity_id}>
                  <tr id={companyAnchor(r.name)} className="cursor-pointer border-b border-rule align-top hover:bg-panel" onClick={() => setOpen(isOpen ? null : r.entity_id)}>
                    <td className="py-1 pr-3">
                      <button type="button" aria-expanded={isOpen} className="mr-1 text-accent" aria-label={isOpen ? "Hide details" : "Show details"}>
                        {isOpen ? "▾" : "▸"}
                      </button>
                      {r.name}
                    </td>
                    <td className="py-1 pr-3 text-xs">{split(r.niche_tags).join(", ")}</td>
                    <td className="py-1 pr-3">{r.stage || "not disclosed"}</td>
                    <td className="py-1 pr-3">{r.location || "not disclosed"}</td>
                    <td className="py-1 text-right tabular-nums">{r.confidence}</td>
                  </tr>
                  <tr hidden={!isOpen} className="border-b border-rule bg-panel">
                    <td colSpan={5} className="px-3 py-2 text-sm">
                      <dl className="grid grid-cols-1 gap-x-6 gap-y-1 sm:grid-cols-[9rem_1fr]">
                        <dt className="text-muted">What it does</dt>
                        <dd>{r.description || "not stated"}</dd>
                        <dt className="text-muted">Founders</dt>
                        <dd>{r.founders || "not disclosed"}</dd>
                        <dt className="text-muted">Raised</dt>
                        <dd>{r.raised || (/^public company/.test(r.confidence_note) ? "blank: public company" : "not disclosed")}</dd>
                        <dt className="text-muted">Website</dt>
                        <dd>{r.website ? <a href={r.website}>{r.website}</a> : "not stated"}</dd>
                        <dt className="text-muted">Confidence</dt>
                        <dd>
                          {r.confidence} of 100: {r.confidence_note}
                        </dd>
                        <dt className="text-muted">Sources</dt>
                        <dd className="break-all">
                          {srcs.length
                            ? srcs.map((u, i) => (
                                <span key={u}>
                                  {i ? " | " : ""}
                                  <a href={u}>{u.replace(/^https?:\/\/(www\.)?/, "").slice(0, 60)}</a>
                                </span>
                              ))
                            : "none"}
                        </dd>
                        <dt className="text-muted">First seen</dt>
                        <dd>{r.first_seen}</dd>
                      </dl>
                    </td>
                  </tr>
                </Fragment>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
