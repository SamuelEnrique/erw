import { SiteLink as Link } from "@/components/SiteLink";
import { caisoJoinDay } from "@/lib/caisoJoin";
import faultsJson from "@/data/data_faults.json";

// Session 118: where an older page drew California's generation by fuel from EIA-930, it now says why it does not.
// From the join date (lib/caisoJoin.ts) EIA's California generation is the series the faults register calls changed
// (fault eia930_ciso_generation_break), and a page in review must not show a figure the register calls wrong. The
// figures in the sentence are the register's own evidence, read from the site's copy of it: none is written here.
// California's mix on CAISO's own supply is on /mix/v2.

type Fault = { id: string; evidence: string };
const FAULT = (faultsJson as unknown as { rows: Fault[] }).rows.find((f) => f.id === "eia930_ciso_generation_break");

export function CaisoMixWithheld({ what = "California's generation by fuel", className = "mb-4" }: { what?: string; className?: string }) {
  return (
    <div className={`${className} max-w-3xl border-l-2 border-accent bg-paper px-3 py-2 text-sm`} data-caiso-mix-withheld="1">
      <p>
        <strong>Not shown: {what}.</strong> Since {caisoJoinDay()} the generation EIA-930 reports for California is not the
        series it was, and this page reads only EIA-930.
      </p>
      {FAULT ? <p className="mt-1 text-xs text-muted">{FAULT.evidence}</p> : null}
      <p className="mt-1 text-xs">
        California&apos;s mix from CAISO&apos;s own supply by fuel: <Link href="/mix/v2">the energy mix, version 2</Link>.{" "}
        <Link href="/data/faults#eia930_ciso_generation_break">The fault</Link>; <Link href="/data/methods/eia930_caiso_break">the method note</Link>.
      </p>
    </div>
  );
}
