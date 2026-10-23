"use client";
// Session 24: the /policy table: filters by agency, type, sector, state, significance and date; each row expands to its
// impact read, the sectors, ISOs and states it affects, and its sources.
// Session 164: a seventh filter, Tag (the written rule's four tags: large loads, interconnection, transmission cost,
// tax credits), kept in the address (/policy?tag=large_load, or tag=any for every tagged action), and each tagged row's
// chips under its title, each with the rule's matched term and field on hover. The table holds every action, so this is
// where a reader reaches a tagged action of any date. Choosing a tag lifts the significance floor, so that no tagged
// action is hidden by it; the count beside the filters says how many are listed.
import { Fragment, useMemo, useState } from "react";
import type { PolicyAction, PolicyRead } from "@/lib/data";
import { ANY_TAG, LOAD_GROUP, LOAD_GROUP_LABEL, LOAD_GROUP_TAGS, actionsCountKey, hasTag, tagHref, type TagChip } from "@/lib/policyweek";
import { CITE_WORDS, type ReadCite } from "@/lib/policyreads";
import { Num } from "@/components/Num";

export type Row = PolicyAction & { read: PolicyRead | null; cite?: ReadCite | null; tags?: TagChip[] };
export type TagChoice = { key: string; label: string; why: string };

const TYPE: Record<string, string> = { rule: "Final rule", proposed_rule: "Proposed rule", notice: "Notice", press_release: "News release" };
const split = (s: string | null | undefined) => (s ? s.split(";").filter(Boolean) : []);
const uniq = (xs: string[]) => Array.from(new Set(xs)).sort();

