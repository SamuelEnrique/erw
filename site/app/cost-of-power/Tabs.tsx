import Link from "next/link";

// Session 51: the cost of power's two tabs: what power costs to buy (/cost-of-power, the buyer's, unchanged) and
// what a generator earns selling it (/cost-of-power/seller).
export function CostTabs({ active }: { active: "buy" | "sell" }) {
  const tab = (href: string, label: string, on: boolean) => (
    <Link href={href} aria-current={on ? "page" : undefined}
      className={`border-b-2 px-3 py-1 no-underline ${on ? "border-accent text-ink" : "border-transparent text-muted hover:text-ink"}`}>{label}</Link>
  );
  return (
    <nav className="mb-4 flex gap-2 border-b border-rule text-sm" aria-label="Cost of power">
      {tab("/cost-of-power", "What power costs to buy", active === "buy")}
      {tab("/cost-of-power/seller", "What a generator earns", active === "sell")}
    </nav>
  );
}
