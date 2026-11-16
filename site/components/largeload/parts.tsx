// Energy Research Warehouse (ERW) site, chain 302 (session 7201): the pieces the large-load rules share on the All grids
// tab of /cost-of-power and in the monitor of /policy. No "use client" and no server-only import, so the server's panel
// (the rule a row of the tab opens) and the client's table draw a rule with the same code. The owner's page rules: an
// explanation or a source is a hover tip, never grey text; a held row or a withheld field is drawn blank with "license
// needed" on hover; the tool states the document's words and takes no view.
import { useId, type ReactNode } from "react";
import { FIELDS, FIELD_HEAD, FIELD_TIP, GRID_WORDS, LICENSE_NEEDED, RULES_TABLE, UPGRADES_TIP, UPGRADES_WORDS, drawn, statusTip, statusWords,
  type FieldId, type HeldRule, type Rule } from "@/lib/largeloadrules";

/** A hover tip a keyboard reaches: the trigger is a button its tip describes (app/tokens.css, ".tip" and "[data-llr]"). */
export function Tip({ tip, children, plain, className = "", data }: { tip: ReactNode; children: ReactNode; plain?: boolean; className?: string; data?: Record<string, string> }) {
  const id = useId();
  return (
    <span className={`tip relative inline-block max-w-full ${className}`.trim()} {...Object.fromEntries(Object.entries(data ?? {}).map(([k, v]) => [`data-${k}`, v]))}>
      <button type="button" aria-describedby={id} data-tip-trigger="1" className={`max-w-full text-left text-inherit ${plain ? "" : "cursor-help border-b border-dotted border-muted"}`}>{children}</button>
      <span role="tooltip" id={id} data-tp="">{tip}</span>
    </span>
  );
}
/** A held row's cell or a withheld field: nothing printed, "license needed" on hover and to a screen reader. `data-license-held`
 * names the table, as the site's held figures do (components/Num.tsx), so the value checker passes it by and a test counts it. */
export function Blank({ tip, table = RULES_TABLE, what, label = LICENSE_NEEDED }: { tip: string; table?: string; what: string; label?: string }) {
  const id = useId();
  return (
    <span className="tip relative block" {...(label === LICENSE_NEEDED ? { "data-license-held": table } : { "data-not-shown": table })} data-llr-blank={what}>
      <button type="button" aria-label={`${what}: ${label}`} aria-describedby={id} data-tip-trigger="1" className="block h-5 w-full min-w-[2.5rem] cursor-help">{String.fromCharCode(160)}</button>
      <span role="tooltip" id={id} data-tp="">{tip}</span>
    </span>
  );
}
export const HELD_ROW_TIP = (utility: string) => `${LICENSE_NEEDED}: the ERW read ${utility}'s rule in a document whose publisher's terms ask permission before it is shown. The row is counted and its values are not printed.`;

