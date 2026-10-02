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

export const NO_PREFETCH = ["/severance/lease", "/cost-of-power/battery"];

export function noPrefetch(path: string | null): boolean {
  return !!path && NO_PREFETCH.some((p) => path === p || path.startsWith(p + "/"));
}

export function SiteLink(props: ComponentProps<typeof Link>) {
  const path = usePathname();
  const internal = useInternal();
  const href = typeof props.href === "string" ? props.href : (props.href.pathname ?? "");
  if (!internal && gated(href)) {
    return (
      <span className={`${props.className ?? ""} gate-review`} aria-disabled="true" title={typeof props.title === "string" ? props.title : undefined}>
        {props.children}
        <span className="gate-label">in review</span>
      </span>
    );
  }
  return <Link {...props} prefetch={noPrefetch(path) ? false : props.prefetch} />;
}
