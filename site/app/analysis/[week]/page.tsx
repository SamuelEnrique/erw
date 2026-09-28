import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { DOCS, analysisWeeks } from "@/lib/markdown";
import { ChartOfWeekView } from "../view";

export const revalidate = 3600;
export const dynamicParams = false;

export function generateStaticParams() {
  return analysisWeeks().map((week) => ({ week }));
}

export async function generateMetadata({ params }: PageProps<"/analysis/[week]">): Promise<Metadata> {
  return { title: `ERW's Chart of the Week, ${(await params).week}` };
}

export default async function AnalysisWeek({ params }: PageProps<"/analysis/[week]">) {
  const { week } = await params;
  const c = DOCS.analysis.weeks[week];
  if (!c) notFound();
  return (
    <>
      <p className="mb-4 flex gap-4 text-sm">
        <Link href="/analysis">Automated Analysis</Link>
        <Link href={`/roundup/${week}`}>ERW&apos;s Roundup, {week}</Link>
      </p>
      <h1 className="mb-4 text-3xl">ERW&apos;s Chart of the Week, {week}</h1>
      <ChartOfWeekView c={c} />
    </>
  );
}
