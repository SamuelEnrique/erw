// Session 419: a number as an ordinal, "1st", "2nd", "3rd", "11th", "22nd", "101st", for words like "the 22nd
// percentile". A number with a decimal part takes the suffix of its last digit as written ("13.4th", "21.1st",
// "99.9th"). Pure, no imports: the research view (a client component) and Node's tests both read it.
export function ordinal(n: number): string {
  const s = String(n);
  const whole = Number.isInteger(n);
  const last = Number(s.at(-1));
  const lastTwo = whole ? Math.abs(n) % 100 : -1;
  const suffix = whole && lastTwo >= 11 && lastTwo <= 13 ? "th" : last === 1 ? "st" : last === 2 ? "nd" : last === 3 ? "rd" : "th";
  return `${s}${suffix}`;
}
