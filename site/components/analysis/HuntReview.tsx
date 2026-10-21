import { DOCS, type HuntFinding } from "@/lib/markdown";
import { Section } from "@/components/Section";

// The findings hunt of 20 October 2026 (warehouse/analysis/findings/hunt_oct20.py; docs/findings/<day>/): the ten findings
// the hunt kept, each with its state, its tests, its chart, its caption and the downloads of its extract and its Stata
// do-file. Everything here is read from the committed files at build (lib/markdown.ts, findings_review), not from the
// review list in the database: the hunt ran on a machine that writes nothing to Supabase, and its findings travel on a
// branch. The four states are new, approved, rejected and Stata checked. A state is changed on the branch, not here:
//   python warehouse/analysis/findings/hunt_oct20.py state <slug> <new|approved|rejected|stata_checked>
// then a commit; the page shows the state the committed file holds. Nothing here posts anywhere, and no sentence is a
// model's: the fact, the tests and the caption are computed from the numbers. A finding marked internal is listed with
// its state and nothing else; none of this hunt's is.
const STATE_WORDS: Record<HuntFinding["state"], string> = { new: "New, not reviewed", approved: "Approved", rejected: "Rejected", stata_checked: "Stata checked" };
const STATES: HuntFinding["state"][] = ["new", "approved", "rejected", "stata_checked"];
const n = (v: number, nd: number) => v.toLocaleString("en-US", { minimumFractionDigits: nd, maximumFractionDigits: nd });

function href(f: HuntFinding, name: string, show = false) {
  return `/internal/findings/local?day=${encodeURIComponent(f.day)}&slug=${encodeURIComponent(f.slug)}&name=${encodeURIComponent(name)}${show ? "&show=1" : ""}`;
}

function Finding({ f }: { f: HuntFinding }) {
  const c = f.claim as Record<string, string | number>;
  const has = (name: string) => f.files_held.includes(name);
  return (
    <div className="border border-rule p-3" data-hunt-finding={f.slug} data-hunt-state={f.state} data-hunt-kind={f.kind} data-hunt-internal={f.internal ? "1" : "0"}>
      <p className="mb-1 text-xs text-muted">
        Finding {f.rank} of the hunt of {f.day}; {f.kind === "record" ? "a record" : "a trend"}; strength {n(f.strength, 2)} typical moves; table{f.tables.length > 1 ? "s" : ""}{" "}
        <span className="font-mono">{f.tables.join(", ")}</span>; license {f.license}{f.internal ? "; internal: never on a public page or in a caption" : ""}
      </p>
      <p className="mb-1 text-xs" data-hunt-state-words={f.state}>
        State: <strong>{STATE_WORDS[f.state]}</strong>
        {f.state_history.length ? <span className="text-muted"> (since {f.state_history[f.state_history.length - 1].at.replace("T", " ").slice(0, 16)} UTC)</span> : null}
        <span className="text-muted">. To change it on the branch: </span>
        <span className="font-mono">python warehouse/analysis/findings/hunt_oct20.py state {f.slug} {"<"}{STATES.join("|")}{">"}</span>
      </p>
      {f.shown_before ? <p className="mb-1 text-xs text-muted" data-hunt-shown="1">The ERW has shown this topic before: {f.shown_before}.</p> : null}
      <h3 className="mt-2 text-lg">{f.title}</h3>
      <p className="mb-2 text-sm" data-hunt-fact={f.slug}>{f.fact}</p>
      {f.internal ? null : (
        <>
          <ul className="mb-2 list-disc pl-5 text-xs" data-hunt-tests={f.tests.length}>
            {f.tests.map((t) => <li key={t.name}>{t.passed ? "Passed" : "Failed"}: {t.name}. {t.words}.</li>)}
          </ul>
          {f.note ? <p className="mb-2 text-xs text-muted">{f.note.charAt(0).toUpperCase() + f.note.slice(1)}.</p> : null}
          <p className="mb-2 text-xs text-muted">
            Headline in the do-file: <span className="font-mono" data-hunt-expected={f.headline.expected_in_do_file}>{f.headline.expected_in_do_file}</span> {f.unit} for period {f.headline.period}
            {" "}({f.extract_rows.toLocaleString("en-US")} extract rows); the comparison period {f.headline.compare_period} gives{" "}
            <span className="font-mono">{n(f.headline.compare_value, f.decimals)}</span>.
            {" "}Kind {c.kind as string}, computed {f.computed_at.replace("T", " ").slice(0, 16)} UTC by hunt {f.hunt_version}.
          </p>
          <div className="mb-2 flex flex-wrap gap-3">
            {["chart_wide.png", "chart_square.png"].filter(has).map((name) => (
              // eslint-disable-next-line @next/next/no-img-element
              <img key={name} src={href(f, name, true)} alt={`${f.title}: ${name === "chart_wide.png" ? "1600 by 900" : "1200 by 1200"}`} loading="lazy" className="max-h-72 w-auto border border-rule" data-hunt-picture={name} />
            ))}
          </div>
          <p className="mb-2 flex flex-wrap items-center gap-3 text-xs" data-hunt-downloads={["extract.csv", "check.do", "series.csv", "caption.md", "chart_square.png", "chart_wide.png", "finding.json"].filter(has).length}>
            <span className="text-muted">Downloads:</span>
            {has("extract.csv") ? <a href={href(f, "extract.csv")} download data-hunt-file="extract.csv">extract.csv (the exact rows)</a> : null}
            {has("check.do") ? <a href={href(f, "check.do")} download data-hunt-file="check.do">check.do (Stata)</a> : null}
            {has("series.csv") ? <a href={href(f, "series.csv")} download data-hunt-file="series.csv">series.csv</a> : null}
            {has("caption.md") ? <a href={href(f, "caption.md")} download data-hunt-file="caption.md">caption.md</a> : null}
            {has("chart_square.png") ? <a href={href(f, "chart_square.png")} download data-hunt-file="chart_square.png">chart, 1200 by 1200</a> : null}
            {has("chart_wide.png") ? <a href={href(f, "chart_wide.png")} download data-hunt-file="chart_wide.png">chart, 1600 by 900</a> : null}
            {has("finding.json") ? <a href={href(f, "finding.json")} download data-hunt-file="finding.json">finding.json</a> : null}
          </p>
          <p className="text-xs text-muted">LinkedIn caption, {f.caption.length.toLocaleString("en-US")} characters, computed from the numbers; nothing is posted by this page:</p>
          <pre className="mt-1 whitespace-pre-wrap border border-rule bg-panel p-2 text-xs" data-hunt-caption={f.slug}>{f.caption}</pre>
        </>
      )}
    </div>
  );
}

