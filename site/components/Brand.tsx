// Session 235 (the owner's ruling of 12 October 2026: the brand is approved, the battery page is the reference).
// The one way a page takes the brand (docs/brand.md): it wraps what it draws in <Brand>. Every rule of the brand,
// its colors, type, spacing, tables and chart styling, is in app/tokens.css, scoped to the class this wrapper carries;
// a page writes no color, font or spacing of its own. A change of brand is that one file (and, if the families change,
// the three loaded here). Until session 235 the battery page loaded the families and carried the wrapper itself, with
// the rules in app/cost-of-power/battery/brand.css (sessions 203 to 211).
import type { ReactNode } from "react";
import { IBM_Plex_Mono, IBM_Plex_Sans, Source_Serif_4 } from "next/font/google";

const brandSerif = Source_Serif_4({ variable: "--font-brand-serif", subsets: ["latin"], weight: ["600"] });
const brandSans = IBM_Plex_Sans({ variable: "--font-brand-sans", subsets: ["latin"], weight: ["400", "500", "600"] });
const brandMono = IBM_Plex_Mono({ variable: "--font-brand-mono", subsets: ["latin"], weight: ["400", "500"] });

/**
 * The brand's wrapper. `noUsage`: the page's typed inputs are never sent, so no usage count is taken on it
 * (components/Usage.tsx reads data-no-usage; the owner's ruling of 11 October 2026 for the tool pages).
 */
export function Brand({ children, noUsage }: { children: ReactNode; noUsage?: boolean }) {
  return (
    <div className={`brand-a ${brandSerif.variable} ${brandSans.variable} ${brandMono.variable}`} data-brand="a" data-no-usage={noUsage ? "1" : undefined}>
      {/* the header and the footer are outside this wrapper: they take the text face by its name */}
      <style>{`body:has(.brand-a) > header, body:has(.brand-a) > footer { font-family: ${brandSans.style.fontFamily}, system-ui, sans-serif; }`}</style>
      {children}
    </div>
  );
}
