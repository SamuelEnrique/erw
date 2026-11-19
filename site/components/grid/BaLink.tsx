"use client";
// Energy Research Warehouse (ERW) site, session 8612 (chain 504): a link of a region's list of balancing authorities
// (the Network tab of /grid?region=...) that keeps the shape the reader is looking at. The list is drawn on the
// server, which does not know that the reader has switched the network to its Map or Gravity shape (the network
// writes `shape=` into the address as it is toggled). Followed in the Map shape, the plain link opened the authority's
// panel in the 3D network and the map was gone (the second read of the map, row 36). This link reads the address at
// the click and keeps the shape. A click that opens a new tab or window is left to the browser, with the plain link.
import { useRouter } from "next/navigation";
import type { ComponentProps, MouseEvent } from "react";
import { SiteLink } from "@/components/SiteLink";
import { keepShape } from "@/lib/gridregions";

export function BaLink({ href, ...rest }: Omit<ComponentProps<typeof SiteLink>, "href" | "onClick"> & { href: string }) {
  const router = useRouter();
  const follow = (e: MouseEvent<HTMLAnchorElement>) => {
    if (e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    const to = keepShape(href, window.location.search);
    if (to === href) return;
    e.preventDefault();
    router.push(to);
  };
  return <SiteLink href={href} {...rest} onClick={follow} />;
}
