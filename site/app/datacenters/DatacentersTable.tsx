"use client";
// The /datacenters table (session 16): filters in one row, one row per facility, story links on each.
import { useMemo, useState } from "react";

export type Facility = {
  id: string;
  operator: string;
  developer: string;
  site: string;
  state: string;
  county: string;
  city: string;
  mw: number | null;
  phase: string;
  status: string;
  plannedYear: string;
  power: string;
  utility: string;
  confidence: number | null;
  placed: boolean;
  firstStory: string;
  storyUrls: string[];
};

const uniq = (xs: string[]) => Array.from(new Set(xs.filter(Boolean))).sort();
const label = (s: string) => s.replace("_", " ");

function Select({ name, value, set, options }: { name: string; value: string; set: (v: string) => void; options: string[] }) {
  return (
    <label className="flex flex-col gap-1 text-xs text-muted">
      {name}
      <select value={value} onChange={(e) => set(e.target.value)} className="border border-rule bg-panel px-2 py-1 text-sm text-ink">
        <option value="">All</option>
        {options.map((o) => (
          <option key={o} value={o}>
            {label(o)}
          </option>
        ))}
      </select>
    </label>
  );
}

export function DatacentersTable({ rows }: { rows: Facility[] }) {
  const [state, setState] = useState("");
  const [status, setStatus] = useState("");
  const [operator, setOperator] = useState("");
  const [minMw, setMinMw] = useState("");
  const shown = useMemo(
    () =>
      rows
        .filter((f) => (!state || f.state === state) && (!status || f.status === status) && (!operator || f.operator === operator))
        .filter((f) => !minMw || (f.mw !== null && f.mw >= Number(minMw)))
        .sort((a, b) => b.firstStory.localeCompare(a.firstStory)),
    [rows, state, status, operator, minMw],
  );
  const blank = <span className="text-muted">not stated</span>;
  return (
    <section aria-label="Facilities">
      <div className="mb-2 flex flex-wrap items-end gap-3">
        <Select name="State" value={state} set={setState} options={uniq(rows.map((f) => f.state))} />
        <Select name="Status" value={status} set={setStatus} options={uniq(rows.map((f) => f.status))} />
        <Select name="Operator" value={operator} set={setOperator} options={uniq(rows.map((f) => f.operator))} />
        <label className="flex flex-col gap-1 text-xs text-muted">
          MW at least
          <input
            value={minMw}
            onChange={(e) => setMinMw(e.target.value.replace(/[^0-9.]/g, ""))}
            inputMode="decimal"
            placeholder="any"
            className="w-24 border border-rule bg-panel px-2 py-1 text-sm text-ink"
          />
        </label>
        <span className="pb-1 text-sm text-muted">
          {shown.length} of {rows.length} facilities
        </span>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full border-collapse text-sm">
          <thead>
            <tr className="border-b border-rule text-left text-xs text-muted">
              <th className="py-1 pr-3 font-normal">First reported</th>
              <th className="py-1 pr-3 font-normal">Operator, site</th>
              <th className="py-1 pr-3 font-normal">Place</th>
              <th className="py-1 pr-3 text-right font-normal">MW</th>
              <th className="py-1 pr-3 font-normal">Status</th>
              <th className="py-1 pr-3 font-normal">Planned year</th>
              <th className="py-1 pr-3 font-normal">Power</th>
              <th className="py-1 font-normal">Stories</th>
            </tr>
          </thead>
          <tbody>
            {shown.map((f) => (
              <tr key={f.id} className="border-b border-rule align-top">
                <td className="py-1 pr-3 tabular-nums">{f.firstStory.slice(0, 10)}</td>
                <td className="py-1 pr-3">
                  <div>{f.operator || blank}</div>
                  {f.site ? <div className="text-xs">{f.site}</div> : null}
                  {f.developer && f.developer !== f.operator ? <div className="text-xs text-muted">developer {f.developer}</div> : null}
                  {f.phase ? <div className="text-xs text-muted">{f.phase}</div> : null}
                </td>
                <td className="py-1 pr-3">
                  {[f.city, f.county, f.state].filter(Boolean).join(", ") || blank}
                  {f.placed ? <div className="text-xs text-muted">on the map</div> : null}
                </td>
                <td className="py-1 pr-3 text-right tabular-nums">{f.mw === null ? blank : f.mw.toLocaleString("en-US")}</td>
                <td className="py-1 pr-3">{f.status ? label(f.status) : blank}</td>
                <td className="py-1 pr-3 tabular-nums">{f.plannedYear || blank}</td>
                <td className="py-1 pr-3">
                  {f.power || f.utility ? [f.power, f.utility ? `utility ${f.utility}` : ""].filter(Boolean).join("; ") : blank}
                </td>
                <td className="py-1">
                  {f.storyUrls.map((u, i) => (
                    <a key={u} href={u} target="_blank" rel="noreferrer" className="mr-2">
                      {i + 1}
                    </a>
                  ))}
                  {f.confidence !== null ? <div className="text-xs text-muted">model confidence {f.confidence}</div> : null}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
