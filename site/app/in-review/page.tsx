import type { Metadata } from "next";
import { SiteLink as Link } from "@/components/SiteLink";
import { PAGES } from "@/lib/pages";
import { RELEASE } from "@/lib/release";

// Session 67: what a visitor sees at the address of a tool in review (the proxy rewrites the request here and passes
// the address asked for). Short, not indexed, with links to the tools that are open.
export const metadata: Metadata = { title: "In review", robots: { index: false, follow: false } };
export const dynamic = "force-dynamic";

/** The tool's name: the page of lib/pages.ts whose address is the path or its nearest parent; else the path. */
function nameOf(path: string): string {
  let p = path;
  for (;;) {
    const hit = PAGES.find((x) => x.href === p);
    if (hit) return hit.label;
    const i = p.lastIndexOf("/");
    if (i <= 0) return path;
    p = p.slice(0, i);
  }
}

export default async function InReview({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const sp = await searchParams;
  const raw = typeof sp.path === "string" ? sp.path : "";
  const path = /^\/[A-Za-z0-9_\-./%:]*$/.test(raw) ? raw : "";
  const live = PAGES.filter((p) => RELEASE[p.href] === "live");
  return (
    <div data-in-review="1" className="max-w-2xl">
      <h1 className="mb-2 font-serif text-3xl text-accent">{path ? nameOf(path) : "This tool"}</h1>
      <p className="mb-6 text-base">This tool is in review and will open when it is approved.</p>
      <h2 className="mb-2 border-b border-rule pb-1 font-serif text-xl text-accent">Open now</h2>
      <ul className="space-y-2 text-sm">
        <li><Link href="/">Home</Link></li>
        {live.map((p) => (
          <li key={p.href}><Link href={p.href}>{p.label}</Link><span className="text-muted">: {p.line}</span></li>
        ))}
      </ul>
    </div>
  );
}
