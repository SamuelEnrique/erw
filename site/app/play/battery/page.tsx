import type { Metadata } from "next";
import Link from "next/link";
import { Cite } from "@/components/Cite";
import { NoData } from "@/components/NoData";
import { Num } from "@/components/Num";
import { Section } from "@/components/Section";
import { shown } from "@/lib/format";
import { ADDONS, EMERGENCY, FLEET, FLEET_MW, FLEET_MWH, LIGHTS_OUT, SOLAR, SPIKE_LABEL, START_MONEY } from "@/lib/battery";
import { storageUnits, type StorageUnit } from "@/lib/data";
import { leaderboard, presetsPlayed, type PresetCount, type ScoreRow } from "@/lib/game";
import { FAMOUS, todayLevel, TZ, type Level } from "@/lib/levels";
import { attempt } from "@/lib/supabase";
import { Game, type GameLevel } from "./Game";

// Session 38: the home battery game, MVP. Real prices (ERCOT HB_HUBAVG real-time, one operating day: today's level
// from the live set, five famous days from the history); a fictional battery, home, brand and fleet.
export const metadata: Metadata = { title: "The home battery game" };
export const revalidate = 600;

const T = "iso_rtm_hub_prices";

// Session 46: the fictional fleet beside ERCOT's real one: the operating battery units of storage_capacity (EIA-860M)
// whose balancing authority is ERCOT. Each sum carries the check key check-values.mjs recomputes.
function RealFleet({ units }: { units: StorageUnit[] }) {
  const op = units.filter((u) => u.iso === "ERCOT" && u.status === "operating");
  const mw = Math.round(op.reduce((a, u) => a + (u.capacity_mw ?? 0), 0) * 10) / 10;
  const withMwh = op.filter((u) => u.mwh !== null && u.mwh !== "");
  const mwh = Math.round(withMwh.reduce((a, u) => a + Number(u.mwh), 0) * 10) / 10;
  const ratio = mw / FLEET_MW;
  const cell = "border border-rule bg-panel p-3";
  return (
    <div className="grid gap-3 sm:grid-cols-2">
      <div className={cell}>
        <div className="text-xs text-muted">The game&apos;s fleet (fictional)</div>
        <div className="text-2xl tabular-nums"><Num check="battery|fleet_mw" raw={FLEET_MW}>{shown(FLEET_MW)}</Num> <span className="text-sm text-muted">MW</span></div>
        <div className="text-sm">
          <Num check="battery|fleet_mwh" raw={FLEET_MWH}>{shown(FLEET_MWH)}</Num> MWh: {FLEET.toLocaleString("en-US")} homes, each 5 kW and 13.5 kWh (an assumption)
        </div>
      </div>
      <div className={cell}>
        <div className="text-xs text-muted">ERCOT&apos;s real battery fleet, operating (EIA-860M)</div>
        <div className="text-2xl tabular-nums"><Num check="storage|iso_mw|ERCOT|operating" raw={mw}>{shown(mw)}</Num> <span className="text-sm text-muted">MW</span></div>
        <div className="text-sm">
          <Num check="storage|iso_n|ERCOT|operating" raw={op.length}>{op.length.toLocaleString("en-US")}</Num> units;{" "}
          <Num check="storage|iso_mwh|ERCOT|operating" raw={mwh}>{shown(mwh)}</Num> MWh where EIA gives the energy capacity (
          <Num check="storage|iso_n_mwh|ERCOT|operating" raw={withMwh.length}>{withMwh.length.toLocaleString("en-US")}</Num> units)
        </div>
      </div>
      <p className="text-sm sm:col-span-2">
        ERCOT&apos;s real fleet has <Num check="calc|ratio|storage~iso_mw~ERCOT~operating|battery~fleet_mw" raw={ratio}>{shown(ratio)}</Num> times the power of
        the game&apos;s 10,000 homes. A real grid battery is a power plant: it bids into the same real-time market the game replays.
      </p>
    </div>
  );
}

