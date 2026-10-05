import type { Metadata } from "next";
import { SiteLink as Link } from "@/components/SiteLink";
import { Cite } from "@/components/Cite";
import { Section } from "@/components/Section";
import faultsJson from "@/data/data_faults.json";

// Session 103: known faults in source data. The page reads the site's own copy of the table known_data_faults
// (warehouse/derived/data_faults.py --snapshot), written from the register warehouse/faults/faults.yaml. Every
// figure on it is one a session measured and recorded; the page computes nothing but the counts of its own rows.

export const metadata: Metadata = { title: "Known data faults" };

type Fault = {
  id: string; title: string; publisher: string; source: string; first: string; last: string; dates_note: string;
  status: string; tables: string[]; evidence: string; erw_does: string; open: string; recorded_in: string;
  resolution: string; resolution_reason: string;
};
type File = {
  table: string; built: string; faults: number; by_status: Record<string, number>; status_words: Record<string, string>;
  tables_touched: number; with_open: number; rows: Fault[];
  by_resolution: Record<string, number>; resolution_words: Record<string, string>;
};
const file = faultsJson as unknown as File;

const STATUS_LABEL: Record<string, string> = {
  screened: "Screened", corrected: "Corrected", worked_around: "Worked around", held_as_published: "Held as published",
};
const ORDER = ["worked_around", "corrected", "screened", "held_as_published"];
// session 118: where the ERW's own work on each fault stands
const RESOLUTION_LABEL: Record<string, string> = { fixed: "Fixed", held_for_approval: "Held for approval", open: "Open" };
const RESOLUTION_ORDER = ["held_for_approval", "open", "fixed"];

/** The dates of a fault in words: a range, one day, "from" a day when it continues, or what the note says. */
function dates(f: Fault): string {
  if (f.first && f.last) return f.first === f.last ? f.first : `${f.first} to ${f.last}`;
  if (f.first) return `from ${f.first}, continuing`;
  if (f.last) return `to ${f.last}`;
  return "no day recorded";
}

