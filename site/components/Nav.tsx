"use client";
// The top nav (session 20): six groups from lib/pages.ts, each a <details> menu, so it works
// without JavaScript and fits a phone's width in one or two lines. A group of one page is a
// plain link. A menu closes when a page is chosen or another menu opens. Session 67: a page in review (lib/release.ts)
// is listed greyed with an "in review" label and is not a link (components/SiteLink.tsx); a menu whose pages are all
// in review still opens.
// Session 203 (the roadmap's ruling of 12 October 2026): the menus are Economics, Grid, Infrastructure, Analysis, Games
// and About. A menu may end with a sub-group: a short list under its own name (Economics: "Infrastructure Economics"),
// or a line of short links (Grid: "Your grid"). The group marked aside (Energy Digest, Roundup, Email) is not a menu:
// its three links stand at the right of the header, in grey. A page's name here is its short menu name where it has
// one (lib/pages.ts, menu). On a phone the header wraps: the menus on their lines, the three grey links on their own.
// Session 412 (the accessibility pass): the page in view is marked aria-current="page" in the menus too, where only its
// color said so (WCAG 1.3.1); the grey links at the right carried it already.
import { SiteLink as Link } from "@/components/SiteLink";  // session 46: no prefetch on /severance/lease
import { usePathname } from "next/navigation";
import { useEffect, useRef } from "react";
import { useInternal } from "@/components/Internal";
import { GROUPS, type Page } from "@/lib/pages";

const name = (p: Page) => p.menu ?? p.label;
const MENUS = GROUPS.filter((g) => !g.aside);
const ASIDE = GROUPS.filter((g) => g.aside).flatMap((g) => g.pages);

export function Nav() {
  const path = usePathname();
  const internal = useInternal();  // session 67: the release gate's internal view (lib/release.ts)
  const box = useRef<HTMLElement>(null);
  useEffect(() => {
    box.current?.querySelectorAll("details[open]").forEach((d) => d.removeAttribute("open"));
  }, [path]);
  const closeOthers = (e: React.SyntheticEvent<HTMLDetailsElement>) => {
    if (!e.currentTarget.open) return;
    box.current?.querySelectorAll("details[open]").forEach((d) => {
      if (d !== e.currentTarget) d.removeAttribute("open");
    });
  };
  return (
    <nav ref={box} className="relative flex min-w-0 flex-1 flex-wrap gap-x-5 gap-y-1 text-sm" aria-label="Site">
      {MENUS.map((g, gi) => {
        const here = [...g.pages, ...(g.sub?.pages ?? [])].some((p) => path === p.href || path.startsWith(p.href + "/"));
        if (g.pages.length === 1) {
          const p = g.pages[0];
          return (
            <Link key={g.label} href={p.href} aria-current={path === p.href ? "page" : undefined} className={`no-underline ${here ? "text-accent" : "text-ink hover:text-accent"}`}>
              {g.label}
            </Link>
          );
        }
        return (
          <details key={g.label} className="sm:relative" onToggle={closeOthers} data-menu={g.label}>
            <summary className={`cursor-pointer list-none select-none ${here ? "text-accent" : "text-ink hover:text-accent"}`}>
              {g.label} <span aria-hidden="true" className="text-xs text-muted">▾</span>
            </summary>
            {/* the later groups open leftward. Session 203: on a phone the header wraps, so a menu's place on its line
                says nothing of the room beside it (at 390 px Grid ran 33 px past the right edge and Games 8 px past the
                left): there a menu spans the menus' own width, under its line; from 640 px it hangs from its name */}
            <ul className={`absolute left-0 right-0 ${gi >= 3 ? "sm:left-auto sm:right-0" : "sm:right-auto"} z-20 mt-1 min-w-48 border border-rule bg-panel py-1 shadow-sm`}>
              {g.pages.map((p) => (
                <li key={p.href}>
                  <Link href={p.href} aria-current={path === p.href ? "page" : undefined} className={`block px-3 py-1 no-underline ${path === p.href ? "text-accent" : "text-ink hover:text-accent"}`}>
                    {name(p)}
                  </Link>
                </li>
              ))}
              {g.sub?.inline ? (
                <li className="mt-1 border-t border-rule px-3 pt-1" data-menu-sub={g.sub.label}>
                  <div className="text-xs text-muted">{g.sub.label}</div>
                  <div className="flex flex-wrap gap-x-2 text-sm">
                    {g.sub.pages.map((l) => (
                      <Link key={l.href} href={l.href} aria-current={path === l.href ? "page" : undefined} className={`no-underline ${path === l.href ? "text-accent" : "text-ink hover:text-accent"}`}>
                        {name(l)}
                      </Link>
                    ))}
                  </div>
                </li>
              ) : g.sub ? (
                <li className="mt-1 border-t border-rule pt-1" data-menu-sub={g.sub.label}>
                  <div className="px-3 text-xs text-muted">{g.sub.label}</div>
                  <ul>
                    {g.sub.pages.map((p) => (
                      <li key={p.href}>
                        <Link href={p.href} aria-current={path === p.href ? "page" : undefined} className={`block py-1 pl-5 pr-3 no-underline ${path === p.href ? "text-accent" : "text-ink hover:text-accent"}`}>
                          {name(p)}
                        </Link>
                      </li>
                    ))}
                  </ul>
                </li>
              ) : null}
            </ul>
          </details>
        );
      })}
      {ASIDE.length ? (
        <span className="nav-aside ml-auto flex flex-wrap gap-x-4" data-nav-aside="1">
          {/* session 423: 24 px tall (WCAG 2.2, 2.5.8): at 390 px the aside wraps to a row of its own between the menus and
              the internal line, and its 20 px links' circles met theirs (scripts/check-targets.mjs) */}
          {ASIDE.map((p) => (
            <Link key={p.href} href={p.href} className="inline-flex min-h-6 items-center no-underline hover:underline" aria-current={path === p.href ? "page" : undefined}>
              {name(p)}
            </Link>
          ))}
        </span>
      ) : null}
      {internal ? (
        <span className="text-xs text-muted" title="The release gate is open in this browser: every page is reachable (docs/release-gate.md)">
          {/* session 423: underlined, the one thing that tells it from its line (axe link-in-text-block; the internal view only) */}
          internal view <a href="/internal/lock" className="text-muted underline">lock</a>
        </span>
      ) : null}
    </nav>
  );
}
