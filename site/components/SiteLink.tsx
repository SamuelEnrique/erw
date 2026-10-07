"use client";
// Session 46: next/link with prefetch off on the pages listed in NO_PREFETCH. /severance/lease reads a reader's lease
// file in the browser and promises that nothing is sent; Next.js prefetches a link's route when the link enters the
// viewport (production only), which showed as requests in the network panel after a file was loaded. On those pages the
// shared links (the header, the nav, the footer, the citations) do not prefetch; elsewhere they behave as next/link.
// Session 67: /cost-of-power/battery makes the same promise for its contract inputs. And the release gate
// (lib/release.ts): a link to a page in review is drawn greyed, with a small "in review" label, as text: it cannot be
// clicked or reached by keyboard. In the internal view every link is a link, as before. Every link of the site comes
// through here.
import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ComponentProps } from "react";
import { useInternal } from "@/components/Internal";
import { gated } from "@/lib/release";

// Session 88: /battery/customer promises that nothing typed is sent. The browser proof (scripts/check-no-request.mjs)
// caught the footer's links prefetching when the result made the page taller; on that page too the shared links do not.
// Session 138: /cost-of-power makes the same promise for its contract inputs (the rule below is by prefix, so the
// two tabs beside it are covered too).
export const NO_PREFETCH = ["/severance/lease", "/cost-of-power/battery", "/battery/customer", "/cost-of-power"];

export function noPrefetch(path: string | null): boolean {
  return !!path && NO_PREFETCH.some((p) => path === p || path.startsWith(p + "/"));
}

/** Session 71: how a link to a page in review is drawn for a visitor. "label" (the default, as in the menu): greyed with
 * the "in review" label. "quiet": greyed, no label (the home page's "In review" list). "plain": plain text, no label,
 * not greyed (a table name in a citation line, a node name on a price card). Never a link, in any of the three. */
export type GateLook = "label" | "quiet" | "plain";

export function SiteLink({ gate = "label", ...props }: ComponentProps<typeof Link> & { gate?: GateLook }) {
  const path = usePathname();
  const internal = useInternal();
  const href = typeof props.href === "string" ? props.href : (props.href.pathname ?? "");
  if (!internal && gated(href)) {
    return (
      <span className={`${props.className ?? ""} ${gate === "plain" ? "gate-plain" : "gate-review"}`} aria-disabled="true" title={typeof props.title === "string" ? props.title : undefined}>
        {props.children}
        {gate === "label" ? <span className="gate-label">in review</span> : null}
      </span>
    );
  }
  return <Link {...props} prefetch={noPrefetch(path) ? false : props.prefetch} />;
}
