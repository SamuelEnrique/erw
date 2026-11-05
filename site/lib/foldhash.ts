// Session 419: a link to "#financing" lands on a fold (<details>) that starts closed and did not open it
// (docs/reviews/tooling-pass-2026-10-20.md). The fold an address names is the element with that id when it is a fold,
// the fold it sits in, or the fold that is its own first child (the battery page wraps its Financing fold in a div
// with the id). Pure: the client component that calls it (components/tool/OpenFoldOnHash.tsx) passes the DOM; the
// test passes plain objects.
export type FoldLike = { open: boolean };
export type ElementLike = {
  tagName: string;
  closest: (sel: string) => unknown;
  querySelector: (sel: string) => unknown;
};

/** The id an address's hash names, or null ("#financing" gives "financing"; "" and "#" give null). */
export function idOfHash(hash: string): string | null {
  const h = hash.startsWith("#") ? hash.slice(1) : hash;
  if (!h) return null;
  try {
    return decodeURIComponent(h);
  } catch {
    return h;
  }
}

/** The fold to open for the element the address names, or null when there is none. */
export function foldFor(el: ElementLike | null): FoldLike | null {
  if (!el) return null;
  if (el.tagName.toUpperCase() === "DETAILS") return el as unknown as FoldLike;
  const inside = el.closest("details") as FoldLike | null;
  if (inside) return inside;
  return (el.querySelector(":scope > details") as FoldLike | null) ?? null;
}
