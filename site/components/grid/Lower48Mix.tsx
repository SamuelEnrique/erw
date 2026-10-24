// Energy Research Warehouse (ERW) site, session 1185 (chain 091): the energy mix panel's view by month for the Lower 48
// (grid_mix_us48, mixp=month). generation_mix_hourly_profile is built for the seven ISO grids only, so the Lower 48's
// months are the sum of the 48 contiguous states and DC in state_generation_mix_monthly (EIA-923), lib/lower48.ts: the
// last 24 months every one of the 49 holds, stacked by fuel group (each group's MWh and share on hover), the newest
// month's MWh and share and the twelve months' MWh, keyed (states_sum, recomputed by scripts/check-values.mjs with the
// same function). The panel says plainly that this is the sum of the states from EIA-923, not EIA-930's US48.
// Its own file (not MixFigures.tsx): it imports nothing of components/mix/Now.tsx (tests/test_session473.py).
import { Num } from "@/components/Num";
import { SiteLink } from "@/components/SiteLink";
import { TimeChart } from "@/components/TimeChart";
import { PanelFile } from "@/components/grid/PanelFile";
import { scrollRegion } from "@/lib/cells";
import { shown } from "@/lib/format";
import { METHOD_MIX_US48 } from "@/lib/gridAnchors";
import { gridHref } from "@/lib/gridtool";
import { LOWER48_STATES, STATE_MIX, lower48Monthly, type L48Fig, type L48Row } from "@/lib/lower48";

/** A figure with its key and its one-line source as the hover tip. */
function F({ f, unit }: { f: L48Fig; unit?: string }) {
  return (
    <span title={f.tip} className="cursor-help border-b border-dotted border-muted">
      <Num check={f.check} raw={f.raw}>{shown(f.raw)}</Num>{unit ?? ""}
    </span>
  );
}

