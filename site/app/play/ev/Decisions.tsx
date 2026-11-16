import { SiteLink as Link } from "@/components/SiteLink";
import { Tip } from "@/components/tool/ToolPage";

// Session 7536 (chain 304): the decisions of "Should your family get an EV?", in the form the battery page, /deals,
// /impact, /severance and /battery/customer carry: one fold, closed to start, one line a choice that moves a figure of
// the game, each with its default and its source on hover, tap or focus (the page standard: no grey note under the
// line). The list is kept here, in the game's own folder, and exported so site/scripts/test-ev-game-render.mjs,
// tests/test_session7536_ev_game.py and the method note (docs/methods/ev_game.md, "The choices that move a figure") can
// be checked against it. Words only: nothing in the game is computed from this list. It is drawn by the server, the
// same for everyone, and makes no request: the page's promise that nothing typed leaves the browser is untouched (the
// tips are CSS alone, and the one link does not prefetch). Every choice a player can change is changed in place, in the
// field the line names.
export type EvDecision = { key: string; text: string; def: string; source: string };

export const EV_DECISIONS: EvDecision[] = [
  { key: "home-price",
    text: "Charging at home is priced at the average price homes in the state paid for electricity in the newest month EIA has published: every utility of the state, every hour of the day, the bill's fixed charges spread over its kWh. Change it in the field \"Electricity at home\".",
    def: "The state's newest month in the file the game was built from (July 2026; the United States, 18.31 cents a kWh, before a state is chosen).",
    source: "EIA, Electric Power Monthly, Table 5.6.A, residential average price, through the ERW table eia_retail_electricity_prices (entity eia:retail_price:<state>:RES). A rate made for EV owners can be lower at night: PG&E's E-TOU-C off-peak total rate was 36.757 cents in winter and 39.940 in summer as read on 30 September 2026, against California's average of 33.61 in July 2026." },
  { key: "gasoline-price",
    text: "Gasoline is regular grade, the newest weekly price EIA publishes: the state's own series for the nine states that have one, else its region's (its PADD, the East Coast by its three parts, the West Coast without California). Change it in the field \"Gasoline, a gallon\".",
    def: "The newest week in the file the game was built from (the week of October 5, 2026; the United States, $4.354).",
    source: "EIA, Gasoline and Diesel Fuel Update (weekly retail prices), through the ERW table eia_regional_retail_fuel_prices. EIA's own series page gives $4.354 for the United States that week (read 16 November 2026)." },
  { key: "prices-held",
    text: "Today's two prices are held for every year the car is kept: no rise or fall in either is assumed.",
    def: "Held flat.",
    source: "A choice of the game (session 3276), stated in the method note. Gasoline moved from $4.157 to $4.478 and back to $3.995 a gallon in the ten weeks from September 7 to November 9, 2026 (EIA's weekly series)." },
  { key: "home-share",
    text: "Every mile is charged at home unless the player says otherwise. Below 100 percent, the rest is charged at the price the player types for a public charger; the game guesses none and waits for it. Change it in the field \"Charging done at home\".",
    def: "100 percent at home.",
    source: "An assumption of the game. No ERW table holds what public chargers charge, and the Department of Energy's Alternative Fuel Price Report of July 2026 gives no electricity row." },
  { key: "miles",
    text: "The distance driven a year. Change it in the field \"Miles a year\".",
    def: "15,000 miles.",
    source: "The yearly distance fueleconomy.gov's fuel cost estimates assume (its 2025 Fuel Economy Guide)." },
  { key: "cars",
    text: "The two cars are the same small SUV, gasoline and electric, at their combined city and highway ratings. The EV's rating counts the energy drawn from the wall, so charging losses are in it. Change them in the fields \"The gasoline car's miles per gallon\" and \"The EV's kWh per mile\".",
    def: "27 mpg and 0.31 kWh a mile.",
    source: "fueleconomy.gov: the 2025 Chevrolet Equinox FWD (vehicle 48061) and the 2025 Chevrolet Equinox EV FWD, 31.24 kWh per 100 miles (vehicle 48697), read 15 October 2026. Not read again in session 7536: fueleconomy.gov refused the connection." },
  { key: "car-prices",
    text: "Each car's price is its starting price before the destination charge. Change them in the fields \"The gasoline car's price\" and \"The EV's price\": a dealer's quote is better than either.",
    def: "$28,600 and $33,600: the EV costs $5,000 more.",
    source: "Chevrolet's starting prices for the 2025 Equinox LT and the 2025 Equinox EV LT1, as a search read them on 15 October 2026 (GM gave $34,995 for the EV with its $1,395 destination charge). Marked \"to confirm\" since." },
  { key: "payback",
    text: "Payback is what the EV costs more to buy, after any credit, divided by one year's saving on fuel, not discounted. \"At once\" when the EV costs no more; \"never\" when it saves nothing a year. The chart's lines cross at the same year.",
    def: "Undiscounted, today's prices.",
    source: "Arithmetic, stated in the method note." },
  { key: "npv",
    text: "The net present value counts each year's saving at the end of that year, divided by one plus the rate for each year that has passed, over the years the car is kept, less what the EV costs more to buy on the day it is bought. Change the rate in the field \"Interest rate\" and the years in \"Years you keep the car\".",
    def: "5 percent a year over 8 years.",
    source: "A round rate the game chooses. OMB's rates for 2026 are lower: 3.6 percent nominal on a 7-year Treasury note, 3.7 on a 10-year (Circular A-94, Appendix C, revised 6 March 2026). Eight years is an assumption." },
  { key: "credit",
    text: "The federal tax credit is off. Switched on, the amount the player sets comes off the EV's price, as the family's own assumption.",
    def: "Off; $7,500 when switched on.",
    source: "The IRS, Credits for new clean vehicles purchased in 2023 or after (reviewed 13 July 2026): no credit for a vehicle acquired after 30 September 2025; $7,500 was its most." },
  { key: "left-out",
    text: "Only the price of each car and its fuel are counted. Repairs and maintenance, insurance, a home charger, state and utility incentives, registration fees and what each car is worth when sold are not.",
    def: "Left out.",
    source: "A choice of the game, said on the page in the net present value's hover and in the method note." },
];

export function EvDecisions() {
  return (
    <details className="mt-10 border-t border-rule pt-3 text-sm" data-decisions="7536">
      <summary className="cursor-pointer py-1 text-accent">Decisions in this game (each with its default and its source on hover)</summary>
      <ul className="mt-2 max-w-3xl list-disc space-y-1 pl-5 text-sm" data-decision-count={EV_DECISIONS.length}>
        {EV_DECISIONS.map((d) => (
          <li key={d.key} data-decision={d.key}>
            {d.text}
            <Tip id={`decision-7536-${d.key}`} label="this choice's default and source">
              <span className="block" data-decision-default={d.key}><strong>Default:</strong> {d.def}</span>
              <span className="block" data-decision-source={d.key}><strong>Source:</strong> {d.source}</span>
            </Tip>
          </li>
        ))}
      </ul>
      <p className="mt-2 max-w-3xl text-sm">
        Each is described in <Link href="/data/methods/ev_game" prefetch={false}>the method note</Link>, with the arithmetic of every figure.
      </p>
    </details>
  );
}
