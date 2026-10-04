"use client";
// Energy Research Warehouse (ERW) site, session 92: the link an ERCOT view carries to Ask ERCOT, with the view's
// period and settings as context (lib/askContext.ts). While /ask/ercot is in review the link is drawn only in the
// internal view: a visitor's page is exactly as it was, without even the greyed "in review" text a gated link leaves
// (a live page must not change while the site is frozen). When the page is opened in lib/release.ts, every visitor
// sees the link.
import Link from "next/link";
import { useInternal } from "@/components/Internal";
import { askHref, type AskContext } from "@/lib/askContext";
import { statusOf } from "@/lib/release";

export function AskErcotLink({ context, className }: { context: AskContext; className?: string }) {
  const internal = useInternal();
  if (!internal && statusOf("/ask/ercot") !== "live") return null;
  return (
    <p className={className ?? "mb-4 text-sm"} data-ask-ercot={context.view}>
      <Link href={askHref(context)} prefetch={false} className="border border-accent px-3 py-1 text-accent no-underline">Ask ERCOT about this view</Link>
    </p>
  );
}
