import type { Metadata } from "next";
import { Brand } from "@/components/Brand";  // session 261: the page takes the brand (docs/brand.md), as /learn/bill does
import { SiteLink as Link } from "@/components/SiteLink";  // session 67: every link passes the release gate
import { Section } from "@/components/Section";
import { SETS } from "@/lib/problems";
import { editionPath, editions, longDate, teacherPath } from "@/lib/problemEditions";

// Session 44: the problem sets' index (lib/problems.ts).
export const metadata: Metadata = { title: "Problem sets" };

export default function ProblemSets() {
  return (
    <Brand>
    <div>
      <h1 className="mb-1 text-3xl">Problem sets</h1>
      <p className="mb-5 max-w-3xl text-sm text-muted">
        Questions for an undergraduate class, answered from the warehouse&apos;s own tables. Each question names its tables, and each answer opens to
        a worked solution with the actual numbers and a line on why it matters.
      </p>
      {/* session 293 (Samuel's ruling 8a): each set live, and as a dated edition with a teacher's copy */}
      <p className="mb-5 max-w-3xl text-sm">
        Each set comes two ways. The live set asks its questions of the newest data, so its numbers move as the tables update. A dated edition keeps the
        numbers of its day{editions().length ? <>, the newest of {longDate(editions()[0])}</> : null}: its students&apos; copy has no answers, each question
        comes with the rows it needs, and its teacher&apos;s copy has every answer, ready to print.
      </p>
      <Section title="Sets">
        <ul className="space-y-3">
          {SETS.map((s) => (
            <li key={s.slug}>
              <Link href={`/learn/problems/${s.slug}`} className="text-lg">{s.title}</Link>
              <div className="text-sm text-muted">{s.line}</div>
              {editions().length ? (
                <div className="text-sm">The live set; <Link href={editionPath(s.slug, editions()[0])}>the edition of {editions()[0]}</Link>; <Link href={teacherPath(s.slug, editions()[0])}>its teacher&apos;s copy</Link>.</div>
              ) : null}
            </li>
          ))}
        </ul>
      </Section>
    </div>
    </Brand>
  );
}
