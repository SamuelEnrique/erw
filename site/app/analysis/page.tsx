import type { Metadata } from "next";
import Link from "next/link";
import { AnalysisGallery } from "@/components/AnalysisGallery";
import { Section } from "@/components/Section";
import { DOCS, analysisWeeks } from "@/lib/markdown";
import { ChartOfWeekView } from "./view";

export const revalidate = 3600;
export const metadata: Metadata = { title: "Automated Analysis" };

// Session 23: Automated Analysis (platform tool 26). warehouse/analysis/run.py runs every template weekly, scores each
// result against its own history by a rule, and picks the chart of the week; this page shows it, the archive, this
// week's results for every public template, and the gallery.
export default function AnalysisPage() {
  const weeks = analysisWeeks();
  const a = DOCS.analysis;
  if (weeks.length === 0) {
    return (
      <>
        <h1 className="mb-2 text-3xl">Automated Analysis</h1>
        <p className="text-sm text-muted">no data: no week has been analysed yet (docs/analysis/ is empty).</p>
      </>
    );
  }
  const week = weeks[0];
  const res = a.results[week];
  return (
    <>
      <h1 className="mb-1 text-3xl">Automated Analysis</h1>
      <p className="mb-6 max-w-3xl text-sm text-muted">
        Ten chart templates run on the warehouse every week; a fixed rule picks the chart of the week, the result that stands furthest from
        its own history. Every chart names its tables, and every number in a note is checked against the template&apos;s output.
      </p>
      <Section title={`Chart of the week, ${week}`} aside={<Link href={`/analysis/${week}`}>This week&apos;s page</Link>}>
        <ChartOfWeekView c={a.weeks[week]} />
      </Section>
      {res ? (
        <Section title="This week's results">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-rule text-left text-xs text-muted">
                  <th className="py-1 pr-3">Template</th>
                  <th className="py-1 pr-3">Headline</th>
                  <th className="py-1 pr-3">Period</th>
                  <th className="py-1 pr-3 text-right">Value</th>
                  <th className="py-1 pr-3 text-right">Earlier values</th>
                  <th className="py-1 pr-3 text-right">Robust z</th>
                  <th className="py-1 text-right">Percentile</th>
                </tr>
              </thead>
              <tbody>
                {res.results.map((r) => (
                  <tr key={r.template} className="border-b border-rule align-top">
                    <td className="py-1 pr-3">
                      {r.title}
                      {r.template === res.picked ? <strong className="text-accent"> (picked)</strong> : null}
                    </td>
                    <td className="py-1 pr-3">{r.headline.label}</td>
                    <td className="py-1 pr-3 font-mono text-xs">{r.headline.period}</td>
                    <td className="py-1 pr-3 text-right">
                      {r.headline.value.toLocaleString("en-US")} {r.headline.unit}
                    </td>
                    <td className="py-1 pr-3 text-right">{r.history_n}</td>
                    <td className="py-1 pr-3 text-right">{r.notability_z ?? "not scored"}</td>
                    <td className="py-1 text-right">{r.percentile ?? ""}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="mt-2 text-xs text-muted">
            The rule: robust z = |value minus the median of its history| over 1.4826 times the median absolute deviation, capped at 10; a template needs at
            least 8 earlier values and a headline period that ended within 45 days. Internal templates (chokepoint transits) run on the
            warehouse&apos;s machines only.{" "}
            {res.skipped.length ? `Skipped this week: ${res.skipped.map((s) => `${s.template} (${s.reason})`).join("; ")}.` : null}
          </p>
        </Section>
      ) : null}
      <Section title="Template gallery">
        <AnalysisGallery gallery={a.gallery.templates} templates={a.templates.filter((t) => t.public)} />
        <p className="mt-3 text-xs text-muted">
          Each chart is computed by the warehouse&apos;s template code from public tables only, for every choice of its parameters, and served from that
          cache; the whole grid is recomputed every week{a.gallery.computed_at ? ` (last ${a.gallery.computed_at.slice(0, 10)})` : ""}.
        </p>
      </Section>
      <Section title="Archive">
        <ul className="text-sm">
          {weeks.map((w) => (
            <li key={w}>
              <Link href={`/analysis/${w}`}>{w}</Link>: {a.weeks[w].title}
            </li>
          ))}
        </ul>
      </Section>
    </>
  );
}
