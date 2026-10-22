"use client";
// Session 700: the input box of the All grids tab (/cost-of-power?view=allgrids). Every input lives in the address: the
// load's profile (datacenter selected), its size and its load factor. Each shows its default in grey with its source on
// hover, is editable in place, and has a Reset named for its field (docs/brand.md, section 7). A profile sets three
// inputs, the load factor, the curtailment rule and whether the load is interruptible, and nothing else; choosing one
// puts its load factor back to the profile's default. The form is a plain GET form: it works without script.
import { useRouter } from "next/navigation";
import { CURTAIL_WORDS, PROFILES, PROFILE_ORDER, SITING_DEFAULTS, SITING_LIMITS, hasStrike, sitingHref, type ProfileId, type SitingInputs } from "@/lib/siting";

const field = "mt-1 block w-full max-w-full border border-rule bg-white px-2 py-1 text-sm text-ink";
const two = (v: number) => v.toFixed(2);

export function AllGridsForm({ x }: { x: SitingInputs }) {
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
        go({ mw: num("mw") ?? x.mw, lf: num("lf") ?? x.lf, ...(hasStrike(x.profile) ? { strike: st === null || st === "" ? null : num("strike") ?? x.strike } : {}) });
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

      <button type="submit" className="border border-accent bg-accent px-3 py-1 text-white" data-allgrids-show="1">Show</button>
    </form>
  );
}
