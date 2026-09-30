import type { Metadata } from "next";
import Link from "next/link";
import { Cite } from "@/components/Cite";
import { Section } from "@/components/Section";

// Session 36B: the Historical Event Analyzer's index (session 36C: two events); each has its own page, drawn from
// event_window_daily (docs/methods/events.md).
export const metadata: Metadata = { title: "Events" };

const EVENTS = [
  {
    href: "/events/uri-2021",
    title: "Winter Storm Uri: ERCOT, February 2021",
    line: "Prices, demand served, net generation and carbon intensity over 2021-02-07 to 2021-02-24, against the same days of 2019 and 2020.",
  },
  {
    href: "/events/covid-2020",
    title: "COVID-19: demand in the seven ISO grids, spring 2020",
    line: "Demand served in CAISO, ERCOT, ISO-NE, MISO, NYISO, PJM, SPP and the lower 48, 2020-03-01 to 2020-05-31, against the same weekday of 2019.",
  },
];

export default function Events() {
  return (
    <>
      <h1 className="mb-1 text-3xl">Events</h1>
      <p className="mb-5 max-w-3xl text-sm text-muted">
        What happened to a grid during a major event, day by day, set against the same days of earlier years. Every figure is read from the
        warehouse&apos;s table event_window_daily. <Link href="/data/methods/events">Method</Link>.
      </p>
      <Section title="Events in the warehouse">
        <ul className="space-y-2">
          {EVENTS.map((e) => (
            <li key={e.href}>
              <Link href={e.href} className="text-lg">{e.title}</Link>
              <div className="text-sm text-muted">{e.line}</div>
            </li>
          ))}
        </ul>
        <Cite tables={["event_window_daily"]} />
      </Section>
    </>
  );
}
