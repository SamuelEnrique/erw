// Session 1137: the rows the price board draws, as a CSV (lib/board.ts rowsCsv), from the page's own file after the hold
// of the day (holdRows, session 1116), so a held grid's row carries no figure. Under /board and without an extension, so
// the release gate covers it as it covers the page. Made when the site is built; it asks nothing of Supabase.
import fileJson from "@/data/board.json";
import { holdRows, rowsCsv, type BoardFile } from "@/lib/board";
import { gridName, licenseHeldGrids } from "@/lib/license";

export const dynamic = "force-static";

export function GET() {
  const file = holdRows(fileJson as unknown as BoardFile, licenseHeldGrids().map(gridName));
  return new Response(rowsCsv(file), { headers: { "Content-Type": "text/csv; charset=utf-8", "Content-Disposition": "attachment; filename=\"erw_board_rows.csv\"", "X-Robots-Tag": "noindex" } });
}
