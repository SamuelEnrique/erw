import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { SiteLink as Link } from "@/components/SiteLink";
import { FindingCard } from "@/components/analysis/FindingCard";
import { loadCard, loadCards } from "@/lib/findings";
import "../render.css";

// Session 170: one finding card on its own address, and the frame the renderer photographs (scripts/render-cards.mjs)
// at 1080 x 1350 and 1600 x 900 with ?render=1: the card alone in the bundled fonts (Source Serif 4 for the title and
// subtitle, Inter for the rest), nothing else on the page. In review like /analysis.
export const dynamicParams = false;

export function generateStaticParams() {
  return loadCards().map((c) => ({ id: c.card_id }));
}

type Props = { params: Promise<{ id: string }>; searchParams: Promise<Record<string, string | string[] | undefined>> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const c = loadCard((await params).id);
  return { title: c ? `${c.title}: Automated Analysis` : "Automated Analysis" };
}

export default async function CardPage({ params, searchParams }: Props) {
  const { id } = await params;
  const sp = await searchParams;
  const render = sp?.render === "1";
  const c = loadCard(id);
  if (!c) notFound();
  if (render) {
    return (
      <div className="finding-render" data-render="1">
        <FindingCard card={c} render />
        <p className="finding-render-foot">Energy Research Warehouse, erw-flame.vercel.app/analysis</p>
      </div>
    );
  }
  return (
    <>
      <p className="mb-4 text-sm"><Link href="/analysis">Automated Analysis</Link></p>
      <FindingCard card={c} formKey="form" />
    </>
  );
}
