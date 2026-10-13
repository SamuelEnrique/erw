"use client";
// Session 238: the findings library of /research. One card a screen (the class screen-card of app/tokens.css gives a
// card the height of the window), an index of every card by title beside it (above it on a narrow screen), and two
// filters, by grid and by topic. The index marks the card in view and a click goes to it. The filters are kept in the
// address (?grid=ercot&topic=batteries), so a filtered view can be linked; a card's grids and topics are computed on
// the server from the card's own data (lib/research.ts) and arrive here as words. The cards themselves are drawn on
// the server and passed in whole: nothing a card says is computed or changed here, and a card the filter leaves out
// stays in the page's markup, hidden.
import { useEffect, useMemo, useState, type ReactNode } from "react";

export type LibraryItem = { id: string; title: string; grids: string[]; topics: string[]; node: ReactNode };
export type Choice = { id: string; label: string };

const read = (key: string, among: Choice[]) => {
  const v = new URLSearchParams(window.location.search).get(key);
  return v && among.some((c) => c.id === v) ? v : "";
};

export function Library({ items, grids, topics }: { items: LibraryItem[]; grids: Choice[]; topics: Choice[] }) {
  const [grid, setGrid] = useState("");
  const [topic, setTopic] = useState("");
  const [inView, setInView] = useState(items[0]?.id ?? "");
  useEffect(() => {
    const t = setTimeout(() => {     // the address is read after the mount, so that the first paint is the page as it was built
      setGrid(read("grid", grids));
      setTopic(read("topic", topics));
    }, 0);
    return () => clearTimeout(t);
  }, [grids, topics]);
  const shown = useMemo(() => items.filter((i) => (!grid || i.grids.includes(grid)) && (!topic || i.topics.includes(topic))), [items, grid, topic]);
  const shownIds = shown.map((i) => i.id).join(",");
  useEffect(() => {
    const ids = shownIds ? shownIds.split(",") : [];
    const els = ids.map((id) => document.getElementById(`card-${id}`)).filter((e): e is HTMLElement => Boolean(e));
    if (!els.length || typeof IntersectionObserver === "undefined") return;
    // the card in view: the one that crosses the line a third of the way down the window
    const io = new IntersectionObserver((entries) => {
      for (const e of entries) if (e.isIntersecting) setInView((e.target as HTMLElement).dataset.libraryCard ?? "");
    }, { rootMargin: "-33% 0px -66% 0px" });
    els.forEach((e) => io.observe(e));
    return () => io.disconnect();
  }, [shownIds]);
  const pick = (key: "grid" | "topic", v: string) => {
    if (key === "grid") setGrid(v); else setTopic(v);
    const u = new URL(window.location.href);
    if (v) u.searchParams.set(key, v); else u.searchParams.delete(key);
    window.history.replaceState(null, "", u.toString());
  };
  const count = (key: "grid" | "topic", id: string) => items.filter((i) => (key === "grid" ? i.grids : i.topics).includes(id)).length;
  const marked = shown.some((i) => i.id === inView) ? inView : shown[0]?.id ?? "";
  const row = (key: "grid" | "topic", label: string, among: Choice[], value: string) => (
    <div className="filter-row" role="group" aria-label={`Findings by ${label}`} data-library-filter={key} data-library-value={value || "all"}>
      <span className="filter-label">By {label}</span>
      <button type="button" aria-pressed={value === ""} onClick={() => pick(key, "")} data-library-pick={`${key}:all`}>All</button>
      {among.map((c) => (
        <button key={c.id} type="button" aria-pressed={value === c.id} onClick={() => pick(key, c.id)} data-library-pick={`${key}:${c.id}`}>
          {c.label} <span className="filter-count">{count(key, c.id)}</span>
        </button>
      ))}
    </div>
  );
  return (
    <div data-library="1" data-library-shown={shown.length} data-finding-cards={items.length}>
      {row("grid", "grid", grids, grid)}
      {row("topic", "topic", topics, topic)}
      <div className="with-index">
        <nav className="index-side" aria-label="Card index" data-library-index={shown.length}>
          <p className="index-title">Card index, {shown.length} of {items.length}</p>
          <ol className="index-list">
            {shown.map((i) => (
              <li key={i.id}>
                <a href={`#card-${i.id}`} aria-current={marked === i.id ? "true" : undefined} data-library-link={i.id}>{i.title}</a>
              </li>
            ))}
          </ol>
          {shown.length === 0 ? <p className="index-none" data-library-none="1">No card is filed under both. Choose All in one of the two rows.</p> : null}
        </nav>
        <div className="index-main">
        {items.map((i) => (
          <section key={i.id} id={`card-${i.id}`} className="screen-card" hidden={!shown.includes(i)} data-library-card={i.id} data-grids={i.grids.join(" ")} data-topics={i.topics.join(" ")}>
            {i.node}
          </section>
        ))}
        </div>
      </div>
    </div>
  );
}
