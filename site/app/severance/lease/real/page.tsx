import type { Metadata } from "next";
import { SiteLink as Link } from "@/components/SiteLink";  // session 67: every link passes the release gate
import { notFound } from "next/navigation";
import fs from "node:fs";
import zlib from "node:zlib";
import { Cite } from "@/components/Cite";
import { Section } from "@/components/Section";
import rulesJson from "@/data/severance_rules.json";
import { COLUMNS, type PriceBook } from "@/lib/lease";
import { monthMeans } from "@/lib/leaseprices";
import { leaseCsv, parseRrc, parseStatewideLease, type RrcLease } from "@/lib/rrclease";
import type { Rules } from "@/lib/severance";
import { attempt } from "@/lib/supabase";
import { LeaseTool } from "../LeaseTool";

// Session 49: "Load a real lease", behind the internal token. The Railroad Commission of Texas's monthly production by
// lease (rrc_lease_production_monthly, internal: the RRC grants no reuse in writing, so the table is in neither git, the
// public database nor the public Redivis dataset) is read on the server from the warehouse's output directory, where it
// exists only on a machine that built it. Pick an operator and a lease: the lease tool opens on its real monthly
// production, the warehouse's monthly prices and the rules' flags. The reader's own files are still read in the browser.
export const metadata: Metadata = { title: "Internal: load a real lease", robots: { index: false, follow: false } };
export const dynamic = "force-dynamic";

const rules = rulesJson as unknown as Rules;
const NAME = "rrc_lease_production_monthly";
// the path comes from the environment so the build does not trace (and bundle) the warehouse directory
const fileOf = () => `${process.env.ERW_OUTPUT_DIR || "../warehouse/output"}/${NAME}.csv`;
let cache: { mtime: number; data: ReturnType<typeof parseRrc> } | null = null;
// session 57: a lease of the statewide table, opened from the refund finder (/severance/finder): one county's partition,
// the county looked up in the partition index, never a path from the query
const STATEWIDE = "rrc_lease_production_statewide";
const dirOf = () => `${process.env.ERW_OUTPUT_DIR || "../warehouse/output"}/${STATEWIDE}`;
function statewideLease(county: string, lease: string): { lease: RrcLease | null; header: string[]; unfiled: number } | null {
  const idx = `${dirOf()}/_index.csv`;
  if (!fs.existsSync(idx) || !/^[OG]-[0-9A-Z]{2}-\d{1,6}$/.test(lease)) return null;
  const row = fs.readFileSync(idx, "utf8").split(/\r?\n/).slice(1).map((l) => l.split(",")).find((r) => r[0] === county);
  if (!row) return null;
  return parseStatewideLease(zlib.gunzipSync(fs.readFileSync(`${dirOf()}/${row[1]}`)).toString("utf8"), lease);
}

function readTable() {
  const f = fileOf();
  if (!fs.existsSync(f)) return null;
  const mtime = fs.statSync(f).mtimeMs;
  if (!cache || cache.mtime !== mtime) cache = { mtime, data: parseRrc(fs.readFileSync(f, "utf8")) };
  return cache.data;
}