/** One field of a rule, in a table's cell (cut at a word, the whole and its cite on hover) or whole (a rule's card). */
export function FieldView({ rule, f, whole, onSee }: { rule: Rule; f: FieldId; whole?: boolean; onSee?: (id: string) => ReactNode }) {
  const d = drawn(rule.fields[f], f, whole ? 100_000 : 96);
  if (d.kind === "empty") return null;
  if (d.kind === "withheld" || d.kind === "held") return <Blank tip={d.tip} what={FIELD_HEAD[f]} />;
  if (d.kind === "see" && d.row && onSee) return <span data-llr-field={f} data-llr-kind="see">{onSee(d.row)}</span>;
  if (whole && d.kind === "value") {
    const c = rule.fields[f] as { cite: string; registry?: string };
    return (
      <span data-llr-field={f} data-llr-kind="value">
        {d.whole} <Tip tip={`As the document prints it: ${c.cite}${c.registry ? ` Held in the ERW's registry of filed schedules (warehouse/sources/${c.registry}).` : ""}`} data={{ "llr-cite": f }}>source</Tip>
      </span>
    );
  }
  return <Tip tip={d.tip} data={{ "llr-field": f, "llr-kind": d.kind }}>{d.words}</Tip>;
}

/** A rule in full: its utility and place, its name as a link to the document, its status and date, and every field as
 * the document prints it, each with its cite on hover. */
export function RuleCard({ rule, onSee, lawsHref, actions }: { rule: Rule; onSee?: (id: string) => ReactNode; lawsHref?: ReactNode; actions?: ReactNode }) {
  return (
    <article className="border border-rule bg-white px-3 py-2 text-sm" data-rule-card={rule.id} aria-label={`${rule.utility}: ${rule.name}`}>
      <h4 className="font-semibold">
        {rule.utility} <span className="font-normal">({rule.state}, <Tip tip={`The grid or region is the ERW's classification, not a cited value: ${rule.region}.`}>{GRID_WORDS[rule.grid] ?? rule.grid}</Tip>)</span>
        {actions ? <span className="ml-2 font-normal">{actions}</span> : null}
      </h4>
      <p className="mt-0.5">
        <a href={rule.url} title={`${rule.title}, read ${rule.read}`} data-rule-doc={rule.id}>{rule.name}</a>
        {rule.clause ? <> <Tip tip={`The words that make it a large-load rule: ${rule.clause}`} data={{ "llr-clause": "1" }}>its clause</Tip></> : null}
      </p>
      {/* session 7600 (the browser read, rows 6 and 7): the status, the docket and what else the row holds are a line
          each. As one sentence, a long docket took the line whole and left the sentence's period and "The ERW's notes"
          at the head of the next (". The ERW's notes"). A status with no date printed says so of the date. */}
      <p className="mt-0.5" data-rule-status={rule.id}>
        Status: <Tip tip={statusTip(rule)}>{statusWords(rule.status, rule.status_date)}</Tip>
      </p>
      {rule.docket && rule.docket !== "not published" ? <p className="mt-0.5" data-rule-docket={rule.id}>Docket: <Tip tip={rule.docket_cite || "The docket as the document names it."}>{rule.docket}</Tip></p> : null}
      {lawsHref || rule.notes ? (
        <p className="mt-0.5" data-rule-more={rule.id}>
          {lawsHref}{lawsHref && rule.notes ? ". " : null}
          {rule.notes ? <Tip tip={rule.notes} data={{ "llr-notes": "1" }}>The ERW&apos;s notes</Tip> : null}
        </p>
      ) : null}
      <table className="mt-2 w-full border-collapse text-sm" data-rule-fields={rule.id}>
        <caption className="sr-only">{rule.utility}: the rule&apos;s terms as the document prints them</caption>
        <tbody>
          {FIELDS.map((f) => (
            <tr key={f} className="border-t border-rule align-top">
              <th scope="row" className="w-36 py-1 pr-3 text-left font-normal"><Tip tip={FIELD_TIP[f]}>{FIELD_HEAD[f]}</Tip></th>
              <td className="py-1"><FieldView rule={rule} f={f} whole onSee={onSee} /></td>
            </tr>
          ))}
          <tr className="border-t border-rule align-top">
            <th scope="row" className="w-36 py-1 pr-3 text-left font-normal">Upgrades</th>
            <td className="py-1"><Tip tip={UPGRADES_TIP} data={{ "llr-upgrades": "1" }}>{UPGRADES_WORDS}</Tip></td>
          </tr>
        </tbody>
      </table>
    </article>
  );
}
/** A rule held for a license: the utility and its place, and every other cell blank with "license needed" on hover. */
export function HeldCard({ rule }: { rule: HeldRule }) {
  return (
    <article className="border border-rule bg-white px-3 py-2 text-sm" data-rule-card={rule.id} data-rule-held="1" aria-label={`${rule.utility}: ${LICENSE_NEEDED}`}>
      <h4 className="font-semibold">{rule.utility} <span className="font-normal">({rule.state}, {GRID_WORDS[rule.grid] ?? rule.grid})</span></h4>
      <table className="mt-2 w-full border-collapse text-sm">
        <caption className="sr-only">{rule.utility}: held for a license</caption>
        <tbody>
          {(["Rule", "Status", ...FIELDS.map((f) => FIELD_HEAD[f])]).map((h) => (
            <tr key={h} className="border-t border-rule align-top">
              <th scope="row" className="w-36 py-1 pr-3 text-left font-normal">{h}</th>
              <td className="py-1"><Blank tip={HELD_ROW_TIP(rule.utility)} what={h} /></td>
            </tr>
          ))}
        </tbody>
      </table>
    </article>
  );
}
