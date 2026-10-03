"use client";
// Session 67: in the internal view of the release gate, the links that rendered markdown drew as greyed text
// (lib/markdown.ts, gateLinks) are links again. A visitor's page is untouched.
import { usePathname } from "next/navigation";
import { useEffect } from "react";
import { useInternal } from "@/components/Internal";

export function GateRestore() {
  const internal = useInternal();
  const path = usePathname();
  useEffect(() => {
    if (!internal) return;
    document.querySelectorAll<HTMLElement>("span[data-gate-href]").forEach((s) => {
      const a = document.createElement("a");
      a.href = s.dataset.gateHref!;
      s.querySelector(".gate-label")?.remove();
      a.innerHTML = s.innerHTML;
      s.replaceWith(a);
    });
  }, [internal, path]);
  return null;
}
