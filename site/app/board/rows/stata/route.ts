// Session 1614 (chain 165): a Stata reader of the rows the price board draws (/board/rows), with the address of the
// rows on the site that serves it (lib/board.ts rowsReader). Under /board, so the release gate covers it as it covers the
// page. It asks nothing of Supabase.
import { rowsReader } from "@/lib/board";

export function GET(req: Request) {
  const url = new URL("/board/rows", req.url).toString();
  return new Response(rowsReader("do", url), {
    headers: { "Content-Type": "text/plain; charset=utf-8", "Content-Disposition": "attachment; filename=\"erw_board_rows.do\"", "X-Robots-Tag": "noindex" },
  });
}
