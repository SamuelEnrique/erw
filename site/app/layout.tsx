import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { SiteLink as Link } from "@/components/SiteLink";  // session 46: no prefetch on /severance/lease
import { Wordmark } from "@/components/Wordmark";
import { Nav } from "@/components/Nav";
import { GateRestore } from "@/components/GateRestore";
import "./globals.css";

const body = Inter({ variable: "--font-body", subsets: ["latin"] });

export const metadata: Metadata = {
  title: { default: "ERW", template: "%s | ERW" }, // session 21: the full name only on the home page and /about
  description:
    "The live, citable record of the US energy system: prices, flows, projects, deals and policy across power, gas, oil, nuclear, renewables, storage and transmission.",
};


export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" className={`${body.variable} antialiased`}>
      <body className="min-h-screen bg-paper text-ink flex flex-col">
        <header className="border-b border-rule">
          <div className="mx-auto max-w-6xl px-4 py-3 flex flex-wrap items-baseline gap-x-6 gap-y-2">
            <Link href="/" className="self-center no-underline" aria-label="ERW, home">
              <Wordmark />
            </Link>
            <Nav />
          </div>
        </header>
        <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-6">{children}</main>
        <GateRestore />
        <footer className="border-t border-rule">
          <div className="mx-auto max-w-6xl px-4 py-4 text-xs text-muted">
            Every number on this site is read from the ERW tables and names the table it came from. Public tables only.{" "}
            <Link href="/data">Data and methods</Link>. <Link href="/terms">Terms</Link>.
          </div>
        </footer>
      </body>
    </html>
  );
}
