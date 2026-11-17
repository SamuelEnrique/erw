// Energy Research Warehouse (ERW) site, session 700: the files the All grids tab of /cost-of-power reads (docs/methods/
// siting.md). The hub and zone rows are the index of "Your load" (data/datacenter/index.json, lib/datacenterdata.ts), so
// the two views hold the same regions; the ERCOT nodes are data/siting/nodes.json, written from node_basis_daily by
// warehouse/derived/siting_page.py. Nothing is read from the database. Session 701: a grid's years of hourly prices, read
// as "Your load" reads them (lib/datacenterdata.ts, yearFiles).
import "server-only";
import loadJson from "@/data/large_load_status.json";
import howSoonJson from "@/data/datacenter/how_soon.json";
import rulesJson from "@/data/datacenter/rules.json";
import capJson from "@/data/siting/capacity.json";
import connectJson from "@/data/siting/connect.json";
import demandJson from "@/data/demand_growth.json";
import headroomJson from "@/data/siting/headroom.json";
import carbonJson from "@/data/siting/carbon.json";
import utilityJson from "@/data/siting/utility.json";
import tariffsJson from "@/data/siting/tariffs.json";
import connRulesJson from "@/data/siting/conn_rules.json";
import facilitiesJson from "@/data/siting/facilities.json";
import cpJson from "@/data/siting/ercot_4cp.json";
import nodesJson from "@/data/siting/nodes.json";
import largeLoadJson from "@/data/siting/large_load_rules.json";
import type { RulesFile as LargeLoadFile } from "@/lib/largeloadrules";
import * as DCL from "@/lib/datacenter";
import { DELIVERY, INDEX, yearFiles } from "@/lib/datacenterdata";
import { deliveryOf, utilitiesOf } from "@/lib/datacenter/delivery";
import { newestRate, type CapFile, type ConnectFile, type CpFile, type DC, type Files, type LoadStatus, type CarbonFile, type DemandYears, type FacilityGridFile, type UtilityFile, type TariffFile, type ConnRulesFile, type HeadroomFile, type NodeFile, type RulesFile, type WaitsFile } from "@/lib/siting";

export const NODES = nodesJson as unknown as NodeFile;
/** Chain 302 (session 7201): US utilities' large-load rules, their changes and the states' laws (data/siting/
 * large_load_rules.json, warehouse/derived/large_load_rules_page.py): the public rows, and the held rows' names only. */
export const LARGE_LOAD = largeLoadJson as unknown as LargeLoadFile;
/** Session 702: ERCOT's four summer peak intervals (data/siting/ercot_4cp.json, from ercot_4cp_intervals). */
export const CP = cpJson as unknown as CpFile;
/** Session 703: the Commission's newest approved postage stamp rate, as "Your load"'s four-peak block takes it. */
export const RATE = newestRate(DELIVERY.matrix ?? []);
/** Session 7622, the other choice of the ruling on a Texas row's transmission rate (wip/alt-cost-of-power-3, not
 * landed): each of the four large wires utilities' own transmission rate, USD per kW of four-peak demand a year: the
 * transmission component of its tariff lines for a flat 100 MW load (lib/datacenter/delivery.ts, USD per MWh) times
 * 8,760 hours over 1,000. A row whose wires utility is one of them takes it in place of the Commission's rate. */
export const UTILITY_TX_RATES: Record<string, number> = Object.fromEntries(utilitiesOf(DELIVERY.rows).map((u) => {
  const t = deliveryOf(DELIVERY.rows, u, 100).components.find((c) => c.kind === "transmission");
  return [u, t ? (t.perMwh * 8760) / 1000 : 0];
}).filter(([, v]) => (v as number) > 0));
/** Session 704: the capacity tables' newest periods and zones, no price (data/siting/capacity.json). */
export const CAP = capJson as unknown as CapFile;
/** Session 705: the queue durations, and "Your load"'s own files of rules, ERCOT's reports and the measured waits. */
export const CONNECT = connectJson as unknown as ConnectFile;
/** Session 719: where a tracked datacenter sits on the tab (data/siting/facilities.json). */
export const FACILITY_GRID = facilitiesJson as unknown as FacilityGridFile;
export const SITING_FILES: Files = { index: INDEX, nodes: NODES, years: yearFiles, cp: CP, rate: RATE, utilRates: UTILITY_TX_RATES, cap: CAP, connect: CONNECT,
  rules: rulesJson as unknown as RulesFile, status: loadJson as unknown as LoadStatus, waits: howSoonJson as unknown as WaitsFile,
  demand: demandJson as unknown as DemandYears, headroom: headroomJson as unknown as HeadroomFile, carbon: carbonJson as unknown as CarbonFile,
  utility: utilityJson as unknown as UtilityFile,
  // session 3764: the filed large-load schedules and the operators' connection rules
  tariffs: tariffsJson as unknown as TariffFile, connRules: connRulesJson as unknown as ConnRulesFile };
/** Session 701: lib/datacenter.ts's own functions, for lib/siting.ts (one arithmetic for both views). */
export const SITING_DC: DC = { monthsRuled: DCL.monthsRuled, lastTwelve: DCL.lastTwelve, span: DCL.span, years: DCL.years, expand: DCL.expand, monthsOfYear: DCL.monthsOfYear, monthStarts: DCL.monthStarts };
