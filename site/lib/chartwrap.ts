// Energy Research Warehouse (ERW) site, session 370: the names drawn at the right of a shared SVG chart
// (components/svgchart.tsx, CategoryChart), in lines that fit the room the chart leaves them. On /research/card/* the
// names of the lines (a fleet's megawatts, a multiple, a control series) ran past the chart's box and were cut by its
// edge, at 390 px and at 1280. No import: Node runs this file as it is (tests/test_session370.py).

/** The width of a character of the chart's 12 px text, as a share of the size: about 0.46 measured on the face at 390
 * and 1280 px (runs/chain_oct20d/s370), with a margin. */
export const CHAR = 0.52;
/** The height of a line of a name, px (the step the chart already keeps between two names). */
export const LINE = 13;

/** A name split into lines that each fit `room` px: words kept whole, a word wider than the room cut into pieces that
 * fit. A name that fits stays one line, so a chart whose names fit is drawn as before. */
export function wrapName(s: string, room: number, size = 12): string[] {
  const per = size * CHAR, fits = (t: string) => t.length * per <= room;
  if (fits(s)) return [s];
  const most = Math.max(4, Math.floor(room / per));
  const words = s.split(/\s+/).filter(Boolean).flatMap((w) => (fits(w) ? [w] : Array.from({ length: Math.ceil(w.length / most) }, (_, k) => w.slice(k * most, (k + 1) * most))));
  const out: string[] = [];
  let line = "";
  for (const w of words) {
    const next = line ? `${line} ${w}` : w;
    if (line && !fits(next)) { out.push(line); line = w; } else line = next;
  }
  if (line) out.push(line);
  return out;
}

/** The names placed top to bottom (each at its series' last value, `y` the middle of its first line): a name starts
 * below the lines of the one above it; when a name runs to more than one line, the last is kept above `bottom` and the
 * ones above it make room. Returns the new `y` of each, in the order given (sorted by `y` first). */
export function stackNames<T extends { y: number; lines: string[] }>(names: T[], bottom: number): T[] {
  names.sort((a, b) => a.y - b.y);
  for (let i = 1; i < names.length; i++) { const below = names[i - 1].y + LINE * names[i - 1].lines.length; if (names[i].y < below) names[i].y = below; }
  if (names.some((e) => e.lines.length > 1)) {
    for (let i = names.length - 1; i >= 0; i--) {
      const floor = i === names.length - 1 ? bottom - LINE * (names[i].lines.length - 1) : names[i + 1].y - LINE * names[i].lines.length;
      if (names[i].y > floor) names[i].y = floor;
    }
  }
  return names;
}
