import type { Metadata } from "next";
import { SiteLink as Link } from "@/components/SiteLink";
import { Fold, HeadlineNumber, HeadlineRow, InputPanel, SourceLine, ToolHeader, ToolPage, ToolSection } from "@/components/tool/ToolPage";
import file from "@/data/deals_v3.json";
import {
  KINDS, KIND_LABEL, NOT_STATED, STATES, TECH_LABEL, counts, hrefOf, inputsOf, monthWords, parties, select, selectionWords, stated, summary, technologies, toDeal, usd, whole,
  type Deal, type Inputs, type Num, type Row,
} from "@/lib/deals3";

// Session 130: the deals tracker, version 3, re-aimed at power deals. It reads the site's copy of power_deals
// (data/deals_v3.json, written by warehouse/deals/extract_v3.py): the public fields only, no outlet text. Every number
// on the page is in the table with the sentence it was read from (the sentences are outlet text and stay in the
// internal table); here each number links to the story it was read from. A figure a story does not state is "not
// stated", never an estimate. The choices live in the address and the form is a plain GET form, so the page works
// without JavaScript. Versions 1 and 2 (/deals, /deals/v2) are as they were.
export const metadata: Metadata = { title: "Power deals", robots: { index: false, follow: false } };
export const dynamic = "force-dynamic";

type Stated = { version: string; deals: number; size: number; mw: number; mwh: number; price: number; price_usd_mwh: number; term: number; dollars: number; any_number: number };
type Tier = { tier: number; words: string; stories: number; read: number; remain: number };
type Summary = {
  built_at: string; models: string[]; stories_held: number; stories_read: number; stories_remaining: number; tiers: Tier[]; calls: number;
  model_deals: number; deals_not_kept: number; folded: number; deals: number; numbers_given: number; numbers_kept: number; numbers_checked: number;
  second_read: { power_deal: number; not_power: number; not_a_transaction: number }; roles_not_stated: number; numbers_not_the_deals: number; names_not_parties: number;
  v2_table: { rows: number; first: string; last: string }; compare: Record<"all" | "storage" | "datacenter", Stated[]>;
};
const S = (file as unknown as { summary: Summary }).summary;
const ROWS = (file as unknown as { deals: Row[] }).deals;
const field = "w-full border border-rule bg-white px-2 py-1 text-sm";
const none = <span className="text-muted">{NOT_STATED}</span>;
const cell = "px-3 py-1.5 align-top";

/** A stated number with the story it was read from. */
function N({ n, figure, name }: { n: Num; figure: string; name: string }) {
  return (
    <span data-number={name}>
      {stated(n, figure)}{" "}
      {n.url ? <a href={n.url} rel="noopener noreferrer" target="_blank" className="text-xs underline" title="The story this number was read from">story</a> : null}
    </span>
  );
}

function Parties({ d }: { d: Deal }) {
  const lines: [string, string][] = [];
  if (d.buyer) lines.push(["Buyer", d.buyer]);
  if (d.seller) lines.push(["Seller", d.seller]);
  if (d.others.length) lines.push([d.buyer || d.seller ? "Also" : "Parties", d.others.join(", ")]);
  if (!lines.length) return none;
  return <>{lines.map(([k, v]) => <div key={k}><span className="text-xs text-muted">{k}</span> {v}</div>)}</>;
}

