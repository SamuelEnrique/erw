"use client";
// Session 700: the input box of the All grids tab (/cost-of-power?view=allgrids). Every input lives in the address: the
// load's profile (datacenter selected), its size and its load factor. Each shows its default in grey with its source on
// hover, is editable in place, and has a Reset named for its field (docs/brand.md, section 7). A profile sets three
// inputs, the load factor, the curtailment rule and whether the load is interruptible, and nothing else; choosing one
// puts its load factor back to the profile's default. The form is a plain GET form: it works without script.
import { useRouter } from "next/navigation";
import { COLUMNS, CURTAIL_WORDS, GRID_NAMES, GRID_ORDER, PROFILES, PROFILE_ORDER, SITING_DEFAULTS, SITING_LIMITS, SORT_WORDS, hasStrike, sitingHref, type ColumnId, type ProfileId, type SitingInputs } from "@/lib/siting";

const field = "mt-1 block w-full max-w-full border border-rule bg-white px-2 py-1 text-sm text-ink";
const two = (v: number) => v.toFixed(2);

// Session 710: the screen's inputs in the same box: the sort, the filters (grid, kind, an energy band, only rows whose
// every cost part is held) and the two rows set side by side as A and B, each folded under its own heading.
export function AllGridsForm({ x, rows }: { x: SitingInputs; rows: { id: string; label: string }[] }) {
  const router = useRouter();
  const p = PROFILES[x.profile];
  const go = (change: Partial<SitingInputs>) => router.push(sitingHref(x, change), { scroll: false });
  const reset = (name: string, label: string, change: Partial<SitingInputs>) => (
    <button type="button" data-reset={name} aria-label={`Reset ${label}`} onClick={() => go(change)} className="mt-1 border border-rule px-1.5 py-px text-xs">Reset {label}</button>
  );
  const fixedLf = p.lfRange[0] === p.lfRange[1];
  return (
    <form method="get" action="/cost-of-power" className="space-y-4 text-sm" data-allgrids-form="1"
      onSubmit={(e) => {
        e.preventDefault();
        const f = new FormData(e.currentTarget);
        const num = (k: string) => { const v = Number(f.get(k)); return Number.isFinite(v) ? v : undefined; };
        const st = f.get("strike");
        const str = (k: string) => { const v = f.get(k); return typeof v === "string" ? v : ""; };
        const lo = str("lo"), hi = str("hi");
        go({ mw: num("mw") ?? x.mw, lf: num("lf") ?? x.lf, ...(hasStrike(x.profile) ? { strike: st === null || st === "" ? null : num("strike") ?? x.strike } : {}),
          sort: (str("sort") || "name") as SitingInputs["sort"], dir: str("dir") === "asc" ? "asc" : "desc", grids: f.getAll("grid").filter((g): g is string => typeof g === "string"),
          kind: (str("kind") || "all") as SitingInputs["kind"], band: lo !== "" && hi !== "" && Number.isFinite(Number(lo)) && Number.isFinite(Number(hi)) ? [Number(lo), Number(hi)] : null,
          held: f.get("held") === "1", a: str("a") || null, b: str("b") || null });
      }}>
      <input type="hidden" name="view" value="allgrids" />
      <label className="block">
        <span className="font-semibold">Profile</span>
        <select name="profile" value={x.profile} onChange={(e) => go({ profile: e.target.value as ProfileId })} className={field} data-allgrids-profile="1">
          {PROFILE_ORDER.map((id) => <option key={id} value={id}>{PROFILES[id].label}</option>)}
        </select>
        <span className="mt-1 block text-xs leading-snug text-muted" data-default="profile">
          Default: Datacenter. This one: load factor {two(p.lf)}, {CURTAIL_WORDS[p.curtail]}, {p.interruptible ? "interruptible" : "not interruptible"}.
        </span>
      </label>
      {x.profile !== SITING_DEFAULTS.profile ? reset("profile", "profile", { profile: SITING_DEFAULTS.profile }) : null}

      <label className="block">
        <span className="font-semibold">Size, MW</span>
        <input name="mw" type="number" min={SITING_LIMITS.mw[0]} max={SITING_LIMITS.mw[1]} step="any" defaultValue={x.mw} key={`mw${x.mw}`} className={field} data-allgrids-mw="1" />
        <span className="mt-1 block text-xs leading-snug text-muted" data-default="mw" title="The size &quot;Your load&quot; opens on (lib/datacenter.ts, DEFAULTS.mw)">Default {SITING_DEFAULTS.mw} MW</span>
      </label>
      {x.mw !== SITING_DEFAULTS.mw ? reset("mw", "size", { mw: SITING_DEFAULTS.mw }) : null}

      <label className="block">
        <span className="font-semibold">Load factor</span>
        <input name="lf" type="number" min={p.lfRange[0]} max={p.lfRange[1]} step="0.01" defaultValue={x.lf} key={`lf${x.profile}${x.lf}`} readOnly={fixedLf} className={field} data-allgrids-lf="1"
          aria-describedby="allgrids-lf-default" />
        <span id="allgrids-lf-default" className="mt-1 block text-xs leading-snug text-muted" data-default="lf" title={p.source.lf}>
          Default {two(p.lf)}{fixedLf ? ", set by the profile" : `, from ${two(p.lfRange[0])} to ${two(p.lfRange[1])}`}
        </span>
      </label>
      {x.lf !== p.lf ? reset("lf", "load factor", { lf: p.lf }) : null}

      {/* session 702: the strike, for the two profiles whose rule has one */}
      {hasStrike(x.profile) ? (
        <label className="block">
          <span className="font-semibold">Strike, USD per MWh</span>
          <input name="strike" type="number" min={SITING_LIMITS.strike[0]} max={SITING_LIMITS.strike[1]} step="any" defaultValue={x.strike ?? ""} key={`st${x.profile}${x.strike}`}
            placeholder={p.strike === null ? "each row's own" : undefined} className={field} data-allgrids-strike="1" aria-describedby="allgrids-strike-default" />
          <span id="allgrids-strike-default" className="mt-1 block text-xs leading-snug text-muted" data-default="strike" title={p.source.strike}>
            Default {p.strike === null ? `each row's own price at the load factor (empty field)` : `${p.strike.toLocaleString("en-US")}`}
          </span>
        </label>
      ) : null}
      {hasStrike(x.profile) && x.strike !== p.strike ? reset("strike", "strike", { strike: p.strike }) : null}

      <details className="border-t border-rule pt-3" open={x.sort !== "name" || x.grids.length > 0 || x.kind !== "all" || !!x.band || x.held} data-allgrids-screen="1">
        <summary className="cursor-pointer font-semibold">Sort and filter</summary>
        <label className="mt-2 block"><span className="text-sm">Sort by</span>
          <select name="sort" defaultValue={x.sort} key={`s${x.sort}`} className={field} data-allgrids-sort="1">
            <option value="name">{SORT_WORDS.name}</option>
            {COLUMNS.map((c) => <option key={c.id} value={c.id}>{SORT_WORDS[c.id as ColumnId]}</option>)}
          </select>
        </label>
        <label className="mt-2 block"><span className="text-sm">Order</span>
          <select name="dir" defaultValue={x.dir} key={`d${x.dir}`} className={field} data-allgrids-dir="1">
            <option value="desc">largest first</option><option value="asc">smallest first</option>
          </select>
          <span className="mt-1 block text-xs text-muted" data-default="sort">Default: by grid, then name (A to Z)</span>
        </label>
        <fieldset className="mt-2"><legend className="text-sm">Grids shown</legend>
          <span className="mt-1 grid grid-cols-2 gap-x-2 text-sm">
            {GRID_ORDER.map((g) => <label key={g} className="flex items-center gap-1"><input type="checkbox" name="grid" value={g} defaultChecked={x.grids.includes(g)} key={`g${g}${x.grids.join()}`} />{GRID_NAMES[g]}</label>)}
          </span>
          <span className="mt-1 block text-xs text-muted" data-default="grid">Default: none ticked, every grid</span>
        </fieldset>
        <label className="mt-2 block"><span className="text-sm">Kind</span>
          <select name="kind" defaultValue={x.kind} key={`k${x.kind}`} className={field} data-allgrids-kind="1">
            <option value="all">load zones and hubs</option><option value="zone">load zones only</option><option value="hub">hubs only</option>
          </select>
        </label>
        <span className="mt-2 block text-sm">Energy band, USD per MWh</span>
        <span className="flex gap-2">
          <input name="lo" type="number" step="any" defaultValue={x.band?.[0] ?? ""} key={`lo${x.band?.[0]}`} placeholder="from" aria-label="Energy band from, USD per MWh" className={field} data-allgrids-lo="1" />
          <input name="hi" type="number" step="any" defaultValue={x.band?.[1] ?? ""} key={`hi${x.band?.[1]}`} placeholder="to" aria-label="Energy band to, USD per MWh" className={field} data-allgrids-hi="1" />
        </span>
        <label className="mt-2 flex items-center gap-2 text-sm"><input type="checkbox" name="held" value="1" defaultChecked={x.held} key={`h${x.held}`} data-allgrids-held="1" />Only rows whose every cost part is held</label>
        {x.sort !== "name" || x.grids.length || x.kind !== "all" || x.band || x.held ? reset("screen", "sort and filters", { sort: "name", dir: "asc", grids: [], kind: "all", band: null, held: false }) : null}
      </details>

      <details className="border-t border-rule pt-3" open={!!(x.a || x.b)} data-allgrids-ab="1">
        <summary className="cursor-pointer font-semibold">A and B, side by side</summary>
        {(["a", "b"] as const).map((k) => (
          <label key={k} className="mt-2 block"><span className="text-sm">{k.toUpperCase()}</span>
            <select name={k} defaultValue={x[k] ?? ""} key={`${k}${x[k]}`} className={field} data-allgrids-pick={k}>
              <option value="">none</option>
              {rows.map((r) => <option key={r.id} value={r.id}>{r.label}</option>)}
            </select>
          </label>
        ))}
        {x.a || x.b ? reset("ab", "A and B", { a: null, b: null }) : null}
      </details>

      <button type="submit" className="border border-accent bg-accent px-3 py-1 text-white" data-allgrids-show="1">Show</button>
    </form>
  );
}
