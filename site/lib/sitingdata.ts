// Energy Research Warehouse (ERW) site, session 700: the files the All grids tab of /cost-of-power reads (docs/methods/
// siting.md). The hub and zone rows are the index of "Your load" (data/datacenter/index.json, lib/datacenterdata.ts), so
// the two views hold the same regions; the ERCOT nodes are data/siting/nodes.json, written from node_basis_daily by
// warehouse/derived/siting_page.py. Nothing is read from the database. Session 701: a grid's years of hourly prices, read
// as "Your load" reads them (lib/datacenterdata.ts, yearFiles).
import "server-only";
import capJson from "@/data/siting/capacity.json";
import cpJson from "@/data/siting/ercot_4cp.json";
import nodesJson from "@/data/siting/nodes.json";
import * as DCL from "@/lib/datacenter";
import { DELIVERY, INDEX, yearFiles } from "@/lib/datacenterdata";
import { newestRate, type CapFile, type CpFile, type DC, type Files, type NodeFile } from "@/lib/siting";

export const NODES = nodesJson as unknown as NodeFile;
/** Session 702: ERCOT's four summer peak intervals (data/siting/ercot_4cp.json, from ercot_4cp_intervals). */
export const CP = cpJson as unknown as CpFile;
/** Session 703: the Commission's newest approved postage stamp rate, as "Your load"'s four-peak block takes it. */
export const RATE = newestRate(DELIVERY.matrix ?? []);
/** Session 704: the capacity tables' newest periods and zones, no price (data/siting/capacity.json). */
export const CAP = capJson as unknown as CapFile;
export const SITING_FILES: Files = { index: INDEX, nodes: NODES, years: yearFiles, cp: CP, rate: RATE, cap: CAP };
/** Session 701: lib/datacenter.ts's own functions, for lib/siting.ts (one arithmetic for both views). */
export const SITING_DC: DC = { monthsRuled: DCL.monthsRuled, lastTwelve: DCL.lastTwelve, span: DCL.span, years: DCL.years, expand: DCL.expand, monthsOfYear: DCL.monthsOfYear, monthStarts: DCL.monthStarts };
