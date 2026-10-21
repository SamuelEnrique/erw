import type { Metadata } from "next";
import { BoardView } from "@/components/board/BoardView";
import { Brand } from "@/components/Brand";
import { TableDownloads } from "@/components/tool/TableDownloads";
import { TableLicenses } from "@/components/tool/TableLicenses";
import fileJson from "@/data/board.json";
import type { BoardFile } from "@/lib/board";

// Session 132: the price board and its markets workbench, one page at one address. It holds what the first board,
// version 3, the version 4 work and /markets showed (those addresses now redirect here: next.config.ts; their pages
// are kept, unrouted, under app/_retired), with ERCOT's history since 2015 as a link to its explorer, and the series
// the session added. Every figure is in the site's own file (data/board.json, written by
// warehouse/derived/board_page.py from tables already in the warehouse); the workbench reads one small file a series
// when a row is opened (public/board/). Method, sources and gaps: docs/methods/price_board.md.
// Session 240: on the brand (components/Brand.tsx, app/tokens.css). A top block of the twelve numbers a trader checks first
// (lib/board.ts, TOP_TWELVE: the one list), then the wall as it was, folded by group, with the workbench beside it.
export const metadata: Metadata = { title: "Price board", robots: { index: false, follow: false } };

const file = fileJson as unknown as BoardFile;

// Session 328: the tables board_page.py reads (scripts/page_tables.py on this page and its builder); the downloads keep
// those in the public catalogue, each as its CSV with a Python and a Stata reader
const TABLES = ["ercot_all_hub_prices_history", "iso_hub_prices_history", "caiso_as_prices", "ercot_as_prices", "nyiso_as_prices", "spp_as_prices",
  "eia_fuel_spot_prices", "eia_product_spot_prices", "eia_crude_stream_prices", "eia_power_plant_fuel_costs", "eia_regional_retail_fuel_prices",
  "eia_retail_electricity_prices", "carb_lcfs_credit_prices", "frb_treasury_yields", "imf_commodity_prices"];

export default function Board() {
  // session 502: the same list, with each table's license, under the title
  return <Brand><BoardView file={file} under={<TableLicenses tables={TABLES} />} footer={<TableDownloads tables={TABLES} />} /></Brand>;
}
