import type { Metadata } from "next";
import { Brand } from "@/components/Brand";
import { AutoSubmitSelect } from "@/components/AutoSubmit";
import { Hint } from "@/components/demand/Hint";
import { HeadlineNumber, HeadlineRow, SourceLine, ToolHeader, ToolPage, ToolSection, ToolTable } from "@/components/tool/ToolPage";
import { TableDownloads } from "@/components/tool/TableDownloads";
import { ORDERS, figure, measures, ordered, publishers, readAiFile, type AiFile, type Order } from "@/lib/aienergy";
import raw from "@/data/ai_energy.json";
import { AiEnergyDecisions } from "./Decisions";

// Session 8012 (chain 505, part B2): "Energy per AI query, as published". Every figure a model maker, a cloud operator
// or a peer-reviewed paper printed for the energy of a query, a token, a training run or a fleet, as its publisher
// printed it: the publication's own words, its date and what the figure measures, sortable by publisher and by what is
// measured. The page reads data/ai_energy.json (warehouse/derived/ai_energy_page.py, from the table
// ai_energy_published, whose rows a session read from each publication's saved copy; method
// docs/methods/ai_energy_published.md). No figure of the ERW's own: nothing averaged or summed across publishers, no
// unit converted, no ranking of companies. In review (no line in lib/release.ts); in no menu (chain 505).
export const metadata: Metadata = { title: "Energy per AI query, as published", robots: { index: false, follow: false } };
export const dynamic = "force-dynamic";

const F = readAiFile(raw) as AiFile;

type Query = Record<string, string | string[] | undefined>;
const one = (q: Query, k: string) => (typeof q[k] === "string" ? (q[k] as string) : undefined);
const dateWords = (d: string) => new Date(`${d}T00:00:00Z`).toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric", timeZone: "UTC" });

export default async function AiEnergyPage({ searchParams }: { searchParams: Promise<Query> }) {
  const q = await searchParams;
  const orderKeys = ORDERS.map((o) => o.value) as readonly string[];
  const order = (orderKeys.includes(one(q, "sort") ?? "") ? one(q, "sort") : "publisher") as Order;
  const all = measures(F.rows);
  const m = one(q, "m");
  const measure = m && all.includes(m) ? m : "all";
  const rows = ordered(measure === "all" ? F.rows : F.rows.filter((r) => r.x_measures === measure), order);
  const pubs = new Set(F.rows.map((r) => r.x_title)).size;
  const peer = new Set(F.rows.filter((r) => r.x_publisher_kind === "peer-reviewed paper").map((r) => r.x_title)).size;
  const newest = [...F.rows].sort((a, b) => b.event_date.localeCompare(a.event_date))[0];

  return (
    <Brand>
    <ToolPage>
      <div data-ai-energy="1">
      <ToolHeader
        title="Energy per AI query, as published"
        lead={<>Every figure a model maker, a cloud operator or a peer-reviewed paper has printed for the energy of an AI query, a token, a training run or a fleet, in the publication&apos;s own words, with its date and{" "}
          <Hint words="what it measures" why="Each publication measures something different: one prompt, a thousand inferences, a training run, a deployment, a year of a fleet. The figures are not comparable with one another, and the page sets none against another." />.{" "}
          <Hint words="Nothing here is the ERW's own" why="No figure is averaged, summed, converted to another unit or ranked. Each is the number the publication printed, read by a session from the publication's saved copy." />.</>}
        under={<p className="mt-2 text-xs text-muted" data-license-line="1">License: {F.license}. File built {F.built.slice(0, 10)}.</p>}
      />

      <HeadlineRow>
        <HeadlineNumber label="Figures" value={<span data-fig="h-figures">{F.rows.length}</span>} note="each a number a publication printed" />
        <HeadlineNumber label="Publications" value={<span data-fig="h-publications">{pubs}</span>} note={`${peer} of them peer-reviewed papers`} />
        <HeadlineNumber label="Newest" value={<span className="text-2xl" data-fig="h-newest">{dateWords(newest.event_date)}</span>} note={`${newest.parties}: ${newest.x_title}`} />
      </HeadlineRow>

      <ToolSection title="Every figure, as printed" id="figures">
        <form method="get" action="/ai-energy#figures" className="mb-3 flex flex-wrap items-end gap-3 text-sm [&_label]:max-w-full [&_select]:max-w-full" data-ai-form="1">
          <AutoSubmitSelect name="sort" value={order} options={ORDERS.map((o) => ({ value: o.value, label: o.label }))} label="Order" />
          <AutoSubmitSelect name="m" value={measure} options={[{ value: "all", label: "Every measure" }, ...all.map((x) => ({ value: x, label: x }))]} label="What is measured" />
          <button type="submit" className="border border-rule bg-white px-3 py-1 text-sm">Show</button>
          <Hint words="The order shown first" why="By publisher, A to Z, then by date: the page's own choice. No order by the figure's size is offered, so no company is ranked." />
        </form>
        <ToolTable
          words
          minWidth={1100}
          caption="Every published figure of the energy of AI, as printed"
          head={["Publisher", "Publication", "What it measures", "Of what", "Figure", "The publication's words"]}
          rows={rows.map((r) => ({ key: r.event_id, cells: [
            <span key="p" data-ai-row={r.event_id}>{r.parties}<span className="block text-xs text-muted">{r.x_publisher_kind}</span></span>,
            <span key="t"><a href={r.source_url} rel="noopener noreferrer">{r.x_title}</a><span className="block text-xs text-muted">{dateWords(r.event_date)}{r.x_authors ? `; ${r.x_authors}` : ""}</span></span>,
            <span key="m" className="cursor-help" title={`Period: ${r.x_period}. Peer-reviewed: ${r.x_peer_reviewed}.`}>{r.x_measures}</span>,
            r.x_subject,
            <span key="v" className="cursor-help whitespace-nowrap tabular-nums" data-fig={`v-${r.event_id}`} title={`Basis: ${r.x_basis}. Source: ${r.x_title} (${r.source_url}), page ${r.x_page}, as saved on ${r.x_retrieved_at.slice(0, 10)} (sha256 ${r.x_sha256.slice(0, 12)}).`}>{figure(r.x_value)} {r.x_unit}</span>,
            <span key="w" className="cursor-help" title={`Page ${r.x_page} of the publication, as saved; the ERW cut these words from its saved copy.`}>&ldquo;{r.x_printed}&rdquo;<span className="text-xs text-muted"> (p. {r.x_page})</span></span>,
          ] }))}
        />
      </ToolSection>

      <ToolSection title="The publishers" id="publishers">
        <ul className="max-w-3xl list-disc space-y-1 pl-5 text-sm" data-ai-publishers={publishers(F.rows).length}>
          {publishers(F.rows).map((p) => {
            const mine = F.rows.filter((r) => r.parties === p);
            return <li key={p}>{p}: {mine.length} figure{mine.length === 1 ? "" : "s"} in {new Set(mine.map((r) => r.x_title)).size} publication{new Set(mine.map((r) => r.x_title)).size === 1 ? "" : "s"} ({[...new Set(mine.map((r) => r.event_date.slice(0, 4)))].join(", ")})</li>;
          })}
        </ul>
      </ToolSection>

      <AiEnergyDecisions />
      <TableDownloads tables={[F.table]} />
      <SourceLine tables={[F.table]} note={<>Method: <a href="/data/methods/ai_energy_published">the table&apos;s method note</a>. Each publication remains its publisher&apos;s; the page quotes the figures with their sources.</>} />
      </div>
    </ToolPage>
    </Brand>
  );
}