// session 2401: pausedAgencies maps an agency code of the table to the paused record's words when that regulator is paused
// (data/policy/paused.json through lib/policyweekdata.ts); its option reads "(paused)" and choosing it says so beside the count.
export function PolicyTable({ rows, tags = [], tag: tagAtOpen = "", missing = [], pausedAgencies = {} }: { rows: Row[]; tags?: TagChoice[]; tag?: string; missing?: { what: string; why: string }[]; pausedAgencies?: Record<string, string> }) {
  // session 304 (the ruling of 18 October 2026, item 5): a date after today is shown as the filing wrote it, with the words "as filed"
  const today = new Date().toISOString().slice(0, 10);
  const [agency, setAgency] = useState("");
  const [type, setType] = useState("");
  const [sector, setSector] = useState("");
  const [state, setState] = useState("");
  const [tag, setTagOnly] = useState(tagAtOpen);
  const [minSig, setMinSig] = useState(tagAtOpen ? "" : "5");
  /** A tag choice changes the rows and the address together, and lifts the significance floor. */
  const setTag = (next: string) => { setTagOnly(next); if (next) setMinSig(""); window.history.replaceState(null, "", tagHref(next)); };
  const tagged = useMemo(() => rows.filter((r) => (r.tags ?? []).length > 0).length, [rows]);
  const [from, setFrom] = useState("");
  const [open, setOpen] = useState<string | null>(null);
  const sectors = useMemo(() => uniq(rows.flatMap((r) => [...split(r.sector_tags), ...split(r.read?.affected_sectors)])), [rows]);
  const states = useMemo(() => uniq(rows.flatMap((r) => [...split(r.states), ...split(r.read?.affected_states)])), [rows]);
  const shown = rows.filter(
    (r) =>
      (!agency || r.agency === agency) &&
      (!type || r.action_type === type) &&
      (!sector || split(r.sector_tags).includes(sector) || split(r.read?.affected_sectors).includes(sector)) &&
      (!state || split(r.states).includes(state) || split(r.read?.affected_states).includes(state)) &&
      hasTag(r.tags, tag) &&
      (!minSig || Number(r.significance) >= Number(minSig)) &&
      (!from || r.event_date >= from),
  );
  const sel = (label: string, v: string, set: (x: string) => void, opts: [string, string][]) => (
    <label className="flex flex-col text-xs text-muted">
      {label}
      <select value={v} onChange={(e) => set(e.target.value)} className="mt-1 border border-rule bg-panel px-2 py-1 text-sm text-ink">
        {opts.map(([k, l]) => (
          <option key={k} value={k}>
            {l}
          </option>
        ))}
      </select>
    </label>
  );
  return (
    <div>
      <div className="mb-3 flex flex-wrap items-end gap-3">
        {sel("Agency", agency, setAgency, [["", "All"], ...uniq(rows.map((r) => r.agency)).map((a) => [a, pausedAgencies[a] ? `${a} (paused)` : a] as [string, string])])}
        {agency && pausedAgencies[agency] ? <span className="cursor-help border-b border-dotted border-muted text-xs italic text-muted" title={pausedAgencies[agency]} data-policy-paused-filter={agency}>paused: the rows held stay, nothing new is read</span> : null}
        {sel("Type", type, setType, [["", "All"], ...Object.entries(TYPE)])}
        {sel("Sector", sector, setSector, [["", "All"], ...sectors.map((s) => [s, s] as [string, string])])}
        {sel("State", state, setState, [["", "All"], ...states.map((s) => [s, s] as [string, string])])}
        {sel("Significance", minSig, setMinSig, [["5", "5 or more"], ["7", "7 or more"], ["", "All"]])}
        <span data-policy-tag-filter={tag} data-policy-tagged={tagged}>
          {tags.length ? sel("Tag", tag, setTag, [["", "All"], [ANY_TAG, `Any tag (${tagged})`],
            // session 469: one choice for what a large load's cost turns on (lib/policyweek.ts, LOAD_GROUP); not chosen by default
            ...(tags.some((t) => (LOAD_GROUP_TAGS as readonly string[]).includes(t.key)) ? [[LOAD_GROUP, LOAD_GROUP_LABEL] as [string, string]] : []),
            ...tags.map((t) => [t.key, t.label] as [string, string])])
            : <span className="cursor-help border-b border-dotted border-muted text-xs italic text-muted" title={missing.map((m) => m.why).join(" ") || "The tag rule is not in this page's files yet."} data-missing="1">tags not held yet</span>}
        </span>
        <label className="flex flex-col text-xs text-muted">
          From
          <input type="date" value={from} onChange={(e) => setFrom(e.target.value)} className="mt-1 border border-rule bg-panel px-2 py-1 text-sm text-ink" />
        </label>
        {/* session 2400: the total is the live table's count and carries its check key (event_count|policy_actions|all); the
            filtered count is this page's own and changes with every filter, so it carries a hover and no key */}
        <span className="text-xs text-muted" data-policy-shown={shown.length}>
          <span className="cursor-help border-b border-dotted border-muted" title="The actions the filters above leave, counted on this page.">{shown.length}</span> of{" "}
          <span className="cursor-help border-b border-dotted border-muted" title="Every action of the live table policy_actions, as this page read it (the count is checked against the table)."><Num check={actionsCountKey(null)} raw={rows.length}>{rows.length}</Num></span> actions
        </span>
        {/* session 282: every filter back to the page's default: all agencies, types, sectors, states and tags, from any
            date, significance 5 or more (the actions read are those of 5 or more) */}
        <button type="button" data-reset="1" onClick={() => { setAgency(""); setType(""); setSector(""); setState(""); setTag(""); setMinSig("5"); setFrom(""); }} className="border border-rule px-2 py-1 text-xs" title="All agencies, types, sectors, states and tags, from any date, significance 5 or more">Reset the filters</button>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-rule text-left text-xs text-muted">
              <th className="py-1 pr-3">Date</th>
              <th className="py-1 pr-3">Agency</th>
              <th className="py-1 pr-3">Type</th>
              <th className="py-1 pr-3">Title</th>
              <th className="py-1 pr-3">Sector</th>
              <th className="py-1 text-right">Significance</th>
            </tr>
          </thead>
          <tbody>
            {shown.slice(0, 400).map((r) => (
              <Fragment key={r.event_id}>
                <tr className="cursor-pointer border-b border-rule align-top hover:bg-panel" data-policy-row={r.event_id} onClick={() => setOpen(open === r.event_id ? null : r.event_id)}>
                  <td className="whitespace-nowrap py-1 pr-3 font-mono text-xs">{r.event_date}{r.event_date > today ? <span className="font-sans text-muted" data-as-filed="1"> as filed</span> : null}</td>
                  <td className="py-1 pr-3">{r.agency}</td>
                  <td className="whitespace-nowrap py-1 pr-3">{TYPE[r.action_type] ?? r.action_type}</td>
                  <td className="py-1 pr-3">
                    {r.title}
                    {r.read ? <span className="ml-1 text-xs text-accent">(read)</span> : null}
                    {(r.tags ?? []).length ? (
                      <span className="mt-0.5 block text-xs" data-policy-tags={(r.tags ?? []).map((t) => t.key).join(" ")}>
                        {(r.tags ?? []).map((t) => <span key={t.key} title={t.why} data-policy-tag={t.key} data-policy-tag-of={r.event_id} className="mb-0.5 mr-1 inline-block cursor-help whitespace-nowrap border border-rule bg-white px-1">{t.label}</span>)}
                      </span>
                    ) : null}
                  </td>
                  <td className="py-1 pr-3 text-xs">{split(r.sector_tags).join(", ")}</td>
                  {/* session 332: the score is the table's, read again by check-values (event|policy_actions|<id>|significance) */}
                  <td className="py-1 text-right">{r.significance ? <Num check={`event|policy_actions|${r.event_id}|significance`} raw={Number(r.significance)}>{r.significance}</Num> : "not scored"}</td>
                </tr>
                {open === r.event_id ? (
                  <tr className="border-b border-rule bg-panel">
                    <td colSpan={6} className="px-3 py-2 text-sm">
                      <Detail r={r} />
                    </td>
                  </tr>
                ) : null}
              </Fragment>
            ))}
          </tbody>
        </table>
      </div>
      {shown.length > 400 ? <p className="mt-2 text-xs text-muted">The first 400 are shown; narrow the filters to see the rest.</p> : null}
    </div>
  );
}

