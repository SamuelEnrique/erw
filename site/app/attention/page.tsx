import type { Metadata } from "next";
import fs from "node:fs";
import path from "node:path";
import { feature } from "topojson-client";
import type { GeometryCollection, Topology } from "topojson-specification";
import statesTopo from "us-atlas/states-albers-10m.json";
import { Brand } from "@/components/Brand";
import { Cite } from "@/components/Cite";
import { Related } from "@/components/Related";
import { SiteLink } from "@/components/SiteLink";
import { TableDownloads } from "@/components/tool/TableDownloads";
import { AttentionView, type AttentionFile } from "./AttentionView";

// Session 3405 (chain 202): the Attention Index and the Friction Index, by week, sector and place. The page reads
// data/attention.json, written by warehouse/derived/attention_index.py from the three tables (attention_index_weekly,
// friction_index_weekly, attention_story_links) at the same run, and the stories of a week from
// public/attention/stories/<monday>.json when a reader opens them. Every number on the page is a value of those tables;
// the page computes none. It says what the coverage did, not what anyone should do (docs/methods/attention.md).
export const metadata: Metadata = { title: "Attention" };

const TABLES = ["attention_index_weekly", "friction_index_weekly", "attention_story_links"];

export default function AttentionPage() {
  const d = JSON.parse(fs.readFileSync(path.join(process.cwd(), "data", "attention.json"), "utf-8")) as AttentionFile;
  const topo = statesTopo as unknown as Topology<{ states: GeometryCollection }>;
  return (
    <Brand>
    <div data-attention="1">
      <h1 className="mb-1 text-3xl">Attention</h1>
      <p className="mb-2 max-w-3xl" data-attention-lead="1">
        What the energy news covered, week by week, by sector and by place: the <span className="cursor-help border-b border-dotted border-muted" title="The Attention Index: a sector's or a place's classified stories in a week as a percent of that week's judged stories (the stories classified plus the stories the news scorer gave significance 0, counted as not about energy).">Attention Index</span> says how much of a week&apos;s coverage a sector or a place got, and the{" "}
        <span className="cursor-help border-b border-dotted border-muted" title="The Friction Index: the share of a sector's or a place's stories in a week that report opposition: a moratorium or ban, a lawsuit, a protest, a permit denied, a fight over rates, political opposition.">Friction Index</span> says how much of that coverage reported opposition. Each story was read once by a model from its title and summary (sector, place, opposition, tone); the indices are counts of those readings.
        Every value opens the stories that make it. <SiteLink href="/data/methods/attention">Method, accuracy and limits</SiteLink>.
      </p>
      <AttentionView file={d} statesGeo={feature(topo, topo.objects.states)} />
      <Cite tables={TABLES} note="The classification is a model's reading of each story's title and summary (model-extracted); the indices are counted by code from those rows. The page says what the coverage did, not why." />
      <TableDownloads tables={TABLES} />
      <Related href="/attention" />
    </div>
    </Brand>
  );
}
