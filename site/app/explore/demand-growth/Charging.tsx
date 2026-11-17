// Energy Research Warehouse (ERW) site, session 7709: ruling alternative 1 of /explore/demand-growth (branch
// wip/alt-demand-growth-1; not a default on main). California's growth with the batteries' charging (the table's own
// figure) and a second row without it, for the windows CAISO's own data holds (lib/explore/demandgrowth.ts
// chargingWindows). Drawn on the CAISO view only. A window that cannot be read is said so; no figure is filled.
import { Tip, ToolSection, ToolTable } from "@/components/tool/ToolPage";
import { BASE, monthName, type Charging } from "@/lib/explore/demandgrowth";

const two = (x: number) => `${x > 0 ? "+" : ""}${x.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
const whole = (x: number) => Math.round(x).toLocaleString("en-US");
const span = (w: Charging) => (w.months.length === 1 ? `${monthName(w.months[0])} ${w.year}` : `${monthName(w.months[0])} to ${monthName(w.months[w.months.length - 1])} ${w.year}`);

export function CaliforniaCharging({ windows, unread }: { windows: Charging[]; unread: string | null }) {
  return (
    <ToolSection title="California: growth with and without the batteries' charging"
      note={<>EIA&apos;s demand counts what California&apos;s batteries draw when they charge; the second row takes the charging off.
        <Tip id="demand-growth-charging" label="how the charging is taken off"><span data-charging-tip="1">A month&apos;s charging is, on that month&apos;s average day by CAISO&apos;s own data (shoulder_hours_monthly,
        the batteries&apos; output by local hour), the hours below zero summed, sign turned, over 24: MW on average. A window is the mean of its months, each weighted by its days, against the same months of {BASE};
        the charging is taken off the newer year only ({BASE}&apos;s is not held: the fleet was 186 MW at the end of {BASE}). CAISO&apos;s own data starts later than EIA&apos;s (its first month is the first month of the first window below), so no whole year is given without the charging.
        Default on the site: the table&apos;s row only. Source: EIA Form EIA-930 (eia930_demand_growth); CAISO, Today&apos;s Outlook, supply by fuel (shoulder_hours_monthly); docs/methods/demand_growth.md.</span></Tip></>}>
      {unread !== null ? <p className="text-sm" role="status" data-charging="unread">CAISO&apos;s own data could not be read, so no second row is shown: {unread}</p>
        : windows.length === 0 ? <p className="text-sm" role="status" data-charging="none">No window of months is held by both EIA&apos;s demand and CAISO&apos;s own data.</p> : (
        <ToolTable caption={`California's growth since ${BASE}, with and without the batteries' charging`} minWidth={560}
          head={["Months", `${BASE}, MW`, "Then, MW", "Charging, MW", "Growth, percent", "Less the charging, percent"]}
          rows={windows.map((w) => ({
            key: String(w.year),
            cells: [<span key="s" data-charging-window={w.year}>{span(w)}</span>, whole(w.base), whole(w.eia), whole(w.charging),
              <span key="g" data-charging-growth={w.year}>{two(w.growthPct)}</span>, <span key="l" data-charging-less={w.year}>{two(w.lessChargingPct)}</span>],
          }))} />
      )}
    </ToolSection>
  );
}
