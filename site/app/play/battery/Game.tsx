"use client";
// Session 38: the home battery game. One canvas for the prices, plain React for the rest; mouse, touch and keys.
// The prices are real (ERCOT HB_HUBAVG, every 15-minute interval of one operating day); the battery, the home, the
// brand and the fleet are fictional and say so. Each interval's action is the control held for most of its time.
// Session 50 (v2): the battery's settings and a difficulty (lib/battery.ts), a 30-second first-run tutorial, a
// house-and-battery animation, Easy's forecast band, a 15-minute notice before the fleet call, the replay of the
// perfect battery beside the player's with a reason at each switch, and the leaderboard by preset.
// Session 63 (v3): every play starts with $5 and ends when the money falls below $0; on Hard a grid emergency (the price
// climbs toward the cap, then a two-hour outage runs the house on the battery; lights out ends the round); the state is
// computed with simulate(), the server's own scorer, so the two cannot differ; and a simple mode (the default page): one
// sentence, two big buttons, the battery and the price, with everything else behind "more".
import { SiteLink as Link } from "@/components/SiteLink";  // session 67: every link passes the release gate
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  DEFAULT_SETTINGS, DIFFICULTIES, EMERGENCY, emergencyOf, eventPageFor, explain, FLEET, isPerfect, optimum, perfectShare, presetLabel, presetOf, rulesOf, SETTINGS,
  simulate, START_MONEY, validSettings, vppHour, type Action, type Difficulty, type Rules, type Settings,
} from "@/lib/battery";
import type { PresetCount, ScoreRow } from "@/lib/game";

// session 56: a level names its grid and its operating day's time zone (the California days are Pacific), and the
// California days their selection rule
export type GameLevel = { slug: string; date: string; title: string; why: string; ts_utc: string[]; price: number[]; grid: "ERCOT" | "CAISO"; tz: string; rule?: string };

