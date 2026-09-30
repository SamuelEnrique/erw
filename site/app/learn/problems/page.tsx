import type { Metadata } from "next";
import Link from "next/link";
import { Section } from "@/components/Section";
import { SETS } from "@/lib/problems";

// Session 44: the problem sets' index (lib/problems.ts).
export const metadata: Metadata = { title: "Problem sets" };

export default function ProblemSets() {
  return (
    <>
      <h1 className="mb-1 text-3xl">Problem sets</h1>
      <p className="mb-5 max-w-3xl text-sm text-muted">
        Questions for an undergraduate class, answered from the warehouse&apos;s own tables. Each question names its tables, and each answer opens to
        a worked solution with the actual numbers and a line on why it matters.
      </p>
      <Section title="Sets">
        <ul className="space-y-3">
          {SETS.map((s) => (
            <li key={s.slug}>
              <Link href={`/learn/problems/${s.slug}`} className="text-lg">{s.title}</Link>
              <div className="text-sm text-muted">{s.line}</div>
            </li>
          ))}
        </ul>
      </Section>
    </>
  );
}