function Choices({ x, all }: { x: Inputs; all: Deal[] }) {
  const c = counts(all);
  const years = [...new Set(all.map((d) => d.year))].sort().reverse();
  const views: { id: Inputs["view"]; label: string }[] = [{ id: "", label: "All" }, { id: "storage", label: "Storage" }, { id: "datacenter", label: "Datacenters" }];
  const n = (f: (d: Deal) => boolean) => all.filter(f).length;
  return (
    <form method="get" action="/deals/v3" className="space-y-4 text-sm">
      <div>
        <div className="mb-1 font-semibold" id="view-label">One click</div>
        <div className="grid grid-cols-3 border border-accent" role="group" aria-labelledby="view-label">
          {views.map((v, i) => (
            <Link key={v.id || "all"} href={hrefOf(x, { view: v.id })} scroll={false} aria-current={x.view === v.id ? "true" : undefined} data-view={v.id || "all"}
              style={x.view === v.id ? { color: "#fff" } : undefined}
              className={`px-1 py-1.5 text-center no-underline ${i ? "border-l border-accent" : ""} ${x.view === v.id ? "bg-accent font-semibold" : "bg-white text-accent"}`}>
              {v.label}
            </Link>
          ))}
        </div>
        <input type="hidden" name="view" value={x.view} />
      </div>
      <label className="block"><span className="mb-1 block font-semibold">Kind of deal</span>
        <select name="kind" defaultValue={x.kind} className={field}>
          <option value="">All kinds ({whole(c.deals)})</option>
          {KINDS.map((k) => <option key={k.id} value={k.id}>{k.label} ({whole(c.byKind[k.id])})</option>)}
        </select>
      </label>
      <label className="block"><span className="mb-1 block font-semibold">Technology</span>
        <select name="tech" defaultValue={x.tech} className={field}>
          <option value="">All</option>
          {technologies(all).map((t) => <option key={t.value} value={t.value}>{TECH_LABEL[t.value] ?? t.value} ({whole(t.n)})</option>)}
        </select>
      </label>
      <label className="block"><span className="mb-1 block font-semibold">What the story states</span>
        <select name="states" defaultValue={x.states} className={field}>
          <option value="">Anything or nothing</option>
          {STATES.map((s) => <option key={s.id} value={s.id}>{s.label} ({whole(n((d) => (s.id === "size" ? d.mw !== null || d.mwh !== null : s.id === "price" ? d.price !== null : s.id === "term" ? d.term !== null : d.dollars !== null)))})</option>)}
        </select>
      </label>
      <label className="block"><span className="mb-1 block font-semibold">Counterparty</span>
        <input name="party" type="text" defaultValue={x.party} list="deal-parties" maxLength={80} placeholder="a name, or part of one" className={field} />
        <datalist id="deal-parties">{parties(all).map((p) => <option key={p.name} value={p.name}>{`${p.n} deals`}</option>)}</datalist>
      </label>
      <label className="block"><span className="mb-1 block font-semibold">Year</span>
        <select name="year" defaultValue={x.year} className={field}>
          <option value="">All</option>
          {years.map((y) => <option key={y} value={y}>{y} ({whole(n((d) => d.year === y))})</option>)}
        </select>
      </label>
      <div className="flex items-baseline gap-3">
        <button type="submit" className="border border-accent bg-accent px-4 py-1.5 text-white">Show</button>
        <Link href="/deals/v3" scroll={false} className="text-xs">Show every deal</Link>
      </div>
    </form>
  );
}

