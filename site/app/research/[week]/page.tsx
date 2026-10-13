import type { Metadata } from "next";
import { SiteLink as Link } from "@/components/SiteLink";  // session 67: every link passes the release gate
import { notFound } from "next/navigation";
import { DOCS, analysisWeeks } from "@/lib/markdown";
import { ChartOfWeekView } from "../view";
import { Brand } from "@/components/Brand";   // session 238: the page takes the brand
import { ToolPage } from "@/components/tool/ToolPage";

export const revalidate = 3600;
export const dynamicParams = false;

export function generateStaticParams() {
  return analysisWeeks().map((week) => ({ week }));
}

export async function generateMetadata({ params }: PageProps<"/research/[week]">): Promise<Metadata> {
  return { title: `ERW's Chart of the Week, ${(await params).week}` };
}

export default async function AnalysisWeek({ params }: PageProps<"/research/[week]">) {
  const { week } = await params;
  const c = DOCS.analysis.weeks[week];
  if (!c) notFound();
  return (
    <Brand>
      <ToolPage>
      <div data-chart-tokens="1">
      <p className="mb-4 flex gap-4 text-sm">
        <Link href="/research">Research</Link>
        <Link href={`/roundup/${week}`}>ERW&apos;s Roundup, {week}</Link>
      </p>
      <h1 className="mb-4 text-3xl">ERW&apos;s Chart of the Week, {week}</h1>
      <ChartOfWeekView c={c} />
      </div>
      </ToolPage>
    </Brand>
  );
}
