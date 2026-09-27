import type { Metadata } from "next";
import Link from "next/link";
import site from "@/data/site.json";
import { GROUPS } from "@/lib/pages";

export const metadata: Metadata = { title: "About" };

export default function About() {
  return (
    <article className="max-w-3xl">
      <h1 className="mb-4 text-3xl">About</h1>
      <p className="mb-4 leading-relaxed">
        The Energy Research Warehouse (ERW) is the live, citable record of the US energy system: prices, flows, projects, deals and policy across power,
        natural gas, oil, nuclear, renewables, storage and transmission, with the global prices and events that move US markets. AI&apos;s demand for
        power is the sharpest current lens on that system, not its boundary. It is built as a Stanford independent study. Its design follows the{" "}
        <a href="https://github.com/ben-domingue/irw">Item Response Warehouse</a> (IRW), whose owner allowed the ERW to copy its infrastructure and
        documents: one connector per source, a small number of standard table shapes so that sources can be joined and compared, a validator every table
        must pass, a provenance header on every table naming the source report and the time it was retrieved, and a versioned store of record on Redivis
        that only a human releases. Every table carries a license from its sources: a table is public only if all of its sources allow republication,
        and a table derived from other tables takes the most restrictive license among them. Tables licensed for internal use only, such as PJM market
        data, stay in the warehouse and are never shown on this site.
      </p>
      <h2 className="mb-2 mt-6 text-xl">The site</h2>
      <dl className="mb-6 text-sm">
        {GROUPS.map((g) => (
          <div key={g.label} className="mb-3">
            <dt className="text-xs uppercase tracking-wide text-muted">{g.label}</dt>
            {g.pages.map((p) => (
              <dd key={p.href} className="ml-0">
                <Link href={p.href}>{p.label}</Link>: {p.line}
              </dd>
            ))}
          </div>
        ))}
      </dl>
      <p className="text-sm text-muted">
        Code, data standard and session logs: <a href={site.repository}>{site.repository.replace("https://", "")}</a>.
      </p>
    </article>
  );
}
