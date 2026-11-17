// Energy Research Warehouse (ERW) site, session 7535 (chain 304): the decisions of the home battery game (/play/battery),
// in the form of the battery awards page's block (app/cost-of-power/battery/awards/Decisions.tsx): one fold at the foot of
// the page, one line a choice that moves a figure the game shows (a score, the perfect battery's score, a price played,
// the end table, the fleet), and on hover, tap or focus its default, its source and the session that made it. The
// battery's five settings are editable in place, in the settings panel of the game on Normal and Hard (SettingsPanel in
// Game.tsx, which says each default's source beside its input); every other choice is a fixed game rule, and the line
// says so. The defaults are read from lib/battery.ts's own constants, so a rule changed there changes here. Words only:
// no figure reads it. docs/methods/battery_game.md, "The done line (session 7535)", carries the same list, and
// tests/test_session7535_battery_game.py holds the two to one list of keys.
import { Tip } from "@/components/tool/ToolPage";
import { EMERGENCY, FLEET, LIGHTS_OUT, SETTINGS, SOLAR, START_MONEY } from "@/lib/battery";

export type GameDecision = { key: string; text: string; session: string; def: string; source: string; editable?: boolean };

const pct = (v: number) => `${Math.round(v * 100)} percent`;

export const GAME_DECISIONS: GameDecision[] = [
  { key: "kwh", session: "sessions 38 and 50", editable: true,
    text: "The battery's usable energy: how much it can hold. A larger battery can buy more in the cheap hours and sell more in the dear ones.",
    def: `${SETTINGS.kwh.def} kWh (${SETTINGS.kwh.min} to ${SETTINGS.kwh.max}); set it in the battery's settings on Normal and Hard. Easy plays the default.`,
    source: SETTINGS.kwh.source },
  { key: "kw", session: "sessions 38 and 50", editable: true,
    text: "The battery's continuous power: how much it can buy or sell in fifteen minutes (kW times 0.25 kWh at the meter).",
    def: `${SETTINGS.kw.def} kW (${SETTINGS.kw.min} to ${SETTINGS.kw.max}); set it in the battery's settings on Normal and Hard.`,
    source: SETTINGS.kw.source },
  { key: "rte", session: "sessions 38 and 50", editable: true,
    text: "The round-trip efficiency, split evenly: the square root of it is kept on the way in and again on the way out. Every spread must pay for the loss.",
    def: `${pct(SETTINGS.rte.def)} (${pct(SETTINGS.rte.min)} to ${pct(SETTINGS.rte.max)}); set it in the battery's settings on Normal and Hard.`,
    source: SETTINGS.rte.source },
  { key: "reserve", session: "sessions 50 and 289", editable: true,
    text: "The backup reserve, on Hard only: the battery never sells below it, and only the outage draws on it.",
    def: `${pct(SETTINGS.reserve.def)} of the usable energy, ${(13.5 * SETTINGS.reserve.def).toFixed(2)} kWh of the default battery (0 to ${pct(SETTINGS.reserve.max)}); set it in the battery's settings on Hard.`,
    source: SETTINGS.reserve.source },
  { key: "deg", session: "sessions 50 and 7535", editable: true,
    text: "The wear (degradation cost), on Hard only: charged on each kWh drawn out of the battery, before the loss on the way out, so each kWh sold carries a little more than the setting.",
    def: `USD ${SETTINGS.deg.def.toFixed(2)} per kWh drawn out (0 to ${SETTINGS.deg.max.toFixed(2)}); set it in the battery's settings on Hard.`,
    source: SETTINGS.deg.source },
  { key: "start", session: "session 38", text: "The battery starts every play half full, so a play can sell more than it buys.",
    def: "Half the usable energy; a fixed game rule.", source: "The session 38 game's assumption (docs/methods/battery_game.md, \"The fixed rules\")." },
  { key: "money", session: "session 63", text: `Every play starts with USD ${START_MONEY}, and ends in the first interval the money falls below zero. The perfect battery never does.`,
    def: `USD ${START_MONEY}; a fixed game rule.`, source: "docs/methods/battery_game.md, \"Version 3\"." },
  { key: "price", session: "sessions 38 and 56",
    text: "The battery buys and sells at the real-time price at one hub: ERCOT's hub average, or on the two California days CAISO's SP15 hub, every 15 minutes. No retail rate, no tariff, no grid fee.",
    def: "ERCOT HB_HUBAVG (spp_rtm); CAISO TH_SP15_GEN-APND, the 15-minute means of its 5-minute prices; a fixed game rule.",
    source: "The famous days: ERCOT's historical real-time settlement point prices (NP6-785-ER) and CAISO OASIS interval LMPs (PRC_INTVL_LMP), frozen in site/data/battery_levels.json; today's level: the live set's iso_rtm_hub_prices." },
  { key: "call", session: "session 50",
    text: "The fleet call is the day's dearest clock hour, the earliest on a tie, with fifteen minutes' notice; each kWh delivered in it earns the hour's mean price again, never below zero.",
    def: "One hour, a bonus of the hour's mean price; a fixed game rule, the game's stand-in for what an aggregator may pass on to a home.",
    source: "Modeled on ERCOT's ADER pilot (Governing Document, Phase 3.3, June 2026), which pays no such bonus (docs/methods/battery_game.md, \"The fleet call\")." },
  { key: "spike", session: "session 63",
    text: `On Hard the fleet call's hour climbs toward USD ${EMERGENCY.cap.toLocaleString("en-US")} per MWh: ${EMERGENCY.ramp.map((r) => Math.round(r * 100)).join(", ")} percent of the way from the real price, one step each fifteen minutes. A price already at or above the cap is left as it is.`,
    def: `USD ${EMERGENCY.cap.toLocaleString("en-US")} per MWh on every grid, the California days included; a fixed game rule.`,
    source: "ERCOT's high system-wide offer cap since 1 January 2022: ERCOT market notice M-A120721-01, 7 December 2021." },
  { key: "outage", session: "sessions 63 and 70",
    text: `On Hard the grid then goes down for two hours: nothing is bought or sold, and the house draws ${EMERGENCY.houseKw} kW from the battery (the roof's power first), its reserve included.`,
    def: `Eight intervals after the spike, clipped at the day's end; ${EMERGENCY.houseKw} kW; a fixed game rule.`,
    source: "docs/methods/battery_game.md, \"Version 3\"; the house's draw is an assumption." },
  { key: "voll", session: "session 70",
    text: `If the lights go out in the outage, the round ends and the house pays for the power it needed in the whole outage at USD ${LIGHTS_OUT.usdPerMwh.toLocaleString("en-US")} per MWh, so giving the house up is never the best play.`,
    def: `USD ${LIGHTS_OUT.usdPerMwh.toLocaleString("en-US")} per MWh, the whole outage (USD ${((LIGHTS_OUT.usdPerMwh * EMERGENCY.houseKw * EMERGENCY.outageIntervals) / 4000).toFixed(2)} without a roof); the Texas figure on the California days too.`,
    source: `The value of lost load the Public Utility Commission of Texas approved on 29 August 2024 (Project No. 55837), rounding the Brattle study's USD ${LIGHTS_OUT.study.toLocaleString("en-US")}; residential customers alone: USD ${LIGHTS_OUT.residential.toLocaleString("en-US")}.` },
  { key: "roof", session: "sessions 66 and 70",
    text: `Hard's rooftop add-on: a ${SOLAR.kw} kW array on the grid's whole solar fleet's shape that day; its power earns the price, and below zero it is switched off unless the battery is charging.`,
    def: "Off; on Hard only, and only on a day whose shape the warehouse holds whole.",
    source: "EIA-930 hourly solar generation over EIA-860M nameplate (warehouse/derived/battery_solar.py), kept between 0 and 1." },
  { key: "fleet", session: "session 289",
    text: `The fleet of ${FLEET.toLocaleString("en-US")} homes multiplies one battery's score; it is fictional.`,
    def: `${FLEET.toLocaleString("en-US")} homes, ${(FLEET * 5) / 1000} MW with the default battery; a fixed game rule.`,
    source: "Samuel's ruling 3a of 14 October 2026; beside it, ERCOT's real operating battery fleet from storage_capacity (EIA-860M)." },
  { key: "perfect", session: "sessions 38 and 7535",
    text: "The perfect battery is the exact best play under the same rules, every price known in advance; a move that moves no charge is not counted as a move.",
    def: "Dynamic programming over every state of charge the three actions reach, at a grain of a nanowatt-hour.",
    source: "docs/methods/battery_game.md, \"The perfect-foresight optimum\"; checked against every play of 3^12 on toy days (site/scripts/test-battery.mjs)." },
];

export function GameDecisions() {
  return (
    <details className="mt-10 border-t border-rule pt-3 text-sm" data-decisions="battery-game">
      <summary className="cursor-pointer py-1 text-accent">Decisions in this game ({GAME_DECISIONS.length}): each choice that moves a score or a price played, with its default and its source</summary>
      <p className="mt-2 max-w-3xl text-xs text-muted">The first five are yours to change, in the battery&apos;s settings of the game on Normal and Hard; the rest are fixed game rules.</p>
      <ul className="mt-2 max-w-3xl list-disc space-y-1 pl-5 text-sm" data-decision-count={GAME_DECISIONS.length}>
        {GAME_DECISIONS.map((d) => (
          <li key={d.key} data-decision={d.key} data-decision-editable={d.editable ? "1" : "0"}>
            {d.text}{d.editable ? <span className="text-muted"> (editable)</span> : null}
            <Tip id={`decision-game-${d.key}`} label="this choice's default and source">
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
