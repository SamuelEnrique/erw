import type { Metadata } from "next";
import { Inter } from "next/font/google";
import Link from "next/link";
import "./globals.css";

const body = Inter({ variable: "--font-body", subsets: ["latin"] });

export const metadata: Metadata = {
  title: { default: "Energy Research Warehouse", template: "%s | Energy Research Warehouse" },
  description:
    "The live, citable record of the US energy system: prices, flows, projects, deals and policy across power, gas, oil, nuclear, renewables, storage and transmission.",
};

const NAV = [
  { href: "/prices", label: "Prices" },
  { href: "/grid", label: "Grid" },
  { href: "/mix", label: "Mix" },
  { href: "/curtailment", label: "Curtailment" },
  { href: "/consumption", label: "Consumption" },
  { href: "/deals", label: "Deals" },
  { href: "/map", label: "Map" },
  { href: "/datacenters", label: "Datacenters" },
  { href: "/digest", label: "Digest" },
  { href: "/weekly", label: "Weekly" },
  { href: "/explorer/ercot-peak-premium", label: "Explorer" },
  { href: "/data", label: "Data" },
  { href: "/ask", label: "Ask" },
  { href: "/about", label: "About" },
];

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" className={`${body.variable} antialiased`}>
      <body className="min-h-screen bg-paper text-ink flex flex-col">
        <header className="border-b border-rule">
          <div className="mx-auto max-w-6xl px-4 py-3 flex flex-wrap items-baseline gap-x-6 gap-y-2">
            <Link href="/" className="font-serif text-xl text-ink no-underline">
              Energy Research Warehouse
            </Link>
            <nav className="flex flex-wrap gap-x-4 gap-y-1 text-sm">
              {NAV.map((n) => (
                <Link key={n.href} href={n.href} className="text-ink hover:text-accent no-underline">
                  {n.label}
                </Link>
              ))}
            </nav>
          </div>
        </header>
        <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-6">{children}</main>
        <footer className="border-t border-rule">
          <div className="mx-auto max-w-6xl px-4 py-4 text-xs text-muted">
            Every number on this site is read from the ERW tables and names the table it came from. Public tables only.{" "}
            <Link href="/data">Data and methods</Link>.
          </div>
        </footer>
      </body>
    </html>
  );
}
