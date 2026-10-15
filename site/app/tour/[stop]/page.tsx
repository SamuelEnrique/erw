import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { Brand } from "@/components/Brand";
import { SiteLink as Link } from "@/components/SiteLink";  // session 67: every link passes the release gate
import { STOPS, stopPath } from "@/lib/tour";
import { TourBar } from "../TourBar";

// Session 292 (Samuel's ruling 11a of 14 October 2026): one stop of the guided tour. The progress bar, the stop's page
// in a sentence, what to look at there, and the one action: open it. Back and Next on every stop. No numbers here: the
// stop's page carries its own, checked.
export function generateStaticParams() {
  return STOPS.map((_, i) => ({ stop: String(i + 1) }));
}
const at = (raw: string) => (/^[1-9]\d*$/.test(raw) && Number(raw) <= STOPS.length ? Number(raw) : null);

export async function generateMetadata({ params }: { params: Promise<{ stop: string }> }): Promise<Metadata> {
  const n = at((await params).stop);
  return { title: n ? `The tour, stop ${n}: ${STOPS[n - 1].title}` : "The tour" };
}

export default async function TourStop({ params }: { params: Promise<{ stop: string }> }) {
  const n = at((await params).stop);
  if (!n) notFound();
  const s = STOPS[n - 1];
  return (
    <Brand>
    <div>
      <p className="mb-1 text-xs text-muted"><Link href="/tour">The tour</Link></p>
      <TourBar at={n} />
      <h1 className="mb-3 text-3xl">{s.title}</h1>
      <p className="mb-3 max-w-3xl text-base">{s.line}</p>
      <section className="mb-4 max-w-3xl border border-rule bg-paper p-4 text-sm" data-tour-look>
        <h2 className="mb-1 text-base">What to look at</h2>
        <p className="max-w-3xl">{s.look}</p>
        <p className="mt-1 text-xs text-muted">About {s.seconds} seconds. Come back with the browser&apos;s Back button, or open the page in a new tab.</p>
      </section>
      {/* the words in a span of their own: the site's base link colour (cardinal) wins over a colour class on the link
          itself (docs/brand.md, section 9), and would draw cardinal on cardinal */}
      <div className="mb-8">
        <Link href={s.href} className="inline-block border border-accent bg-accent px-4 py-2 no-underline" data-tour-open><span className="text-white">Open {s.title.replace(/^The /, "the ")}</span></Link>
      </div>
      <p className="text-sm text-muted">{n < STOPS.length ? <>Next: <Link href={stopPath(n + 1)}>{STOPS[n].title}</Link>.</> : <>The last stop. After the tour: the <Link href="/">home page</Link> lists every tool by who it is for, and <Link href="/data">data and methods</Link> says how every number is built.</>}</p>
    </div>
    </Brand>
  );
}
