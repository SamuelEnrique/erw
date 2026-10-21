"use client";
// Session 296 (the owner's rulings of 15 October 2026, items 1 to 5, 7 and 10): the left box of /cost-of-power/battery
// is "Assumptions", five sections that open and close, each with a one-line summary of its settings while closed:
// Assumptions (the battery: grid, duration, strategy, size, and the units) and Headline figures open by default;
// Charts, Financing (the twelve assumptions of the scenario in view, the contract as a sub-group) and Sensitivity
// closed. Every choice lives in the address with the two scenarios (lib/battery/view.ts; nothing is requested), so a
// view can be shared as a link. The twelve assumptions are the ones the decisions block drew in the second question
// until this session, moved here unchanged (components/decisions/ScenarioBlock.tsx, ScenarioPanel).
import { useScenarios } from "@/components/decisions/ScenarioBlock";
import { SCALES } from "@/components/tool/SeriesChart";
import { SettingsFold, Tip } from "@/components/tool/ToolPage";
import type { Assumptions } from "@/lib/battery/finance";
import { CHARTS, CHARTS_MAX, HEADS, HEADS_MAX, type ChartKey, type HeadKey } from "@/lib/battery/view";
import { STRATEGIES, type Inputs } from "@/lib/batterystack";
import { BatteryForm } from "./BatteryForm";
import { BatteryFinancing, type StepMeta } from "./Scenarios";
import { useView } from "./ViewState";
import { PriceYearsChoice } from "@/components/tool/PriceYearsChoice";
import type { PriceYear } from "@/lib/priceyears";

const plain = (v: number) => v.toLocaleString("en-US", { maximumFractionDigits: 2 });

/** A row of segments, one pressed: the brand's control in its active state (as the scenario tabs are drawn). */
export function Seg<T extends string>({ label, items, value, onChange, id }: { label: string; items: { key: T; label: string; title?: string }[]; value: T; onChange: (k: T) => void; id: string }) {
  return (
    <span className="inline-grid border border-accent text-sm" style={{ gridTemplateColumns: `repeat(${items.length}, minmax(0, auto))` }} role="group" aria-label={label} data-seg={id}>
      {items.map((it, i) => (
        <button key={it.key} type="button" aria-pressed={value === it.key} data-seg-key={it.key} title={it.title} onClick={() => onChange(it.key)}
          style={value === it.key ? { color: "#fff" } : undefined}
          className={`px-3 py-1 ${i ? "border-l border-accent" : ""} ${value === it.key ? "bg-accent font-semibold" : "bg-white text-accent"}`}>{it.label}</button>
      ))}
    </span>
  );
}

function Picks<T extends string>({ all, chosen, max, onChange, id }: { all: { key: T; label: string; words: string }[]; chosen: T[]; max: number; onChange: (next: T[]) => void; id: string }) {
  const full = chosen.length >= max;
  return (
    <ul className="space-y-1 text-sm" data-picks={id}>
      {all.map((h) => {
        const on = chosen.includes(h.key);
        return (
          <li key={h.key}>
            <label className={`flex items-baseline gap-2 ${!on && full ? "text-muted" : ""}`} title={h.words}>
              <input type="checkbox" checked={on} disabled={!on && full} data-pick={h.key} className="accent-[var(--color-accent)]"
                onChange={(e) => onChange(e.target.checked ? all.filter((a) => chosen.includes(a.key) || a.key === h.key).map((a) => a.key) : chosen.filter((k) => k !== h.key))} />
              <span>{h.label}</span>
            </label>
          </li>
        );
      })}
    </ul>
  );
}

