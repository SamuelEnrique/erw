"use client";
// Session 45: severance v0.2, the lease tool. The reader's file is read with the browser's File API and computed here
// (lib/lease.ts on lib/severance.ts); this component makes no network request: no fetch, no form post, no upload. The
// results and the template download as Blobs made in the page. An estimate for education and planning, not tax advice.
import { useMemo, useState } from "react";
import {
  analyzeLease, bestTicks, COLUMN_HELP, COLUMNS, parseLease, PRODUCTS, SAMPLE_CSV, TEMPLATE_CSV, ticksFromFile, toCsv,
  type Analysis, type PriceBook, type Product,
} from "@/lib/lease";
import { compute, creditPct, type Rules } from "@/lib/severance";

const usd = (v: number | null) => (v === null ? "n/a" : `$${v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`);
const field = "border border-rule bg-panel px-2 py-1 text-sm";
const btn = "border border-rule bg-panel px-3 py-1 text-sm hover:border-accent";

/** Save text as a file, from a Blob made in the page (nothing leaves the browser). */
function save(name: string, text: string) {
  const url = URL.createObjectURL(new Blob([text], { type: "text/csv;charset=utf-8" }));
  const a = document.createElement("a");
  a.href = url;
  a.download = name;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

// session 49: `initial`, a file the server rendered into the page (the internal real-lease route); still no request
export function LeaseTool({ rules, prices, initial }: { rules: Rules; prices: PriceBook; initial?: { text: string; source: string } }) {
  const [text, setText] = useState(initial?.text ?? "");
  const [source, setSource] = useState(initial?.source ?? "");
  const [manual, setManual] = useState<Record<string, string[]> | null>(null);
  const [over, setOver] = useState(false);
  const load = (t: string, from: string) => { setText(t); setSource(from); setManual(null); };

  const parsed = useMemo(() => (text.trim() ? parseLease(text, rules) : null), [text, rules]);
  const fileTicks = useMemo(() => (parsed ? ticksFromFile(rules, parsed.rows) : { ticks: {}, unknown: [] }), [parsed, rules]);
  const ticks = manual ?? fileTicks.ticks;
  const a: Analysis | null = useMemo(
    () => (parsed && parsed.rows.length ? analyzeLease(rules, { compute, creditPct }, parsed.rows, { prices, ticks }) : null),
    [parsed, rules, prices, ticks],
  );
  const issues = [...(parsed?.errors ?? []), ...fileTicks.unknown, ...(a?.issues ?? [])];

  function readFile(f: File | undefined) {
    if (!f) return;
    f.text().then((t) => load(t, f.name));
  }
  function setRate(key: string, product: Product, id: string) {
    const opts = rules.states[key.split("|")[0]].products[product]?.options ?? [];
    const drop = new Set(opts.filter((o) => o.group === "rate").map((o) => o.id));
    const cur = (ticks[key] ?? []).filter((x) => !drop.has(x));
    setManual({ ...ticks, [key]: id ? [...cur, id] : cur });
  }
  function setCredit(key: string, id: string, on: boolean) {
    const cur = (ticks[key] ?? []).filter((x) => x !== id);
    setManual({ ...ticks, [key]: on ? [...cur, id] : cur });
  }
  const src = (id: string) => rules.sources[id];
  const CiteLink = ({ id }: { id: string }) => <a href={src(id)?.url} className="text-xs">{src(id)?.title ?? id}</a>;

  return (
    <div className="space-y-6 text-sm">
      <div className="grid gap-4 lg:grid-cols-[minmax(0,1.2fr)_minmax(0,1fr)]">
        <div className="space-y-2">
          <label
            className={`flex min-h-24 cursor-pointer flex-col items-center justify-center border-2 border-dashed p-4 text-center ${over ? "border-accent" : "border-rule"}`}
            onDragOver={(e) => { e.preventDefault(); setOver(true); }}
            onDragLeave={() => setOver(false)}
            onDrop={(e) => { e.preventDefault(); setOver(false); readFile(e.dataTransfer.files[0]); }}
          >
            <span><strong>Drop a CSV here</strong>, or click to choose one. It is read in this tab only.</span>
            <input type="file" accept=".csv,.txt,text/csv,text/plain" className="sr-only" onChange={(e) => readFile(e.target.files?.[0])} />
            {source ? <span className="mt-1 text-xs text-muted">Loaded: {source}</span> : null}
          </label>
          <label className="flex flex-col">Or paste the rows (a header line first)
            <textarea value={text} onChange={(e) => load(e.target.value, "pasted rows")} rows={7} spellCheck={false}
              className={field + " font-mono text-xs"} placeholder={COLUMNS.join(",")} />
          </label>
          <div className="flex flex-wrap gap-2">
            <button type="button" className={btn} onClick={() => load(SAMPLE_CSV, "the sample lease (fictional wells)")}>Try the sample (fictional wells)</button>
            <button type="button" className={btn} onClick={() => save("erw_lease_template.csv", TEMPLATE_CSV)}>Download the template</button>
            <button type="button" className={btn} onClick={() => save("erw_lease_sample_fictional.csv", SAMPLE_CSV)}>Download the sample</button>
            {text ? <button type="button" className={btn} onClick={() => load("", "")}>Clear</button> : null}
          </div>
          <p className="text-xs text-muted">
            The sample&apos;s wells, FICTIONAL-TX-1 to FICTIONAL-NM-3, are made up: not real wells, operators or production. They are there to show what
            each flag looks like.
          </p>
        </div>
        <details className="border border-rule p-2" open={!text}>
          <summary className="cursor-pointer">The columns ({COLUMNS.length}; state, well_id and month are required)</summary>
          <dl className="mt-2 grid grid-cols-[auto_1fr] gap-x-3 gap-y-1 text-xs">
            {COLUMNS.map((c) => [<dt key={c} className="font-mono">{c}</dt>, <dd key={c + "d"} className="text-muted">{COLUMN_HELP[c]}</dd>])}
          </dl>
        </details>
      </div>

      {issues.length ? (
        <div className="border-l-2 border-accent pl-2">
          <p className="font-semibold">Rows to check ({issues.length})</p>
          <ul className="list-disc pl-5 text-xs">
            {issues.slice(0, 50).map((e, i) => <li key={i}>{e.line ? `Line ${e.line}: ` : ""}{e.message}</li>)}
          </ul>
          {parsed?.unknownColumns.length ? <p className="text-xs text-muted">Columns not used: {parsed.unknownColumns.join(", ")}.</p> : null}
        </div>
      ) : null}

      {a ? (
        <>
          <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
            {[
              ["Base tax, the lease", usd(a.lease.base)],
              ["With the rules you ticked", usd(a.lease.withTicked)],
              ["Potential savings, flagged rules", usd(a.lease.potential)],
              ["Regulatory fees (not in the tax)", usd(a.lease.fees)],
            ].map(([k, v]) => (
              <div key={k} className="border border-rule bg-panel p-3">
                <div className="text-xs text-muted">{k}</div>
                <div className="text-xl">{v}</div>
              </div>
            ))}
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <button type="button" className={btn} onClick={() => save("erw_lease_severance_results.csv", toCsv(a, rules.version))}>Download the results (CSV)</button>
            <button type="button" className={btn} onClick={() => setManual(bestTicks(a, rules))}>Tick the best flagged rule of each well</button>
            <button type="button" className={btn} onClick={() => setManual({})}>Untick all</button>
            <span className="text-xs text-muted">Potential savings take, for each well, month and product, the one flagged rule that saves the most (reduced rates do not stack).</span>
          </div>

          <div>
            <h3 className="mb-1 text-base">May qualify: the largest potential savings first</h3>
            {a.opportunities.length === 0 ? <p className="text-muted">No rule&apos;s thresholds are met by the numbers in the file.</p> : (
              <table className="w-full text-left text-xs">
                <thead><tr className="border-b border-rule"><th className="py-1">Well</th><th>Rule</th><th>Months</th><th className="text-right">Savings</th><th>Source</th></tr></thead>
                <tbody>
                  {a.opportunities.map((o) => (
                    <tr key={o.key + o.id} className="border-b border-rule">
                      <td className="py-1">{o.well} ({o.state})</td>
                      <td>{o.name} <span className="font-mono text-muted">{o.id}</span></td>
                      <td>{o.months.join(", ")}</td>
                      <td className="text-right">{usd(o.savings)}</td>
                      <td><CiteLink id={o.cite} /></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>

          <div>
            <h3 className="mb-1 text-base">Each well: totals and the rules you tick</h3>
            <div className="space-y-3">
              {a.wells.map((w) => {
                const prods = PRODUCTS.filter((p) => a.lines.some((l) => l.key === w.key && l.product === p));
                const flagged = new Set(a.lines.filter((l) => l.key === w.key).flatMap((l) => l.flags.filter((f) => !f.info).map((f) => f.id)));
                return (
                  <div key={w.key} className="border border-rule p-2">
                    <div className="flex flex-wrap justify-between gap-2">
                      <strong>{w.well} ({rules.states[w.state].name}), {w.months} month{w.months === 1 ? "" : "s"}</strong>
                      <span>base {usd(w.base)}; with ticks {usd(w.withTicked)}; potential savings {usd(w.potential)}</span>
                    </div>
                    <div className="mt-1 flex flex-wrap gap-4">
                      {prods.map((p) => {
                        const opts = rules.states[w.state].products[p]?.options ?? [];
                        const rate = opts.filter((o) => o.group === "rate"), credits = opts.filter((o) => o.group === "credit");
                        const cur = rate.find((o) => (ticks[w.key] ?? []).includes(o.id))?.id ?? "";
                        return (
                          <div key={p} className="text-xs">
                            <label className="flex flex-col">{p}: reduced rate or exemption
                              <select value={cur} onChange={(e) => setRate(w.key, p, e.target.value)} className={field + " text-xs"}>
                                <option value="">None: the base rate</option>
                                {rate.map((o) => <option key={o.id} value={o.id}>{flagged.has(o.id) ? "May qualify: " : ""}{o.name}</option>)}
                              </select>
                            </label>
                            {credits.map((o) => (
                              <label key={o.id} className="mt-1 block">
                                <input type="checkbox" checked={(ticks[w.key] ?? []).includes(o.id)} onChange={(e) => setCredit(w.key, o.id, e.target.checked)} />{" "}
                                {flagged.has(o.id) ? "May qualify: " : ""}{o.name}
                              </label>
                            ))}
                          </div>
                        );
                      })}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          <div>
            <h3 className="mb-1 text-base">Every well, month and product</h3>
            <div className="overflow-x-auto">
              <table className="w-full min-w-[56rem] text-left text-xs">
                <thead>
                  <tr className="border-b border-rule">
                    <th className="py-1">Well</th><th>Month</th><th>Product</th><th className="text-right">Volume</th><th className="text-right">Price</th>
                    <th className="text-right">Base tax</th><th className="text-right">With ticks</th><th>May qualify (the well&apos;s numbers against the rule)</th>
                  </tr>
                </thead>
                <tbody>
                  {a.lines.map((l) => (
                    <tr key={`${l.key}|${l.month}|${l.product}`} className="border-b border-rule align-top">
                      <td className="py-1">{l.well}</td><td>{l.month}</td><td>{l.product}</td>
                      <td className="text-right">{l.volume.toLocaleString("en-US")} {l.unit}</td>
                      <td className="text-right" title={l.priceSource}>{l.price === null ? "none" : `$${l.price.toFixed(2)}`}<div className="text-muted">{l.priceSource === "the file" ? "file" : "warehouse"}</div></td>
                      <td className="text-right">{usd(l.base)}</td>
                      <td className="text-right">{usd(l.withTicked)}{l.ticked.length ? <div className="font-mono text-muted">{l.ticked.join(", ")}</div> : null}</td>
                      <td>
                        {l.flags.map((f) => (
                          <div key={f.id} className="mb-1">
                            {f.info ? <span className="text-muted">{f.name}: </span> : <strong>{f.name}, saves {usd(f.savings)}: </strong>}
                            {f.test}{f.notes.length ? <span className="text-muted">. {f.notes.join("; ")}</span> : null}. <CiteLink id={f.cite} />
                          </div>
                        ))}
                        {l.notes.map((n, i) => <div key={i} className="text-muted">{n}</div>)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p className="mt-1 text-xs text-muted">
              Prices marked &quot;warehouse&quot; are the month&apos;s hub means (hover for the label), not the value at the well, which is what the states tax.
              Texas&apos;s low-producing credits use the Comptroller&apos;s certified price of the production month (2005 dollars), never the price here.
            </p>
          </div>
        </>
      ) : null}
    </div>
  );
}
