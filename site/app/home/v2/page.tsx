import type { Metadata } from "next";
import { SiteLink as Link } from "@/components/SiteLink";
import { AUDIENCES, ONE_SENTENCE, counts, listed } from "@/lib/audience";

// Session 110: the home page and menu by audience, a draft. Three ways in (investors and lenders, operators and
// developers, students and teachers), each with its tools: the live ones first, the ones in review greyed. One
// sentence says what the ERW is. The draft menu is drawn here, inside this page, and nowhere else: the site's menu
// (components/Nav.tsx) and the live home page (app/page.tsx) are as they were. Every tool's status is read from the
// release gate, never written here.

export const metadata: Metadata = { title: "Home, by audience (draft)", robots: { index: false, follow: false } };

export default function HomeTwo() {
  const c = counts();
  return (
    <>
      <nav aria-label="Draft menu, by audience" data-draft-menu="1" className="mb-8 border border-rule bg-paper px-4 py-3">
        <div className="mb-2 text-xs uppercase tracking-wide text-muted">Draft menu, shown on this page only</div>
        <ul className="flex flex-wrap gap-x-6 gap-y-2 text-sm">
          {AUDIENCES.map((a) => (
            <li key={a.id}>
              <details>
                <summary className="cursor-pointer font-serif text-base text-accent">{a.label}</summary>
                <ul className="mt-2 space-y-1 border-l-2 border-rule pl-3">
                  {listed(a).map((t) => (
                    <li key={t.href} data-menu-item={t.status}>
                      {t.status === "live"
                        ? <Link href={t.href} className="underline">{t.label}</Link>
                        : <span className="text-muted"><Link href={t.href}>{t.label}</Link> <span className="text-[11px]">in review</span></span>}
                    </li>
                  ))}
                </ul>
              </details>
            </li>
          ))}
          <li><Link href="/about" className="underline">About</Link></li>
        </ul>
      </nav>

      <header className="mb-8">
        <h1 className="font-serif text-4xl text-accent">Energy Research Warehouse</h1>
        <p className="mt-3 max-w-3xl text-lg leading-relaxed" data-one-sentence="1">{ONE_SENTENCE}</p>
        <p className="mt-2 max-w-3xl text-sm text-muted" data-home-counts="1">
          Three ways in. {c.tools} tools are listed below; {c.live} are open today and {c.review} are in review, shown greyed.
        </p>
      </header>

      <div className="grid gap-8 lg:grid-cols-3">
        {AUDIENCES.map((a) => {
          const tools = listed(a);
          const live = tools.filter((t) => t.status === "live");
          const review = tools.filter((t) => t.status === "review");
          return (
            <section key={a.id} aria-labelledby={`way-${a.id}`} data-audience={a.id} className="border-t-2 border-accent pt-3">
              <h2 id={`way-${a.id}`} className="font-serif text-2xl text-accent">{a.label}</h2>
              <p className="mb-4 mt-1 text-sm text-muted">{a.line}</p>
              <ul className="space-y-3">
                {live.map((t) => (
                  <li key={t.href} data-tool="live">
                    <Link href={t.href} className="font-semibold underline">{t.label}</Link>
                    <p className="text-sm leading-snug">{t.question}</p>
                  </li>
                ))}
              </ul>
              {review.length ? (
                <>
                  <div className="mb-2 mt-5 border-t border-rule pt-2 text-xs uppercase tracking-wide text-muted">In review</div>
                  <ul className="space-y-3">
                    {review.map((t) => (
                      <li key={t.href} data-tool="review" className="text-muted">
                        <Link href={t.href} className="font-semibold">{t.label}</Link>
                        <p className="text-sm leading-snug">{t.question}</p>
                      </li>
                    ))}
                  </ul>
                </>
              ) : null}
            </section>
          );
        })}
      </div>

      <p className="mt-10 max-w-3xl border-t border-rule pt-3 text-xs leading-relaxed text-muted">
        A draft for review. The home page and the menu visitors see are unchanged. A tool is open or in review as the site&apos;s release list says today, not as this page was written; a tool listed under two audiences is counted once.
      </p>
    </>
  );
}
