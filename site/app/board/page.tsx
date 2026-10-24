import type { Metadata } from "next";
import { BoardView } from "@/components/board/BoardView";
import { Brand } from "@/components/Brand";
import { SiteLink } from "@/components/SiteLink";
import { AskForm } from "@/app/ask/AskForm";
import boardQuestions from "@/data/board_questions.json";
import { TableDownloads } from "@/components/tool/TableDownloads";
import { TableLicenses } from "@/components/tool/TableLicenses";
import fileJson from "@/data/board.json";
import { holdRows, type BoardFile } from "@/lib/board";
import { gridName, licenseHeldGrids } from "@/lib/license";

// Session 132: the price board and its markets workbench, one page at one address. It holds what the first board,
// version 3, the version 4 work and /markets showed (those addresses now redirect here: next.config.ts; their pages
// are kept, unrouted, under app/_retired), with ERCOT's history since 2015 as a link to its explorer, and the series
// the session added. Every figure is in the site's own file (data/board.json, written by
// warehouse/derived/board_page.py from tables already in the warehouse); the workbench reads one small file a series
// when a row is opened (public/board/). Method, sources and gaps: docs/methods/price_board.md.
// Session 240: on the brand (components/Brand.tsx, app/tokens.css). A top block of the twelve numbers a trader checks first
// (lib/board.ts, TOP_TWELVE: the one list), then the wall as it was, folded by group, with the workbench beside it.
export const metadata: Metadata = { title: "Price board", robots: { index: false, follow: false } };

// session 1116: the rows of the grids held for a license on the day are made "license needed" here, on the server, so no
// held figure is in what the browser receives (lib/board.ts, holdRows)
const raw = fileJson as unknown as BoardFile;

// Session 328: the tables board_page.py reads (scripts/page_tables.py on this page and its builder); the downloads keep
// those in the public catalogue, each as its CSV with a Python and a Stata reader
const TABLES = ["ercot_all_hub_prices_history", "iso_hub_prices_history", "caiso_as_prices", "ercot_as_prices", "nyiso_as_prices", "spp_as_prices",
  "eia_fuel_spot_prices", "eia_product_spot_prices", "eia_crude_stream_prices", "eia_power_plant_fuel_costs", "eia_regional_retail_fuel_prices",
  "eia_retail_electricity_prices", "carb_lcfs_credit_prices", "frb_treasury_yields", "imf_commodity_prices",
  // session 1117: three public price tables the board did not draw
  "wb_commodity_prices_monthly", "eia_gas_prices_state_monthly", "eia_heating_fuel_prices_weekly"];

// session 1145: the five board questions of warehouse/chat/eval/questions_s1122.yaml, as examples a reader can click
const BOARD_QUESTIONS = (boardQuestions as { questions: { question: string }[] }).questions.map((q) => q.question);

export default function Board() {
  const file = holdRows(raw, licenseHeldGrids().map(gridName));
  // session 502: the same list, with each table's license, under the title
  // session 1137: the rows drawn here, as one CSV (app/board/rows/route.ts), beside each table's own download
  return <Brand><BoardView file={file} under={<TableLicenses tables={TABLES} />} footer={<><p className="mb-2 text-sm" data-board-rows="1"><SiteLink href="/board/rows">The rows drawn here, as one CSV</SiteLink> (every figure of this page, each with its source; a held row with none)</p><section className="mb-6" aria-label="Ask the board" data-board-ask="1"><h2 className="mb-1 text-lg">Ask the board</h2><p className="mb-2 max-w-3xl text-sm">Questions of the board's own derived tables, answered by the general chat: every number from a query, each hub's value with its own date.</p><AskForm examples={BOARD_QUESTIONS} placeholder="For example: which hub is highest today?" /></section><TableDownloads tables={TABLES} /></>} /></Brand>;
}
