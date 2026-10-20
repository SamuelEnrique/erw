import type { Metadata } from "next";
import type { ReactNode } from "react";
import { Brand } from "@/components/Brand";
import { Num } from "@/components/Num";
import { SiteLink as Link } from "@/components/SiteLink";
import { TableDownloads } from "@/components/tool/TableDownloads";
import { HeadlineNumber, HeadlineRow, InputPanel, SourceLine, Tip, ToolHeader, ToolPage, ToolSection, ToolTable } from "@/components/tool/ToolPage";
import {
  BOUNDS, EFFECTS, EFFECT_TIPS, EFFECT_WORDS, METHOD, NOT_MODELED, STATES, TABLE, TAX_STATES, TAX_TABLE, TECHS, UNIT,
  fmt, inputsKey, inputsOf, lineWords, mwOf, perMw, projectMw, stat, stateName, statesHeld, techOf,
  type Effect, type Inputs, type Measure, type Phase, type Row,
} from "@/lib/impact";
import { HOURLY, attempt, rest } from "@/lib/supabase";
import { StateChart } from "./StateChart";

// Session 347: "What a project does for a state", the economic impact tool (tool 17), in the battery page's three
// questions: (1) how many jobs, from NLR's JEDI models per MW (nlr_jedi_multipliers, sessions 345 and 347) times the
// reader's project; (2) what it pays the state, from the rules the ERW holds (impact_tax_rules, session 346), which
// for a power plant's property tax is none, said as such; (3) what matters most, the swing of each lever and the state
// the plant is built in. The inputs are a plain form whose state is the address, so every figure is drawn on the
// server and carries a check key that scripts/check-values.mjs recomputes from its own read (lib/impact.ts, stat).
// At the defaults (JEDI's own project, its costs and its local shares) every figure is JEDI's own.
export const metadata: Metadata = { title: "What a project does for a state" };
export const dynamic = "force-dynamic";

type TaxRow = { event_id: string; event_type: string; status: string; source_url: string; extra: Record<string, string> };
const SEVERANCE = "/severance";
const field = "w-full border border-rule bg-white px-2 py-1 text-sm";
const iso = (ts: string) => new Date(ts).toISOString().replace(".000Z", "Z");

function V({ x, s, v, m }: { x: Inputs; s: string; v: number | null; m: Measure | "mw" | "rank" }) {
  if (v === null) return <span className="text-muted">not held</span>;
  const n = <Num check={`${inputsKey(x)}|${s}`} raw={v}>{fmt(v, m)}</Num>;
  return m === "earnings" || m === "output" ? <span data-format="usd">{n}</span> : n;
}
function S({ r, m }: { r: Row | undefined; m: Measure | "mw" }) {
  if (!r) return <span className="text-muted">not held</span>;
  const n = <Num check={`series|${TABLE}|${r.entity}|${r.variable}|${iso(r.ts_utc)}`} raw={Number(r.value)}>{fmt(Number(r.value), m)}</Num>;
  return m === "earnings" || m === "output" ? <span data-format="usd">{n}</span> : n;
}

