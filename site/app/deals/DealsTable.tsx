"use client";
// The /deals table: filters, sorted by date, each row expandable to the whole deal.
import { Fragment, useEffect, useMemo, useState } from "react";
import { Num } from "@/components/Num";

export type Deal = {
  id: string;
  date: string;
  dateBasis: string;
  type: string;
  status: string;
  buyer: string;
  seller: string;
  others: string;
  asset: string;
  technology: string;
  state: string;
  country: string;
  mw: number | null;
  mwh: number | null;
  dollars: number | null;
  priceValue: number | null;
  priceUnit: string;
  termYears: number | null;
  aiPower: boolean;
  confidence: number | null;
  storyUrls: string[];
  source: string;
};

const TYPE_LABEL: Record<string, string> = {
  ppa: "PPA", offtake: "Offtake", m_and_a: "M&A", project_finance: "Project finance", tax_equity: "Tax equity", debt: "Debt",
  equity_raise: "Equity raise", joint_venture: "Joint venture", lease: "Lease", behind_the_meter: "Behind the meter",
  nuclear_restart: "Nuclear restart", smr: "SMR", fuel_supply: "Fuel supply", other: "Other",
};

// session 19: "capital" in the type filter (and /deals?type=capital, the home page's investor path)
// is every financing deal type together
const CAPITAL = ["equity_raise", "debt", "project_finance", "tax_equity"];
const CAPITAL_LABEL = "Capital: equity, debt, project finance, tax equity";

/** US dollars, short: 6000000000 gives "6 billion". scripts/check-values.mjs formats the same way (data-format usd). */
export function usd(v: number): string {
  const t = (x: number) => x.toLocaleString("en-US", { maximumFractionDigits: 2 });
  if (Math.abs(v) >= 1e9) return `${t(v / 1e9)} billion`;
  if (Math.abs(v) >= 1e6) return `${t(v / 1e6)} million`;
  return v.toLocaleString("en-US");
}

const n = (v: number) => v.toLocaleString("en-US", { maximumFractionDigits: 2 });
const day = (d: string) => d.slice(0, 10);
const uniq = (xs: string[]) => Array.from(new Set(xs.filter(Boolean))).sort();

function Select({ label, value, set, options, render }: { label: string; value: string; set: (v: string) => void; options: string[]; render?: (v: string) => string }) {
  return (
    <label className="flex flex-col gap-1 text-xs text-muted">
      {label}
      <select value={value} onChange={(e) => set(e.target.value)} className="border border-rule bg-panel px-2 py-1 text-sm text-ink">
        <option value="">All</option>
        {options.map((o) => (
          <option key={o} value={o}>
            {render ? render(o) : o}
          </option>
        ))}
      </select>
    </label>
  );
}

