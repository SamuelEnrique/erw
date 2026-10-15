import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { Brand } from "@/components/Brand";
import { SiteLink as Link } from "@/components/SiteLink";  // session 67: every link passes the release gate
import { Section } from "@/components/Section";
import { edition, editions, longDate, teacherPath } from "@/lib/problemEditions";
import { SETS } from "@/lib/problems";

// Session 293 (Samuel's ruling 8a of 14 October 2026): a dated edition of a problem set, the students' copy. The
// questions as they were built on the edition's date, each with its tables and a download of the rows it needs; no
// answers (they are in the teacher's copy). The numbers do not move.
export function generateStaticParams() {
  return SETS.flatMap((s) => editions().map((e) => ({ slug: s.slug, edition: e })));
}
export async function generateMetadata({ params }: { params: Promise<{ slug: string; edition: string }> }): Promise<Metadata> {
  const { slug, edition: d } = await params;
  const t = SETS.find((s) => s.slug === slug)?.title;
  return { title: t ? `${t}: the edition of ${d}` : "Problem set" };
}

export default async function EditionPage({ params }: { params: Promise<{ slug: string; edition: string }> }) {
  const { slug, edition: d } = await params;
  const e = edition(d);
  const set = e?.sets.find((s) => s.slug === slug);
  if (!e || !set) notFound();
  return (
    <Brand>
    <div>
      <p className="mb-1 text-xs text-muted"><Link href="/learn/problems">Problem sets</Link> / <Link href={`/learn/problems/${slug}`}>{set.title}</Link> / the edition of {d}</p>
      <h1 className="mb-1 text-3xl">{set.title}</h1>
      <p className="mb-3 max-w-3xl text-base">The edition of {longDate(d)}: the questions as the warehouse&apos;s tables stood that day. Its numbers do not move, so a class answers what its teacher prepared.</p>
      <div className="mb-6 max-w-3xl border border-rule bg-paper p-4 text-sm">
        <p className="max-w-3xl"><strong>For teachers.</strong> {set.teacher}</p>
        <p className="mt-1 max-w-3xl">The answers and worked solutions are in <Link href={teacherPath(slug, d)}>the teacher&apos;s copy</Link>. <Link href={`/learn/problems/${slug}`}>The live set</Link> asks the same questions of the newest data.</p>
      </div>
      <ol className="space-y-6">
        {set.questions.map((q, n) => (
          <li key={q.id}>
            <Section title={`Question ${n + 1}`}>
              <p className="mb-1 max-w-3xl">{q.q}</p>
              <p className="max-w-3xl text-xs text-muted">
                Tables: {q.tables.map((t, i) => <span key={t}>{i ? ", " : ""}<Link href={`/data#${t}`} className="font-mono">{t}</Link></span>)}.{" "}
                <a href={q.csv} download data-rows={q.rows}>The {q.rows} rows this question needs (CSV)</a>.
              </p>
            </Section>
          </li>
        ))}
      </ol>
      <p className="mt-6 max-w-3xl text-xs text-muted">Built on {e.built_at.replace("T", " ").replace("Z", " UTC")} from the ERW live set by <span className="font-mono">site/scripts/build-problem-edition.mjs</span>, the same code as the live set (<span className="font-mono">site/lib/problems.ts</span>).</p>
    </div>
    </Brand>
  );
}
