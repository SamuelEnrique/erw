import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { DOCS, render, weeklyWeeks } from "@/lib/markdown";

export const revalidate = 3600;
export const dynamicParams = false;

export function generateStaticParams() {
  return weeklyWeeks().map((week) => ({ week }));
}

export async function generateMetadata({ params }: PageProps<"/roundup/[week]">): Promise<Metadata> {
  const { week } = await params;
  const name = DOCS.weekly_source[week]?.startsWith("docs/weekly/") ? "Energy Week" : "ERW's Roundup";
  return { title: `${name}, ${week}` };
}

// Session 23: the Energy Roundup for one ISO week (an Energy Week before session 23); /weekly/<week> redirects here
export default async function RoundupWeek({ params }: PageProps<"/roundup/[week]">) {
  const { week } = await params;
  const md = DOCS.weeklies[week];
  if (!md) notFound();
  const weeks = weeklyWeeks();
  const i = weeks.indexOf(week);
  return (
    <>
      <p className="mb-4 flex gap-4 text-sm">
        <Link href="/roundup">Archive</Link>
        {weeks[i + 1] ? <Link href={`/roundup/${weeks[i + 1]}`}>Earlier: {weeks[i + 1]}</Link> : null}
        {i > 0 ? <Link href={`/roundup/${weeks[i - 1]}`}>Later: {weeks[i - 1]}</Link> : null}
      </p>
      <article className="prose-erw" dangerouslySetInnerHTML={{ __html: render(md, DOCS.weekly_source[week]) }} />
    </>
  );
}
