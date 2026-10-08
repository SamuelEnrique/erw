// Energy Research Warehouse (ERW) site, session 137: the rule that judges an answer of Ask ERCOT to one of the 100
// test questions (warehouse/chat/eval_ercot_panel.json, rules). One rule a kind, the same whatever version of the tool
// gave the answer, so "before" and "after" are measured alike. No request, no model call: it reads the answer's record.
export const words = (t) => (String(t ?? "").trim().match(/\S+/g) ?? []).length;
const PAGE = /docs\/grids\/ercot\.md/;

/** The reasons an answer fails the rule of its question's kind; none when it passes. */
export function judge(q, r) {
  const why = [];
  const series = Array.isArray(r.series) ? r.series : [];
  const cites = (Array.isArray(r.citations) ? r.citations : []).map((c) => String(c.table ?? ""));
  const answered = r.status === "answered";
  if (q.kind === "conceptual") {
    if (!answered) why.push(`status ${r.status}`);
    if (words(r.answer) < 15) why.push(`${words(r.answer)} words`);
    if (series.length) why.push(`${series.length} series shown for a question about an idea`);
    if (!cites.some((t) => PAGE.test(t))) why.push("the ERCOT page's written content is not cited");
  } else if (q.kind === "chart") {
    if (!answered) why.push(`status ${r.status}`);
    if (!series.length) why.push("no series");
    if (series.some((s) => !s.check || !s.check.same)) why.push("a series does not equal the rows fetched");
    if (series.some((s) => (s.rows ?? []).length < 3)) why.push("a series of fewer than 3 rows");
    if (words(r.answer) > 120) why.push(`${words(r.answer)} words`);
  } else if (q.kind === "sentence") {
    if (!answered) why.push(`status ${r.status}`);
    if (series.length) why.push(`${series.length} series shown for one figure`);
    if (!/\d/.test(String(r.answer ?? ""))) why.push("no number in the answer");
    if (words(r.answer) > 70) why.push(`${words(r.answer)} words`);
    if (!cites.length) why.push("no table cited");
  } else if (q.kind === "refuse") {
    if (!["not_in_warehouse", "model_refusal"].includes(r.status)) why.push(`status ${r.status}`);
    if (series.length) why.push(`${series.length} series shown`);
    if (q.say && !new RegExp(q.say, "i").test(String(r.answer ?? ""))) why.push(`the answer does not name what was asked (${q.say})`);
    // session 156: the closing words of a refusal about another grid. Since session 153 the tool answers for the other
    // grids what four pages show, so "this chat speaks for ERCOT only" is no longer true: such a refusal must close in the
    // tool's own name (q.close) and may not say the old words (q.never). A refusal that carries neither field (licensed
    // data, a company's accounts, a forecast) is judged exactly as it was.
    if (q.close && !new RegExp(q.close, "i").test(String(r.answer ?? ""))) why.push(`the refusal does not close in the tool's own words (${q.close})`);
    if (q.never && new RegExp(q.never, "i").test(String(r.answer ?? ""))) why.push(`the refusal still says what is no longer true (${q.never})`);
  }
  // session 153: what a question of the four pages adds to the rule of its kind (warehouse/chat/eval_ercot_pages.json,
  // rules_added). A question of the 100 carries none of these fields and is judged exactly as it was.
  if (q.kind !== "refuse") {
    const text = String(r.answer ?? "");
    const tables = [...cites, ...series.map((s) => String(s.table ?? ""))];
    if (q.cite && !tables.some((t) => new RegExp(q.cite).test(t))) why.push(`no source matches ${q.cite} (${tables.join(", ") || "none"})`);
    if (Array.isArray(q.expect) && !q.expect.some((e) => holds(text, e))) why.push(`none of ${q.expect.join(", ")} is in the answer`);
    for (const e of Array.isArray(q.expect_all) ? q.expect_all : []) if (!holds(text, e)) why.push(`${e} is not in the answer`);
    if (q.must && !new RegExp(q.must, "i").test(text)) why.push(`the answer does not say ${q.must}`);
    if (q.series_has) {
      const d = decimals(q.series_has.value);
      const hit = series.some((s) => (s.rows ?? []).some((x) => String(x.key) === String(q.series_has.key) && typeof x.value === "number" && Math.abs(Math.round(x.value * 10 ** d) / 10 ** d - q.series_has.value) < 1e-9));
      if (!hit) why.push(`no series holds ${q.series_has.key}: ${q.series_has.value}`);
    }
    if (q.series_rows !== undefined && !series.some((s) => (s.rows ?? []).length === q.series_rows)) why.push(`no series of ${q.series_rows} rows (${series.map((s) => (s.rows ?? []).length).join(", ") || "none"})`);
  }
  return why;
}

/** The decimals a number is written with: 2 for 33.73, 0 for 9042. */
export const decimals = (v) => { const s = String(v); const i = s.indexOf("."); return i < 0 || /e/i.test(s) ? 0 : s.length - i - 1; };
/** The numbers of a text with the decimals each is written with: "1,678 hours at 33.7" gives [1678, 0] and [33.7, 1]. */
export function numbersIn(text) {
  const out = [];
  for (const m of String(text).matchAll(/(?<![A-Za-z_\d.])(\d{1,3}(?:,\d{3})+|\d+)(\.\d+)?(?!\d)/g)) out.push([parseFloat(m[1].replace(/,/g, "") + (m[2] ?? "")), m[2] ? m[2].length - 1 : 0]);
  return out;
}
/** Whether a text holds an expected number: some number of the text equals it at that number's own precision, which may
 * be one decimal coarser than the expected number's and no coarser (a number of 100 or more may be written whole).
 * Signs are not compared: a discount of 14.66 may be written -14.66 or "14.66 below". */
export function holds(text, expected) {
  const e = Math.abs(Number(expected)), de = decimals(expected);
  return numbersIn(text).some(([v, d]) => (d >= de - 1 || e >= 100) && d <= de && Math.abs(v - Math.round(e * 10 ** d) / 10 ** d) < 1e-9);
}
