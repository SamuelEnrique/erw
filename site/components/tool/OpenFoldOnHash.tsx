"use client";
// Session 419: opens the fold an address names (#financing and the like), on load, when the hash changes, and when a
// link to the hash the address already has is followed again. Draws nothing; the folds keep their own default state.
import { useEffect } from "react";
import { foldFor, idOfHash, type ElementLike } from "@/lib/foldhash";

export function OpenFoldOnHash() {
  useEffect(() => {
    const openNamed = () => {
      const id = idOfHash(window.location.hash);
      if (!id) return;
      const el = document.getElementById(id);
      const fold = foldFor(el as unknown as ElementLike | null);
      if (fold && !fold.open) {
        fold.open = true;
        el?.scrollIntoView();
      }
    };
    const onClick = (e: MouseEvent) => {
      const a = (e.target as Element | null)?.closest?.("a[href^='#']");
      if (a) window.setTimeout(openNamed, 0);
    };
    openNamed();
    window.addEventListener("hashchange", openNamed);
    document.addEventListener("click", onClick);
    return () => {
      window.removeEventListener("hashchange", openNamed);
      document.removeEventListener("click", onClick);
    };
  }, []);
  return null;
}
