import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { DOCS, render, weeklyWeeks } from "@/lib/markdown";

export const revalidate = 3600;
export const dynamicParams = false;

export function generateStaticParams() {
  return weeklyWeeks().map((week) => ({ week }));
}

export async function generateMetadata({ params }: PageProps<"/weekly/[week]">): Promise<Metadata> {
  return { title: `Energy Week, ${(await params).week}` };
}

export default async function WeeklyWeek({ params }: PageProps<"/weekly/[week]">) {
  const { week } = await params;
  const md = DOCS.weeklies[week];
  if (!md) notFound();
  const weeks = weeklyWeeks();
  const i = weeks.indexOf(week);
  return (
    <>
      <p className="mb-4 flex gap-4 text-sm">
        <Link href="/weekly">Archive</Link>
        {weeks[i + 1] ? <Link href={`/weekly/${weeks[i + 1]}`}>Earlier: {weeks[i + 1]}</Link> : null}
        {i > 0 ? <Link href={`/weekly/${weeks[i - 1]}`}>Later: {weeks[i - 1]}</Link> : null}
      </p>
      <article className="prose-erw" dangerouslySetInnerHTML={{ __html: render(md, `docs/weekly/${week}.md`) }} />
    </>
  );
}