export default async function RealLease({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const sp = await searchParams;
  const one = (k: string) => (typeof sp[k] === "string" ? (sp[k] as string) : "");
  const token = one("token");
  const want = process.env.INTERNAL_COSTS_TOKEN ?? "";
  if (want.length < 24 || token !== want) notFound();

  const field = "border border-rule bg-panel px-2 py-1 text-sm";
  const head = (
    <>
      <p className="mb-1 text-sm"><Link href="/severance/lease" prefetch={false}>The lease tool</Link> / load a real lease</p>
      <p className="mb-2 text-xs uppercase tracking-wide text-accent">Internal: not for circulation. The RRC data here is internal.</p>
      <h1 className="mb-1 text-3xl">Load a real lease</h1>
    </>
  );
  // session 57: a lease from the statewide table, opened by the refund finder
  if (one("src") === "statewide") {
    const got = statewideLease(one("county"), one("lease"));
    const l = got?.lease ?? null;
    const ms = l ? Object.keys(l.months).sort() : [];
    const [wti, hh] = l
      ? await Promise.all([
        attempt(() => monthMeans("eia:wti_cushing", "WTI Cushing", "per barrel", "")),
        attempt(() => monthMeans("eia:henry_hub", "Henry Hub", "per MMBtu", ", applied per Mcf as if one Mcf held one MMBtu")),
      ])
      : [null, null];
    const book: PriceBook = { oil: wti?.ok ? wti.data : {}, gas: hh?.ok ? hh.data : {} };
    return (
      <>
        {head}
        <p className="mb-3 text-sm"><Link href={`/severance/finder?token=${encodeURIComponent(token)}`} prefetch={false}>Back to the refund finder</Link></p>
        {!got ? (
          <p className="max-w-3xl text-sm">The statewide table (<code className="font-mono">{STATEWIDE}</code>) is not on this server, or the county is not in its index.</p>
        ) : !l ? (
          <p className="max-w-3xl text-sm">Lease {one("lease")} has no filed report in {one("county")} County in the table.</p>
        ) : (
          <Section title={`${l.name}, ${l.operator}`}>
            <p className="mb-2 max-w-3xl text-sm">
              RRC {l.code === "G" ? "gas" : "oil"} lease {one("lease")}, district {l.district}, field {l.field}, {l.county} County; {ms.length} months with a
              filed report, {ms[0]} to {ms.at(-1)}{got.unfiled ? `, and ${got.unfiled} without one (left out, as the session 49 table leaves them)` : ""}. The RRC lists{" "}
              {l.wells} well{l.wells === 1 ? "" : "s"} on it. The lease&apos;s production in this county: a lease reported in several counties shows this county&apos;s share.
            </p>
            {l.wells > 1 ? (
              <p className="mb-2 max-w-3xl border-l-2 border-accent pl-2 text-sm">
                <strong>This lease has {l.wells} wells; the tool reads it as one.</strong> The refund finder divides the oil test by the wells listed and not shut in, so
                the two can differ on the low-producing oil lease test.
              </p>
            ) : null}
            <LeaseTool key={l.entity} rules={rules} prices={book} initial={{ text: leaseCsv(l, COLUMNS), source: `RRC lease ${one("lease")}, ${l.name}` }} />
            <Cite tables={[STATEWIDE, "eia_fuel_spot_prices"]} note="Production: the RRC's Production Data Query dump, OG_COUNTY_LEASE_CYCLE (internal); prices: monthly means of EIA daily spot prices" />
          </Section>
        )}
      </>
    );
  }

  const t = readTable();
  if (!t) {
    return (
      <>
        {head}
        <p className="max-w-3xl text-sm">
          The internal table <code className="font-mono">{NAME}</code> is not on this server. It is built on a warehouse machine by{" "}
          <code className="font-mono">warehouse/connectors/rrc_production.py</code> and kept out of git and the public database; run the site there
          (or set <code className="font-mono">ERW_OUTPUT_DIR</code>) to use this page.
        </p>
      </>
    );
  }
  const leases = [...t.leases.values()];
  const ops = new Map<string, { name: string; n: number }>();
  for (const l of leases) ops.set(l.operatorNo, { name: l.operator, n: (ops.get(l.operatorNo)?.n ?? 0) + 1 });
  const opList = [...ops.entries()].sort((a, b) => b[1].n - a[1].n || a[1].name.localeCompare(b[1].name));
  const op = one("op") && ops.has(one("op")) ? one("op") : "";
  const mine = op ? leases.filter((l) => l.operatorNo === op).sort((a, b) => a.name.localeCompare(b.name)) : [];
  const pick = mine.find((l) => l.entity === one("lease")) ?? null;
  const months = pick ? Object.keys(pick.months).sort() : [];
  const county = leases[0]?.county ?? "";
  const pilot = t.header.find((h) => h.startsWith("Pilot county:")) ?? "";
  const lic = t.header.find((h) => h.startsWith("License:")) ?? "";
  const retrieved = t.header.find((h) => h.startsWith("Retrieved:")) ?? "";

  const [wti, hh] = pick
    ? await Promise.all([
      attempt(() => monthMeans("eia:wti_cushing", "WTI Cushing", "per barrel", "")),
      attempt(() => monthMeans("eia:henry_hub", "Henry Hub", "per MMBtu", ", applied per Mcf as if one Mcf held one MMBtu")),
    ])
    : [null, null];
  const prices: PriceBook = { oil: wti?.ok ? wti.data : {}, gas: hh?.ok ? hh.data : {} };

  return (
    <>
      {head}
      <div className="mb-5 max-w-3xl space-y-2 text-sm">
        <p>
          The Railroad Commission of Texas&apos;s monthly production for every lease in {county.charAt(0) + county.slice(1).toLowerCase()} County,{" "}
          {leases.length.toLocaleString("en-US")} leases of {ops.size.toLocaleString("en-US")} operators, as the operators reported it. {pilot}
        </p>
        <p className="text-muted">{lic} {retrieved}</p>
      </div>
      <Section title="Pick a lease">
        {/* a GET form on this internal page only: the lease tool itself still makes no request */}
        <form method="get" className="flex flex-wrap items-end gap-3 text-sm">
          <input type="hidden" name="token" value={token} />
          <label className="flex flex-col">Operator (leases)
            <select name="op" defaultValue={op} className={field}>
              <option value="">Choose an operator</option>
              {opList.map(([no, o]) => <option key={no} value={no}>{o.name} ({o.n})</option>)}
            </select>
          </label>
          {op ? (
            <label className="flex flex-col">Lease (wells the RRC lists)
              <select name="lease" defaultValue={pick?.entity ?? ""} className={field}>
                <option value="">Choose a lease</option>
                {mine.map((l) => <option key={l.entity} value={l.entity}>{l.name} ({l.entity.replace(/^rrc:/, "")}, {l.wells} well{l.wells === 1 ? "" : "s"})</option>)}
              </select>
            </label>
          ) : null}
          <button type="submit" className="border border-accent px-3 py-1 text-accent">{op ? "Load" : "Show the leases"}</button>
        </form>
      </Section>
      {pick ? (
        <Section title={`${pick.name}, ${pick.operator}`}>
          <p className="mb-2 max-w-3xl text-sm">
            RRC {pick.code === "G" ? "gas" : "oil"} lease {pick.entity.replace(/^rrc:/, "")}, district {pick.district}, field {pick.field};{" "}
            {months.length} months, {months[0]} to {months.at(-1)}. The RRC lists {pick.wells} well{pick.wells === 1 ? "" : "s"} on it.
          </p>
          {pick.wells > 1 ? (
            <p className="mb-2 max-w-3xl border-l-2 border-accent pl-2 text-sm">
              <strong>This lease has {pick.wells} wells; the tool reads it as one.</strong> The RRC reports production by lease, not by well, so a
              threshold stated per well (a low-producing well&apos;s daily volume) is tested here on the whole lease&apos;s volume. A flag that needs a
              per-well volume can be missed; read the flags as the lease&apos;s, not any one well&apos;s.
            </p>
          ) : null}
          <p className="mb-3 max-w-3xl text-xs text-muted">
            The file below is made from the table: oil, gas (a gas well&apos;s gas, or an oil lease&apos;s casinghead gas) and condensate by month, and
            the well type from the RRC&apos;s lease code. Prices are blank, so the tool uses the warehouse&apos;s monthly WTI Cushing and Henry Hub
            means. Completion date, depth, days produced and the other columns are not in the RRC&apos;s production table, so the rules that need them
            are not tested. Recent months may be incomplete: operators file late.
          </p>
          <LeaseTool key={pick.entity} rules={rules} prices={prices} initial={{ text: leaseCsv(pick, COLUMNS), source: `RRC lease ${pick.entity.replace(/^rrc:/, "")}, ${pick.name}` }} />
          <Cite tables={[NAME, "eia_fuel_spot_prices"]} note="Production: the RRC's Production Data Query dump, OG_COUNTY_LEASE_CYCLE (internal); prices: monthly means of EIA daily spot prices" />
        </Section>
      ) : null}
    </>
  );
}
