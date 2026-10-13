import { TABBED, tabHref, type Tabbed, type TabbedPage } from "@/lib/tabs";

// Session 239: the one tabs component of the merged pages (lib/tabs.ts: /storage, /severance, /prices, /demand, /deals
// and /map). A row of links over a rule, the tab in view marked with aria-current, as the cost-of-power tabs are drawn
// (app/cost-of-power/Tabs.tsx); the brand styles both by one rule (app/tokens.css, "the tabs"). The links are plain
// anchors: a tab is the same page at another address, so it has the page's own release status, and a plain anchor is
// never prefetched (the lease tab of /severance promises that nothing is sent after a file is loaded).
export function Tabs({ page, active }: { page: TabbedPage; active: string }) {
  const t: Tabbed = TABBED[page];
  return (
    <nav className="mb-4 flex flex-wrap gap-x-2 gap-y-1 border-b border-rule text-sm" aria-label={`${t.name}: tabs`} data-tabs={page} data-views="1">
      {t.tabs.map(([k, label]) => (
        <a key={k} href={tabHref(page, k)} aria-current={k === active ? "page" : undefined} data-tab={k} data-view={k}
          className={`border-b-2 px-3 py-1 no-underline ${k === active ? "border-accent text-ink" : "border-transparent text-muted hover:text-ink"}`}>{label}</a>
      ))}
    </nav>
  );
}