function Detail({ r }: { r: Row }) {
  const x = r.read;
  const dirs = x
    ? ([["supply", x.direction_supply], ["demand", x.direction_demand], ["prices", x.direction_prices], ["buildout", x.direction_buildout]] as const).filter(([, v]) => v)
    : [];
  return (
    <div className="space-y-2">
      {x ? (
        <>
          {x.plain_read ? <p>{x.plain_read}</p> : null}
          {x.what_changes ? (
            <p>
              <span className="text-xs text-muted">What changes: </span>
              {x.what_changes}
            </p>
          ) : null}
          {x.affected_sectors || x.affected_isos || x.affected_states ? (
            <p className="text-xs">
              <span className="text-muted">Affected: </span>
              {[split(x.affected_sectors).join(", "), split(x.affected_isos).join(", "), split(x.affected_states).join(", ")].filter(Boolean).join("; ")}
            </p>
          ) : null}
          {dirs.length ? (
            <p className="text-xs">
              <span className="text-muted">Direction of effect: </span>
              {dirs.map(([k, v]) => k + " " + v).join(", ")}
            </p>
          ) : null}
          {x.timeline ? (
            <p className="text-xs">
              <span className="text-muted">Timeline: </span>
              {x.timeline}
            </p>
          ) : null}
          <p className="text-xs text-muted">
            Read by {x.model_id} from the action&apos;s own text; fields kept: {x.fields_kept || "none"}
            {x.fields_dropped ? "; dropped (their words or numbers were not found in the text): " + x.fields_dropped : ""}.
          </p>
          {/* session 469: what the read cites: its figures and their source (the action's own text), or "no figure" */}
          {r.cite ? (
            <p className="text-xs" data-read-cites={r.cite.kind} data-read-cites-of={r.event_id}>
              <span className="text-muted">Figures: </span>
              {r.cite.kind === "none" ? CITE_WORDS.none
                : r.cite.kind === "table" ? <>{CITE_WORDS.table} {r.cite.tables.join(", ")}{r.cite.figures.length ? `; figures ${r.cite.figures.join(", ")}` : ""}.</>
                : <>{r.cite.figures.join(", ")}. {CITE_WORDS.text} Source: <a href={r.source_url}>the action</a>.</>}
            </p>
          ) : null}
        </>
      ) : (
        <p className="text-xs text-muted">
          {Number(r.significance) >= 5 ? "Not read yet." : "Scored below 5: not read."} {r.why}
        </p>
      )}
      <p className="text-xs">
        <span className="text-muted">Source: </span>
        <a href={r.source_url}>{r.source_url}</a>
        {r.docket ? <span className="text-muted"> (docket or RIN {r.docket.split(";").join(", ")})</span> : null}
        {split(r.related_urls).map((u) => (
          <span key={u}>
            {" "}
            | <a href={u}>news release</a>
          </span>
        ))}
        {split(r.news_story_urls)
          .slice(0, 3)
          .map((u, i) => (
            <span key={u}>
              {" "}
              | <a href={u}>news story {i + 1}</a>
            </span>
          ))}
      </p>
    </div>
  );
}
