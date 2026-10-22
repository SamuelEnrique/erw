// Energy Research Warehouse (ERW) site, session 700: the files the All grids tab of /cost-of-power reads (docs/methods/
// siting.md). The hub and zone rows are the index of "Your load" (data/datacenter/index.json, lib/datacenterdata.ts), so
// the two views hold the same regions; the ERCOT nodes are data/siting/nodes.json, written from node_basis_daily by
// warehouse/derived/siting_page.py. Nothing is read from the database.
import "server-only";
import nodesJson from "@/data/siting/nodes.json";
import { INDEX } from "@/lib/datacenterdata";
import type { Files, NodeFile } from "@/lib/siting";

export const NODES = nodesJson as unknown as NodeFile;
export const SITING_FILES: Files = { index: INDEX, nodes: NODES };
