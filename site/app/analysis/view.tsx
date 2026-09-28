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
      <p className="mt-3 max-w-3xl">{c.note}</p>
      <figcaption className="mt-2 text-xs text-muted">
        {c.source_line} Headline: {c.headline.label}, {c.headline.period}: {c.headline.value.toLocaleString("en-US")} {c.headline.unit}; robust z{" "}
        {c.notability_z} against {c.history_n} earlier values ({c.percentile}th percentile). Picked by rule: {c.rule}. Note: {c.note_by}.
      </figcaption>
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
