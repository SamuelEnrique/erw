import { SiteLink as Link } from "@/components/SiteLink";
import { Num } from "@/components/Num";
import { abKey, abPair, usdPerMw } from "@/lib/dealspublic";
import type { Deal } from "./DealsTable";

// Session 826: two deals of the table compared side by side, in the battery page's A and B form (components/decisions/
// ScenarioBlock.tsx: the same rows, two columns, a "What differs" row), no verdict. The pair is in the address
// (/deals?a=<deal id>&b=<deal id>), chosen with a plain GET form so the page works without JavaScript and a comparison
// can be shared as a link. Only the shown rows (the public rows' file, session 822) can be chosen: nothing of a held
// row is drawn. Every figure carries its key: a deal's MW and dollars as the table's (dealpub|<id>|mw, |dollars), and
// USD per MW, the one figure computed here (dealpub|ab|<id>|usd_per_mw), only where the deal states both.

const n = (v: number) => v.toLocaleString("en-US", { maximumFractionDigits: 2 });
// US dollars, short, as DealsTable.tsx writes them (data-format usd); its own copy here, since that file is a client
// module and a server component may not call its functions (session 829 found the page failing on it)
function usd(v: number): string {
  const t = (x: number) => x.toLocaleString("en-US", { maximumFractionDigits: 2 });
  if (Math.abs(v) >= 1e9) return `${t(v / 1e9)} billion`;
  if (Math.abs(v) >= 1e6) return `${t(v / 1e6)} million`;
  return v.toLocaleString("en-US");
}
const TYPE: Record<string, string> = {
  ppa: "PPA", offtake: "Offtake", m_and_a: "M&A", project_finance: "Project finance", tax_equity: "Tax equity", debt: "Debt",
  equity_raise: "Equity raise", joint_venture: "Joint venture", lease: "Lease", behind_the_meter: "Behind the meter",
  nuclear_restart: "Nuclear restart", smr: "SMR", fuel_supply: "Fuel supply", other: "Other",
};
// the grid operator that serves most of a state (lib/deals2.ts STATE_GRID); the table holds no point of delivery
const STATE_GRID: Record<string, string> = {
  TX: "ERCOT", CA: "CAISO", NY: "NYISO", CT: "ISO-NE", ME: "ISO-NE", MA: "ISO-NE", NH: "ISO-NE", RI: "ISO-NE", VT: "ISO-NE",
  PA: "PJM", NJ: "PJM", MD: "PJM", DE: "PJM", VA: "PJM", WV: "PJM", OH: "PJM", DC: "PJM", MN: "MISO", IA: "MISO", WI: "MISO", MI: "MISO", LA: "MISO", OK: "SPP", KS: "SPP", NE: "SPP",
};
const NOT = <span className="text-muted">not stated</span>;

function label(d: Deal): string {
  const parties = [d.buyer, d.seller].filter(Boolean).join(" / ") || d.others.split(";").filter(Boolean).join(", ");
  return `${d.date.slice(0, 10)}: ${parties}${d.asset ? `, ${d.asset}` : ""}`.slice(0, 110);
}