export function HuntReview() {
  const days = Object.entries(DOCS.findings_review?.days ?? {}).sort((a, b) => b[0].localeCompare(a[0]));
  if (days.length === 0) return <Section title="The findings hunt"><p className="text-sm text-muted" data-hunt-days="0">No hunt folder is committed under docs/findings.</p></Section>;
  return (
    <>
      {days.map(([day, d]) => {
        const count = (s: HuntFinding["state"]) => d.findings.filter((f) => f.state === s).length;
        return (
          <Section key={day} title={`The findings hunt of ${day}`} aside={`${d.findings.length}`} id={`hunt-${day}`}>
            <p className="mb-3 max-w-3xl text-sm text-muted" data-hunt-day={day} data-hunt-count={d.findings.length}>
              {d.index.summary.candidates} candidate claims were computed from the warehouse&apos;s own tables, {d.index.summary.passing} passed their tests and{" "}
              {d.findings.length} were kept, strongest first, a claim the ERW has shown before ranked after the new ones. Each has the exact rows its number comes from,
              a Stata do-file that reproduces the number (run it, then mark the finding Stata checked), two charts and a caption. Grids that need a license or are held
              ({d.index.summary.blocked_grids.join(", ")}) were never drafted. Hunt {d.index.hunt_version}, computed {d.index.computed_at.replace("T", " ").slice(0, 16)} UTC.
            </p>
            <div className="mb-6 grid grid-cols-2 gap-px border border-rule bg-rule sm:grid-cols-4">
              {STATES.map((s) => (
                <div key={s} className="bg-panel p-3"><div className="text-xs text-muted">{STATE_WORDS[s]}</div><div className="text-2xl tabular-nums" data-hunt-n={s}>{count(s)}</div></div>
              ))}
            </div>
            <div className="flex flex-col gap-8">{d.findings.map((f) => <Finding key={f.slug} f={f} />)}</div>
          </Section>
        );
      })}
    </>
  );
}
