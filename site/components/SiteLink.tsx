"use client";
// Session 46: next/link with prefetch off on the pages listed in NO_PREFETCH. /severance/lease reads a reader's lease
// file in the browser and promises that nothing is sent; Next.js prefetches a link's route when the link enters the
// viewport (production only), which showed as requests in the network panel after a file was loaded. On those pages the
// shared links (the header, the nav, the footer, the citations) do not prefetch; elsewhere they behave as next/link.
import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ComponentProps } from "react";

export const NO_PREFETCH = ["/severance/lease"];

export function noPrefetch(path: string | null): boolean {
  return !!path && NO_PREFETCH.some((p) => path === p || path.startsWith(p + "/"));
}

export function SiteLink(props: ComponentProps<typeof Link>) {
  const path = usePathname();
  return <Link {...props} prefetch={noPrefetch(path) ? false : props.prefetch} />;
}
