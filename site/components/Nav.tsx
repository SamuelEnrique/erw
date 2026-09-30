"use client";
// The top nav (session 20): six groups from lib/pages.ts, each a <details> menu, so it works
// without JavaScript and fits a phone's width in one or two lines. A group of one page is a
// plain link. A menu closes when a page is chosen or another menu opens.
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useRef } from "react";
import { GROUPS } from "@/lib/pages";

export function Nav() {
  const path = usePathname();
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
    <nav ref={box} className="flex flex-wrap gap-x-5 gap-y-1 text-sm" aria-label="Site">
      {GROUPS.map((g, gi) => {
        const here = g.pages.some((p) => path === p.href || path.startsWith(p.href + "/")) || !!g.sub?.links.some((l) => path === l.href);
        if (g.pages.length === 1) {
          const p = g.pages[0];
          return (
            <Link key={g.label} href={p.href} className={`no-underline ${here ? "text-accent" : "text-ink hover:text-accent"}`}>
              {g.label}
            </Link>
          );
        }
        return (
          <details key={g.label} className="relative" onToggle={closeOthers}>
            <summary className={`cursor-pointer list-none select-none ${here ? "text-accent" : "text-ink hover:text-accent"}`}>
              {g.label} <span aria-hidden="true" className="text-xs text-muted">▾</span>
            </summary>
            {/* the later groups open leftward, so a menu stays inside a phone's width */}
            <ul className={`absolute ${gi >= 3 ? "right-0" : "left-0"} z-20 mt-1 min-w-48 border border-rule bg-panel py-1 shadow-sm`}>
              {g.pages.map((p) => (
                <li key={p.href}>
                  <Link href={p.href} className={`block px-3 py-1 no-underline ${path === p.href ? "text-accent" : "text-ink hover:text-accent"}`}>
                    {p.label}
                  </Link>
                </li>
              ))}
              {g.sub ? (
                <li className="mt-1 border-t border-rule px-3 pt-1">
                  <div className="text-xs text-muted">{g.sub.label}</div>
                  <div className="flex flex-wrap gap-x-2 text-sm">
                    {g.sub.links.map((l) => (
                      <Link key={l.href} href={l.href} className={`no-underline ${path === l.href ? "text-accent" : "text-ink hover:text-accent"}`}>
                        {l.label}
                      </Link>
                    ))}
                  </div>
                </li>
              ) : null}
            </ul>
          </details>
        );
      })}
    </nav>
  );
}