export function Settings({ x, internal, gridName, costs, defaultDs, stepMeta, years = [], yearsRead = true }: {
  x: Inputs; internal: boolean; gridName: string; costs: { capex: number; fom: number; note: string; source: string }; defaultDs: number; stepMeta: StepMeta;
  /** session 352: the price years held for the battery shown, and whether the table could be read */
  years?: PriceYear[]; yearsRead?: boolean;
}) {
  const { v, set } = useView();
  const { s } = useScenarios<Assumptions>();
  const a = s[s.view];
  const size = `${x.mw.toLocaleString("en-US")} MW`;
  const headWords = v.heads.map((k) => HEADS.find((h) => h.key === k)?.label.split(",")[0].split(":")[0]).join(", ");
  const chartWords = v.charts.length ? v.charts.map((k) => CHARTS.find((c) => c.key === k)?.label).join(", ") : "none";
  const contract = a.cshare > 0 ? `${plain(a.cshare)}% contracted at USD ${plain(a.cprice)} per kW-month` : "no contract";
  // session 297: the credit and the fade method, when set
  const more = `${(a.itc ?? 0) > 0 ? `, ${plain(a.itc)}% tax credit` : ""}${(a.method ?? 0) === 1 ? `, capacity fade ${plain(a.fade)}% a year${(a.aug ?? 0) > 0 ? ` restored every ${plain(a.aug)} years` : ""}` : ""}`;
  return (
    <section className="mb-4 bg-paper px-4 py-4" aria-label="Assumptions" data-settings="1">
      <h2 className="mb-1 font-serif text-lg text-accent">Assumptions</h2>
      <SettingsFold id="battery" title="Assumptions" open={true}
        summary={`${gridName}, ${x.dur} hours, ${STRATEGIES[x.strat].toLowerCase()}, ${size}; ${v.units === "kw" ? "per kW" : "this battery"}`}>
        <BatteryForm key={`${x.grid}|${x.dur}|${x.strat}|${x.mw}`} x={x} internal={internal} />
        <div className="mt-3 flex flex-wrap items-center gap-2 text-sm" data-units={v.units}>
          <span className="font-semibold">Units<Tip id="units" label="the units">Per kW of rated power, or this battery: the figures for {size} of power. The headline&apos;s first figure is always per kW.</Tip></span>
          <Seg id="units" label="Units" value={v.units} onChange={(units) => set({ units })}
            items={[{ key: "kw", label: "Per kW" }, { key: "battery", label: `This battery (${size})` }]} />
        </div>
        {/* session 352: the price years the page is priced on (price_years_by_window), at the model's own efficiency and cycles */}
        <PriceYearsChoice ws={years} read={yearsRead} value={v.py} onChange={(py) => set({ py })} unit="USD per kW a year" />
        <p className="mt-3 text-xs leading-snug text-muted" data-costs-in-a="1">
          Defaults for {x.dur} hours: capital {costs.capex.toLocaleString("en-US")} USD/kW and fixed O&amp;M {costs.fom} USD/kW a year ({costs.note}).
          The costs, the debt and a contract are set under <a href="#financing">Financing</a>, below: scenario A gives the headline, and its debt payments default to USD {defaultDs.toLocaleString("en-US")} a year for {size}.
        </p>
      </SettingsFold>

      <SettingsFold id="heads" title="Headline figures" open={true} summary={`${v.heads.length} of ${HEADS.length}: ${headWords}`}>
        <p className="mb-2 text-xs text-muted">Up to {HEADS_MAX} of {HEADS.length}, in this order. Each is scenario A&apos;s.</p>
        <Picks<HeadKey> id="heads" all={HEADS} chosen={v.heads} max={HEADS_MAX} onChange={(heads) => set({ heads: heads.length ? heads : v.heads })} />
      </SettingsFold>

      <SettingsFold id="charts" title="Charts" open={false} summary={`${chartWords}; ${v.scale} scale`}>
        <p className="mb-2 text-xs text-muted">Up to {CHARTS_MAX} of {CHARTS.length}, side by side on a wide screen. Each has a Chart | Table toggle.</p>
        <Picks<ChartKey> id="charts" all={CHARTS} chosen={v.charts} max={CHARTS_MAX} onChange={(charts) => set({ charts })} />
        <div className="mt-3 flex flex-wrap items-center gap-2 text-sm" data-scale={v.scale}>
          <span className="font-semibold">Scale<Tip id="scale" label="the chart scale">{SCALES.map((sc) => <span key={sc.key} className="block">{sc.label}: {sc.words}.</span>)}</Tip></span>
          <Seg id="scale" label="Chart scale" value={v.scale} onChange={(scale) => set({ scale })} items={SCALES.map((sc) => ({ key: sc.key, label: sc.label, title: sc.words }))} />
        </div>
      </SettingsFold>

      <div id="financing">
        <SettingsFold id="financing" title="Financing" open={false}
          summary={`Scenario ${s.view.toUpperCase()}: ${plain(a.share)}% debt at ${plain(a.rate)}%, ${plain(a.hurdle)}% hurdle, ${contract}${more}`}>
          <BatteryFinancing x={x} costs={costs} gridName={gridName} stepMeta={stepMeta} />
        </SettingsFold>
      </div>

      <SettingsFold id="sensitivity" title="Sensitivity" open={false}
        summary={`${v.mode === "range" ? "Sourced range" : `${v.pct} percent step`}, ${v.measure.toUpperCase()}`}>
        <div className="space-y-3 text-sm">
          <div className="flex flex-wrap items-center gap-2" data-mode={v.mode}>
            <span className="font-semibold">Mode<Tip id="mode" label="the sensitivity mode">Sourced range: each assumption moves to its published low and its published high case, Lazard&apos;s Levelized Cost of Energy+ (June 2025) and NREL&apos;s Annual Technology Baseline 2025, with the source in each row&apos;s hover; an assumption the sources state once has no row. Percent step: each assumption moves down and up by the percent you set, held inside its bounds; round-trip efficiency and cycles a day move to the nearest step the model was run at, within their limits.</Tip></span>
            <Seg id="mode" label="Sensitivity mode" value={v.mode} onChange={(mode) => set({ mode })} items={[{ key: "range", label: "Sourced range" }, { key: "pct", label: "Percent step" }]} />
          </div>
          {v.mode === "pct" ? (
            <label className="flex items-center gap-2">
              <span className="font-semibold">Percent</span>
              <input type="number" autoComplete="off" inputMode="numeric" min={1} max={100} step={1} value={v.pct} data-pct="1" aria-label="Percent step" className="w-20 border border-muted bg-white px-2 py-1 text-sm"
                onChange={(e) => { const p = Number(e.target.value); if (Number.isFinite(p) && e.target.value !== "") set({ pct: Math.min(100, Math.max(1, Math.round(p))) }); }} />
              <span className="text-xs text-muted">of each assumption&apos;s value, 1 to 100</span>
            </label>
          ) : null}
          <div className="flex flex-wrap items-center gap-2" data-measure={v.measure}>
            <span className="font-semibold">Measured in<Tip id="measure" label="the sensitivity's measure">NPV to equity at the hurdle rate, or the IRR to equity. A move that leaves no rate of return (NPV of one sign at every rate) draws no bar on that side.</Tip></span>
            <Seg id="measure" label="Sensitivity measure" value={v.measure} onChange={(measure) => set({ measure })} items={[{ key: "npv", label: "NPV" }, { key: "irr", label: "IRR" }]} />
          </div>
        </div>
      </SettingsFold>
    </section>
  );
}
