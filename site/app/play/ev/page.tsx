import type { Metadata } from "next";
import fs from "node:fs";
import path from "node:path";
import { Brand } from "@/components/Brand";
import { EvGame, type StatePrices } from "./EvGame";

// Session 294 (Samuel's ruling 17 of 14 October 2026): the EV game, EV only (the solar half is a later game). The prices
// are the warehouse's, built into data/ev_prices.json by scripts/build-ev-prices.mjs (the two tables are not in the live
// set); the page reads that file when it is built. Nothing the family types leaves the browser.
export const metadata: Metadata = { title: "Should your family get an EV?" };

type File = { built_at: string; us: { power: StatePrices["power"]; gas: StatePrices["gas"] }; states: StatePrices[] };

export default function EvPage() {
  const d = JSON.parse(fs.readFileSync(path.join(process.cwd(), "data", "ev_prices.json"), "utf-8")) as File;
  return (
    <Brand noUsage>
    <div>
      <h1 className="mb-1 text-3xl">Should your family get an EV?</h1>
      <p className="mb-6 max-w-3xl text-base">
        Five steps, about five minutes. Find out what driving costs where you live, on gasoline and on electricity, then show your parents every number and where
        it comes from.
      </p>
      <EvGame states={d.states} us={{ code: "US", name: "United States", power: d.us.power, gas: d.us.gas }} built={d.built_at} />
    </div>
    </Brand>
  );
}
