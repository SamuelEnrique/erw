import type { Metadata } from "next";
import Link from "next/link";
import { Cite } from "@/components/Cite";
import { NoData } from "@/components/NoData";
import { Num } from "@/components/Num";
import { Section } from "@/components/Section";
import { shown } from "@/lib/format";
import { FLEET, FLEET_MW, FLEET_MWH } from "@/lib/battery";
import { storageUnits, type StorageUnit } from "@/lib/data";
import { leaderboard, type ScoreRow } from "@/lib/game";
import { FAMOUS, todayLevel, type Level } from "@/lib/levels";
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

export default async function Battery() {
  const today = await attempt(() => todayLevel(600));
  const t: Level | null = today.ok ? today.data : null;
  const levels: GameLevel[] = [...(t ? [t] : []), ...FAMOUS].map(({ slug, date, title, why, ts_utc, price }) => ({ slug, date, title, why, ts_utc, price }));
  const top = t ? await attempt(() => leaderboard(t.date)) : null;
  const fleet = await attempt(storageUnits);
  const first: ScoreRow[] = top && top.ok ? top.data : [];
  const hi = t ? t.price.indexOf(Math.max(...t.price)) : -1, lo = t ? t.price.indexOf(Math.min(...t.price)) : -1;
  const key = (i: number) => `series|${T}|ercot:HB_HUBAVG|spp_rtm|${t!.ts_utc[i]}`;
  return (
    <>
      <h1 className="mb-1 text-3xl">The home battery game</h1>
      <div className="mb-4 max-w-3xl text-sm">
        <p className="mb-2">
          You own one home battery in Texas. A real day of ERCOT&apos;s wholesale power prices scrolls past in about 90 seconds, fifteen minutes at a
          time. Hold to charge when power is cheap, hold to sell when it is dear. Once a day the grid calls the fleet: answer it for a bonus. At the end,
          see what the same battery would have earned with perfect foresight.
        </p>
        <p className="text-muted">
          The prices are real: ERCOT&apos;s real-time settlement point price at the hub average (HB_HUBAVG), every interval of the day. The battery, the home,
          the brand (&quot;Mockingbird Home Battery&quot; is made up) and the fleet of 10,000 homes are fictional. The battery is an assumption: 13.5 kWh usable,
          5 kW, 90 percent round trip, half full at the start. The fleet bonus is a game rule: energy delivered in the day&apos;s dearest hour earns that
          hour&apos;s mean price again (never below zero); it is not any real program&apos;s terms.
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
        <Game levels={levels} top={first} />
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
