"use client";
// Session 40: the severance tax calculator. The rules (data/severance_rules.json) each cite the page that states them;
// the arithmetic is lib/severance.ts. An estimate for education and planning, not tax advice.
import { useMemo, useState } from "react";
import { Tip } from "@/components/tool/ToolPage";
import { compute, type Input, type Option, type Rules } from "@/lib/severance";
import gasData from "@/data/forecast/gas.json";

// ruling alternative 3 (wip/alt-severance-3, not a default on main): one Mcf is 1.034 MMBtu, the heat content /impact uses
const MMBTU_PER_MCF = gasData.btu_per_cf / 1000;

const usd = (v: number) => `$${v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
const pct = (r: number) => `${(r * 100).toLocaleString("en-US", { maximumFractionDigits: 4 })}%`;
const field = "w-full border border-rule bg-panel px-2 py-1 text-sm";

export function Calculator({ rules, prices }: { rules: Rules; prices: { oil: number | null; gas: number | null; label: { oil: string; gas: string } } }) {
  const [state, setState] = useState("TX");
  const products = Object.keys(rules.states[state].products);
  const [product, setProduct] = useState("oil");
  const prod = rules.states[state].products[product] ?? rules.states[state].products[products[0]];
  const kind = product === "gas" ? "gas" : "oil";
  const [volume, setVolume] = useState(1000);
  const [price, setPrice] = useState<number | "">(prices.oil ?? "");
  const [variant, setVariant] = useState("la_oil_pre2025");
  const choice = 0.0024;
  // session 7502: the district chosen is kept by its label, not by its rate: three pairs of TRD's 35 districts share a
  // rate (Rio Arriba 3910 and 3920, Roosevelt 4110 and 4130, San Juan 4521 and 4530), and a list keyed by the rate
  // showed the first of a pair when a reader chose the second (docs/reviews/severance-faults-2026-11-16.md, row 3)
  const [district, setDistrict] = useState("");
  const districtRate = prod.base.find((b) => b.rate === "district")?.districts?.list.find((d) => d.label === district)?.rate;
  const adval = districtRate === undefined ? 0 : Math.round(districtRate * 1e6) / 1e4;
  const [royaltyPct, setRoyaltyPct] = useState(0);
  const [trucking, setTrucking] = useState(0);
  const [transport, setTransport] = useState(0);
  const [option, setOption] = useState<string>("");
  const [param, setParam] = useState<Record<string, number>>({});
  const [tier, setTier] = useState<Record<string, number>>({});
  // session 41: a report period for the Texas low-producing credits; the tier follows from its certified price
  const [period, setPeriod] = useState<Record<string, string>>({});
  const [credit, setCredit] = useState<string>("");

  function latest(id: string): string | undefined {
    const o = Object.values(rules.states).flatMap((st) => Object.values(st.products)).flatMap((pr) => pr.options).find((q) => q.id === id);
    return o?.certified?.prices[0]?.period;
  }
  // session 7511 (docs/reviews/severance-read-2026-11-16.md, rows 1 and 3): a certified price is drawn to the cent
  // ("$1.20", not "$1.2"); and the list's own tip says the period is the production month, which month's mean the price
  // box opened on, and that choosing a period does not change the price: until then a reader saw August's certified
  // price beside October's hub price with no word that they were two months
  const tierPick = (o: Option) => o.certified ? (
    <div className="ml-5" data-report-period={o.id}>
      <span className="text-xs">Report period (the production month)
        <Tip id={`sev-period-${o.id}`} label="the report period and the price">
          <span className="block">The credit follows the Comptroller&apos;s certified price of the month chosen here. The latest month this page holds is {o.certified.as_of}.</span>
          <span className="block">The price box is not changed by this list. It opened on: {kind === "gas" ? prices.label.gas : prices.label.oil}. For another month, type that month&apos;s price; the Lease tab prices each month of a file at its own mean.</span>
        </Tip>
      </span>
      <select value={period[o.id] ?? o.certified.prices[0].period} onChange={(e) => setPeriod({ ...period, [o.id]: e.target.value })} className={field + " text-xs"} aria-label={`Report period, ${o.name}`}>
        {o.certified.prices.map((p) => <option key={p.period} value={p.period}>Report period {p.period}: certified ${p.price.toFixed(2)} ({p.eligibility})</option>)}
      </select>
    </div>
  ) : (
    <select value={tier[o.id] ?? 0} onChange={(e) => setTier({ ...tier, [o.id]: Number(e.target.value) })} className={field + " ml-5 text-xs"}>
      {o.tiers!.map((t) => <option key={t.pct} value={t.pct}>{t.label}</option>)}
    </select>
  );
  const pick = (s: string, p: string) => {
    const ps = Object.keys(rules.states[s].products);
    const np = ps.includes(p) ? p : ps[0];
    setState(s); setProduct(np); setOption(""); setCredit("");
    setPrice((np === "gas" ? prices.gas : prices.oil) ?? "");
  };
  const x: Input = {
    state, product, volume, price: typeof price === "number" ? price : 0, variant, choice, adval, royaltyPct, trucking, transport, mmbtuPerMcf: MMBTU_PER_MCF,
    option: option ? { id: option, param: param[option], tierPct: tier[option], period: period[option] ?? latest(option) } : undefined,
    credit: credit ? { id: credit, tierPct: tier[credit] ?? 0, period: period[credit] ?? latest(credit) } : undefined,
  };
  const r = useMemo(() => {
    // session 282: an empty price is no result, not a price of 0 (the line "Enter a volume and a price." then shows)
    if (price === "") return null;
    try { return compute(rules, x); } catch { return null; }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [JSON.stringify(x)]);
  // session 282: every input back to what the page opens on
  const reset = () => {
    setState("TX"); setProduct("oil"); setVolume(1000); setPrice(prices.oil ?? ""); setVariant("la_oil_pre2025");
    setDistrict(""); setRoyaltyPct(0); setTrucking(0); setTransport(0); setOption(""); setParam({}); setTier({}); setPeriod({}); setCredit("");
  };
  const src = (id: string) => rules.sources[id];
  const Cite = ({ id }: { id: string }) => <a href={src(id)?.url} className="text-xs">{src(id)?.publisher === "Louisiana State Legislature" ? "La. R.S. 47:633" : src(id)?.title}</a>;
  const rateOpts = prod.options.filter((o) => o.group === "rate");
  const credits = prod.options.filter((o) => o.group === "credit");
  const st = rules.states[state];
  const nm = state === "NM", la = state === "LA";

  return (
    <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.2fr)]">
      <div className="space-y-3 text-sm">
        <p className="text-xs"><button type="button" onClick={reset} className="underline">Reset to the defaults</button><span className="text-muted">: Texas, oil, a monthly volume of 1,000 at the latest price shown, no deductions.</span></p>
        <div className="grid grid-cols-2 gap-3">
          <label className="flex flex-col">State
            <select value={state} onChange={(e) => pick(e.target.value, product)} className={field}>
              {Object.entries(rules.states).map(([k, s]) => <option key={k} value={k}>{s.name}</option>)}
            </select>
          </label>
          <label className="flex flex-col">Product
            <select value={product} onChange={(e) => pick(state, e.target.value)} className={field}>
              {Object.keys(st.products).map((p) => <option key={p} value={p}>{p}</option>)}
            </select>
          </label>
          {/* session 7511 (the read's row 9): the label and its tip sit beside each other, the tip outside the label so the
              box keeps its one name; the tip says the tax follows the volume in proportion, so an owner's share of a
              month can be typed. Who bears the tax is no rule this page has read, and the tip says so */}
          <div className="flex flex-col" data-volume-share="1">
            <span><label htmlFor="sev-volume">Monthly volume, {prod.unit}</label>
              <Tip id="sev-volume-share" label="the volume and a share of it">
                <span className="block">Every tax and fee here is in proportion to the volume: the whole well&apos;s or lease&apos;s month gives the whole tax, and one owner&apos;s share of the volume (a one-eighth royalty: the month&apos;s volume divided by 8) gives the tax on that share.</span>
                <span className="block">Who bears the tax, the operator or each owner, is not a rule this page has read.</span>
              </Tip>
            </span>
            <input id="sev-volume" type="number" min={0} value={volume} onChange={(e) => setVolume(Math.max(0, Number(e.target.value)))} className={field} />
          </div>
          {kind === "gas" ? (
            <div className="flex flex-col" data-mmbtu-per-mcf={MMBTU_PER_MCF}>
              <span><label htmlFor="sev-price">Price, USD per MMBtu</label>
                <Tip id="sev-mmbtu-per-mcf" label="the price per MMBtu and the Mcf">
                  <span className="block">Gas is priced per MMBtu (Henry Hub) and taxed per Mcf: each Mcf is taken as {MMBTU_PER_MCF.toLocaleString("en-US", { maximumFractionDigits: 3 })} MMBtu, the heat content of natural gas ({gasData.btu_per_cf.toLocaleString("en-US")} Btu a cubic foot), as the forecast tool prices it. A tax that is a percent of value moves with it; a tax per Mcf (Louisiana&apos;s) does not.</span>
                  <span className="block">Default on the site: one Mcf priced as one MMBtu. Source: EIA, Heat Content of Natural Gas Consumed, U.S., Electric Power, {gasData.btu_per_cf_source.year}.</span>
                </Tip>
              </span>
              <input id="sev-price" type="number" min={0} step="0.01" value={price} onChange={(e) => setPrice(e.target.value === "" ? "" : Number(e.target.value))} className={field} />
            </div>
          ) : (
            <label className="flex flex-col">Price, USD per {prod.unit}
              <input type="number" min={0} step="0.01" value={price} onChange={(e) => setPrice(e.target.value === "" ? "" : Number(e.target.value))} className={field} />
            </label>
          )}
        </div>
        <p className="text-xs text-muted">Default price (an assumption, edit it): {kind === "gas" ? prices.label.gas : prices.label.oil}. A hub price is not the value at the well, which is what the states tax.</p>
        {la && product === "oil" ? (
          <label className="flex flex-col">Well completion
            <select value={variant} onChange={(e) => setVariant(e.target.value)} className={field}>
              {prod.variants?.map((v) => <option key={v.id} value={v.id}>{v.label} ({pct(v.rate)})</option>)}
            </select>
          </label>
        ) : null}
        {la && st.value_deduction?.products.includes(product) ? (
          <label className="flex flex-col">{st.value_deduction.label}
            <input type="number" min={0} step="0.01" value={transport} onChange={(e) => setTransport(Math.max(0, Number(e.target.value)))} className={field} />
          </label>
        ) : null}
        {nm ? (
          <div className="grid grid-cols-2 gap-3">
            <label className="flex flex-col">Royalties to the US, NM or a tribe, % of value
              <input type="number" min={0} max={100} step="0.1" value={royaltyPct} onChange={(e) => setRoyaltyPct(Math.min(100, Math.max(0, Number(e.target.value))))} className={field} />
            </label>
            <label className="flex flex-col">Trucking, USD per {prod.unit}
              <input type="number" min={0} step="0.01" value={trucking} onChange={(e) => setTrucking(Math.max(0, Number(e.target.value)))} className={field} />
            </label>
            <label className="col-span-2 flex flex-col">Ad valorem production: your unit&apos;s county, district and suffix (TRD&apos;s 2026 table)
              <select value={district} onChange={(e) => setDistrict(e.target.value)} className={field} data-nm-district={district || "none"}>
                <option value="">Not chosen: ad valorem left out</option>
                {prod.base.find((b) => b.rate === "district")?.districts?.list.map((d) => <option key={d.label} value={d.label}>{d.label}: {(d.rate * 100).toFixed(4)}%</option>)}
              </select>
            </label>
          </div>
        ) : null}
        <fieldset className="border border-rule p-2">
          <legend className="px-1 text-xs text-muted">Reduced rate or exemption (one per well and month)</legend>
          <label className="block"><input type="radio" name="opt" checked={option === ""} onChange={() => setOption("")} /> None: the base rate</label>
          {rateOpts.length === 0 ? <p className="text-xs text-muted">None listed for {st.name} {product} on the pages read (see the method).</p> : null}
          {rateOpts.map((o) => (
            <div key={o.id} className="mt-1">
              <label className="block"><input type="radio" name="opt" checked={option === o.id} onChange={() => setOption(o.id)} /> {o.name}</label>
              {option === o.id && (o.kind === "rate_param" || o.kind === "hcg_ratio") ? (
                <label className="ml-5 flex flex-col text-xs">{o.param!.label}
                  <input type="number" min={o.param!.min} max={o.param!.max} step="0.1" value={param[o.id] ?? o.param!.default} onChange={(e) => setParam({ ...param, [o.id]: Math.min(o.param!.max, Math.max(o.param!.min, Number(e.target.value))) })} className={field} />
                </label>
              ) : null}
              {option === o.id && o.kind === "credit_tier" ? tierPick(o) : null}
            </div>
          ))}
        </fieldset>
        {credits.map((o) => (
          <div key={o.id}>
            <label className="block"><input type="checkbox" checked={credit === o.id} onChange={(e) => setCredit(e.target.checked ? o.id : "")} /> {o.name}</label>
            {credit === o.id ? tierPick(o) : null}
          </div>
        ))}
      </div>

      <div className="text-sm">
        {!r ? <p className="text-muted">Enter a volume and a price.</p> : (
          <>
            <table className="w-full">
              <tbody>
                <tr><td className="py-1">Gross value</td><td className="text-right font-mono">{usd(r.gross)}</td><td /></tr>
                {r.taxable !== r.gross ? <tr><td className="py-1">Taxable value, after the deductions the rule states</td><td className="text-right font-mono">{usd(r.taxable)}</td><td className="pl-2">{st.value_deduction ? <Cite id={st.value_deduction.cite} /> : null}</td></tr> : null}
                {r.base.map((l) => {
                  // session 7511 (the read's rows 5 and 6): the district's rate is TRD's rate table's, so the line cites the
                  // table (as the Lease tab does), not TRD's general page; and with no district chosen the line says the
                  // tax is left out and how far the districts run, where it read "0%" and "$0.00" as if none were owed
                  const dist = prod.base.find((b) => b.id === l.id && b.rate === "district")?.districts;
                  const out = dist && districtRate === undefined;
                  const rs = dist ? dist.list.map((d) => d.rate) : [];
                  return (
                    <tr key={l.id} className="border-t border-rule" data-base-line={l.id} data-left-out={out ? "1" : undefined}>
                      <td className="py-1">{l.name}, {out ? `no district chosen: left out of the total (${(Math.min(...rs) * 100).toFixed(4)}% to ${(Math.max(...rs) * 100).toFixed(4)}% by district)` : l.basis === "per_unit" ? `$${l.rate} per ${prod.unit}` : pct(l.rate)}</td>
                      <td className="text-right font-mono">{out ? "left out" : usd(l.tax)}</td><td className="pl-2"><Cite id={dist ? dist.cite : l.cite} /></td>
                    </tr>
                  );
                })}
                <tr className="border-t border-ink font-semibold"><td className="py-1">Tax at the base rate</td><td className="text-right font-mono">{usd(r.baseTotal)}</td><td /></tr>
                {r.applied.map((a) => (
                  <tr key={a.id}><td className="py-1 text-muted">{a.name}: {a.effect}</td><td /><td className="pl-2"><Cite id={a.cite} /></td></tr>
                ))}
                <tr className="font-semibold"><td className="py-1">Tax with the exemptions chosen</td><td className="text-right font-mono">{usd(r.withTotal)}</td><td /></tr>
                <tr className="font-semibold text-[var(--color-down)]"><td className="py-1">Savings</td><td className="text-right font-mono">{usd(r.savings)}</td><td /></tr>
                {r.fees.map((f) => (
                  <tr key={f.id} className="border-t border-rule"><td className="py-1 text-muted">{f.name} (a fee, not in the tax or the savings)</td><td className="text-right font-mono text-muted">{usd(f.amount)}</td><td className="pl-2"><Cite id={f.cite} /></td></tr>
                ))}
              </tbody>
            </table>
            {[...rateOpts, ...credits].filter((o) => o.id === option || o.id === credit).map((o) => (
              <div key={o.id} className="mt-3 border-l-2 border-accent pl-2 text-xs">
                <p><strong>{o.name}.</strong> Who qualifies: {o.who}. What it reduces: {o.what}.{o.how_long ? ` How long: ${o.how_long}.` : ""}</p>
                <p className="text-muted">&quot;{o.quote}&quot; (<Cite id={o.cite} />)</p>
                {o.code ? <p className="text-muted">{o.code.section}: &quot;{o.code.quote}&quot; (<Cite id={o.code.cite} />)</p> : null}
              </div>
            ))}
            <p className="mt-3 text-xs text-muted">{st.basis_note}</p>
          </>
        )}
      </div>
    </div>
  );
}