export function DealsTable({ rows }: { rows: Deal[] }) {
  const [type, setType] = useState("");
  const [tech, setTech] = useState("");
  const [state, setState] = useState("");
  const [ai, setAi] = useState("");
  const [status, setStatus] = useState("");
  const [from, setFrom] = useState("");
  const [to, setTo] = useState("");
  const [open, setOpen] = useState<string | null>(null);
  // a type in the address (/deals?type=capital) sets the filter once, after the page loads
  useEffect(() => {
    const t = new URLSearchParams(window.location.search).get("type");
    if (t && (t === "capital" || rows.some((d) => d.type === t))) setType(t); // eslint-disable-line react-hooks/set-state-in-effect
  }, [rows]);

  const shown = useMemo(
    () =>
      rows
        .filter((d) => (!type || (type === "capital" ? CAPITAL.includes(d.type) : d.type === type)) && (!tech || d.technology === tech) && (!state || d.state === state))
        .filter((d) => (!ai || (ai === "yes") === d.aiPower) && (!status || d.status === status))
        .filter((d) => (!from || day(d.date) >= from) && (!to || day(d.date) <= to))
        .sort((a, b) => (a.date < b.date ? 1 : a.date > b.date ? -1 : a.id.localeCompare(b.id))),
    [rows, type, tech, state, ai, status, from, to],
  );

  return (
    <section aria-label="Deals">
      <div className="mb-3 flex flex-wrap items-end gap-3">
        <Select label="Deal type" value={type} set={setType} options={[...uniq(rows.map((d) => d.type)), "capital"]} render={(v) => (v === "capital" ? CAPITAL_LABEL : TYPE_LABEL[v] ?? v)} />
        <Select label="Technology" value={tech} set={setTech} options={uniq(rows.map((d) => d.technology))} />
        <Select label="State" value={state} set={setState} options={uniq(rows.map((d) => d.state))} />
        <Select label="AI or datacenter power" value={ai} set={setAi} options={["yes", "no"]} />
        <Select label="Status" value={status} set={setStatus} options={uniq(rows.map((d) => d.status))} />
        <label className="flex flex-col gap-1 text-xs text-muted">
          From
          <input type="date" value={from} onChange={(e) => setFrom(e.target.value)} className="border border-rule bg-panel px-2 py-1 text-sm text-ink" />
        </label>
        <label className="flex flex-col gap-1 text-xs text-muted">
          To
          <input type="date" value={to} onChange={(e) => setTo(e.target.value)} className="border border-rule bg-panel px-2 py-1 text-sm text-ink" />
        </label>
        <span className="pb-1 text-xs text-muted">
          {shown.length} of {rows.length} deals
        </span>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full border-collapse text-sm">
          <thead>
            <tr className="border-b border-rule text-left text-xs text-muted">
              <th className="py-1 pr-3 font-normal">Date</th>
              <th className="py-1 pr-3 font-normal">Type</th>
              <th className="py-1 pr-3 font-normal">Parties</th>
              <th className="py-1 pr-3 font-normal">Asset</th>
              <th className="py-1 pr-3 font-normal">Technology</th>
              <th className="py-1 pr-3 font-normal">Where</th>
              <th className="py-1 pr-3 text-right font-normal">MW</th>
              <th className="py-1 pr-3 text-right font-normal">US dollars</th>
              <th className="py-1 pr-3 font-normal">Status</th>
              <th className="py-1 pr-3 font-normal">AI</th>
            </tr>
          </thead>
          <tbody>
            {shown.map((d) => {
              const isOpen = open === d.id;
              const parties = [d.buyer, d.seller].filter(Boolean).join(" / ") || d.others.split(";").join(", ");
              return (
                <Fragment key={d.id}>
                  <tr className="cursor-pointer border-b border-rule/60 align-top hover:bg-panel" onClick={() => setOpen(isOpen ? null : d.id)}>
                    <td className="py-1 pr-3 whitespace-nowrap">
                      <button type="button" aria-expanded={isOpen} className="mr-1 text-accent" aria-label={isOpen ? "Hide details" : "Show details"}>
                        {isOpen ? "▾" : "▸"}
                      </button>
                      {day(d.date)}
                    </td>
                    <td className="py-1 pr-3 whitespace-nowrap">{TYPE_LABEL[d.type] ?? d.type}</td>
                    <td className="py-1 pr-3">{parties}</td>
                    <td className="py-1 pr-3">{d.asset}</td>
                    <td className="py-1 pr-3">{d.technology}</td>
                    <td className="py-1 pr-3 whitespace-nowrap">{[d.state, d.country].filter(Boolean).join(", ")}</td>
                    <td className="py-1 pr-3 text-right tabular-nums">
                      {d.mw !== null ? <Num check={`event|energy_deals|${d.id}|mw`} raw={d.mw}>{n(d.mw)}</Num> : ""}
                    </td>
                    <td className="py-1 pr-3 text-right tabular-nums whitespace-nowrap">
                      {d.dollars !== null ? (
                        <span data-format="usd">
                          <Num check={`event|energy_deals|${d.id}|dollars`} raw={d.dollars}>{usd(d.dollars)}</Num>
                        </span>
                      ) : (
                        ""
                      )}
                    </td>
                    <td className="py-1 pr-3">{d.status}</td>
                    <td className="py-1 pr-3">{d.aiPower ? "yes" : ""}</td>
                  </tr>
                  <tr hidden={!isOpen} className="border-b border-rule/60 bg-panel">
                    <td colSpan={10} className="px-3 py-2 text-sm">
                      <dl className="grid grid-cols-1 gap-x-6 gap-y-1 sm:grid-cols-[10rem_1fr]">
                        <dt className="text-muted">Buyer</dt>
                        <dd>{d.buyer || "not stated"}</dd>
                        <dt className="text-muted">Seller</dt>
                        <dd>{d.seller || "not stated"}</dd>
                        <dt className="text-muted">Other parties</dt>
                        <dd>{d.others ? d.others.split(";").join(", ") : "none named"}</dd>
                        <dt className="text-muted">Capacity</dt>
                        <dd>
                          {d.mw !== null ? `${n(d.mw)} MW` : "MW not stated"}
                          {d.mwh !== null ? `; ${n(d.mwh)} MWh` : ""}
                        </dd>
                        <dt className="text-muted">Value</dt>
                        <dd>{d.dollars !== null ? `USD ${usd(d.dollars)}` : "not stated in US dollars"}</dd>
                        <dt className="text-muted">Price</dt>
                        <dd>{d.priceValue !== null ? `${n(d.priceValue)} ${d.priceUnit}` : "not stated"}</dd>
                        <dt className="text-muted">Term</dt>
                        <dd>{d.termYears !== null ? `${n(d.termYears)} years` : "not stated"}</dd>
                        <dt className="text-muted">Date</dt>
                        <dd>
                          {day(d.date)} ({d.dateBasis === "stated" ? "announced date stated in the story" : "first story's publish date"})
                        </dd>
                        <dt className="text-muted">Model confidence</dt>
                        <dd>{d.confidence !== null ? n(d.confidence) : ""}</dd>
                        <dt className="text-muted">Sources</dt>
                        <dd>
                          {d.storyUrls.map((u, i) => (
                            <span key={u}>
                              {i ? ", " : ""}
                              <a href={u} rel="noopener noreferrer" target="_blank">
                                {i === 0 ? d.source : `story ${i + 1}`}
                              </a>
                            </span>
                          ))}
                        </dd>
                        <dt className="text-muted">Evidence</dt>
                        <dd className="text-muted">
                          The sentence each deal was read from is outlet text, which the ERW does not republish; it is kept in the internal table
                          energy_deals_evidence. Read it in the stories above.
                        </dd>
                      </dl>
                    </td>
                  </tr>
                </Fragment>
              );
            })}
          </tbody>
        </table>
      </div>
      {shown.length === 0 ? <p className="mt-2 text-sm text-muted">No deal matches these filters.</p> : null}
    </section>
  );
}