export function DealsCompare({ rows, sp }: { rows: Deal[]; sp: Record<string, string | undefined> }) {
  const pair = abPair(sp, rows.map((d) => d.id));
  const a = rows.find((d) => d.id === pair.a), b = rows.find((d) => d.id === pair.b);
  // session 830: a select takes its longest option's width and would run to the page's edge; it stops at the panel's measure
  const field = "w-full max-w-md border border-rule bg-panel px-2 py-1 text-sm text-ink";
  const cell = "px-3 py-1.5 align-top";
  const lines: { label: string; note?: string; of: (d: Deal) => React.ReactNode; differs?: (x: Deal, y: Deal) => string }[] = [
    { label: "Date", note: "the announced date where a story states it, else the first story's publish date", of: (d) => d.date.slice(0, 10) },
    { label: "Type", of: (d) => TYPE[d.type] ?? d.type },
    { label: "Parties", note: "buyer / seller, or the parties named", of: (d) => [d.buyer, d.seller].filter(Boolean).join(" / ") || d.others.split(";").filter(Boolean).join(", ") || NOT },
    { label: "Asset", of: (d) => d.asset || NOT },
    { label: "Technology", of: (d) => d.technology || NOT },
    { label: "Grid", note: "read from the state a story names, for the states one grid operator mostly serves", of: (d) => (d.state && STATE_GRID[d.state]) || (d.state ? `${d.state}: no one grid` : NOT) },
    { label: "Size, MW", of: (d) => (d.mw !== null ? <Num check={`dealpub|${d.id}|mw`} raw={d.mw}>{n(d.mw)}</Num> : NOT), differs: (x, y) => (x.mw !== null && y.mw !== null ? `${n(y.mw - x.mw)} MW` : "") },
    { label: "Term, years", of: (d) => (d.termYears !== null ? n(d.termYears) : NOT) },
    { label: "Value, USD", of: (d) => (d.dollars !== null ? <span data-format="usd"><Num check={`dealpub|${d.id}|dollars`} raw={d.dollars}>{usd(d.dollars)}</Num></span> : NOT), differs: (x, y) => (x.dollars !== null && y.dollars !== null ? `USD ${usd(y.dollars - x.dollars)}` : "") },
    { label: "USD per MW", note: "the value over the size, only where the story states both; nothing is estimated", of: (d) => { const v = usdPerMw(d); return v !== null ? <Num check={abKey(d.id, "usd_per_mw")} raw={v}>{n(v)}</Num> : NOT; } },
    { label: "Status", of: (d) => d.status || NOT },
    { label: "Evidence", note: "the public source the row rests on; other outlets are a count, never a name", of: (d) => <>{(d.publicEvidence ?? []).map((e, i) => <span key={e.url}>{i ? ", " : ""}<a href={e.url} rel="noopener noreferrer" target="_blank">{e.publisher}</a></span>)}{d.otherPublishers ? <span className="text-xs text-muted"> (+{d.otherPublishers} other {d.otherPublishers === 1 ? "outlet" : "outlets"})</span> : null}</> },
  ];
  return (
    <section aria-label="Compare two deals" className="mb-8" data-deals-compare={a && b ? `${a.id}|${b.id}` : "none"}>
      <h2 className="mb-1 text-xl">Compare two deals, A and B</h2>
      <p className="mb-3 max-w-3xl text-sm text-muted">
        Two of the shown deals side by side on the same rows, the figures as the stories state them. No sentence here judges; the last row states what differs.
        The pair is kept in the address, so a comparison can be shared as a link.
      </p>
      <form method="get" action="/deals" className="mb-4 flex max-w-3xl flex-wrap items-end gap-3 text-xs text-muted">
        <label className="flex min-w-0 flex-1 basis-64 flex-col gap-1">
          A
          <select name="a" defaultValue={pair.a ?? ""} className={field} aria-label="Deal A">
            <option value="">choose a deal</option>
            {rows.map((d) => <option key={d.id} value={d.id}>{label(d)}</option>)}
          </select>
        </label>
        <label className="flex min-w-0 flex-1 basis-64 flex-col gap-1">
          B
          <select name="b" defaultValue={pair.b ?? ""} className={field} aria-label="Deal B">
            <option value="">choose a deal</option>
            {rows.map((d) => <option key={d.id} value={d.id}>{label(d)}</option>)}
          </select>
        </label>
        <button type="submit" className="border border-accent bg-accent px-3 py-1 text-white">Compare</button>
        {a && b ? <Link href="/deals" className="pb-1 text-xs underline" data-reset="compare">Reset the comparison</Link> : null}
      </form>
      {a && b ? (
        <div className="overflow-x-auto">
          <table className="w-full border-collapse text-left text-sm" style={{ minWidth: 640 }} data-compare-table="1">
            <caption className="sr-only">Deals A and B side by side</caption>
            <thead>
              <tr className="border-b border-rule text-xs text-muted">
                <th scope="col" className={`${cell} font-normal`}>Row</th>
                <th scope="col" className={`${cell} font-normal`} data-head="a">A: {label(a)}</th>
                <th scope="col" className={`${cell} font-normal`} data-head="b">B: {label(b)}</th>
              </tr>
            </thead>
            <tbody>
              {lines.map((r) => (
                <tr key={r.label} className="border-b border-rule/60">
                  <th scope="row" className={`${cell} font-normal`}>{r.label}{r.note ? <div className="text-xs font-normal text-muted">{r.note}</div> : null}</th>
                  <td className={`${cell} tabular-nums`}>{r.of(a)}</td>
                  <td className={`${cell} tabular-nums`}>{r.of(b)}</td>
                </tr>
              ))}
              <tr className="bg-panel">
                <th scope="row" className={`${cell} font-normal`}>What differs, B against A</th>
                <td className={cell} colSpan={2}>
                  {lines.filter((r) => r.differs && r.differs(a, b)).map((r) => <span key={r.label} className="mr-4">{r.label}: {r.differs!(a, b)}</span>)}
                  {!lines.some((r) => r.differs && r.differs(a, b)) ? <span className="text-muted">No figure both deals state.</span> : null}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      ) : (
        <p className="text-sm text-muted" role="status">{pair.why}</p>
      )}
    </section>
  );
}