const DURATION_MS = 90_000;
const HHMM = new Map<string, Intl.DateTimeFormat>();
/** An interval's local clock time in the level's time zone, HH:MM. */
const clock = (tz: string, ts: string) => {
  if (!HHMM.has(tz)) HHMM.set(tz, new Intl.DateTimeFormat("en-US", { timeZone: tz, hour: "2-digit", minute: "2-digit", hourCycle: "h23" }));
  return HHMM.get(tz)!.format(new Date(ts));
};
/** Session 56: what the game says about each grid's prices. */
const GRIDS: Record<GameLevel["grid"], { name: string; hub: string; prices: string; href: string; page: string; zone: string }> = {
  ERCOT: { name: "ERCOT (Texas)", hub: "ERCOT's hub average (HB_HUBAVG)", prices: "ERCOT real-time, hub average (HB_HUBAVG)", href: "/grid/ercot", page: "ERCOT's grid page", zone: "Central" },
  CAISO: { name: "CAISO SP15 (Southern California)", hub: "CAISO's SP15 trading hub (TH_SP15_GEN-APND)", prices: "CAISO SP15 real-time (TH_SP15_GEN-APND), 15-minute means of its 5-minute prices", href: "/grid/caiso", page: "CAISO's grid page", zone: "Pacific" },
};
const usd = (v: number) => `${v < 0 ? "-" : ""}$${Math.abs(v).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
const css = (name: string) => (typeof window === "undefined" ? "#6B665E" : getComputedStyle(document.documentElement).getPropertyValue(`--color-${name}`).trim() || "#6B665E");
const TUTORIAL_KEY = "erw.battery.tutorial.v2";
const SETTINGS_KEY = "erw.battery.settings.v2";

type Phase = "pick" | "play" | "done";
type Control = 1 | 0 | -1;

/** Runs of one action in a list of intervals, as "HH:MM to HH:MM" (the end is the last interval's end). */
function runs(actions: Action[], ts: string[], which: Action, tz: string): string[] {
  const out: string[] = [];
  let i = 0;
  while (i < actions.length) {
    if (actions[i] !== which) { i++; continue; }
    let j = i;
    while (j + 1 < actions.length && actions[j + 1] === which) j++;
    const end = new Date(Date.parse(ts[j]) + 15 * 60_000).toISOString();
    out.push(`${clock(tz, ts[i])} to ${clock(tz, end)}`);
    i = j + 1;
  }
  return out;
}

function list(xs: string[]): string {
  if (xs.length <= 1) return xs[0] ?? "";
  const shown = xs.slice(0, 4);
  const more = xs.length > 4 ? `, and ${xs.length - 4} more` : "";
  return `${shown.slice(0, -1).join(", ")}${shown.length > 1 ? " and " : ""}${shown.at(-1)}${more}`;
}

/** Browser storage, for this viewer's conveniences only (the tutorial seen, the last settings): it may be absent or
 * refuse, and the game works without it. */
function load(key: string): string | null {
  try { return window.localStorage.getItem(key); } catch { return null; }
}
function save(key: string, v: string) {
  try { window.localStorage.setItem(key, v); } catch { /* private window or blocked storage: nothing to keep */ }
}

/** Session 46: a share card drawn on a canvas in this page and saved from it: nothing is uploaded. */
function ShareCard({ level, score, optimal, preset }: { level: GameLevel; score: number; optimal: number; preset: string }) {
  const [png, setPng] = useState("");
  const [copied, setCopied] = useState("");
  const share = perfectShare(score, optimal);
  const lines = [
    `${level.title}, ${level.date}`,
    `I earned ${usd(score)} with one home battery${share !== null ? `: ${Math.round(share)} percent of perfect foresight (${usd(optimal)})` : ""}.`,
    `My fleet of ${FLEET.toLocaleString("en-US")} homes: ${usd(score * FLEET)}.`,
  ];
  const text = () => `${lines.join(" ")} ${presetLabel(preset)}. Real ${GRIDS[level.grid].prices} prices; the battery and the fleet are fictional. ${window.location.origin}/play/battery`;
  const make = () => {
    const cv = document.createElement("canvas");
    cv.width = 1200; cv.height = 630;
    const ctx = cv.getContext("2d")!;
    ctx.fillStyle = css("paper"); ctx.fillRect(0, 0, 1200, 630);
    ctx.fillStyle = css("accent"); ctx.fillRect(0, 0, 1200, 14);
    ctx.fillStyle = css("muted"); ctx.font = "28px system-ui, sans-serif";
    ctx.fillText("The home battery game, Energy Research Warehouse (ERW)", 60, 90);
    ctx.fillStyle = css("ink"); ctx.font = "bold 44px system-ui, sans-serif";
    ctx.fillText(lines[0], 60, 170);
    ctx.fillStyle = css("accent"); ctx.font = "bold 96px system-ui, sans-serif";
    ctx.fillText(usd(score), 60, 300);
    ctx.fillStyle = css("ink"); ctx.font = "36px system-ui, sans-serif";
    if (share !== null) ctx.fillText(`${Math.round(share)} percent of perfect foresight (${usd(optimal)})`, 60, 370);
    ctx.fillText(`A fleet of ${FLEET.toLocaleString("en-US")} homes: ${usd(score * FLEET)}`, 60, 425);
    ctx.fillStyle = css("muted"); ctx.font = "24px system-ui, sans-serif";
    ctx.fillText(presetLabel(preset), 60, 480);
    ctx.fillText(`Real prices: ${level.grid === "CAISO" ? "CAISO SP15 real-time" : "ERCOT real-time, hub average (HB_HUBAVG)"}, every 15 minutes of the day.`, 60, 520);
    ctx.fillText(`The battery, home and fleet are fictional. ${window.location.host}/play/battery`, 60, 560);
    setPng(cv.toDataURL("image/png"));
  };
  return (
    <div className="mt-3 border-t border-rule pt-2 text-sm">
      <div className="flex flex-wrap items-center gap-2">
        <button onClick={make} className="border border-rule px-3 py-1">Make a share card</button>
        <button onClick={() => { navigator.clipboard?.writeText(text()).then(() => setCopied("Copied."), () => setCopied("Could not copy.")); }} className="border border-rule px-3 py-1">Copy the text</button>
        {png ? <a href={png} download={`erw-battery-${level.date}.png`} className="border border-accent px-3 py-1 text-accent no-underline">Save the card (PNG)</a> : null}
        <span className="text-xs text-muted">{copied || "Drawn in this page and saved from it; nothing is uploaded."}</span>
      </div>
      {/* a data: URL drawn in this page; next/image would add nothing here */}
      {/* eslint-disable-next-line @next/next/no-img-element */}
      {png ? <img src={png} alt={lines.join(" ")} className="mt-2 w-full max-w-xl border border-rule" /> : null}
    </div>
  );
}

/** Session 50: the 30-second first-run tutorial, four cards of about 7.5 seconds; skippable, remembered. */
const STEPS = [
  "A real day of wholesale prices, Texas's (ERCOT) or California's (CAISO), scrolls past in about 90 seconds, fifteen minutes at a time. You see the past; on Easy, the next three hours show as a band.",
  "Hold Charge to buy power into your battery when it is cheap; hold Sell to discharge it when it is dear. Let go to idle. Keys: C and S, or the arrows.",
  "Once a day the fleet is called for the day's dearest hour, with a 15-minute warning. Energy you deliver in that hour earns a bonus: a game rule, modeled on ERCOT's ADER pilot.",
  "On Hard the battery keeps a backup reserve, and every kWh you discharge wears it (a cost). After the day, replay the perfect battery's day beside yours.",
];
function Tutorial({ onDone }: { onDone: () => void }) {
  const [k, setK] = useState(0);
  useEffect(() => {
    const t = setTimeout(() => (k + 1 < STEPS.length ? setK(k + 1) : onDone()), 7500);
    return () => clearTimeout(t);
  }, [k, onDone]);
  return (
    <div className="mb-3 border border-accent bg-panel p-3 text-sm" role="dialog" aria-label="How to play, in 30 seconds">
      <div className="mb-1 flex items-center justify-between text-xs text-muted">
        <span>How to play: {k + 1} of {STEPS.length}</span>
        <button onClick={onDone} className="border border-rule px-2 py-0.5">Skip</button>
      </div>
      <p className="mb-2 min-h-[3.5rem]">{STEPS[k]}</p>
      <div className="flex items-center gap-2">
        <div className="h-1 flex-1 bg-[var(--color-rule)]"><div className="h-1 bg-accent" style={{ width: `${((k + 1) / STEPS.length) * 100}%` }} /></div>
        <button onClick={() => (k + 1 < STEPS.length ? setK(k + 1) : onDone())} className="border border-accent px-2 py-0.5 text-accent">{k + 1 < STEPS.length ? "Next" : "Play"}</button>
      </div>
    </div>
  );
}

/** Session 50: the house and its battery. Charge flows in from the grid along the wire; discharge flows out to it; the
 * battery shows its charge and, on Hard, the reserve line. Motion stops for readers who ask for less. */
function HouseFlow({ flow, soc, kwh, reserveKwh, blocked }: { flow: Action; soc: number; kwh: number; reserveKwh: number; blocked: boolean }) {
  const fill = Math.max(0, Math.min(1, soc / kwh)), res = reserveKwh / kwh;
  const H = 70, top = 22;
  const state = blocked ? "held at the reserve" : flow === 1 ? "charging from the grid" : flow === -1 ? "sending power to the grid" : "idle";
  return (
    <svg viewBox="0 0 320 110" className="h-[110px] w-full max-w-[420px]" role="img" aria-label={`The battery is ${state}; ${Math.round(fill * 100)} percent charged`}>
      <style>{`
        .erw-flow { stroke-dasharray: 6 8; }
        .erw-in { animation: erw-in 0.6s linear infinite; }
        .erw-out { animation: erw-out 0.6s linear infinite; }
        @keyframes erw-in { to { stroke-dashoffset: -14; } }
        @keyframes erw-out { to { stroke-dashoffset: 14; } }
        @media (prefers-reduced-motion: reduce) { .erw-in, .erw-out { animation: none; } }
      `}</style>
      {/* the grid: a pylon */}
      <g stroke="var(--color-muted)" strokeWidth="2" fill="none">
        <path d="M28 96 L40 24 L52 96 M33 66 L47 66 M36 46 L44 46 M24 34 L56 34" />
      </g>
      <text x="40" y="18" textAnchor="middle" fontSize="10" fill="var(--color-muted)">grid</text>
      {/* the wire, grid to battery */}
      <line x1="56" y1="58" x2="128" y2="58" stroke="var(--color-rule)" strokeWidth="4" />
      {flow !== 0 && !blocked ? (
        <line x1="56" y1="58" x2="128" y2="58" stroke={flow === 1 ? "var(--color-down)" : "var(--color-accent)"} strokeWidth="4" className={`erw-flow ${flow === 1 ? "erw-in" : "erw-out"}`} />
      ) : null}
      {/* the battery */}
      <rect x="130" y={top} width="44" height={H} rx="4" fill="var(--color-panel)" stroke="var(--color-ink)" strokeWidth="2" />
      <rect x="144" y={top - 6} width="16" height="6" fill="var(--color-ink)" />
      <rect x="134" y={top + 4 + (H - 8) * (1 - fill)} width="36" height={(H - 8) * fill} fill="var(--color-down)" />
      {reserveKwh > 0 ? (
        <g>
          <line x1="126" x2="178" y1={top + 4 + (H - 8) * (1 - res)} y2={top + 4 + (H - 8) * (1 - res)} stroke="var(--color-accent)" strokeWidth="2" strokeDasharray="4 3" />
          <text x="182" y={top + 8 + (H - 8) * (1 - res)} fontSize="9" fill="var(--color-accent)">reserve</text>
        </g>
      ) : null}
      {/* the wire, battery to house */}
      <line x1="176" y1="70" x2="232" y2="70" stroke="var(--color-rule)" strokeWidth="4" />
      {/* the house */}
      <path d="M236 92 L236 60 L266 38 L296 60 L296 92 Z" fill="var(--color-panel)" stroke="var(--color-ink)" strokeWidth="2" />
      <rect x="258" y="70" width="14" height="22" fill="var(--color-rule)" />
      <text x="160" y="106" textAnchor="middle" fontSize="10" fill="var(--color-ink)">{state}</text>
    </svg>
  );
}

/** Session 50: the replay. The perfect battery's day (perfect foresight, the same rules) plays back beside the
 * player's: both states of charge over the day, a cursor, and at each switch of the perfect plan a reason read from
 * the prices (lib/battery.ts explain). */
function Replay({ level, rules, mine, perfect }: { level: GameLevel; rules: Rules; mine: Action[]; perfect: Action[] }) {
  const n = level.price.length;
  const hours = useMemo(() => level.ts_utc.map((t) => Number(clock(level.tz, t).slice(0, 2))), [level]);
  const segs = useMemo(() => explain(level.price, hours, perfect, rules, (i) => clock(level.tz, level.ts_utc[i])), [level, hours, perfect, rules]);
  const a = useMemo(() => simulate(level.price, mine, rules).soc, [level, mine, rules]);
  const b = useMemo(() => simulate(level.price, perfect, rules).soc, [level, perfect, rules]);
  const [t, setT] = useState(n);
  const [playing, setPlaying] = useState(false);
  const raf = useRef(0);
  useEffect(() => {
    if (!playing) return;
    const t0 = performance.now(), from = t >= n ? 0 : t;
    const tick = (now: number) => {
      const v = Math.min(n, from + ((now - t0) / 20_000) * n);
      setT(v);
      if (v < n) raf.current = requestAnimationFrame(tick); else setPlaying(false);
    };
    raf.current = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf.current);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [playing]);
  const W = 720, H = 200, L = 36, R = 8, T = 10, B = 26;
  const x = (i: number) => L + (i / n) * (W - L - R);
  const y = (v: number) => T + (1 - v / rules.kwh) * (H - T - B);
  const lo = Math.min(...level.price), hi = Math.max(...level.price);
  const py = (v: number) => T + (1 - (v - lo) / (hi - lo || 1)) * (H - T - B);
  const upto = Math.floor(t);
  const path = (s: number[]) => s.slice(0, upto + 1).map((v, i) => `${i ? "L" : "M"}${x(i).toFixed(1)},${y(v).toFixed(1)}`).join(" ");
  const price = level.price.slice(0, upto).map((v, i) => `${i ? "L" : "M"}${x(i).toFixed(1)},${py(v).toFixed(1)}`).join(" ");
  const cur = Math.min(n - 1, upto);
  const seg = segs.find((s) => cur >= s.from && cur <= s.to);
  const verb = (v: Action) => (v === 1 ? "charging" : v === -1 ? "selling" : "holding");
  return (
    <div className="mt-4 border-t border-rule pt-3 text-sm">
      <h3 className="mb-1 text-base">Replay: the perfect battery beside yours</h3>
      <p className="mb-2 text-xs text-muted">The same battery and rules, with every price known in advance. Its state of charge (accent) and yours (ink), kWh, over the day; the day&apos;s price is the faint line behind, on its own scale.</p>
      <div className="mb-2 flex flex-wrap items-center gap-2">
        <button onClick={() => setPlaying(!playing)} className="border border-accent px-3 py-1 text-accent">{playing ? "Pause" : t >= n ? "Play the replay" : "Resume"}</button>
        <input type="range" min={0} max={n} step={1} value={Math.round(t)} onChange={(e) => { setPlaying(false); setT(Number(e.target.value)); }} className="w-56" aria-label="Replay position" />
        <span className="tabular-nums">{clock(level.tz, level.ts_utc[cur])}</span>
      </div>
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img" aria-label="State of charge over the day: the perfect battery and yours">
        {[0, 0.5, 1].map((f) => (
          <g key={f}>
            <line x1={L} x2={W - R} y1={y(rules.kwh * f)} y2={y(rules.kwh * f)} stroke="var(--color-rule)" />
            <text x={L - 4} y={y(rules.kwh * f) + 4} textAnchor="end" fontSize="10" fill="var(--color-muted)">{(rules.kwh * f).toFixed(1)}</text>
          </g>
        ))}
        {rules.reserveKwh > 0 ? <line x1={L} x2={W - R} y1={y(rules.reserveKwh)} y2={y(rules.reserveKwh)} stroke="var(--color-accent)" strokeDasharray="4 3" /> : null}
        <path d={price} fill="none" stroke="var(--color-muted)" strokeOpacity="0.35" strokeWidth="1.5" />
        <path d={path(a)} fill="none" stroke="var(--color-ink)" strokeWidth="2" />
        <path d={path(b)} fill="none" stroke="var(--color-accent)" strokeWidth="2" />
        <line x1={x(upto)} x2={x(upto)} y1={T} y2={H - B} stroke="var(--color-muted)" />
        {[0, Math.floor(n / 2), n - 1].map((i) => <text key={i} x={x(i)} y={H - 8} fontSize="10" textAnchor="middle" fill="var(--color-muted)">{clock(level.tz, level.ts_utc[i])}</text>)}
      </svg>
      <div className="flex flex-wrap gap-4 text-xs">
        <span><span className="mr-1 inline-block h-0.5 w-5 align-middle bg-accent" />the perfect battery</span>
        <span><span className="mr-1 inline-block h-0.5 w-5 align-middle bg-[var(--color-ink)]" />yours</span>
        {rules.reserveKwh > 0 ? <span className="text-accent">dashed: the reserve</span> : null}
      </div>
      <p className="mt-2 min-h-[2.5rem]" aria-live="polite">
        <strong>{clock(level.tz, level.ts_utc[cur])}</strong>: the perfect battery {seg ? `is ${verb(seg.a)} (${seg.text})` : ""}; you were {verb(mine[cur] ?? 0)}.
      </p>
      <details className="mt-1">
        <summary className="cursor-pointer text-muted">Every switch of the perfect plan ({segs.length})</summary>
        <ol className="mt-1 list-decimal pl-6 text-xs">
          {segs.map((s) => <li key={s.from}>{clock(level.tz, level.ts_utc[s.from])} to {clock(level.tz, new Date(Date.parse(level.ts_utc[s.to]) + 15 * 60_000).toISOString())}: {s.text}</li>)}
        </ol>
      </details>
    </div>
  );
}

/** Session 50: the battery's settings and the difficulty, each default labelled with its source. */
function SettingsPanel({ draft, setDraft, difficulty, setDifficulty }: {
  draft: Record<keyof Settings, string>; setDraft: (d: Record<keyof Settings, string>) => void; difficulty: Difficulty; setDifficulty: (d: Difficulty) => void;
}) {
  const shownAs = (k: keyof Settings) => (k === "rte" || k === "reserve" ? 100 : 1);
  return (
    <div className="mb-3 border border-rule p-3 text-sm">
      <div className="mb-2 flex flex-wrap gap-2" role="radiogroup" aria-label="Difficulty">
        {(Object.keys(DIFFICULTIES) as Difficulty[]).map((d) => (
          <button key={d} role="radio" aria-checked={difficulty === d} onClick={() => setDifficulty(d)}
            className={`border px-3 py-1 ${difficulty === d ? "border-accent bg-accent text-paper" : "border-rule"}`}>{DIFFICULTIES[d].label}</button>
        ))}
        <span className="self-center text-xs text-muted">{DIFFICULTIES[difficulty].what}.</span>
      </div>
      <details>
        <summary className="cursor-pointer">The battery: settings (each default an assumption or a cited figure; editable within its range)</summary>
        <div className="mt-2 grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
          {(Object.keys(SETTINGS) as (keyof Settings)[]).map((k) => {
            const r = SETTINGS[k], f = shownAs(k);
            const onHardOnly = (k === "reserve" || k === "deg") && difficulty !== "hard";
            return (
              <label key={k} className={`flex flex-col ${onHardOnly ? "opacity-60" : ""}`}>
                <span>{r.label}{r.unit === "percent" ? ", percent" : r.unit ? `, ${r.unit}` : ""} <span className="text-xs text-muted">({+(r.min * f).toFixed(2)} to {+(r.max * f).toFixed(2)}, default {+(r.def * f).toFixed(2)}){onHardOnly ? "; applies on Hard" : ""}</span></span>
                <input type="number" inputMode="decimal" min={r.min * f} max={r.max * f} step={r.step * f} value={draft[k]}
                  onChange={(e) => setDraft({ ...draft, [k]: e.target.value })} className="w-32 border border-rule bg-panel px-2 py-1" />
                <span className="text-xs text-muted">{r.source}</span>
              </label>
            );
          })}
        </div>
        <button onClick={() => setDraft(toDraft(DEFAULT_SETTINGS))} className="mt-2 border border-rule px-3 py-1">Reset to the defaults</button>
      </details>
    </div>
  );
}
const toDraft = (s: Settings): Record<keyof Settings, string> => ({
  kwh: String(s.kwh), kw: String(s.kw), rte: String(Math.round(s.rte * 100)), reserve: String(Math.round(s.reserve * 100)), deg: String(s.deg),
});
const fromDraft = (d: Record<keyof Settings, string>): Settings => ({
  kwh: Number(d.kwh), kw: Number(d.kw), rte: Math.round(Number(d.rte)) / 100, reserve: Math.round(Number(d.reserve)) / 100, deg: Math.round(Number(d.deg) * 100) / 100,
});

export function Game({ levels, top: firstTop, presets: firstPresets, simple = false }: { levels: GameLevel[]; top: ScoreRow[]; presets: PresetCount[]; simple?: boolean }) {
  const [phase, setPhase] = useState<Phase>("pick");
  const [pick, setPick] = useState(0);
  const level = levels[pick];
  const n = level.price.length;
  const [draft, setDraft] = useState(toDraft(DEFAULT_SETTINGS));
  const [difficulty, setDifficulty] = useState<Difficulty>("normal");
  const parsed = fromDraft(draft);
  const ok = validSettings(parsed);
  const settings = ok ? parsed : DEFAULT_SETTINGS;
  const settingsKey = JSON.stringify(settings);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  const rules = useMemo(() => rulesOf(settings, difficulty), [settingsKey, difficulty]);
  const preset = presetOf(settings, difficulty);
  // session 63: on Hard the emergency's prices are the ones played and scored (a game rule); elsewhere the real prices
  const em = useMemo(() => emergencyOf(level.price, rules), [level, rules]);
  const P = em.prices;
  const vpp = useMemo(() => vppHour(P), [P]);
  const best = useMemo(() => optimum(level.price, rules), [level, rules]);
  const [tutorial, setTutorial] = useState(false);

  // the viewer's conveniences, from browser storage after the first render (absent or refused: the defaults)
  useEffect(() => {
    if (simple) return;  // session 63: the simple page always plays Normal with the default battery, and skips the tutorial
    const seen = load(TUTORIAL_KEY) === "seen";
    let saved: { settings?: unknown; difficulty?: unknown } | null = null;
    try { saved = JSON.parse(load(SETTINGS_KEY) ?? "null"); } catch { saved = null; }
    queueMicrotask(() => {
      if (!seen) setTutorial(true);
      if (saved && validSettings(saved.settings)) setDraft(toDraft(saved.settings));
      if (saved && (saved.difficulty === "easy" || saved.difficulty === "normal" || saved.difficulty === "hard")) setDifficulty(saved.difficulty);
    });
  }, [simple]);
  useEffect(() => { if (ok && !simple) save(SETTINGS_KEY, JSON.stringify({ settings, difficulty })); }, [ok, settingsKey, difficulty, simple]); // eslint-disable-line react-hooks/exhaustive-deps
  const endTutorial = useCallback(() => { save(TUTORIAL_KEY, "seen"); setTutorial(false); }, []);

  // mutable game state, read by the animation loop
  const g = useRef({ t0: 0, idx: 0, held: [0, 0, 0], last: 0, soc: 0, cash: 0, wear: 0, bonus: 0, vppKwh: 0, actions: [] as Action[], control: 0 as Control, ended: false });
  const [hud, setHud] = useState({ idx: 0, soc: rules.start, cash: 0, wear: 0, bonus: 0, vppKwh: 0, control: 0 as Control });
  const [result, setResult] = useState<{
    score: number; cash: number; wear: number; bonus: number; actions: Action[]; rules: Rules; preset: string; settings: Settings; difficulty: Difficulty;
    end: number | null; why: "" | "bankrupt" | "lights_out"; outageStartKwh: number | null; outageNeedKwh: number;
  } | null>(null);
  const [server, setServer] = useState<string>("");
  const [top, setTop] = useState<ScoreRow[]>(firstTop);
  const [topFor, setTopFor] = useState<{ date: string; preset: string }>({ date: levels[0].date, preset: firstTop[0]?.preset ?? presetOf(DEFAULT_SETTINGS, "normal") });
  const [boardNote, setBoardNote] = useState("");
  // session 55: on the pick screen the leaderboard follows the chosen day, difficulty and battery (GET /api/play/top),
  // so the board shown is the one a play would join; 400 ms after the last change, and only for valid settings
  useEffect(() => {
    if (phase !== "pick" || !ok || (topFor.date === level.date && topFor.preset === preset)) return;
    let live = true;
    const t = setTimeout(async () => {
      try {
        const res = await fetch(`/api/play/top?${new URLSearchParams({ level: level.date, preset })}`);
        const j = await res.json();
        if (!live) return;
        if (!res.ok) { setBoardNote(j.error ?? `The leaderboard could not be loaded (HTTP ${res.status}).`); return; }
        setTop(j.top); setTopFor({ date: j.level, preset: j.preset }); setBoardNote("");
      } catch {
        if (live) setBoardNote("The leaderboard could not be loaded.");
      }
    }, 400);
    return () => { live = false; clearTimeout(t); };
  }, [phase, ok, level.date, preset, topFor.date, topFor.preset]);
  const [nick, setNick] = useState("");
  const [posted, setPosted] = useState<string>("");
  const canvas = useRef<HTMLCanvasElement>(null);
  const board = useRef<HTMLDivElement>(null);  // session 50: scrolled into view when a game starts (phones)
  const raf = useRef(0);
  const next = useRef<(now: number) => void>(() => {});  // the loop's next frame, through a ref (react-hooks/immutability)

  const setControl = useCallback((c: Control) => { g.current.control = c; setHud((h) => ({ ...h, control: c })); }, []);
  const forecast = DIFFICULTIES[difficulty].forecastHours * 4;

  const draw = useCallback((pos: number) => {
    const cv = canvas.current;
    if (!cv) return;
    const dpr = window.devicePixelRatio || 1;
    const w = cv.clientWidth, h = cv.clientHeight;
    if (cv.width !== Math.round(w * dpr) || cv.height !== Math.round(h * dpr)) { cv.width = Math.round(w * dpr); cv.height = Math.round(h * dpr); }
    const ctx = cv.getContext("2d")!;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.fillStyle = css("panel"); ctx.fillRect(0, 0, w, h);
    const shown = Math.max(1, Math.min(n, Math.floor(pos) + 1));
    const seen = P.slice(0, shown);
    // Easy: the next hours as a band, each clock hour's lowest to highest real price
    const bands: { i: number; lo: number; hi: number }[] = [];
    if (forecast) {
      for (let i = Math.floor(shown / 4) * 4; i < Math.min(n, shown + forecast); i += 4) {
        const hr = P.slice(i, i + 4);
        bands.push({ i, lo: Math.min(...hr), hi: Math.max(...hr) });
      }
    }
    let lo = Math.min(0, ...seen, ...bands.map((b) => b.lo)), hi = Math.max(10, ...seen, ...bands.map((b) => b.hi));
    const pad = (hi - lo) * 0.12; lo -= pad; hi += pad;
    const top = 18, bottom = h - 34;
    const y = (v: number) => bottom - ((v - lo) / (hi - lo)) * (bottom - top);
    const span = 24; // intervals visible behind the now line (six hours)
    const nowX = w * (forecast ? 0.55 : 0.72);
    const dx = (nowX - 44) / span;
    const x = (i: number) => nowX - (pos - i) * dx;
    // grid and zero line
    ctx.strokeStyle = css("rule"); ctx.lineWidth = 1; ctx.font = "11px system-ui, sans-serif"; ctx.fillStyle = css("muted");
    for (let k = 0; k <= 4; k++) {
      const v = lo + ((hi - lo) * k) / 4, yy = y(v);
      ctx.beginPath(); ctx.moveTo(40, yy); ctx.lineTo(w, yy); ctx.stroke();
      ctx.fillText(Math.round(v).toLocaleString("en-US"), 2, yy + 4);
    }
    if (lo < 0) { ctx.strokeStyle = css("ink"); ctx.beginPath(); ctx.moveTo(40, y(0)); ctx.lineTo(w, y(0)); ctx.stroke(); }
    // the VPP hour, from its notice (one interval before) on
    if (pos >= vpp.first - 1) {
      ctx.fillStyle = "rgba(140, 21, 21, 0.08)";
      ctx.fillRect(x(vpp.first), top, (vpp.last + 1 - vpp.first) * dx, bottom - top);
    }
    // session 63: Hard's outage, from its start: the grid is down
    if (em.outage && pos >= em.outage.first) {
      ctx.fillStyle = "rgba(46, 45, 41, 0.10)";
      ctx.fillRect(x(em.outage.first), top, (em.outage.last + 1 - em.outage.first) * dx, bottom - top);
      ctx.fillStyle = css("muted"); ctx.font = "11px system-ui, sans-serif";
      ctx.fillText("grid down", x(em.outage.first) + 4, top + 12);
    }
    // the forecast band, ahead of the now line
    if (bands.length) {
      ctx.fillStyle = "rgba(23, 94, 84, 0.16)";
      for (const b of bands) {
        const x0 = Math.max(nowX, x(b.i)), x1 = x(b.i + 4);
        if (x1 > x0) ctx.fillRect(x0, y(b.hi), x1 - x0, Math.max(2, y(b.lo) - y(b.hi)));
      }
      ctx.fillStyle = css("muted"); ctx.font = "11px system-ui, sans-serif";
      ctx.fillText(w < 520 ? `next ${forecast / 4} h: price range` : `next ${forecast / 4} hours: each hour's price range`, nowX + 6, top + 2);
    }
    // actions taken, under the line
    const acts = g.current.actions;
    for (let i = 0; i < acts.length; i++) {
      if (x(i + 1) < 40 || acts[i] === 0) continue;
      ctx.fillStyle = acts[i] === 1 ? css("down") : css("accent");
      ctx.fillRect(x(i), bottom + 6, dx - 1, 8);
    }
    // hour labels
    ctx.fillStyle = css("muted");
    for (let i = 0; i < n; i += 4) {
      const xx = x(i);
      if (xx < 40 || xx > w - 20 || i > pos + 1 + forecast) continue;
      ctx.fillText(clock(level.tz, level.ts_utc[i]).slice(0, 2), xx - 6, h - 6);
    }
    // the price line so far
    ctx.save(); ctx.beginPath(); ctx.rect(40, 0, w - 40, h); ctx.clip();
    ctx.strokeStyle = css("ink"); ctx.lineWidth = 2; ctx.beginPath();
    for (let i = 0; i < shown; i++) {
      const x0 = x(i), yy = y(P[i]);
      if (i === 0) ctx.moveTo(x0, yy); else ctx.lineTo(x0, yy);
      ctx.lineTo(Math.min(x0 + dx, nowX), yy);
    }
    ctx.stroke(); ctx.restore();
    // the now line and the current price
    ctx.strokeStyle = css("accent"); ctx.lineWidth = 1.5; ctx.beginPath(); ctx.moveTo(nowX, top - 8); ctx.lineTo(nowX, bottom); ctx.stroke();
    const cur = P[Math.min(n - 1, Math.floor(pos))];
    ctx.fillStyle = css("accent"); ctx.beginPath(); ctx.arc(nowX, y(cur), 4, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = css("ink"); ctx.font = "12px system-ui, sans-serif";
    // the label right of the now line where it fits, else left of it (narrow screens), never over the line
    const label = `${cur.toLocaleString("en-US", { maximumFractionDigits: 2 })} USD/MWh`;
    const lw = ctx.measureText(label).width;
    ctx.fillText(label, nowX + 8 + lw <= w - 2 && !forecast ? nowX + 8 : nowX - 8 - lw, Math.max(top + 10, y(cur) - 8));
  }, [level, n, vpp, forecast, P, em]);

  const finish = useCallback(async () => {
    cancelAnimationFrame(raf.current);
    const played = g.current.actions.slice(0, n);
    const actions: Action[] = [...played, ...new Array(Math.max(0, n - played.length)).fill(0)];  // after an early end nothing counts
    const r = simulate(level.price, actions, rules);
    setResult({ score: r.score, cash: r.cash, wear: r.wear, bonus: r.bonus, actions, rules, preset, settings, difficulty,
      end: r.end, why: r.why, outageStartKwh: r.outageStartKwh, outageNeedKwh: r.outageNeedKwh });
    setPhase("done");
    setControl(0);
    try {
      const res = await fetch("/api/play/finish", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ level: level.date, actions, settings, difficulty }) });
      const j = await res.json();
      setServer(res.ok ? (Math.abs(j.score - Math.round(r.score * 10_000) / 10_000) < 1e-6 ? "Score verified by the server." : `The server scored this game ${usd(j.score)}.`) : `Not stored: ${j.error ?? res.status}`);
    } catch {
      setServer("Not stored: the server could not be reached.");
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [level, n, setControl, rules, preset, settingsKey, difficulty]);

  const loop = useCallback((now: number) => {
    const s = g.current;
    const per = DURATION_MS / n;
    const elapsed = now - s.t0;
    const dt = Math.min(100, now - s.last);
    s.last = now;
    s.held[s.control + 1] += dt; // [discharge, idle, charge]
    const target = Math.min(n, Math.floor(elapsed / per));
    while (s.idx < target && !s.ended) {
      const [dis, idle, chg] = s.held;
      const out = em.outage !== null && s.idx >= em.outage.first && s.idx <= em.outage.last;
      const a: Action = out ? 0 : chg > idle && chg > dis ? 1 : dis > idle && dis > chg ? -1 : 0;
      s.actions.push(a);
      s.idx++;
      s.held = [0, 0, 0];
      // session 63: the state from simulate(), the server's scorer: money, the emergency, the outage, an early end
      const r = simulate(level.price, s.actions, rules);
      s.soc = r.soc[r.soc.length - 1]; s.cash = r.cash; s.wear = r.wear; s.bonus = r.bonus; s.vppKwh = r.vppKwh;
      if (r.end !== null) s.ended = true;
    }
    draw(Math.min(n - 0.001, elapsed / per));
    setHud((h) => (h.idx !== s.idx || Math.abs(h.soc - s.soc) > 1e-9 ? { idx: s.idx, soc: s.soc, cash: s.cash, wear: s.wear, bonus: s.bonus, vppKwh: s.vppKwh, control: s.control } : h));
    if (s.idx >= n || s.ended) { finish(); return; }
    raf.current = requestAnimationFrame((t) => next.current(t));
  }, [n, level, draw, finish, rules, em]);
  useEffect(() => { next.current = loop; }, [loop]);

  const start = () => {
    if (!ok) return;
    const t = performance.now();
    g.current = { t0: t, idx: 0, held: [0, 0, 0], last: t, soc: rules.start, cash: 0, wear: 0, bonus: 0, vppKwh: 0, actions: [], control: 0, ended: false };
    setHud({ idx: 0, soc: rules.start, cash: 0, wear: 0, bonus: 0, vppKwh: 0, control: 0 });
    setResult(null); setServer(""); setPosted("");
    setPhase("play");
    requestAnimationFrame(() => board.current?.scrollIntoView({ block: "start", behavior: "auto" }));
    next.current = loop;
    raf.current = requestAnimationFrame((t) => next.current(t));
  };

  useEffect(() => () => cancelAnimationFrame(raf.current), []);
  useEffect(() => { if (phase !== "play") draw(0); }, [phase, draw]);
  useEffect(() => {
    if (phase !== "play") return;
    const key = (down: boolean) => (e: KeyboardEvent) => {
      const c: Control | null = ["ArrowDown", "KeyC"].includes(e.code) ? 1 : ["ArrowUp", "KeyS"].includes(e.code) ? -1 : null;
      if (c === null) return;
      e.preventDefault();
      if (down) setControl(c); else if (g.current.control === c) setControl(0);
    };
    const kd = key(true), ku = key(false);
    window.addEventListener("keydown", kd); window.addEventListener("keyup", ku);
    return () => { window.removeEventListener("keydown", kd); window.removeEventListener("keyup", ku); };
  }, [phase, setControl]);

  const hold = (c: Control) => ({
    onPointerDown: (e: React.PointerEvent) => { (e.target as HTMLElement).setPointerCapture(e.pointerId); setControl(c); },
    onPointerUp: () => setControl(0), onPointerCancel: () => setControl(0), onLostPointerCapture: () => setControl(0),
    onContextMenu: (e: React.MouseEvent) => e.preventDefault(),
  });

  const playing = phase === "play";
  const money = START_MONEY + hud.cash - hud.wear + hud.bonus;
  const inSpike = playing && em.spike !== null && hud.idx >= em.spike.first && hud.idx <= em.spike.last;
  const inOutage = playing && em.outage !== null && hud.idx >= em.outage.first && hud.idx <= em.outage.last;
  const inVpp = playing && hud.idx >= vpp.first && hud.idx <= vpp.last;
  const notice = playing && hud.idx === vpp.first - 1;
  const vppDone = hud.idx > vpp.last;
  const lit = hud.vppKwh > 0;
  const atReserve = rules.reserveKwh > 0 && hud.soc <= rules.reserveKwh + 1e-9;
  const blocked = playing && hud.control === -1 && atReserve;
  const post = async () => {
    if (!result) return;
    setPosted("Posting...");
    const res = await fetch("/api/play/score", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ level: level.date, actions: result.actions, nickname: nick.trim() || undefined, settings: result.settings, difficulty: result.difficulty }),
    });
    const j = await res.json();
    if (!res.ok) { setPosted(j.error ?? `HTTP ${res.status}`); return; }
    setTop(j.top); setTopFor({ date: level.date, preset: j.preset }); setPosted("Posted.");
  };

  // the debrief, from the level's prices and the optimum under the rules played
  const peak = level.price.indexOf(Math.max(...level.price)), low = level.price.indexOf(Math.min(...level.price));
  const at = (i: number | null) => (i === null ? "" : clock(level.tz, level.ts_utc[Math.min(n - 1, i)]));
  const charged = runs(best.actions, level.ts_utc, 1, level.tz), discharged = runs(best.actions, level.ts_utc, -1, level.tz);
  const G = GRIDS[level.grid];
  const otherPresets = topFor.date === levels[0].date ? firstPresets.filter((p) => p.preset !== topFor.preset) : [];

  return (
    <div className="select-none">
      {tutorial && phase === "pick" ? <Tutorial onDone={endTutorial} /> : null}
      {phase === "pick" && simple ? (
        <div>
          <p className="mb-3 text-base">Buy power into your battery when it is cheap and sell it when it is dear: you start with $5, and the game ends if you go below $0.</p>
          <label className="mb-3 block text-sm">The day:{" "}
            <select value={pick} onChange={(e) => setPick(Number(e.target.value))} className="border border-rule bg-panel px-2 py-1">
              {levels.map((l, i) => <option key={l.slug} value={i}>{l.title}, {l.date}</option>)}
            </select>
          </label>
          <button onClick={start} className="w-full border border-accent bg-accent px-6 py-4 text-xl text-paper sm:w-auto">Start</button>
        </div>
      ) : phase === "pick" ? (
        <div>
          <SettingsPanel draft={draft} setDraft={setDraft} difficulty={difficulty} setDifficulty={setDifficulty} />
          {!ok ? <p className="mb-2 text-sm text-accent" role="alert">A setting is outside its range or between its steps; the game will not start until it is within them.</p> : null}
          <p className="mb-2 text-sm">Pick a day. Everyone plays the same level on the same day; the leaderboard ranks plays with the same difficulty and battery.</p>
          {/* session 56: the levels grouped by grid; a California day states its selection rule */}
          {(["ERCOT", "CAISO"] as const).filter((gr) => levels.some((l) => l.grid === gr)).map((gr) => (
            <div key={gr} className="mb-3">
              <h3 className="mb-1 text-sm font-semibold">{GRIDS[gr].name}: {GRIDS[gr].zone} time</h3>
              <div className="grid gap-2 sm:grid-cols-2">
                {levels.map((l, i) => {
                  if (l.grid !== gr) return null;
                  const ev = l.grid === "ERCOT" ? eventPageFor(l.date) : null;  // session 46: a famous ERCOT day inside an /events window links to it
                  return (
                    <div key={l.slug} className={`border text-sm ${i === pick ? "border-accent" : "border-rule"}`}>
                      <button onClick={() => setPick(i)} className="w-full p-2 text-left">
                        <span className="font-semibold">{l.title}</span> <span className="whitespace-nowrap text-muted">{l.date}</span>
                        <span className="block text-xs text-muted">{l.why}</span>
                        {l.rule ? <span className="block text-xs text-muted">The rule: {l.rule}</span> : null}
                      </button>
                      {ev ? <Link href={ev.href} className="block px-2 pb-2 text-xs">What happened: {ev.label}</Link> : null}
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
          <div className="flex flex-wrap items-center gap-3">
            <button onClick={start} disabled={!ok} className="border border-accent bg-accent px-4 py-2 text-paper disabled:opacity-50">Play {level.date}, {DIFFICULTIES[difficulty].label}</button>
            {!tutorial ? <button onClick={() => setTutorial(true)} className="text-sm underline">How to play (30 seconds)</button> : null}
          </div>
        </div>
      ) : null}

      {phase !== "pick" ? (
        <div ref={board} className="scroll-mt-2">
          <div className="mb-1 flex flex-wrap items-baseline justify-between gap-2 text-sm">
            <span><strong>{level.title}</strong>, {level.date} ({GRIDS[level.grid].name}, {GRIDS[level.grid].zone} time), {DIFFICULTIES[difficulty].label}</span>
            <span aria-live="polite">{playing && hud.idx < n ? `${clock(level.tz, level.ts_utc[Math.min(n - 1, hud.idx)])}` : "end of day"}</span>
          </div>
          {inOutage ? (
            <div className="mb-1 border border-ink bg-panel px-2 py-1 text-sm" role="status">
              Outage (a game rule): the grid is down. Your house runs on its battery, {EMERGENCY.houseKw} kW; if the battery runs dry, the lights go out and the round ends.
            </div>
          ) : inSpike ? (
            <div className="mb-1 border border-accent bg-panel px-2 py-1 text-sm text-accent" role="status">
              Grid emergency (a game rule): the price is climbing toward the {usd(EMERGENCY.cap).replace(".00", "")}/MWh cap. Next the grid goes down for two hours: keep charge for the house.
            </div>
          ) : notice ? (
            <div className="mb-1 border border-accent px-2 py-1 text-sm text-accent" role="status">Fleet call in 15 minutes: the grid&apos;s dearest hour of the day. Keep charge to sell then.</div>
          ) : inVpp ? (
            <div className="mb-1 border border-accent bg-panel px-2 py-1 text-sm text-accent" role="status">
              Fleet call: discharge now to earn the bonus (a game rule modeled on ERCOT&apos;s ADER pilot; see the rules below).
            </div>
          ) : null}
          {simple ? (
            <div className="mb-1 text-center"><span className="text-3xl tabular-nums">{P[Math.min(n - 1, hud.idx)].toLocaleString("en-US", { maximumFractionDigits: 2 })}</span> <span className="text-sm text-muted">USD/MWh now</span></div>
          ) : null}
          <canvas ref={canvas} className={`block w-full touch-none ${simple ? "h-[140px]" : "h-[220px] sm:h-[260px]"}`} aria-label="The day's price so far; the future is hidden except Easy's forecast band" />
          <div className="mt-2 grid grid-cols-1 items-center gap-2 sm:grid-cols-[auto_1fr]">
            <HouseFlow flow={playing ? hud.control : 0} soc={hud.soc} kwh={rules.kwh} reserveKwh={rules.reserveKwh} blocked={blocked} />
            <div className="grid grid-cols-[1fr_auto] items-center gap-3 text-sm">
              <div>
                <div className="mb-1 flex justify-between text-xs text-muted"><span>State of charge</span><span>{hud.soc.toFixed(2)} of {rules.kwh} kWh</span></div>
                <div className="relative h-3 w-full border border-rule bg-panel">
                  <div className="h-full bg-[var(--color-down)]" style={{ width: `${(hud.soc / rules.kwh) * 100}%` }} />
                  {rules.reserveKwh > 0 ? <div className="absolute top-[-3px] h-[18px] w-0.5 bg-accent" style={{ left: `${(rules.reserveKwh / rules.kwh) * 100}%` }} title="the backup reserve" /> : null}
                </div>
                {blocked ? <div className="mt-1 text-xs text-accent">Held: the battery is at its backup reserve.</div> : null}
              </div>
              <div className="text-right">
                <span className="text-xs text-muted">Money</span><div className={`font-mono text-lg ${money < 1 ? "text-accent" : ""}`} aria-live="off">{usd(money)}</div>
                <div className="text-xs text-muted">earned {usd(money - START_MONEY)}{rules.deg > 0 ? `, wear ${usd(-hud.wear)}` : ""}</div>
              </div>
            </div>
          </div>
          <div className={`mt-2 flex items-center gap-3 ${simple ? "hidden" : ""}`}>
            <div className="grid grid-cols-10 gap-[3px]" aria-label={lit ? "The fleet map is lit: your battery answered the call" : "The fleet map"} role="img">
              {Array.from({ length: 50 }, (_, i) => <span key={i} className="block h-2 w-2 rounded-full" style={{ background: lit ? "var(--color-accent)" : "var(--color-rule)" }} />)}
            </div>
            <span className="text-xs text-muted">{lit ? `Fleet lit: ${hud.vppKwh.toFixed(2)} kWh delivered in the call hour.` : vppDone ? "The fleet call has passed." : "The fleet map lights when your battery answers the call."}</span>
          </div>
          {playing ? (
            <div className="mt-3 grid grid-cols-2 gap-3">
              <button {...hold(1)} disabled={inOutage} className={`touch-none border px-3 ${simple ? "py-8 text-xl" : "py-4 text-base"} disabled:opacity-40 ${hud.control === 1 ? "border-[var(--color-down)] bg-[var(--color-down)] text-paper" : "border-[var(--color-down)] text-[var(--color-down)]"}`}>{simple ? "Charge" : "Hold to charge (buy)"}</button>
              <button {...hold(-1)} disabled={inOutage} className={`touch-none border px-3 ${simple ? "py-8 text-xl" : "py-4 text-base"} disabled:opacity-40 ${hud.control === -1 ? "border-accent bg-accent text-paper" : "border-accent text-accent"}`}>{simple ? "Sell" : "Hold to sell (discharge)"}</button>
              <p className="col-span-2 text-xs text-muted">{inOutage ? "The grid is down: nothing to buy or sell until it is back." : simple ? "Hold a button down; let go to wait." : "Keys: C or the down arrow to charge, S or the up arrow to sell. Let go to idle."}</p>
            </div>
          ) : null}
        </div>
      ) : null}

      {phase === "done" && result && simple ? (
        <div className="mt-4 border border-rule p-3">
          <p className="text-xl">You finished with <strong>{usd(START_MONEY + result.score)}</strong>: you {result.score >= 0 ? "earned" : "lost"} {usd(Math.abs(result.score))}.</p>
          {result.why === "bankrupt" ? (
            <p className="mt-1 text-sm text-accent" role="status">Out of money at {at(result.end)}: below $0 the game ends (a game rule). Buying when power is dear costs more than the battery can earn back.</p>
          ) : result.why === "lights_out" ? (
            <p className="mt-1 text-sm text-accent" role="status">
              Lights out at {at(result.end)}: the battery ran dry in the outage (a game rule), so the round ended there. The two-hour outage needed{" "}
              {result.outageNeedKwh.toFixed(2)} kWh for the house; at its start the battery held {(result.outageStartKwh ?? 0).toFixed(2)} kWh. Keep at least{" "}
              {result.outageNeedKwh.toFixed(2)} kWh when the grid is in an emergency.
            </p>
          ) : null}
          <p className="mt-1 text-sm">A battery that knew every price in advance would have earned {usd(best.score)}.</p>
          <div className="mt-3 flex flex-wrap gap-3">
            <button onClick={() => setPhase("pick")} className="border border-accent bg-accent px-5 py-3 text-lg text-paper">Play again</button>
            <Link href="/play/battery?more=1" className="self-center text-sm">More: the replay, the settings, Hard&apos;s emergency and the leaderboard</Link>
          </div>
        </div>
      ) : phase === "done" && result ? (
        <div className="mt-4 border border-rule p-3">
          <p className="text-lg">
            You earned <strong>{usd(result.score)}</strong>
            {result.bonus > 0 || result.wear > 0 ? <> ({usd(result.cash)} in the market{result.wear > 0 ? `, less ${usd(result.wear)} of wear` : ""}{result.bonus > 0 ? `, plus the fleet bonus ${usd(result.bonus)}` : ""})</> : null}.
            Your fleet of {FLEET.toLocaleString("en-US")} homes: <strong>{usd(result.score * FLEET)}</strong>.
          </p>
          {result.why === "bankrupt" ? (
            <p className="mt-1 text-sm text-accent" role="status">Out of money at {at(result.end)}: below $0 the game ends (a game rule). Buying when power is dear costs more than the battery can earn back.</p>
          ) : result.why === "lights_out" ? (
            <p className="mt-1 text-sm text-accent" role="status">
              Lights out at {at(result.end)}: the battery ran dry in the outage (a game rule), so the round ended there. The two-hour outage needed{" "}
              {result.outageNeedKwh.toFixed(2)} kWh for the house; at its start the battery held {(result.outageStartKwh ?? 0).toFixed(2)} kWh. Keep at least{" "}
              {result.outageNeedKwh.toFixed(2)} kWh when the grid is in an emergency.
            </p>
          ) : null}
          <p className="text-sm">With perfect foresight the same battery, under the same rules ({presetLabel(result.preset)}), would have earned {usd(best.score)}{best.score > 0 ? `; you made ${Math.round((result.score / best.score) * 100)} percent of it` : ""}. <span className="text-muted">{server}</span></p>
          <p className="mt-2 max-w-3xl text-sm">
            On {level.date} the real-time price at {G.hub} peaked at {level.price[peak].toLocaleString("en-US", { maximumFractionDigits: 2 })} USD/MWh at {clock(level.tz, level.ts_utc[peak])} {G.zone} time and
            was lowest, {level.price[low].toLocaleString("en-US", { maximumFractionDigits: 2 })} USD/MWh, at {clock(level.tz, level.ts_utc[low])}. The dearest hour, the fleet call, began at {clock(level.tz, level.ts_utc[vpp.first])}. Knowing every
            price in advance, this battery would have {charged.length ? `charged ${list(charged)}` : "never charged"} and {discharged.length ? `discharged ${list(discharged)}` : "never discharged"}: buy when power is cheap,
            sell when it is dear, within {result.rules.kwh} kWh and {result.rules.kw} kW, losing {Math.round((1 - result.rules.eta ** 2) * 100)} percent of the energy on the round trip{result.rules.reserveKwh > 0 ? `, never below its ${result.rules.reserveKwh.toFixed(2)} kWh reserve` : ""}{result.rules.deg > 0 ? `, and paying ${usd(result.rules.deg)} of wear for each kWh it discharges` : ""}.
            The grid: {G.name}. Real batteries on the grid do this every day: see <Link href="/storage">storage</Link> and <Link href={G.href}>{G.page}</Link>.
            {level.grid === "ERCOT" && eventPageFor(level.date) ? <> What happened that day on the grid: <Link href={eventPageFor(level.date)!.href}>{eventPageFor(level.date)!.label}</Link>.</> : null}
          </p>
          <Replay level={level} rules={result.rules} mine={result.actions} perfect={best.actions} />
          <ShareCard level={level} score={result.score} optimal={best.score} preset={result.preset} />
          <div className="mt-3 flex flex-wrap items-end gap-2 text-sm">
            <label className="flex flex-col">Nickname (optional, 3 to 16 letters and digits)
              <input value={nick} onChange={(e) => setNick(e.target.value.replace(/[^A-Za-z0-9]/g, "").slice(0, 16))} className="w-48 border border-rule bg-panel px-2 py-1" />
            </label>
            <button onClick={post} disabled={posted === "Posted." || posted === "Posting..."} className="border border-accent px-3 py-1 text-accent">Post to the leaderboard</button>
            <button onClick={() => setPhase("pick")} className="border border-rule px-3 py-1">Play again</button>
            <span className="text-xs text-muted">{posted}</span>
          </div>
        </div>
      ) : null}

      <div className={`mt-6 ${simple ? "hidden" : ""}`}>
        <h3 className="mb-1 text-base">Leaderboard, {topFor.date}: {presetLabel(topFor.preset)}</h3>
        {top.length ? (
          <ol className="list-decimal pl-6 text-sm">
            {top.map((r, i) => (
              <li key={i}>
                {r.nickname ?? <span className="text-muted">anonymous</span>}: {usd(r.score)}{r.optimal_score > 0 ? <span className="text-muted"> ({Math.round((r.score / r.optimal_score) * 100)} percent of perfect)</span> : null}
                {isPerfect(r.score, r.optimal_score) ? <span className="ml-1 border border-accent px-1 text-xs text-accent" title="A score at 100 percent of perfect foresight: the debrief shows the perfect plan, and replaying it scores this">flagged: 100 percent of perfect</span> : null}
              </li>
            ))}
          </ol>
        ) : <p className="text-sm text-muted">No scores yet for this level and preset.</p>}
        {top.some((r) => isPerfect(r.score, r.optimal_score)) ? (
          <p className="mt-1 text-xs text-muted">A flagged score reached 100 percent of perfect foresight. The debrief after each game shows the perfect plan, so such a score may replay it; it stands, marked.</p>
        ) : null}
        {otherPresets.length ? (
          <p className="mt-2 text-xs text-muted">
            Other presets played on {topFor.date}: {otherPresets.map((p) => `${presetLabel(p.preset)} (${p.n} score${p.n === 1 ? "" : "s"}, best ${usd(p.best)})`).join("; ")}. Scores are ranked only within a preset.
          </p>
        ) : null}
        {phase === "pick" && ok && (topFor.date !== level.date || topFor.preset !== preset) ? (
          <p className="mt-1 text-xs text-muted" aria-live="polite">{boardNote || `Loading the board for ${level.date}: ${presetLabel(preset)}...`}</p>
        ) : null}
        <p className="mt-1 text-xs text-muted">Your preset now: {presetLabel(preset)}.</p>
      </div>
    </div>
  );
}
