"use client";
// Session 1153 (chain 077): a picker's link that carries words of the address it is drawn in (lib/carry.ts), read
// with useSearchParams, which follows the address as the network component writes it (window.history.replaceState).
// So on the Grid tool's Gravity tab a day picked in the replay stays in the address when the reader picks another grid.
// It is a SiteLink, so the release gate holds.
import type { ComponentProps } from "react";
import { useSearchParams } from "next/navigation";
import { SiteLink } from "@/components/SiteLink";
import { carryWords, type Carry } from "@/lib/carry";

export function CarryLink({ carry, href, ...rest }: Omit<ComponentProps<typeof SiteLink>, "href"> & { href: string; carry: Carry }) {
  const search = useSearchParams()?.toString() ?? "";
  return <SiteLink href={carryWords(href, search, carry)} {...rest} />;
}
