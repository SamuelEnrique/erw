// Session 237: two shared pieces for a page that is one tool with several views (the Grid tool, /grid): the tabs of
// its views and a picker of the thing in view. Both are plain links, so the state is the address and a view can be
// shared. Their look is the brand's (app/tokens.css: nav[data-tabs], nav[data-segments]); a page writes none of it.
import { SiteLink as Link } from "@/components/SiteLink";
import { CarryLink } from "@/components/tool/CarryLink";
import type { Carry } from "@/lib/carry";

export type ChooseItem = { key: string; label: string; href: string; on: boolean; title?: string };

/** The views of a page, as tabs: the one in view is ink over a cardinal rule, the others captions grey. */
export function ToolTabs({ label, items }: { label: string; items: ChooseItem[] }) {
  return (
    <nav className="mb-6 flex flex-wrap gap-x-2 border-b border-rule text-sm" aria-label={label} data-tabs={label}>
      {items.map((i) => (
        <Link key={i.key} href={i.href} aria-current={i.on ? "page" : undefined} title={i.title} data-tab={i.key}
          className={`border-b-2 px-3 py-2 no-underline ${i.on ? "border-accent text-ink" : "border-transparent text-muted hover:text-ink"}`}>{i.label}</Link>
      ))}
    </nav>
  );
}

/** A picker: one row of segments under a caption, the one in view filled. Session 1153: with `carry`, each link carries
 * those words of the address it is drawn in (lib/carry.ts: the Grid tool's Gravity tab keeps the replay's day). */
export function ToolPicker({ label, items, carry }: { label: string; items: ChooseItem[]; carry?: Carry }) {
  return (
    <nav className="mb-4 flex flex-wrap items-center gap-1 text-sm" aria-label={label} data-segments={label}>
      <span className="mr-2 text-xs text-muted">{label}</span>
      {items.map((i) => {
        const look = `border px-3 py-1.5 no-underline ${i.on ? "border-ink bg-ink text-white" : "border-rule text-ink hover:bg-paper"}`;
        return carry
          ? <CarryLink key={i.key} carry={carry} href={i.href} aria-current={i.on ? "page" : undefined} title={i.title} data-segment={i.key} className={look}>{i.label}</CarryLink>
          : <Link key={i.key} href={i.href} aria-current={i.on ? "page" : undefined} title={i.title} data-segment={i.key} className={look}>{i.label}</Link>;
      })}
    </nav>
  );
}
