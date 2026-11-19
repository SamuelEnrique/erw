// Energy Research Warehouse (ERW) site, session 8410 (chain 503): what the session added to /events and its nine event
// pages stands between marks, so a test can cut it out and hold the rest of each page to what it was
// (scripts/test-events-pin.mjs). The section "The whole country" opens with <section data-whole-country="..."> and is
// followed by <span data-whole-country-end="1"></span>; the index's line of regions opens with
// <span data-regions-reached="..."> and is followed by <span data-regions-reached-end="1"></span>.

/** The page without what session 8410 added. */
export function withoutAdded(html) {
  return html
    .replace(/<section data-whole-country="[^"]*"[\s\S]*?<span data-whole-country-end="1"><\/span>/g, "")
    .replace(/<span data-regions-reached="[^"]*"[\s\S]*?<span data-regions-reached-end="1"><\/span>/g, "");
}
