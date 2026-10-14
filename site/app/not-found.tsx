import type { Metadata } from "next";
import { Brand } from "@/components/Brand";
import { SiteLink as Link } from "@/components/SiteLink";
import { ToolSection } from "@/components/tool/ToolPage";

// Session 268: the site's own page for an address it does not hold, in the brand's frame (the in-review page is the
// model), in place of Next's default. A visitor reaches it only at an address the proxy does not send to the
// in-review page (a file, a route handler); in the internal view, at any address the site does not hold.
export const metadata: Metadata = { title: "Not found", robots: { index: false, follow: false } };

export default function NotFound() {
  return (
    <Brand>
    <div data-not-found="1" className="max-w-2xl">
      <h1 className="mb-2 font-serif text-3xl text-accent">No page at this address</h1>
      <p className="mb-6 text-base">The address may be mistyped, or the page may have moved.</p>
      <ToolSection title="From here">
      <ul className="space-y-2 text-sm">
        <li><Link href="/">Home</Link></li>
        <li><Link href="/data" gate="quiet">Data and methods</Link></li>
      </ul>
      </ToolSection>
    </div>
    </Brand>
  );
}