export default async function Impact({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const sp = await searchParams;
  const q = Object.fromEntries(Object.entries(sp).map(([k, v]) => [k, typeof v === "string" ? v : undefined]));
  const { x, notes } = inputsOf(q);
  const t = techOf(x.tech)!;
  const [read, allRead, taxRead] = await Promise.all([
    attempt(() => rest<Row>("series", { select: "entity,variable,ts_utc,value", table_name: `eq.${TABLE}`, entity: `like.nlr_jedi:${x.tech}:${x.state}:*`, order: "entity,variable" }, HOURLY)),
    attempt(() => rest<Row>("series", { select: "entity,variable,ts_utc,value", table_name: `eq.${TABLE}`, entity: `like.nlr_jedi:${x.tech}:*:construction:*`, variable: "eq.jobs", order: "entity" }, HOURLY)),
    TAX_STATES.includes(x.state)
      ? attempt(() => rest<TaxRow>("events", { select: "event_id,event_type,status,source_url,extra", table_name: `eq.${TAX_TABLE}`, event_id: `like.erw_tax:${x.state}:*`, order: "event_id" }, HOURLY))
      : Promise.resolve({ ok: true as const, data: [] as TaxRow[] }),
  ]);
  const rows = read.ok ? read.data : [];
  const all = allRead.ok ? allRead.data : [];
  const row = (phase: string, effect: string, measure: string) => rows.find((r) => r.entity === `nlr_jedi:${x.tech}:${x.state}:${phase}:${effect}` && r.variable === measure);
  const mw = mwOf(rows, x);
  const jediMw = projectMw(rows, x);
  const held = rows.length > 0 && mw !== null;
  const st = (s: string) => stat(rows, x, s, all);
  const where = stateName(x.state);
  const nation = x.state === "us";
  const taxes = taxRead.ok ? taxRead.data : [];
  const property = taxes.filter((r) => r.event_type === "property_tax_rule");
  const severance = taxes.filter((r) => r.event_type.startsWith("severance"));
  const nStates = statesHeld(all, x.tech);

  const phaseTable = (phase: Phase) => (
    <ToolTable caption={`${phase === "construction" ? "During construction" : "Each year of operation"}, ${t.label}, ${where}`} minWidth={560}
      head={["Effect", <>Jobs per MW<Tip id={`permw-${phase}`} label="jobs per MW">JEDI&apos;s own figure per MW of its default project ({t.basis}), in {where}: the line the rest of the row is computed from. Hover a row&apos;s name for the cell it was read from.</Tip></>,
        `Jobs (${UNIT[phase].jobs})`, `Earnings (${UNIT[phase].earnings})`, `Output (${UNIT[phase].output})`]}
      rows={EFFECTS.map((e: Effect) => ({
        key: e, highlight: e === "total",
        cells: [
          <span key="n" title={lineWords(t, phase, e, "jobs", x.state)} data-jedi-line={`${phase}:${e}`}>{EFFECT_WORDS[e]}<Tip id={`${phase}-${e}`} label={EFFECT_WORDS[e]}>{EFFECT_TIPS[e]} {lineWords(t, phase, e, "jobs", x.state)}.</Tip></span>,
          <S key="p" r={row(phase, e, "jobs")} m="jobs" />,
          <V key="j" x={x} s={`${phase}:${e}:jobs`} v={st(`${phase}:${e}:jobs`)} m="jobs" />,
          <V key="e" x={x} s={`${phase}:${e}:earnings`} v={st(`${phase}:${e}:earnings`)} m="earnings" />,
          <V key="o" x={x} s={`${phase}:${e}:output`} v={st(`${phase}:${e}:output`)} m="output" />,
        ],
      }))} />
  );

  // the chart of every state: the reader's project's construction jobs in each state JEDI gives a figure for
  const perState = STATES.filter(([k]) => k !== "us").map(([k, name]) => {
    const v = (e: Effect) => perMw(all, { tech: x.tech, state: k }, "construction", e, "jobs");
    return { k, name, onsite: v("onsite"), supply: v("supply_chain"), induced: v("induced"), total: v("total") };
  }).filter((r) => r.total !== null).sort((a, b) => (b.total ?? 0) - (a.total ?? 0));
  const f = mw === null ? 0 : mw * (x.local / 100) * (x.capex / 100);

  const levers: { key: string; label: string; change: string; tip: string }[] = [
    { key: "mw", label: "Size", change: "50 percent more MW", tip: "JEDI's effects are proportional to the spending, so 50 percent more MW gives 50 percent more of every figure." },
    { key: "capex", label: "Capital cost", change: "25 points more of JEDI's default", tip: "More spent on the build is more bought, in the state and outside it: the construction figures move in proportion; the operating ones do not." },
    { key: "local", label: "Local content", change: "25 points more of JEDI's default shares", tip: "More of each line bought in the state. JEDI applies a share to each line; the page scales every line of a phase by the same factor, the one approximation it makes (docs/methods/economic_impact.md)." },
    { key: "life", label: "Life", change: "5 more years of operation", tip: "Each year of operation adds the operating figures once more; nothing else moves." },
  ];

  return (
    <Brand noUsage>
      <ToolPage>
        <ToolHeader
          title="What a project does for a state"
          crumb="Economics"
          lead={<>How many jobs, how much in wages and how much output a wind, solar, gas or geothermal plant brings to the state it is built in, while it is built and each year it runs, from NLR&apos;s JEDI models; and what the ERW holds of the state&apos;s taxes on it. <Link href={METHOD}>Method</Link>.</>}
        />
        <div className="grid gap-8 lg:grid-cols-[290px_minmax(0,1fr)]">
          <aside>
            <InputPanel title="Assumptions" reset={{ href: "/impact", defaults: "land-based wind in Texas, JEDI's default project, its costs and its local shares, no life, no abatement" }}>
              <form method="get" action="/impact" className="space-y-4 text-sm" data-impact-form="1">
                <fieldset>
                  <legend className="mb-1 font-semibold">Technology<Tip id="tech" label="the technology">Each is NLR&apos;s own JEDI model of that kind of plant, read for every state. The four models&apos; dollars are each their own year: wind 2017, the others 2010.</Tip></legend>
                  <ul className="space-y-1">
                    {TECHS.map((o) => (
                      <li key={o.key}><label className="flex items-baseline gap-2" data-tech={o.key}>
                        <input type="radio" name="tech" value={o.key} defaultChecked={x.tech === o.key} className="accent-[var(--color-accent)]" />
                        <span>{o.label}</span><span className="text-xs text-muted">{o.model} {o.version}</span>
                      </label></li>
                    ))}
                    <li><label className="flex items-baseline gap-2 text-muted" data-tech={NOT_MODELED.key} title={NOT_MODELED.why}>
                      <input type="radio" name="tech" value={NOT_MODELED.key} disabled /><span>{NOT_MODELED.label}</span><span className="text-xs">not modeled: NLR publishes no JEDI model for it</span>
                    </label></li>
                  </ul>
                </fieldset>
                <label className="block"><span className="mb-1 block font-semibold">State</span>
                  <select name="state" defaultValue={x.state} className={field}>
                    {STATES.map(([k, name]) => <option key={k} value={k}>{name}</option>)}
                  </select>
                </label>
                <label className="block"><span className="mb-1 block font-semibold">Size, MW<Tip id="mw" label="the size">Blank is JEDI&apos;s own default project: {jediMw !== null ? <><S r={row("all", "project", "project_mw")} m="mw" /> {t.basis}</> : "not held"}. Every figure is JEDI&apos;s per MW times this.</Tip></span>
                  <input name="mw" type="number" min={BOUNDS.mw[0]} max={BOUNDS.mw[1]} step="any" defaultValue={x.mw ?? ""} placeholder={jediMw !== null ? `JEDI's ${fmt(jediMw, "mw")}` : ""} className={field} />
                </label>
                <label className="block"><span className="mb-1 block font-semibold">Capital cost, percent of JEDI&apos;s default<Tip id="capex" label="the capital cost">100 is JEDI&apos;s own cost for its default project, in the model&apos;s dollar year. The construction figures move in proportion; the operating ones do not.</Tip></span>
                  <input name="capex" type="number" min={BOUNDS.capex[0]} max={BOUNDS.capex[1]} step={1} defaultValue={x.capex} className={field} />
                </label>
                <label className="block"><span className="mb-1 block font-semibold">Local content, percent of JEDI&apos;s shares<Tip id="local" label="the local content">100 is JEDI&apos;s own share of each line bought in the state. In {where}, of each dollar of construction spending JEDI counts <S r={row("construction", "spending", "local_share")} m="mw" /> as spent in the state, and of each dollar of direct operating cost <S r={row("operations", "spending", "local_share")} m="mw" />.</Tip></span>
                  <input name="local" type="number" min={BOUNDS.local[0]} max={BOUNDS.local[1]} step={1} defaultValue={x.local} className={field} />
                </label>
                <label className="block"><span className="mb-1 block font-semibold">Life, years<Tip id="life" label="the life">JEDI states no life for a plant, so none is assumed. Give one to see the operating years added up.</Tip></span>
                  <input name="life" type="number" min={BOUNDS.life[0]} max={BOUNDS.life[1]} step={1} defaultValue={x.life ?? ""} placeholder="none given" className={field} />
                </label>
                <label className="flex items-baseline gap-2" data-abate={x.abate ? "1" : "0"}>
                  <input type="checkbox" name="abate" value="1" defaultChecked={x.abate} className="accent-[var(--color-accent)]" />
                  <span>Property-tax abatement<Tip id="abate" label="the abatement">A scenario, off by default. The ERW holds no abatement statute for any state, so it applies nothing yet: the second question says so.</Tip></span>
                </label>
                <button type="submit" className="border border-accent bg-accent px-4 py-1.5 text-white">Show</button>
              </form>
            </InputPanel>
          </aside>

          <div className="min-w-0">
            {notes.length ? <p className="mb-6 border border-rule bg-paper px-3 py-2 text-sm" role="status" data-typed-notes={notes.length}>{notes.join(" ")}</p> : null}
            {!read.ok ? (
              <p className="mb-6 border border-rule bg-paper px-3 py-2 text-sm" role="status">The table could not be read, so no number is shown: {read.reason}</p>
            ) : !held ? (
              <p className="mb-6 border border-rule bg-paper px-3 py-2 text-sm" role="status" data-not-held={`${x.tech}:${x.state}`}>JEDI gives no figure for {t.label.toLowerCase()} in {where}: its own answer there is an error (the gas model&apos;s #DIV/0! for the District of Columbia and Hawaii), so the ERW holds none. <Link href={METHOD}>Why</Link>.</p>
            ) : (
              <>
                <div data-question="1">
                  <ToolSection title="How many jobs?" id="jobs">
                    <p className="mb-4 max-w-3xl text-sm" data-summary="1">
                      A {fmt(mw!, "mw")} MW {t.label.toLowerCase()} plant in {where}{nation ? " (spending anywhere in the country counted as local)" : ""}, at JEDI&apos;s {x.capex === 100 ? "default cost" : `default cost times ${x.capex} percent`} and {x.local === 100 ? "its local shares" : `${x.local} percent of its local shares`}: JEDI counts <V x={x} s="construction:total:jobs" v={st("construction:total:jobs")} m="jobs" /> job-years while it is built and <V x={x} s="operations:total:jobs" v={st("operations:total:jobs")} m="jobs" /> jobs in each year it runs, in the state.
                    </p>
                    <HeadlineRow>
                      <HeadlineNumber label="Built" value={<V x={x} s="construction:total:jobs" v={st("construction:total:jobs")} m="jobs" />} unit="job-years" note="One job-year is one full-time job for a year (2,080 hours), over the whole build." />
                      <HeadlineNumber label="Each year it runs" value={<V x={x} s="operations:total:jobs" v={st("operations:total:jobs")} m="jobs" />} unit="jobs" note="On site, in the supply chain and induced, every year of operation." />
                      <HeadlineNumber label="Wages while it is built" value={<V x={x} s="construction:total:earnings" v={st("construction:total:earnings")} m="earnings" />} unit={`USD (${rows[0] ? new Date(rows[0].ts_utc).getUTCFullYear() : ""})`} note="Earnings of the construction phase's jobs, in the model's dollar year." />
                    </HeadlineRow>
                    <h3 className="mb-2 font-serif text-lg text-accent">During construction</h3>
                    {phaseTable("construction")}
                    <h3 className="mb-2 mt-6 font-serif text-lg text-accent">Each year of operation</h3>
                    {phaseTable("operations")}
                    {x.life !== null ? (
                      <p className="mt-3 max-w-3xl text-sm" data-life={x.life}>Over {x.life} years of operation: <V x={x} s="life:total:jobs" v={st("life:total:jobs")} m="jobs" /> job-years and USD <V x={x} s="life:total:earnings" v={st("life:total:earnings")} m="earnings" /> of earnings, in the model&apos;s dollars, not discounted.</p>
                    ) : null}
                    <p className="mt-2 max-w-3xl text-xs text-muted" data-jobs-note="1">
                      Gross effects of an input-output model: what the project adds, not what it adds less what the land, money and workers would have done without it; workers and materials are assumed always there to be had. <Link href={`${METHOD}#what-jedi-cannot-see`}>What JEDI cannot see</Link>.
                    </p>
                  </ToolSection>
                </div>

                <div data-question="2">
                  <ToolSection title="What does it pay the state?" id="taxes">
                    {!TAX_STATES.includes(x.state) ? (
                      <p className="max-w-3xl text-sm" data-tax-held="none">The ERW holds tax rules for Texas, Louisiana and New Mexico only. For {where} no rule is held, so no tax figure is shown.</p>
                    ) : !taxRead.ok ? (
                      <p className="max-w-3xl text-sm" role="status">The tax rules could not be read: {taxRead.reason}</p>
                    ) : (
                      <>
                        <p className="mb-3 max-w-3xl text-sm" data-tax-held={x.state}>
                          <strong>Property tax: no rule held.</strong> A plant&apos;s largest tax is usually property tax, and the abatements below change it most. The ERW holds no statute on any of them for {where}, so no rate, abatement or figure is stated{x.abate ? <span data-abate-applied="0">; the abatement scenario is on and applies nothing</span> : null}.
                        </p>
                        <ToolTable words caption={`Property tax rules for a generating project, ${where}`} minWidth={480} head={["Rule", "What the ERW holds"]}
                          rows={property.map((r) => ({ key: r.event_id, cells: [r.extra.x_rule_name, <span key="s" data-tax-rule={r.extra.x_rule} data-status={r.status}>No rule held<Tip id={r.extra.x_rule} label={r.extra.x_rule_name}>{r.extra.x_note}</Tip></span>] }))} />
                        <p className="mt-3 max-w-3xl text-sm" data-severance={x.state}>
                          <strong>Severance: not a plant&apos;s tax.</strong> {where}&apos;s severance rules are held{severance.length ? "" : " (none read here)"}, each cited, on <Link href={SEVERANCE}>the severance calculator</Link>. Severance falls on oil and gas taken out of the ground, and none of these plants produces either{x.tech === "natural_gas" ? ": a gas plant burns gas that wells produce, and those wells pay it, whoever buys the gas" : ""}. None is computed here.
                        </p>
                      </>
                    )}
                    <p className="mt-2 max-w-3xl text-xs text-muted">JEDI&apos;s own property-tax line is not used: its wind workbook says it does not have default data for taxes per MW. A tax figure on this page comes from a statute or does not appear. <Link href={`${METHOD}#2-the-tax-side-severance-and-property-tax`}>The tax side</Link>.</p>
                  </ToolSection>
                </div>

                <div data-question="3">
                  <ToolSection title="What matters most?" id="matters">
                    <ToolTable caption="The swing of each lever" minWidth={560}
                      head={["Lever", "The change", "Job-years built", "Jobs each year", "Job-years over the life"]}
                      rows={[
                        { key: "now", highlight: true, cells: ["As set", "", <V key="c" x={x} s="construction:total:jobs" v={st("construction:total:jobs")} m="jobs" />, <V key="o" x={x} s="operations:total:jobs" v={st("operations:total:jobs")} m="jobs" />,
                          x.life !== null ? <V key="l" x={x} s="life:total:jobs" v={st("life:total:jobs")} m="jobs" /> : <span key="l" className="text-muted">no life given</span>] },
                        ...levers.map((l) => ({
                          key: l.key,
                          cells: [<span key="n">{l.label}<Tip id={`swing-${l.key}`} label={l.label}>{l.tip}</Tip></span>, l.change,
                            <V key="c" x={x} s={`swing:${l.key}:construction:jobs`} v={st(`swing:${l.key}:construction:jobs`)} m="jobs" />,
                            <V key="o" x={x} s={`swing:${l.key}:operations:jobs`} v={st(`swing:${l.key}:operations:jobs`)} m="jobs" />,
                            x.life !== null || l.key === "life" ? <V key="l" x={x} s={`swing:${l.key}:life:jobs`} v={st(`swing:${l.key}:life:jobs`)} m="jobs" /> : <span key="l" className="text-muted">no life given</span>] as ReactNode[],
                        })),
                      ]} />
                    <p className="mt-2 max-w-3xl text-xs text-muted">In JEDI every effect is proportional to the spending, so each lever moves the jobs in proportion; what differs is which phase it moves. No tax rule is held, so no tax figure moves.</p>
                    {!nation && perState.length ? (
                      <div className="mt-8" data-state-chart={x.tech}>
                        <p className="mb-2 max-w-3xl text-sm" data-state-rank={x.state}>
                          Where it is built matters as much: the same project counts {(() => { const r = st("state_rank:construction:jobs"); return r === null ? <span className="text-muted">no rank</span> : <>the <V x={x} s="state_rank:construction:jobs" v={r} m="rank" />{ordinal(r)} most</>; })()} construction job-years in {where} of the {nStates} places JEDI gives a figure for (the states and the District of Columbia), because each state&apos;s own businesses supply a different share of what it buys.
                        </p>
                        <StateChart id="impact-states" unit="job-years" highlight={x.state}
                          categories={perState.map((r) => r.name)} keys={perState.map((r) => r.k)}
                          onsite={perState.map((r) => (r.onsite ?? 0) * f)} supply={perState.map((r) => (r.supply ?? 0) * f)} induced={perState.map((r) => (r.induced ?? 0) * f)} />
                      </div>
                    ) : null}
                  </ToolSection>
                </div>
              </>
            )}
          </div>
        </div>

        <details className="mt-10 border-t border-rule pt-3 text-sm" data-decisions="347">
          <summary className="cursor-pointer text-accent">Decisions on this page (session 347)</summary>
          <ul className="mt-2 max-w-3xl list-disc space-y-1 pl-5 text-sm">
            <li>Every default is JEDI&apos;s: its default project&apos;s size, its cost and its local shares (Samuel&apos;s ruling of 20 October 2026, in chat). JEDI states no plant life, so the life has no default and the page adds up the operating years only when one is given.</li>
            <li>The four models are read for every state by their own formulas (docs/methods/economic_impact.md, section 1); utility-scale solar is the PV model with its own Utility option. Battery storage has no JEDI model and shows no figure.</li>
            <li>The capital cost and the local content are percents of JEDI&apos;s defaults, and act in proportion, as JEDI&apos;s arithmetic does; the local content scales every line of a phase by one factor, the page&apos;s one approximation.</li>
            <li>The tax side states only what a held statute says. No property-tax statute is held for Texas, Louisiana or New Mexico, so each is &quot;no rule held&quot;, and the abatement scenario, off by default, applies nothing. Severance is shown as a rule of oil and gas, not computed for a plant.</li>
            <li>Each model&apos;s dollars are its own year (wind 2017, the others 2010); nothing is converted.</li>
          </ul>
        </details>
        <TableDownloads tables={[TABLE]} />
        <p className="mt-1 text-xs text-muted" data-tax-download="held"><code className="font-mono">{TAX_TABLE}</code> is held for review and not offered for download: its publishers&apos; terms are not read yet (<Link href="/data">Data and methods</Link>).</p>
        <SourceLine tables={[TABLE, TAX_TABLE]}
          note={<>From the National Laboratory of the Rockies (NLR, formerly NREL), <a href={t.page} rel="noopener">{t.model}</a>, release {t.version} (<a href={t.url} rel="noopener">the workbook</a>), its own formulas evaluated by the ERW for each state; credit U.S. Department of Energy (DOE)/NLR/ALLIANCE. NLR&apos;s terms: &ldquo;The user is granted the right, without any fee or cost, to use or copy the Data, provided that this entire notice appears in all copies of the Data&rdquo; (<a href="https://www.nlr.gov/disclaimer" rel="noopener">the notice</a>); the Data are provided as is. The tax rules: the pages the <Link href={SEVERANCE}>severance calculator</Link> cites.</>} />
      </ToolPage>
    </Brand>
  );
}

function ordinal(n: number): string {
  const s = n % 100;
  if (s >= 11 && s <= 13) return "th";
  return ({ 1: "st", 2: "nd", 3: "rd" } as Record<number, string>)[n % 10] ?? "th";
}

