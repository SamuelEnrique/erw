// Session 292 (Samuel's ruling 11a of 14 October 2026): the tour's progress bar, one shared component for every stop
// of the guided path (and the tour's first page, at stop 0). One segment a stop, the stops done and the one in view in
// ink, the rest in the rule colour; "Stop 3 of 7"; Back and Next as plain links, so the path is the address. The brand's
// rules only (docs/brand.md): square, no motion, cardinal for nothing but the links.
import { SiteLink as Link } from "@/components/SiteLink";
import { STOPS, stopPath } from "@/lib/tour";

export function TourBar({ at }: { at: number }) {
  const n = STOPS.length;
  const back = at <= 1 ? "/tour" : stopPath(at - 1);
  const next = at < n ? stopPath(at + 1) : null;
  return (
    <nav className="mb-6" aria-label="The tour" data-tour-bar={at}>
      {/* one segment a stop, each a link 24 px tall (the brand's smallest target) around an 8 px bar */}
      <div className="mb-1 flex gap-1">
        {STOPS.map((s, i) => (
          <Link key={s.href} href={stopPath(i + 1)} aria-label={`Stop ${i + 1}: ${s.title}`} aria-current={i + 1 === at ? "step" : undefined} className="block flex-1 py-2">
            <span className={`block h-2 ${i + 1 <= at ? "bg-[var(--color-ink)]" : "bg-[var(--color-rule)]"}`} />
          </Link>
        ))}
      </div>
      <div className="flex flex-wrap items-center justify-between gap-2 text-sm">
        <span className="text-muted">{at ? `Stop ${at} of ${n}` : `${n} stops`}</span>
        {at ? (
          <span className="flex gap-6">
            <Link href={back} rel="prev">Back</Link>
            {next ? <Link href={next} rel="next">Next</Link> : <Link href="/tour">The tour&apos;s first page</Link>}
          </span>
        ) : null}
      </div>
    </nav>
  );
}
