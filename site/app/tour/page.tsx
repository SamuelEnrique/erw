import type { Metadata } from "next";
import { Brand } from "@/components/Brand";  // session 261: the page takes the brand (docs/brand.md), as /learn/bill does
import { SiteLink as Link } from "@/components/SiteLink";  // session 67: every link passes the release gate
import { MINUTES, STOPS, stopPath } from "@/lib/tour";
import { TourBar } from "./TourBar";

// Session 53: the guided tour for a first-time visitor, each stop a sentence and a link. No numbers here: each stop's
// page carries its own, checked.
// Session 292 (Samuel's ruling 11a of 14 October 2026): a guided path. This is its first page (stop 0 of the progress
// bar): the seven stops in a list and one action, "Start the tour", which opens /tour/1; each stop then has the bar,
// Back and Next (app/tour/[stop]/page.tsx).
export const metadata: Metadata = { title: "The tour" };

export default function Tour() {
  return (
    <Brand>
    <div>
      <h1 className="mb-1 text-3xl">The tour</h1>
      <p className="mb-5 max-w-3xl text-base">
        {STOPS.length} stops through the Energy Research Warehouse for a first visit, about {MINUTES} minutes in all: the three tools, the grid, research,
        the price board and the daily digest. Each stop says what to look at and opens the page.
      </p>
      <TourBar at={0} />
      <ol className="mb-6 max-w-3xl">
        {STOPS.map((s, i) => (
          <li key={s.href} className="border-b border-rule py-3">
            <div className="flex flex-wrap items-baseline justify-between gap-2">
              <Link href={stopPath(i + 1)} className="font-serif text-lg">{i + 1}. {s.title}</Link>
              <span className="text-xs text-muted">about {s.seconds} seconds</span>
            </div>
            <p className="max-w-3xl text-sm">{s.line}</p>
          </li>
        ))}
      </ol>
      <p className="mb-6">
        <Link href={stopPath(1)} className="inline-block border border-accent bg-accent px-4 py-2 text-white no-underline">Start the tour</Link>
      </p>
      <p className="max-w-3xl text-sm text-muted">
        After the tour: the <Link href="/">home page</Link> lists every tool by who it is for, and <Link href="/data">data and methods</Link> says how every
        number is built.
      </p>
    </div>
    </Brand>
  );
}
