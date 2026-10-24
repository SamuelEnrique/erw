// Session 1171 (chain 078): the sentence each Grid tab's data line carries (lib/gridPreliminary.ts), on an element that
// holds the page's drawing time for the value checker (data-eia930-drawn). `say` writes the time into the words, on the
// tabs that already say when the page was drawn.
import { drawnUtc, preliminaryText } from "@/lib/gridPreliminary";

export function Preliminary({ drawn, say }: { drawn: Date; say?: boolean }) {
  return <span data-eia930-drawn={drawn.toISOString()}>{preliminaryText(say ? drawnUtc(drawn) : null)}</span>;
}
