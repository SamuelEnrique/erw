import type { Metadata } from "next";
import { SiteLink as Link } from "@/components/SiteLink";  // session 67: every link passes the release gate
import { STOPS } from "@/lib/tour";

// Session 53: the guided tour for a first-time visitor: five stops, about three minutes, each a sentence and a link.
// No numbers here: each stop's page carries its own, checked.
export const metadata: Metadata = { title: "The tour" };


export default function Tour() {
  return (
    <>
      <h1 className="mb-1 text-3xl">The tour</h1>
      <p className="mb-5 max-w-3xl text-sm text-muted">
        Five stops through the Energy Research Warehouse for a first visit, about three minutes in all. Each stop opens a page of the site; come back here for
        the next one.
      </p>
      <ol className="max-w-3xl space-y-3">
        {STOPS.map((s, i) => (
          <li key={s.href} className="border border-rule bg-panel p-3">
            <div className="flex flex-wrap items-baseline justify-between gap-2">
              <span className="font-serif text-lg">{i + 1}. {s.title}</span>
              <span className="text-xs text-muted">{s.minutes}</span>
            </div>
            <p className="text-sm">{s.line}</p>
            <p className="text-sm text-muted">{s.look}</p>
            <Link href={s.href} className="mt-1 inline-block text-sm">Open stop {i + 1}: {s.title}</Link>
          </li>
        ))}
      </ol>
      <p className="mt-4 max-w-3xl text-sm">
        After the tour: the <Link href="/">home page</Link> lists every tool by who it is for, and <Link href="/data">data and methods</Link> says how every
        number is built.
      </p>
    </>
  );
}
