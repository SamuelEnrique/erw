import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { Brand } from "@/components/Brand";
import { SiteLink as Link } from "@/components/SiteLink";  // session 67: every link passes the release gate
import { Section } from "@/components/Section";
import { edition, editionPath, editions, longDate } from "@/lib/problemEditions";
import { SETS } from "@/lib/problems";
import { FrozenParts } from "../../../Frozen";
import { PrintButton } from "../../../PrintButton";

// Session 293 (Samuel's ruling 8a of 14 October 2026): the teacher's copy of a dated edition: every question with its
// answer and worked solution open, why it matters, and the rows it needs, ready to print. The figures are the edition's,
// frozen with its date.
export function generateStaticParams() {
  return SETS.flatMap((s) => editions().map((e) => ({ slug: s.slug, edition: e })));
}
export async function generateMetadata({ params }: { params: Promise<{ slug: string; edition: string }> }): Promise<Metadata> {
  const { slug, edition: d } = await params;
  const t = SETS.find((s) => s.slug === slug)?.title;
  return { title: t ? `${t}: the teacher's copy, ${d}` : "Problem set" };
}

export default async function TeacherCopy({ params }: { params: Promise<{ slug: string; edition: string }> }) {
  const { slug, edition: d } = await params;
  const e = edition(d);
  const set = e?.sets.find((s) => s.slug === slug);
  if (!e || !set) notFound();
  return (
    <Brand>
    <div>
      <p className="mb-1 text-xs text-muted print:hidden"><Link href="/learn/problems">Problem sets</Link> / <Link href={editionPath(slug, d)}>{set.title}, the edition of {d}</Link> / the teacher&apos;s copy</p>
      <h1 className="mb-1 text-3xl">{set.title}: the teacher&apos;s copy</h1>
      <p className="mb-3 max-w-3xl text-base">The edition of {longDate(d)}, with every answer. The students&apos; copy, without them: <Link href={editionPath(slug, d)}>{editionPath(slug, d)}</Link>.</p>
      <div className="mb-6 flex flex-wrap items-center gap-3"><PrintButton label="Print the teacher's copy" /></div>
      <div className="mb-6 max-w-3xl border border-rule bg-paper p-4 text-sm">
        <p className="max-w-3xl"><strong>For teachers.</strong> {set.teacher}</p>
      </div>
      <ol className="space-y-6">
        {set.questions.map((q, n) => (
          <li key={q.id} className="break-inside-avoid">
            <Section title={`Question ${n + 1}`}>
              <p className="mb-2 max-w-3xl">{q.q}</p>
              <p className="mb-2 max-w-3xl"><strong>Answer.</strong> <FrozenParts parts={q.answer} /></p>
              <p className="font-semibold">Worked solution</p>
              <ol className="max-w-3xl list-decimal pl-6 text-sm">
                {q.steps.map((s, i) => <li key={i}><FrozenParts parts={s} /></li>)}
              </ol>
              <p className="mt-2 max-w-3xl text-sm text-muted">Why it matters: {q.why}</p>
              <p className="mt-1 max-w-3xl text-xs text-muted">Tables: {q.tables.join(", ")}. <a href={q.csv} download>The {q.rows} rows this question needs (CSV)</a>.</p>
            </Section>
          </li>
        ))}
      </ol>
      <p className="mt-6 max-w-3xl text-xs text-muted">Built on {e.built_at.replace("T", " ").replace("Z", " UTC")} from the ERW live set by <span className="font-mono">site/scripts/build-problem-edition.mjs</span>, the same code as the live set.</p>
    </div>
    </Brand>
  );
}