/** Version 2 beside version 3: how many deals state a size, a price, a term. The counts are the build's (the table's). */
function Compare({ title, rows, id }: { title: string; rows: Stated[]; id: string }) {
  return (
    <div className="mb-5 overflow-x-auto">
      <table className="w-full border-collapse text-left text-sm" style={{ minWidth: 620 }} data-compare={id}>
        <caption className="mb-1 text-left font-semibold">{title}</caption>
        <thead>
          <tr className="bg-accent text-white">
            {["Version", "Deals", "State a size", "State a price", "State a term", "State a value, USD"].map((h) => <th key={h} scope="col" className="px-3 py-1.5 font-normal">{h}</th>)}
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.version} className="border-b border-rule" data-compare-version={r.version}>
              <th scope="row" className={`${cell} font-normal`}>{r.version}</th>
              <td className={`${cell} tabular-nums`} data-c="deals">{whole(r.deals)}</td>
              <td className={`${cell} tabular-nums`} data-c="size">{whole(r.size)}<span className="text-xs text-muted"> ({whole(r.mw)} in MW, {whole(r.mwh)} in MWh)</span></td>
              <td className={`${cell} tabular-nums`} data-c="price">{whole(r.price)}</td>
              <td className={`${cell} tabular-nums`} data-c="term">{whole(r.term)}</td>
              <td className={`${cell} tabular-nums`} data-c="dollars">{whole(r.dollars)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default async function DealsThree({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const sp = await searchParams;
  const all = ROWS.map(toDeal);
  const x = inputsOf(Object.fromEntries(Object.entries(sp).map(([k, v]) => [k, typeof v === "string" ? v : undefined])), all);
  const shown = select(all, x);
  const c = counts(shown), ca = counts(all);
  const words = selectionWords(x);
  const built = `${S.built_at.slice(0, 4)}-${S.built_at.slice(4, 6)}-${S.built_at.slice(6, 8)}`;

  return (
    <ToolPage>
      <ToolHeader title="Power deals" crumb={<>The deals tracker, version 3, in review. Version 2: <Link href="/deals/v2" className="underline">/deals/v2</Link></>}
        lead={<>Power purchases, tolling, offtakes, financings and acquisitions in electricity, as the news reported them: who, what kind, what technology, how large, at what price and for how long, where a story says so. Every number links to the story it was read from. <strong>These are deals reported in the news the ERW reads, not a complete record of the market.</strong></>} />
      <div className="grid gap-8 lg:grid-cols-[290px_minmax(0,1fr)]">
        <aside>
          <InputPanel title="Your selection" note={<>The counts in brackets are of every power deal held. A deal that names two technologies counts under both.</>}>
            <Choices key={hrefOf(x)} x={x} all={all} />
          </InputPanel>
        </aside>

        <div className="min-w-0">
          {!all.length ? (
            <p className="mb-6 border border-rule bg-paper px-3 py-2 text-sm" role="status">No power deal is held.</p>
          ) : (
            <>
              <p className="mb-6 max-w-3xl font-serif text-xl leading-snug" data-deals-summary="1">{summary(all, shown, x)}</p>

              <p className="mb-8 max-w-3xl border-l-2 border-accent bg-paper px-4 py-3 text-sm" data-deals-stated="1">
                <strong>The ERW holds each story&apos;s title and summary, not its body, and most give no figure.</strong> Of the <span data-all="deals">{whole(ca.deals)}</span> power deals held,{" "}
                <span data-all="size">{whole(ca.size)}</span> state a size, <span data-all="price">{whole(ca.price)}</span> a price, <span data-all="term">{whole(ca.term)}</span> a term and{" "}
                <span data-all="dollars">{whole(ca.withDollars)}</span> a value in US dollars. A number is kept only with the sentence it was read from; where a story gives none the table says &quot;{NOT_STATED}&quot;. Nothing is estimated.
              </p>

              <HeadlineRow>
                <HeadlineNumber label={words ? "Power deals in this selection" : "Power deals held"} value={<span data-deals="count">{whole(c.deals)}</span>}
                  note={words ? <>of {whole(ca.deals)} held: {words}</> : <>{monthWords(all[all.length - 1].month)} to {monthWords(all[0].month)}</>} />
                <HeadlineNumber label="State a size" value={<span data-deals="size">{whole(c.size)}</span>} unit={`of ${whole(c.deals)}`}
                  note={c.withMw ? <><span data-deals="mw">{whole(c.mw)}</span> MW over the <span data-deals="with_mw">{whole(c.withMw)}</span> that state megawatts, of every kind together; the others are not zero, they are not known</> : <>no deal in this selection states megawatts</>} />
                <HeadlineNumber label="State a price, a term" value={<><span data-deals="price">{whole(c.price)}</span>, <span data-deals="term">{whole(c.term)}</span></>} unit={`of ${whole(c.deals)}`}
                  note={<><span data-deals="with_dollars">{whole(c.withDollars)}</span> state a value in US dollars{c.withDollars ? <>, USD {usd(c.dollars)} in all</> : null}.</>} />
              </HeadlineRow>

              <ToolSection title="Against version 2" id="compare"
                note={<>Version 2 read {whole(S.tiers[0].stories)} stories and asked for fourteen types of energy deal, oil and LNG among them; its table holds {whole(S.v2_table.rows)} rows. Version 3 asks for power deals only, and has read {whole(S.stories_read)} of the {whole(S.stories_held)} stories held. The middle row of each table is version 3 on the stories version 2 read, the like-for-like comparison. A size is megawatts or megawatt-hours. Counted on {built}.</>}>
                <Compare id="all" title="Every deal" rows={S.compare.all} />
                <Compare id="storage" title="Storage (version 2: the words battery or storage in its technology or asset; version 3: technology storage)" rows={S.compare.storage} />
                <Compare id="datacenter" title="Datacenters (each version's own flag for power that serves datacenters or AI)" rows={S.compare.datacenter} />
              </ToolSection>

              <ToolSection title={words ? `The ${whole(c.deals)} power deals in this selection` : `Every power deal held (${whole(c.deals)})`} id="deals"
                note={<>Newest first, by the day the first story was published (UTC). A deal reported by several stories is one row, with every story linked. The word &quot;story&quot; beside a number opens the story that number was read from. Many links open through Google News, which is where the ERW found the story.</>}>
                {shown.length ? (
                  <div className="overflow-x-auto">
                    <table className="w-full border-collapse text-left text-sm" style={{ minWidth: 940 }}>
                      <caption className="sr-only">Power deals in this selection</caption>
                      <thead>
                        <tr className="bg-accent text-white">
                          {["Date", "Deal", "Parties", "Technology", "Size", "Price", "Term", "Value, USD", "Stories"].map((h) => <th key={h} scope="col" className="px-3 py-1.5 font-normal">{h}</th>)}
                        </tr>
                      </thead>
                      <tbody>
                        {shown.map((d) => (
                          <tr key={d.id} className="border-b border-rule" data-deal={d.id}>
                            <th scope="row" className={`${cell} whitespace-nowrap font-normal tabular-nums`}>{d.date}</th>
                            <td className={cell}>
                              {KIND_LABEL[d.kind] ?? d.kind}
                              {d.asset ? <div className="text-xs text-muted">{d.asset}</div> : null}
                              {d.status || d.datacenter ? <div className="text-xs text-muted">{[d.status, d.datacenter ? "datacenters" : ""].filter(Boolean).join("; ")}</div> : null}
                            </td>
                            <td className={cell}><Parties d={d} /></td>
                            <td className={cell}>
                              {d.technology.length ? d.technology.map((t) => TECH_LABEL[t] ?? t).join(", ") : none}
                              {d.place || d.state || d.country ? <div className="text-xs text-muted">{[d.place, d.state, d.country].filter(Boolean).filter((v, i, a) => a.indexOf(v) === i).join(", ")}</div> : null}
                            </td>
                            <td className={`${cell} tabular-nums`} data-deal-mw={d.mw?.value ?? ""}>
                              {d.mw ? <div><N n={d.mw} figure={`${whole(d.mw.value)} MW`} name="mw" /></div> : null}
                              {d.mwh ? <div><N n={d.mwh} figure={`${whole(d.mwh.value)} MWh`} name="mwh" /></div> : null}
                              {!d.mw && !d.mwh ? none : null}
                            </td>
                            <td className={`${cell} tabular-nums`}>{d.price ? <N n={d.price} figure={`${whole(d.price.value)} ${d.price.unit}`} name="price" /> : none}</td>
                            <td className={`${cell} tabular-nums`}>{d.term ? <N n={d.term} figure={`${whole(d.term.value)} ${d.term.value === 1 ? "year" : "years"}`} name="term" /> : none}</td>
                            <td className={`${cell} tabular-nums`}>{d.dollars ? <N n={d.dollars} figure={usd(d.dollars.value)} name="dollars" /> : none}</td>
                            <td className={cell}>
                              {d.links.map((u, i) => <span key={u}>{i ? ", " : ""}<a href={u} rel="noopener noreferrer" target="_blank" className="underline">{i === 0 ? d.source || "story" : `story ${i + 1}`}</a></span>)}
                              {d.folded ? <div className="text-xs text-muted">{d.folded + 1} reports, one deal</div> : null}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <p className="border border-rule bg-paper px-3 py-2 text-sm" role="status">No power deal held matches this selection. <Link href="/deals/v3" className="underline">Show every deal</Link>.</p>
                )}
              </ToolSection>

              <div className="mb-8 border-t border-rule">
                <Fold title="How a deal gets here">
                  <ul className="max-w-3xl list-disc space-y-1.5 pl-5">
                    <li><strong>From titles and summaries.</strong> A model ({S.models.join(", ")}) reads the title and summary of each story the ERW holds and returns the power deals in them: a transaction between named parties whose subject is electricity, or an asset that makes, stores or moves it. Oil, LNG and pipeline deals, which version 2 kept, are not here.</li>
                    <li><strong>No number without its sentence.</strong> For every number the model must give the words and the sentence it read it from. The number is kept only if that sentence is in the story, the words are in the sentence, and the words state that number with its unit. Of {whole(S.numbers_given)} numbers the model gave, {whole(S.numbers_kept)} passed; {whole(S.numbers_checked)} are in the table, the others belonging to deals turned away below or to a second report of one deal.</li>
                    <li><strong>A range is not a number.</strong> &quot;200 to 300 MW&quot; is left blank. A limit is kept with its word: &quot;up to 500 MW&quot; shows as up to 500 MW. Euros and pounds are not turned into dollars.</li>
                    <li><strong>Every deal is read twice.</strong> The first reading returned {whole(S.model_deals)} deals. A second reading took each one alone with its stories and kept {whole(S.second_read.power_deal)}: {whole(S.second_read.not_power)} were transactions the words did not show to be about power (a datacenter lease, a fund raising money), and {whole(S.second_read.not_a_transaction)} were no transaction at all (a plant starting up, a plan). It also blanked {whole(S.numbers_not_the_deals)} figures that were not the deal&apos;s own and {whole(S.names_not_parties)} names that were not parties.</li>
                    <li><strong>Buyer and seller only where the story says.</strong> Where the words do not say who is on which side (partners, a joint venture), the names are listed as parties: {whole(S.roles_not_stated)} deals.</li>
                    <li><strong>Names and places are the story&apos;s own words.</strong> A party, an asset or a place the story&apos;s text does not hold is left blank; a state or a country is kept only when the story names it.</li>
                    <li><strong>The kind, the technology and the datacenter flag are the model&apos;s reading</strong> of the words, not a copy of them. In twenty deals read against their stories, one was not a power deal the story reported, no number was wrong, and four other fields were (a side, a kind, a datacenter flag, a status); the method note has the three samples.</li>
                    <li><strong>One deal, several reports.</strong> Stories about one event are read together. Deals from different events are shown once when the kind is the same, the dates are within 60 days, no figure differs, and the parties or a party and a figure match: {whole(S.folded)} were folded this way.</li>
                  </ul>
                </Fold>
                <Fold title={`What was read (${whole(S.stories_read)} of ${whole(S.stories_held)} stories)`}>
                  <p className="mb-2 max-w-3xl">Stories were read in this order, under a spending cap for the session; {whole(S.stories_remaining)} remain unread.</p>
                  <div className="overflow-x-auto">
                    <table className="w-full max-w-3xl border-collapse text-left text-sm" data-tiers="1">
                      <thead><tr className="border-b border-rule">{["Order", "Stories", "Read", "Remain"].map((h) => <th key={h} scope="col" className="px-3 py-1 font-semibold">{h}</th>)}</tr></thead>
                      <tbody>
                        {S.tiers.map((t) => (
                          <tr key={t.tier} className="border-b border-rule"><th scope="row" className="px-3 py-1 font-normal">{t.tier}. {t.words}</th><td className="px-3 py-1 tabular-nums">{whole(t.stories)}</td><td className="px-3 py-1 tabular-nums">{whole(t.read)}</td><td className="px-3 py-1 tabular-nums">{whole(t.remain)}</td></tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </Fold>
                <Fold title="What this does not tell you">
                  <ul className="max-w-3xl list-disc space-y-1.5 pl-5">
                    <li><strong>What a story says below its summary.</strong> Sizes, prices and terms are usually in the body of an article, and the ERW does not hold bodies. A blank here means the title and summary did not say, not that the deal has no price.</li>
                    <li><strong>What power sells for.</strong> Contract prices as sellers file them with FERC are on <Link href="/contracts" className="underline">the power contracts page</Link>.</li>
                    <li><strong>How many deals were struck.</strong> This is what a set of news feeds reported and a model read. Most contracts are never announced.</li>
                    <li><strong>A market total.</strong> The megawatts are a sum over the deals that state them, of every kind together: a purchase of output, the sale of a portfolio and an equipment order are different things.</li>
                    <li><strong>Whether a deal closed.</strong> The status is the one the story states, on the day of the story.</li>
                  </ul>
                </Fold>
              </div>
            </>
          )}
        </div>
      </div>
      <SourceLine tables={["power_deals"]} note={<>Read by <code className="font-mono">warehouse/deals/extract_v3.py</code> from the stories of <code className="font-mono">news_stories</code>, built {built}; the sentence each number was read from is outlet text and stays in the internal table <code className="font-mono">power_deals_evidence</code>. Method: <Link href="/data/methods/power_deals" className="underline">power deals</Link>. This page is in review.</>} />
    </ToolPage>
  );
}
