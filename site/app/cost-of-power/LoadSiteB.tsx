"use client";
// Session 236 (the owner's chain prompt of 12 October 2026: scenarios A and B compare two sites or two contracts): the
// one control that gives scenario B a site of its own on /cost-of-power, a zone or hub of any grid the page holds. The
// site lives in the address (`bsite=<grid>:<region>`, lib/datacenter/finance.ts SITE_B), because B's prices are the
// server's to read: the choice opens the same address with that parameter, and the server hands the block B's two ways
// of running at that site (model.ts, facts.b). A plain GET form, so it works without JavaScript (the hidden fields
// carry the rest of the address as the server read it); with JavaScript the address in the browser is opened in place,
// so the assumptions typed since the page loaded are kept. Nothing typed is sent: the choice is a site's name.
import { useRouter } from "next/navigation";
import { SITE_B } from "@/lib/datacenter/finance";

const field = "w-full border border-rule bg-white px-2 py-1 text-sm";

export type SitesB = { grid: string; name: string; regions: { id: string; kind: string | null }[] }[];

export function LoadSiteB({ sites, current, asked, aPlace, keep }: {
  sites: SitesB;
  /** B's site in force ("" when B is at A's), what the address asked for, A's site in words, and the rest of the address */
  current: string; asked: string; aPlace: string; keep: [string, string][];
}) {
  const router = useRouter();
  const go = (v: string) => {
    const q = new URLSearchParams(window.location.search);
    if (v) q.set(SITE_B, v); else q.delete(SITE_B);
    const qs = q.toString();
    router.push(`/cost-of-power${qs ? `?${qs}` : ""}#scenarios`, { scroll: false });
  };
  return (
    <form method="get" action="/cost-of-power" className="mb-4 flex flex-wrap items-end gap-3 text-sm" data-site-b-form="1"
      onSubmit={(e) => { e.preventDefault(); go(String(new FormData(e.currentTarget).get(SITE_B) ?? "")); }}>
      {keep.map(([n, v]) => <input key={n} type="hidden" name={n} value={v} />)}
      <label className="block min-w-0 grow sm:max-w-md"><span className="mb-1 block font-semibold">Scenario B&apos;s site</span>
        <select key={current} name={SITE_B} defaultValue={current} className={field} data-site-b={current}>
          <option value="">The same site as A: {aPlace}</option>
          {sites.map((g) => (
            <optgroup key={g.grid} label={g.name}>
              {g.regions.map((r) => <option key={r.id} value={`${g.grid}:${r.id}`}>{r.id}{r.kind === "zone" ? " (load zone)" : r.kind === "hub" ? " (hub)" : ""}, {g.name}</option>)}
            </optgroup>
          ))}
        </select>
      </label>
      <button type="submit" className="border border-accent bg-accent px-4 py-1.5 text-white">Set B&apos;s site</button>
      {asked && asked !== current ? <p className="basis-full text-xs text-muted" role="status" data-site-b-refused="1">The site the address names for B is not held, or is A&apos;s own: B stays at A&apos;s site.</p> : null}
    </form>
  );
}
