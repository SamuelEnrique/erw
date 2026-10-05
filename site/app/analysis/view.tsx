import { EChartOption } from "@/components/EChartOption";
import type { ChartOfWeek } from "@/lib/markdown";

// Session 23: the chart of the week, as on /analysis and /analysis/<week>
export function ChartOfWeekView({ c }: { c: ChartOfWeek }) {
  const base = `/analysis-files/${c.week}`;
  return (
    <figure>
      <h3 className="text-2xl">{c.title}</h3>
      <p className="mb-2 text-xs text-muted">{c.subtitle}</p>
      <EChartOption option={c.option} label={c.title} height={380} />
      {c.finding ? <p className="mt-3 max-w-3xl font-semibold" data-finding="1">{c.finding}</p> : null}
      <p className="mt-3 max-w-3xl">{c.note}</p>
      <figcaption className="mt-2 text-xs text-muted">
        {c.finding ? (
          // session 119: picked for a change, ranked among the measure's own earlier changes
          <>
            {c.source_line} Picked by rule: {c.rule}.{c.picked_by && c.picked_by !== "the rule" ? ` This week: ${c.picked_by}.` : ""}{" "}
            {c.change && c.change.score !== null ? `Of the ${c.change.earlier_changes} earlier changes it was ranked among, ${c.change.score} percent were smaller. ` : ""}
            Note: {c.note_by}.
          </>
        ) : (
          <>
            {c.source_line} Headline: {c.headline.label}, {c.headline.period}: {c.headline.value.toLocaleString("en-US")} {c.headline.unit}; robust z{" "}
            {c.notability_z} against {c.history_n} earlier values ({c.percentile}th percentile). Picked by rule: {c.rule}. Note: {c.note_by}.
          </>
        )}
      </figcaption>
      {c.also_moved && c.also_moved.length ? (
        <div className="mt-3 max-w-3xl text-sm" data-also-moved={c.also_moved.length}>
          <div className="text-xs text-muted">Also moved, next by the same rule</div>
          <ul className="list-disc pl-5">
            {c.also_moved.map((a) => (
              <li key={a.template}>{a.finding}</li>
            ))}
          </ul>
        </div>
      ) : null}
      <p className="mt-2 text-xs">
        Images: <a href={`${base}/${c.files.email}`}>email</a>, <a href={`${base}/${c.files.social_wide}`}>1200 by 627</a>,{" "}
        <a href={`${base}/${c.files.social_square}`}>1080 by 1080</a>.
      </p>
      <details className="mt-2 text-xs text-muted">
        <summary>Citations</summary>
        <ul className="list-disc pl-5">
          {c.citations.map((x) => (
            <li key={x}>{x}</li>
          ))}
        </ul>
      </details>
    </figure>
  );
}