export default function Faults() {
  const rows = [...file.rows].sort((a, b) => ORDER.indexOf(a.status) - ORDER.indexOf(b.status) || (b.first || "").localeCompare(a.first || "") || a.id.localeCompare(b.id));
  return (
    <>
      <h1 className="mb-1 text-3xl">Known data faults</h1>
      <p className="mb-3 max-w-3xl text-sm text-muted">
        What the ERW&apos;s sources publish is not always right. This page lists every fault an ERW session has found in a
        publisher&apos;s data: values that are wrong, missing, shifted in time or impossible. Each has its evidence, its dates, the
        tables it touches and what the ERW does about it. Nothing here is estimated: every figure is one that was measured and
        written down, and each entry says where.
      </p>
      <p className="mb-6 max-w-3xl text-sm" data-faults-summary="1">
        <strong>{file.faults} faults</strong> are recorded, touching {file.tables_touched} tables:{" "}
        {ORDER.filter((s) => file.by_status[s]).map((s, i, a) => (
          <span key={s}>{file.by_status[s]} {STATUS_LABEL[s].toLowerCase()}{i < a.length - 1 ? ", " : ""}</span>
        ))}. {file.with_open} still have something open.
      </p>
      <p className="mb-6 max-w-3xl text-sm" data-faults-resolution-summary="1">
        Where the ERW&apos;s own work stands:{" "}
        {RESOLUTION_ORDER.filter((s) => file.by_resolution[s]).map((s, i, a) => (
          <span key={s}><strong>{file.by_resolution[s]}</strong> {RESOLUTION_LABEL[s].toLowerCase()}{i < a.length - 1 ? ", " : ""}</span>
        ))}. Each entry gives the reason.
      </p>

      <Section title="What each status means" id="status">
        <ul className="max-w-3xl list-disc space-y-1 pl-5 text-sm">
          {ORDER.map((s) => (
            <li key={s}><strong>{STATUS_LABEL[s]}:</strong> {file.status_words[s]}.</li>
          ))}
        </ul>
        <p className="mt-3 max-w-3xl text-sm text-muted">
          A fault that is held as published is in the tables as the publisher gave it. The ERW does not fill, smooth or
          replace a value; where a rule leaves a value out, the value becomes a blank, and each table&apos;s own rule for
          completeness decides what a blank costs it.
        </p>
      </Section>

      <Section title="Where the work stands" id="resolution">
        <ul className="max-w-3xl list-disc space-y-1 pl-5 text-sm">
          {RESOLUTION_ORDER.map((s) => (
            <li key={s}><strong>{RESOLUTION_LABEL[s]}:</strong> {file.resolution_words[s]}.</li>
          ))}
        </ul>
        <p className="mt-3 max-w-3xl text-sm text-muted">
          A fix that would change a number on a page open to visitors is built, measured in a trial build beside the table as
          it stands, and held until a person has read the numbers before and after. Until then the pages in review that read
          such a table leave the affected figures out and say so.
        </p>
      </Section>

      <Section title="The rule for impossible values" id="rule">
        <p className="max-w-3xl text-sm">
          One rule, in three parts. An hour of demand or of net generation is used when it is held, above zero, within 25
          percent of the median of the four hours around it (the two before and the two after), and within the grid&apos;s own
          range: between one third of and three times its median hour. A zero is a missing value, not a quantity: no grid&apos;s
          demand or generation is zero. A day of interchange between two balancing authorities is used when it is within ten
          times the pair&apos;s median absolute deviation of the pair&apos;s own median, and never left out for less than 5,000 MWh. A value that fails is used for
          nothing, and nothing is filled. The steepest real ramps of these grids move demand about a tenth in an hour, and no
          grid&apos;s lowest or highest real hour comes near the range. Solar, wind and battery output are not put to the
          hour test: they move further than a quarter in an hour by nature. The rule, every table that reads these values,
          and what each changed: <Link href="/data/methods/impossible_hours" className="underline">the method</Link>.
        </p>
      </Section>

      <Section title="The faults" id="faults" aside={<>{file.faults} recorded</>}>
        <div className="overflow-x-auto">
          <table className="mb-6 w-full border-collapse text-sm" data-faults-table="1">
            <thead>
              <tr className="border-b border-rule text-left text-xs text-muted">
                <th className="py-1 pr-3 font-normal">Fault</th>
                <th className="py-1 pr-3 font-normal">Publisher</th>
                <th className="py-1 pr-3 font-normal">Dates</th>
                <th className="py-1 pr-3 font-normal">Status</th>
                <th className="py-1 pr-3 font-normal">Work</th>
                <th className="py-1 pr-3 text-right font-normal">Tables</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((f) => (
                <tr key={f.id} className="border-b border-rule align-top">
                  <td className="py-1 pr-3"><a href={`#${f.id}`} className="underline">{f.title}</a></td>
                  <td className="py-1 pr-3 text-muted">{f.publisher}</td>
                  <td className="py-1 pr-3 whitespace-nowrap">{dates(f)}</td>
                  <td className="py-1 pr-3 whitespace-nowrap">{STATUS_LABEL[f.status]}</td>
                  <td className="py-1 pr-3 whitespace-nowrap" data-fault-resolution={f.resolution}>{RESOLUTION_LABEL[f.resolution]}</td>
                  <td className="py-1 pr-3 text-right tabular-nums">{f.tables.length}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="space-y-8">
          {rows.map((f) => (
            <article key={f.id} id={f.id} data-fault={f.id} className="max-w-3xl scroll-mt-20 border-l-2 border-rule pl-4">
              <h3 className="mb-1 font-serif text-lg">{f.title}</h3>
              <p className="mb-2 text-xs text-muted">
                {f.publisher} · {dates(f)}{f.dates_note ? ` (${f.dates_note})` : ""} · <span data-fault-status={f.status}>{STATUS_LABEL[f.status]}</span>{" "}
                · <strong data-fault-resolution={f.resolution}>{RESOLUTION_LABEL[f.resolution]}</strong>
              </p>
              <dl className="space-y-2 text-sm">
                <div><dt className="font-semibold">Evidence</dt><dd>{f.evidence}</dd></div>
                <div>
                  <dt className="font-semibold">Tables it touches</dt>
                  <dd>{f.tables.length ? f.tables.map((t, i) => <span key={t}><code className="font-mono text-xs">{t}</code>{i < f.tables.length - 1 ? ", " : ""}</span>) : "No table of the warehouse holds it."}</dd>
                </div>
                <div><dt className="font-semibold">What the ERW does</dt><dd>{f.erw_does}</dd></div>
                {f.open ? <div><dt className="font-semibold">Still open</dt><dd>{f.open}</dd></div> : null}
                <div><dt className="font-semibold">{RESOLUTION_LABEL[f.resolution]}: why</dt><dd>{f.resolution_reason}</dd></div>
                <div className="text-xs text-muted"><dt className="inline">Recorded in: </dt><dd className="inline">{f.recorded_in}. Source report: <code className="font-mono">{f.source}</code>.</dd></div>
              </dl>
            </article>
          ))}
        </div>
        <Cite tables={[file.table]} note={`The register as of ${file.built.slice(0, 10)}; a fault is added when a session finds one`} />
      </Section>
    </>
  );
}
