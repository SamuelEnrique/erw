// Energy Research Warehouse (ERW) site, session 700: the files the All grids tab of /cost-of-power reads (docs/methods/
// siting.md). The hub and zone rows are the index of "Your load" (data/datacenter/index.json, lib/datacenterdata.ts), so
// the two views hold the same regions; the ERCOT nodes are data/siting/nodes.json, written from node_basis_daily by
// warehouse/derived/siting_page.py. Nothing is read from the database. Session 701: a grid's years of hourly prices, read
// as "Your load" reads them (lib/datacenterdata.ts, yearFiles).
import "server-only";
import nodesJson from "@/data/siting/nodes.json";
import * as DCL from "@/lib/datacenter";
import { INDEX, yearFiles } from "@/lib/datacenterdata";
import type { DC, Files, NodeFile } from "@/lib/siting";

export const NODES = nodesJson as unknown as NodeFile;
export const SITING_FILES: Files = { index: INDEX, nodes: NODES, years: yearFiles };
/** Session 701: lib/datacenter.ts's own functions, for lib/siting.ts (one arithmetic for both views). */
export const SITING_DC: DC = { monthsRuled: DCL.monthsRuled, lastTwelve: DCL.lastTwelve, span: DCL.span, years: DCL.years };
