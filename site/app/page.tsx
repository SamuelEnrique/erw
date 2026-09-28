import Link from "next/link";
import { GROUPS } from "@/lib/pages";
import { Cite } from "@/components/Cite";
import { NoData } from "@/components/NoData";
import { Num } from "@/components/Num";
import { Section } from "@/components/Section";
import { Sparkline } from "@/components/Sparkline";
import { MARKETS, catalogue, daysAgo, latestPrices, newest, series, type CatalogueRow } from "@/lib/data";
import { count, day, node, price, utc } from "@/lib/format";
import { DOCS, render, topItems, digestTitle } from "@/lib/markdown";
import { attempt } from "@/lib/supabase";
import markets from "@/data/markets.json";

// the latest-price board refreshes every 15 minutes; the rest of the page reads hourly data
export const revalidate = 900;

function StatusStrip({ cat }: { cat: CatalogueRow[] }) {
  const rows = cat.reduce((a, r) => a + (r.n_rows ?? 0), 0);
  const last = cat.map((r) => r.last_run).filter(Boolean).sort().at(-1) ?? null;
  const pass = cat.filter((r) => r.validator_status === "pass").length;
  const cells = [
    { k: "Public tables", v: <Num check="catalogue|count" raw={cat.length}>{count(cat.length)}</Num> },
    { k: "Rows", v: <Num check="catalogue|sum_n_rows" raw={rows}>{count(rows)}</Num> },
    { k: "Last refresh", v: <Num check="catalogue|max_last_run" raw={last ?? ""}>{utc(last)}</Num> },
    {
      k: "Validator",
      v: (
        <Num check="catalogue|n_pass" raw={pass}>
          {count(pass)} of {count(cat.length)} pass
        </Num>
      ),
    },
  ];
  return (
    <div className="grid grid-cols-2 gap-px border border-rule bg-rule sm:grid-cols-4">
      {cells.map((c) => (
        <div key={c.k} className="bg-panel px-3 py-2">
          <div className="text-xs text-muted">{c.k}</div>
          <div className="text-base tabular-nums">{c.v}</div>
        </div>
      ))}
    </div>
  );
}

async function PriceBoard() {
  const latest = await attempt(latestPrices);
  const since = daysAgo(7);
  const cards = await Promise.all(
    MARKETS.map(async (m) => {
      const src = m.rt ?? m.da;
      const spark = await attempt(() => series(src.table, { entity: m.main, variable: src.variable, since }));
      return { m, src, spark };
    }),
  );
  if (!latest.ok) return <NoData what="latest prices" reason={latest.reason} />;
  return (
    <>
      <div className="grid gap-px border border-rule bg-rule sm:grid-cols-2 lg:grid-cols-3">
        {cards.map(({ m, src, spark }) => {
          const p = latest.data.find((r) => r.entity === m.main);
          const pts = spark.ok ? spark.data.map((r) => ({ ts_utc: r.ts_utc, value: r.value })) : [];
          const spanDays = pts.length > 1 ? (new Date(pts.at(-1)!.ts_utc).getTime() - new Date(pts[0].ts_utc).getTime()) / 86_400_000 : 0;
          return (
            <div key={m.iso} className="bg-panel p-3">
              <div className="flex items-baseline justify-between gap-2">
                <span className="font-serif text-lg">{m.iso}</span>
                <Link href={`/prices/${encodeURIComponent(m.main)}`} className="font-mono text-xs">
                  {node(m.main)}
                </Link>
              </div>
              {p ? (
                <>
                  <div className="mt-1 text-2xl tabular-nums">
                    <Num check={`latest_prices|${p.entity}|${p.variable}`} raw={p.value}>{price(p.value)}</Num>{" "}
                    <span className="text-sm text-muted">{p.unit}</span>
                  </div>
                  <div className="text-xs text-muted">
                    real time, interval starting {utc(p.ts_utc)} <span className="font-mono">({p.variable})</span>
                  </div>
                </>
              ) : (
                <NoData reason={`latest_prices has no row for ${m.main}`} />
              )}
              <div className="mt-2">
                {spark.ok && pts.length > 1 ? (
                  <>
                    <Sparkline points={pts} width={220} height={40} label={`${m.iso} ${node(m.main)} ${src.variable}, last 7 days`} />
                    <div className="text-[11px] text-muted">
                      {m.rt ? "real time" : "day-ahead (no real-time series in the ERW)"}, {src.freq === "PT15M" ? "15-minute" : "hourly"},{" "}
                      {spanDays < 6.5 ? `${spanDays.toFixed(1)} days in the ERW table` : "7 days"} to {utc(pts.at(-1)!.ts_utc)}
                    </div>
                  </>
                ) : (
                  <NoData what="the 7-day sparkline" reason={spark.ok ? `${src.table} has fewer than two rows for ${m.main} since ${since}` : spark.reason} />
                )}
              </div>
            </div>
          );
        })}
      </div>
      <Cite
        tables={["latest_prices", ...cards.map((c) => c.src.table)]}
        note="Latest prices refresh every 15 minutes; sparklines come from the ERW tables, refreshed daily. Prices in USD/MWh as published by each ISO"
      />
    </>
  );
}

