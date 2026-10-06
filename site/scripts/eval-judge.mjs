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
  }
  return why;
}
