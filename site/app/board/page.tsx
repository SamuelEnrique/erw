import type { Metadata } from "next";
import { BoardView } from "@/components/board/BoardView";
import fileJson from "@/data/board.json";
import type { BoardFile } from "@/lib/board";

// Session 132: the price board and its markets workbench, one page at one address. It holds what the first board,
// version 3, the version 4 work and /markets showed (those addresses now redirect here: next.config.ts; their pages
// are kept, unrouted, under app/_retired), with ERCOT's history since 2015 as a link to its explorer, and the series
// the session added. Every figure is in the site's own file (data/board.json, written by
// warehouse/derived/board_page.py from tables already in the warehouse); the workbench reads one small file a series
// when a row is opened (public/board/). Method, sources and gaps: docs/methods/price_board.md.
export const metadata: Metadata = { title: "Price board", robots: { index: false, follow: false } };

const file = fileJson as unknown as BoardFile;

export default function Board() {
  return <BoardView file={file} />;
}
