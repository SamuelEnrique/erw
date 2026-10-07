import { SiteLink as Link } from "@/components/SiteLink";  // session 67: every link passes the release gate

// Session 51: the cost of power's two tabs: what power costs to buy (/cost-of-power, the buyer's, unchanged) and
// what a generator earns selling it (/cost-of-power/seller). Session 67: a third, what a battery earns from energy and
// ancillary services together (/cost-of-power/battery).
// Session 138: the first tab is "What a datacenter pays". The battery page is open to visitors and under the review
// freeze through 7 October 2026 (REVIEW_FREEZE), so on that one page the tab keeps the words a visitor saw before,
// FROZEN_LABEL; after the freeze a person deletes FROZEN_LABEL's use below and the three tabs read alike everywhere.
const LABEL = "What a datacenter pays", FROZEN_LABEL = "What power costs to buy";
export function CostTabs({ active }: { active: "buy" | "sell" | "battery" }) {
  const tab = (href: string, label: string, on: boolean) => (
    <Link href={href} aria-current={on ? "page" : undefined}
      className={`border-b-2 px-3 py-1 no-underline ${on ? "border-accent text-ink" : "border-transparent text-muted hover:text-ink"}`}>{label}</Link>
  );
  return (
    <nav className="mb-4 flex gap-2 border-b border-rule text-sm" aria-label="Cost of power">
      {tab("/cost-of-power", active === "battery" ? FROZEN_LABEL : LABEL, active === "buy")}
      {tab("/cost-of-power/seller", "What a generator earns", active === "sell")}
      {tab("/cost-of-power/battery", "What a battery earns", active === "battery")}
    </nav>
  );
}
