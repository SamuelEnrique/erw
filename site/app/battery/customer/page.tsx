import type { Metadata } from "next";
import { SiteLink } from "@/components/SiteLink";
import { Fold, ToolHeader, ToolPage } from "@/components/tool/ToolPage";
import { Calc } from "./Calc";

// Session 88: "What a battery saves a customer". A customer with a demand charge types their peak, their rates and a
// battery's size; the page works out the bill saved by shaving the peak and shifting energy. It reads no ERW table:
// every number on it is the reader's own, and the arithmetic (lib/customerbattery.ts) runs in the reader's browser.
// Nothing typed is sent, stored or put in the address (scripts/check-no-request.mjs proves it with a real browser).
// In review (lib/release.ts). The page itself is static: the server renders the same words for everyone.
export const metadata: Metadata = { title: "What a battery saves a customer", robots: { index: false, follow: false } };
export const dynamic = "force-static";

export default function CustomerBattery() {
  return (
    <ToolPage>
      <ToolHeader title="What a battery saves a customer"
        lead={<>A business that pays a demand charge can lower its bill with a battery in two ways: by discharging through its peak, so the highest demand on the meter is
          lower, and by charging when energy is cheap and discharging when it is dear. Type your own bill and a battery&apos;s size to see what each is worth. What a
          battery earns selling to the grid is another question: <SiteLink href="/cost-of-power/battery">What a battery earns</SiteLink>.</>} />
      <div className="mb-8 border-l-2 border-accent bg-paper px-4 py-3 text-sm" data-own-numbers="1">
        <p className="mb-1"><strong>This page uses your own numbers, not ERW data.</strong> The warehouse holds no customer&apos;s bill and no retail tariff for this page;
          every figure below is arithmetic on what you type.</p>
        <p><strong>Nothing you type is sent or stored.</strong> The arithmetic runs in your browser. Close or reload the page and the numbers are gone.</p>
      </div>
      <Calc />
      <div className="mb-8 border-t border-rule">
        <Fold title="What this assumes">
          <ul className="max-w-3xl list-disc space-y-1.5 pl-5">
            <li><strong>Your peak falls in the peak-rate hours,</strong> so one discharge a day both lowers the peak and avoids peak-rate energy.</li>
            <li><strong>The battery knows when the peak comes</strong> and is full when it does. A battery that misses the peak once in a month saves no demand charge that month.</li>
            <li><strong>One full cycle on each day it runs.</strong> It charges only in off-peak hours, and charging does not set a new peak.</li>
            <li><strong>One demand charge on one monthly peak.</strong> Many tariffs have several (a peak-period charge and an all-hours charge), a ratchet that remembers last summer, or seasons. Use the charge that applies to the hours of your peak.</li>
            <li><strong>Every month alike.</strong> The year is twelve of the month you typed.</li>
          </ul>
        </Fold>
        <Fold title="What it leaves out">
          <ul className="max-w-3xl list-disc space-y-1.5 pl-5">
            <li><strong>What the battery costs:</strong> its price, its installation, its upkeep and its wearing out. This is the saving on the bill, not a return.</li>
            <li><strong>Taxes, riders and fixed charges</strong> on the bill, and any payment from a utility program.</li>
            <li><strong>Solar on the same meter,</strong> which changes both the peak and the hours worth charging in.</li>
            <li><strong>The shape of your load.</strong> A peak that is one sharp hour needs less battery than this asks for; one that lasts all afternoon needs more. The field for how long the peak lasts is where that enters.</li>
          </ul>
        </Fold>
      </div>
      <p className="mt-8 border-t border-rule pt-3 text-xs leading-relaxed text-muted">
        Source: none. No ERW table is read on this page and no number on it comes from the warehouse. The starting values of the last three fields (2 hours, 21 days, 86
        percent) are starting values, not data; change them to yours.
      </p>
    </ToolPage>
  );
}