export default async function Battery({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const more = (await searchParams).more === "1";
  const today = await attempt(() => todayLevel(600));
  const t: Level | null = today.ok ? today.data : null;
  // session 56: each level's grid and time zone (today's level and the session 38 days are ERCOT, Central time)
  // session 66: and the day's solar shape where the warehouse holds one (the rooftop add-on; never filled where it does not)
  const levels: GameLevel[] = [...(t ? [t] : []), ...FAMOUS].map(({ slug, date, title, why, ts_utc, price, grid, tz, rule, solar, solar_source }) =>
    ({ slug, date, title, why, ts_utc, price, grid: grid ?? "ERCOT", tz: tz ?? TZ, ...(rule ? { rule } : {}), ...(solar ? { solar, solar_source } : {}) }));
  const withSolar = levels.filter((l) => l.solar).map((l) => l.date);
  // Session 63: the default page is the simple one, for a class: one sentence, two big buttons, the battery and the
  // price. The settings, the notes, Hard's emergency and the leaderboard are behind "more" (?more=1), the full game.
  if (!more) {
    return (
      <>
        <h1 className="mb-3 text-3xl">The home battery game</h1>
        <Game simple levels={levels} top={[]} presets={[]} />
        <p className="mt-6 text-sm"><Link href="/play/battery?more=1">More: the rules, the battery&apos;s settings, Hard&apos;s grid emergency, the leaderboard and the notes</Link></p>
        <p className="mt-1 text-xs text-muted">Real prices: ERCOT&apos;s real-time hub average (on the California days, CAISO SP15). The battery and the home are made up, and the $5 is a game rule. After each play: what you earned, what a perfect battery earned, and the hour you lost the most.</p>
      </>
    );
  }
  const top = t ? await attempt(() => leaderboard(t.date)) : null;
  const played = t ? await attempt(() => presetsPlayed(t.date)) : null;  // session 50: the presets played today
  const presets: PresetCount[] = played && played.ok ? played.data : [];
  const fleet = await attempt(storageUnits);
  const first: ScoreRow[] = top && top.ok ? top.data : [];
  const hi = t ? t.price.indexOf(Math.max(...t.price)) : -1, lo = t ? t.price.indexOf(Math.min(...t.price)) : -1;
  const key = (i: number) => `series|${T}|ercot:HB_HUBAVG|spp_rtm|${t!.ts_utc[i]}`;
  return (
    <>
      <h1 className="mb-1 text-3xl">The home battery game</h1>
      <div className="mb-4 max-w-3xl text-sm">
        <p className="mb-2">
          You own one home battery in Texas, or, on the two California days, in Southern California. A real day of wholesale power prices scrolls past in about 90 seconds, fifteen minutes at a
          time. Hold to charge when power is cheap, hold to sell when it is dear. Once a day the grid calls the fleet: answer it for a bonus. At the end,
          see what the same battery would have earned with perfect foresight.
        </p>
        <p className="text-muted">
          The prices are real: ERCOT&apos;s real-time settlement point price at the hub average (HB_HUBAVG), every interval of the day; on the California days,
          CAISO&apos;s real-time price at the SP15 trading hub, the 15-minute means of its 5-minute prices. Each California day was chosen by a stated rule, from
          the complete days the warehouse holds since 2025-09-01: the lowest mean price from 10:00 to 15:00 Pacific, and the largest rise from the 12:00 to 15:00
          mean to the 18:00 to 21:00 mean. The battery, the home,
          the brand (&quot;Mockingbird Home Battery&quot; is made up) and the fleet of 10,000 homes are fictional. The battery&apos;s settings are yours to set, within
          stated ranges; by default 13.5 kWh usable, 5 kW, 90 percent round trip, half full at the start (assumptions), a 20 percent backup reserve and a
          degradation cost of $0.11 per kWh discharged (from Lazard&apos;s 2025 storage cost study), both enforced on Hard. Every assumption and its source:{" "}
          <Link href="/data/methods/battery_game">the method</Link>.
        </p>
      </div>
      {t ? (
        <p className="mb-4 text-sm">
          Today&apos;s level, the operating day {t.date}: real-time prices from <Num check={key(lo)} raw={t.price[lo]}>{shown(t.price[lo])}</Num> to{" "}
          <Num check={key(hi)} raw={t.price[hi]}>{shown(t.price[hi])}</Num> USD/MWh.
        </p>
      ) : (
        <NoData what="today's level" reason={today.ok ? "no complete ERCOT operating day in the last four days of the live set" : today.reason} />
      )}
      <Section title="Play">
        <Game levels={levels} top={first} presets={presets} />
      </Section>
      <Section title="The game's rules (version 4)">
        <div className="max-w-3xl space-y-2 text-sm">
          <p>Each of these is a game rule, not a market rule. The prices stay real; on Hard, the emergency changes them for one hour, and wherever such a price is shown the number itself says &quot;{SPIKE_LABEL}&quot;, with the real price beside it.</p>
          <ul className="list-disc space-y-1 pl-5">
            <li><strong>Money:</strong> every play starts with ${START_MONEY}. Buying power costs money and selling earns it; if the money falls below $0, the game ends there. The score is what you earned (the money less the ${START_MONEY}).</li>
            <li><strong>Hard&apos;s grid emergency:</strong> in the day&apos;s dearest hour the price climbs toward the cap: each fifteen minutes {EMERGENCY.ramp.map((r) => `${Math.round(r * 100)}`).join(", ")} percent of the way from the real price to USD {EMERGENCY.cap.toLocaleString("en-US")}/MWh (ERCOT&apos;s offer cap since 2023, used for every grid). Then the grid goes down for two hours: nothing can be bought or sold, and the house draws {EMERGENCY.houseKw} kW from the battery, its backup reserve included (that is what the reserve is for).</li>
            <li><strong>Lights out costs money (a game rule):</strong> if the battery cannot carry the house through the outage, the lights go out and the round ends. Every fifteen minutes left of the outage, the one the lights went out in included, then charges the house&apos;s unserved energy ({EMERGENCY.houseKw} kW for the fifteen minutes, less what a rooftop array makes) at {LIGHTS_OUT.multiple} times the price cap, USD {(LIGHTS_OUT.multiple * EMERGENCY.cap).toLocaleString("en-US")}/MWh: USD {((LIGHTS_OUT.multiple * EMERGENCY.cap * EMERGENCY.houseKw) / 4000).toFixed(2)} for each fifteen minutes without the roof. The money may end below $0. Why: a home without power in a grid emergency is the outcome the battery exists to prevent, so giving the house up must never be the best play.</li>
            <li><strong>Why {LIGHTS_OUT.multiple} times the cap:</strong> priced at the cap itself, the perfect battery still let the house go dark on Winter Storm Uri&apos;s day, whose real prices sat near USD 9,000/MWh, above the game&apos;s cap. {LIGHTS_OUT.multiple} is the smallest whole multiple at which the perfect battery keeps the lights on wherever it can, on every famous day and every test day (the test finds it; <Link href="/data/methods/battery_game">the method</Link>).</li>
            <li><strong>The perfect battery</strong> plays by the same rules: it never runs out of money, and it never gives up the house where the lights can be kept on.</li>
            <li><strong>Add-ons (Hard only, off by default).</strong> {ADDONS.solar.label}: {ADDONS.solar.what}. The shape is the whole fleet&apos;s, not one roof&apos;s: the hourly output of the grid&apos;s solar plants per MW installed (EIA-930 generation over EIA-860M nameplate, as <Link href="/cost-of-power/seller">the seller&apos;s tab</Link> uses), kept between 0 and 1, times {SOLAR.kw} kW. Where the warehouse holds no shape for a level&apos;s day the add-on is unavailable for it; nothing is filled in. {withSolar.length ? `Days with a shape: ${withSolar.join(", ")}.` : "No level holds a shape yet, so the add-on is unavailable on every level for now."}</li>
            <li><strong>The leaderboard</strong> ranks version 4 plays only against version 4 plays with the same difficulty, battery and add-ons; a board from before says &quot;v3 rules&quot; or &quot;v2 rules&quot;.</li>
          </ul>
        </div>
      </Section>
      <Section title="The fleet call: how it mirrors ERCOT's ADER pilot">
        <div className="max-w-3xl space-y-2 text-sm">
          <p>
            The real program the call is modeled on is ERCOT&apos;s Aggregate Distributed Energy Resource (ADER) pilot. Its governing document (Phase 3.3, June 2026)
            defines an ADER as &quot;a Resource consisting of multiple Premises or devices connected at the distribution system level that has the ability in
            aggregate to respond to ERCOT Dispatch Instructions&quot;, and settles its energy at &quot;the Load Zone price&quot;. The game keeps that shape and simplifies the rest:
          </p>
          <ul className="list-disc space-y-1 pl-5">
            <li><strong>When:</strong> the call is the day&apos;s dearest clock hour, with a 15-minute warning. In the pilot, dispatch comes from ERCOT&apos;s Security-Constrained Economic Dispatch (SCED), every five minutes, when prices and the grid call for it; nobody knows the dearest hour in advance. The warning and the hour are the game&apos;s choices.</li>
            <li><strong>How long:</strong> one hour. The pilot&apos;s deployment test lasts &quot;at least one full 15-minute Settlement Interval&quot;; a real call lasts as long as the instruction does.</li>
            <li><strong>What the battery is paid:</strong> every kWh sold, in or out of the call, earns the real-time price, as an ADER&apos;s energy is settled at a market price (the game uses the hub average, not the battery&apos;s Load Zone price). In the call hour, each kWh delivered also earns a bonus of the hour&apos;s mean price (never below zero). The bonus is the game&apos;s stand-in for what an aggregator may pass on to a home: the pilot also lets ADERs earn ancillary-service payments (ECRS and Non-Spin), whose prices the game does not hold, and what a home is paid is set by its retailer or aggregator, not by ERCOT.</li>
            <li><strong>The reserve:</strong> on Hard, the battery never discharges below its backup reserve, even in the call.</li>
            <li><strong>Size:</strong> the game&apos;s fleet of 10,000 homes is 50 MW. The pilot&apos;s Phase 3 limit is 500 MW of ADERs system-wide.</li>
          </ul>
          <p className="text-xs text-muted">
            Source: ERCOT, <a href="https://www.ercot.com/files/docs/2026/03/02/ADER-Pilot-Project-Governing-Document-Phase-3.3.docx">ADER Pilot Project Governing Document, Phase 3.3</a>, from{" "}
            <a href="https://www.ercot.com/mktrules/pilots/ader">ERCOT&apos;s ADER pilot page</a>, read on 2026-10-01. The game is not the program: no telemetry,
            no qualification, no Base Point Deviation, no ancillary-service awards.
          </p>
        </div>
      </Section>
      <Section title="The fleet: fictional and real">
        {fleet.ok ? <RealFleet units={fleet.data} /> : <NoData what="ERCOT's battery fleet" reason={fleet.reason} />}
        <Cite tables={["storage_capacity"]} note="Operating battery units whose balancing authority is ERCOT: nameplate MW, and EIA's energy capacity (MWh) where it gives one. The game's fleet is fictional" />
      </Section>
      <Section title="What is stored">
        <p className="max-w-3xl text-sm">
          Scores are public. Posting one stores the level, your nickname if you give one, your score, the perfect-foresight score and the time; nothing
          else, and no email, account or IP address. Each finished game also stores its moves (one per fifteen minutes) and its score with a random id, for
          later research on how people run batteries: never shown, with no nickname or IP address, and nothing that joins it to a leaderboard row. No
          trackers, no sound.
        </p>
      </Section>
      <Cite tables={[T, "ercot_all_hub_prices_history"]} note="Today's level from the live set; the five famous days frozen from the history (site/data/battery_levels.json, warehouse/derived/battery_levels.py)" />
      <p className="mt-2 text-xs text-muted">Real batteries on the grid: <Link href="/storage">storage</Link>; ERCOT: <Link href="/grid/ercot">its grid page</Link>.</p>
    </>
  );
}