/** The Lower 48 by month, from the 49's rows of state_generation_mix_monthly (read by the caller). */
export function Lower48Monthly({ rows }: { rows: L48Row[] }) {
  const m = lower48Monthly(rows);
  if (!m) {
    return <p className="text-sm italic text-muted" data-missing="1" data-mix-us48-month="none">No month in {STATE_MIX} holds every one of the 48 contiguous states and DC, so no month of the Lower 48 is drawn.</p>;
  }
  const name = (d: string) => d.slice(0, 7);
  const nm = name(m.newest);
  const x = m.months.map((d) => Date.parse(`${d}T00:00:00Z`));
  const caption = `The Lower 48 (the sum of the states): net generation by fuel group in ${nm} and over the twelve months to it`;
  const held = 12 - m.notHeld.length;
  return (
    <div className="mb-2" data-mix-us48-month={m.newest}>
      <p className="mb-1 max-w-3xl text-sm" data-mix-us48-source="1">
        The Lower 48 by month, {name(m.months[0])} to {nm}: the sum of the {LOWER48_STATES.length - 1} contiguous states and the District of Columbia in EIA-923&apos;s
        monthly net generation by state ({STATE_MIX}), not EIA-930&apos;s US48 total, which adds up the balancing authorities hour by hour. A month is drawn only
        when every one of the 49 holds it. Net generation in {nm}: <F f={m.total} /> MWh.
        {m.notHeld.length ? <> Not drawn in the twelve months to {nm}: {m.notHeld.map((g) => `${g.month} (${g.missing.join(", ")} not held)`).join("; ")}.</> : null}
      </p>
      <TimeChart stack share x="month" unit="MWh" height={300}
        ariaLabel={`The Lower 48 (the sum of the states) monthly net generation by fuel group, ${name(m.months[0])} to ${nm}`}
        series={m.fuels.map((f) => ({ name: f.label, color: f.color, points: x.map((t, i) => [t, f.values[i]] as [number, number | null]) }))} />
      <div className="mt-3 overflow-x-auto" {...scrollRegion(caption)}>
        <table className="w-full border-collapse text-sm tabular-nums" style={{ minWidth: 380 }}>
          <caption className="sr-only">{caption}</caption>
          <thead>
            <tr className="border-b border-rule text-left text-xs text-muted">
              <th scope="col" className="py-1 pr-3 font-normal">Fuel group</th>
              <th scope="col" className="py-1 pr-3 text-right font-normal">{nm}, MWh</th>
              <th scope="col" className="py-1 pr-3 text-right font-normal">{nm}, share</th>
              <th scope="col" className="py-1 pr-3 text-right font-normal">12 months to {nm}, MWh{held < 12 ? ` (${held} drawn)` : ""}</th>
            </tr>
          </thead>
          <tbody>
            {m.fuels.map((f) => (
              <tr key={f.key} className="border-b border-rule/60" data-mix-fuel={f.key}>
                <th scope="row" className="py-1 pr-3 text-left font-normal"><span aria-hidden="true" className="mr-1 inline-block h-2.5 w-2.5" style={{ background: f.color }} />{f.label}</th>
                <td className="py-1 pr-3 text-right">{f.mwh ? <F f={f.mwh} /> : ""}</td>
                <td className="py-1 pr-3 text-right">{f.share ? <F f={f.share} unit="%" /> : ""}</td>
                <td className="py-1 pr-3 text-right">{f.year ? <F f={f.year} /> : ""}</td>
              </tr>
            ))}
            <tr className="border-b border-rule/60" data-mix-fuel="total">
              <th scope="row" className="py-1 pr-3 text-left font-normal">Net generation, the nine groups</th>
              <td className="py-1 pr-3 text-right"><F f={m.total} /></td>
              <td className="py-1 pr-3 text-right"></td>
              <td className="py-1 pr-3 text-right"><F f={m.totalYear} /></td>
            </tr>
          </tbody>
        </table>
      </div>
      <p className="mt-1 text-xs text-muted">
        A share is of the nine groups&apos; sum, the states&apos; net generation as EIA totals it; &quot;Not itemized by EIA&quot; is the part of a state&apos;s total that EIA
        withholds by source. Small-scale solar is in no group. EIA-923 is a survey of plants, by state, about two months behind; EIA-930 is the operators&apos;
        hourly report, by balancing authority, so the two Lower 48 totals differ. Hover the chart for each group&apos;s MWh and share in a month.{" "}
        <SiteLink href={METHOD_MIX_US48}>Method: the Lower 48 by month, the sum of the states</SiteLink>
      </p>
      {/* the table as a file, as session 1182's panels offer theirs */}
      <PanelFile of={{ panel: "grid_mix_us48", part: "monthly", title: caption, page: gridHref("us48", "mix", { mixp: "month" }),
        tables: [`${STATE_MIX} (derived from EIA-923's net generation by state, EIA's API route electricity/electric-power-operational-data), summed over the 48 contiguous states and DC`],
        filter: `the 49 locations eia:${LOWER48_STATES.join(", eia:")}: each fuel group's MWh summed over the 49; a month only when every one of them holds it; a share is of the nine groups' sum`,
        window: `Window: ${nm}, and the twelve months ${name(m.from)} to ${nm}${m.notHeld.length ? ` (not drawn: ${m.notHeld.map((g) => g.month).join(", ")})` : ""}` }}
        columns={["Fuel group", `${nm}, MWh`, `${nm}, share, percent`, `12 months to ${nm}, MWh`]}
        rows={[...m.fuels.map((f) => [f.label, f.mwh ? <F key="m" f={f.mwh} /> : "", f.share ? <F key="s" f={f.share} unit="%" /> : "", f.year ? <F key="y" f={f.year} /> : ""]),
          ["Net generation, the nine groups", <F key="t" f={m.total} />, "", <F key="ty" f={m.totalYear} />]]} />
    </div>
  );
}
