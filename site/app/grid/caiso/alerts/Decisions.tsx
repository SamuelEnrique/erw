// Energy Research Warehouse (ERW) site, session 7532 (chain 304): the decisions of /grid/caiso/alerts, the Flex Alert
// scorecard, in the form the battery awards page carries (app/cost-of-power/battery/awards/Decisions.tsx): one fold at the
// foot of the page, one line a choice that moves a figure of the page, and on hover, tap or focus its default, its source
// and the session that made it. The page has no input: every choice is fixed when warehouse/derived/flex_alert_scorecard.py
// builds the two tables, and the line says what the figure would do under the other choice where the tables can say.
// Words only: no figure of the page reads it, and it is drawn whether or not the tables could be read.
// docs/methods/caiso_alerts.md, section 6, carries the same list; site/scripts/test-caiso-alerts-render.mjs holds the two
// to one list.
import { Tip } from "@/components/tool/ToolPage";

export type AlertsDecision = { key: string; text: string; session: string; def: string; source: string };

export const ALERTS_DECISIONS: AlertsDecision[] = [
  { key: "alert-day", session: "session 60",
    text: "An alert day is a local day covered by a CAISO notice for its whole area of one of these kinds: Flex Alert, EEA Watch, Energy Emergency Alert 1, 2 or 3, and before May 2022 Alert, Warning, Stage 1, 2 or 3 emergency, or a one-hour probable load interruption. Restricted Maintenance Operations and transmission emergencies are not alert days and stay in the model's training days.",
    def: "Those eleven kinds, the whole area only. 39 alert days from 2018-07-24 to 2024-07-24.",
    source: "California ISO, Grid Emergencies History Report, 1998 to present (the table caiso_grid_emergencies); docs/methods/flex_alert_scorecard.md, section 3." },
  { key: "alert-hours", session: "session 60",
    text: "A day's alert hours are the local hours its notice covers for at least 30 minutes, 23:59 read as midnight, from the day's Flex Alert, else its emergency notices, else its Warnings. A notice over several days covers each with its daily clock window.",
    def: "The Flex Alert's window first. A day with no window stated would take 16:00 to 21:00, marked assumed; none of the 38 needed it. 204 alert hours in all.",
    source: "The notices' time frames as the report prints them; docs/methods/flex_alert_scorecard.md, section 3." },
  { key: "complete-day", session: "session 60",
    text: "A day enters the scorecard only with all 24 hours of demand and weather. An hour of demand below 30 percent of the median hour, or more than 20 percent from both neighbouring hours, is set missing.",
    def: "Complete days only. The screen removed 27 hours, and one alert day, 2021-07-12, is left out: 38 alert days are scored.",
    source: "U.S. EIA, Form EIA-930, CISO balancing authority, hourly Demand; the screen of warehouse/exports/redivis_starter.py; docs/methods/flex_alert_scorecard.md, section 2." },
  { key: "weather", session: "session 60",
    text: "Weather is three airports, each hour's reading the mean of its observations at the nearest hour, gaps of up to two hours filled, and the three weighted by where CAISO's load lives.",
    def: "Los Angeles 0.50, Sacramento 0.30, Fresno 0.20; an hour is kept only when all three have a value.",
    source: "NOAA NCEI, Integrated Surface Database, global-hourly: stations 72295023174, 72483023232, 72389093193 (the table noaa_isd_hourly)." },
  { key: "sample", session: "session 60",
    text: "The model learns from the non-alert days of May to October, from 2018-07-01 (the start of the demand extract) to 2025-10-31, every hour of which is daylight time.",
    def: "1,276 complete non-alert days. An alert day hotter than every one of them is an extrapolation: three are (2020-09-06, 2022-09-08, 2022-09-09).",
    source: "docs/methods/flex_alert_scorecard.md, sections 2 and 4." },
  { key: "model", session: "session 60",
    text: "The prediction is one least-squares regression for each local hour: cooling degree hours, their square, the 24 hours before and its square, the dew point, cooling degree hours times dew point, the day of the week, federal holidays, the month and the year. Four other specifications are fitted and shown in the table of models.",
    def: "Every term (\"chosen\"), the lowest error on hot days it did not see: pooled -503.2 MW. The same without the square of the 24 hours before and the product (\"base\") gives +861.2 MW.",
    source: "docs/methods/flex_alert_scorecard.md, sections 4 and 6; the table flex_alert_model, variant_<name>_pooled_reduction_mw." },
  { key: "sign", session: "session 60",
    text: "A day's cut is predicted less actual demand, averaged over its alert hours: a positive number is demand below the model. A year's and the pooled cut are the mean over every alert hour they hold, so a long day weighs more than a short one.",
    def: "Predicted less actual, MW, the mean over hours; MWh is the sum, percent is the sum over predicted MWh.",
    source: "docs/methods/flex_alert_scorecard.md, section 5." },
  { key: "interval", session: "session 60",
    text: "Each interval is the 5th to 95th percentile over replicates that refit the 24 models on calendar weeks drawn with replacement and add one out-of-fold residual day, centred by hour, to each alert day.",
    def: "90 percent, 1,000 replicates, seed 20261002; the four other specifications 200 each.",
    source: "docs/methods/flex_alert_scorecard.md, section 5." },
  { key: "bias", session: "session 60",
    text: "The model's error on the hottest days it did not see is shown beside the estimate and is not taken off it.",
    def: "Not netted. The model over-predicts those days by 239.3 MW on average; netting it would move the pooled figure to -742.5 MW.",
    source: "The hottest tenth of training days (128 days, a weighted high of at least 87.0 F), five folds, hours 16:00 to 21:00; flex_alert_model, oos_bias_mw and pooled_reduction_mw_net_of_bias." },
  { key: "price", session: "session 60",
    text: "An alert hour's cut is valued at that hour's day-ahead price, the mean of CAISO's SP15 and NP15 hubs, an hour only with both: a wholesale lower bound, with no real-time price, scarcity, reserves or outages avoided.",
    def: "The day-ahead mean of the two hubs. Prices exist for 4 of the 38 days (19 alert hours), since OASIS serves about 39 months of history.",
    source: "California ISO, OASIS PRC_LMP, day-ahead market, TH_SP15_GEN-APND and TH_NP15_GEN-APND (the table caiso_dam_alert_day_hub_prices)." },
  { key: "notices", session: "session 60",
    text: "The column \"CAISO's notices\" lists every kind of notice dated that day in any region, Restricted Maintenance Operations and transmission emergencies left out.",
    def: "The notice's date as the table holds it. One Flex Alert, for 2020-10-01, is dated the day it was issued, 2020-09-30, so that day's cell lacks it (docs/reviews/caiso-alerts-faults-2026-11-16.md, row 3).",
    source: "caiso_grid_emergencies, event_date and event_type." },
];

export function AlertsDecisions() {
  return (
    <details className="mt-10 border-t border-rule pt-3 text-sm" data-decisions="caiso-alerts">
      <summary className="cursor-pointer py-1 text-accent">Decisions on this page ({ALERTS_DECISIONS.length}): each choice that moves a figure, with its default and its source</summary>
      <ul className="mt-2 max-w-3xl list-disc space-y-1 pl-5 text-sm" data-decision-count={ALERTS_DECISIONS.length}>
        {ALERTS_DECISIONS.map((d) => (
          <li key={d.key} data-decision={d.key}>
            {d.text}
            <Tip id={`decision-alerts-${d.key}`} label="this choice's default and source">
              <span className="block" data-decision-default={d.key}><strong>Default:</strong> {d.def}</span>
              <span className="block" data-decision-source={d.key}><strong>Source:</strong> {d.source}</span>
              <span className="block" data-decision-session={d.key}><strong>Made in:</strong> {d.session}.</span>
            </Tip>
          </li>
        ))}
      </ul>
    </details>
  );
}