async function Fuels() {
  const f = markets.fuels;
  const rows = await Promise.all(f.entities.map(async (e) => ({ e, r: await attempt(() => newest(f.table, e.entity, f.variable)) })));
  return (
    <>
      <div className="grid gap-px border border-rule bg-rule sm:grid-cols-3">
        {rows.map(({ e, r }) => (
          <div key={e.entity} className="bg-panel p-3">
            <div className="text-sm">{e.label}</div>
            {r.ok && r.data ? (
              <>
                <div className="text-2xl tabular-nums">
                  <Num check={`series|${f.table}|${e.entity}|${f.variable}|newest`} raw={r.data.value}>{price(r.data.value)}</Num>{" "}
                  <span className="text-sm text-muted">{r.data.unit}</span>
                </div>
                <div className="text-xs text-muted">daily spot, {day(r.data.ts_utc)}</div>
              </>
            ) : (
              <NoData reason={r.ok ? `${f.table} has no row for ${e.entity}` : r.reason} />
            )}
          </div>
        ))}
      </div>
      <Cite tables={[f.table]} note="EIA publishes daily spot prices with a lag of several days" />
    </>
  );
}

function Digest() {
  const items = topItems(DOCS.latest, 5);
  if (!items || items.length === 0) return <NoData what="the digest" reason="docs/digest/latest.md has no 'Top of the industry' section" />;
  return (
    <>
      <p className="mb-2 text-sm text-muted">What is happening in energy today, from scored news.</p>
      <ol className="prose-erw list-decimal pl-5">
        {items.map((md, i) => (
          <li key={i} dangerouslySetInnerHTML={{ __html: render(md, "docs/digest/latest.md") }} />
        ))}
      </ol>
      <p className="text-sm">
        <Link href="/digest">The full digest ({digestTitle(DOCS.latest).replace(/^(?:ERW's )?Energy Digest,\s*/, "")}) and the archive</Link>
      </p>
    </>
  );
}

// Session 19: four entry paths, one sentence and three links each
const PATHS: { who: string; what: string; links: [string, string][] }[] = [
  {
    who: "Enthusiasts",
    what: "What happened across energy today and this week, from scored news.",
    links: [["Digest", "/digest"], ["Roundup", "/roundup"], ["Email", "/subscribe"]],
  },
  {
    who: "Investors",
    what: "Deals, datacenter projects and financings named in the news, each with its sources.",
    links: [["Deals", "/deals"], ["Datacenters", "/datacenters"], ["Capital", "/deals?type=capital"]],
  },
  {
    who: "Researchers",
    what: "Every table, how it is built, and how to read it in Python or on Redivis.",
    links: [["Coverage", "/data"], ["Methods", "/data#methods"], ["Package and Redivis", "/data#access"]],
  },
  {
    who: "Traders",
    what: "Day-ahead against real-time by hub, the latest prices, and curtailment by ISO.",
    links: [["Markets", "/markets"], ["Prices", "/prices"], ["Curtailment", "/curtailment"]],
  },
];

export default async function Home() {
  const cat = await attempt(catalogue);
  return (
    <>
      <h1 className="mb-1 text-3xl">Energy Research Warehouse</h1>
      <p className="mb-5 max-w-3xl text-sm text-muted">
        The live, citable record of the US energy system.
      </p>

      <nav className="mb-8 grid gap-px border border-rule bg-rule sm:grid-cols-2 lg:grid-cols-4" aria-label="Where to start">
        {PATHS.map((p) => (
          <div key={p.who} className="bg-panel p-3">
            <div className="font-serif text-lg">{p.who}</div>
            <p className="mb-2 text-sm text-muted">{p.what}</p>
            <div className="flex flex-wrap gap-x-3 text-sm">
              {p.links.map(([label, href]) => (
                <Link key={href + label} href={href}>
                  {label}
                </Link>
              ))}
            </div>
          </div>
        ))}
      </nav>

      <section className="mb-10" aria-label="Warehouse status">
        {cat.ok ? <StatusStrip cat={cat.data} /> : <NoData what="warehouse status" reason={cat.reason} />}
        {cat.ok ? <Cite tables={["catalogue"]} note="Rebuilt on every daily run; public tables only" /> : null}
      </section>

      <Section title="Power prices, real time" aside={<Link href="/prices">Every hub and zone</Link>}>
        <PriceBoard />
      </Section>

      <Section title="Gas and oil">
        <Fuels />
      </Section>

      <Section
        title="ERW's Energy Digest"
        aside={
          <>
            <Link href="/digest">Archive</Link> <span className="text-muted">|</span> <Link href="/roundup">ERW's Roundup</Link>
          </>
        }
      >
        <Digest />
      </Section>

      <Section title="Explore">
        {GROUPS.filter((g) => g.label !== "About").map((g) => (
          <div key={g.label} className="mb-4">
            <h3 className="mb-1 text-xs uppercase tracking-wide text-muted">{g.label}</h3>
            <div className="grid gap-px border border-rule bg-rule sm:grid-cols-2 lg:grid-cols-4">
              {g.pages.map((p) => (
                <Link key={p.href} href={p.href} className="bg-panel p-3 no-underline">
                  <div className="font-serif text-lg">{p.label}</div>
                  <div className="text-sm text-muted">{p.line}</div>
                </Link>
              ))}
            </div>
          </div>
        ))}
      </Section>
    </>
  );
}
