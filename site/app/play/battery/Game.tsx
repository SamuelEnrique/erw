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
// Session 66 (v4): lights out costs money (the page says so, with the reason); a spiked price is shown only through
// lib/battery.ts's shownPrices, whose text carries "game rule, not a real price" and the real price beside it (this file
// never formats a played price itself: scripts/test-battery.mjs checks it); after a play, three plain lines (EndLines):
// what you earned, what the perfect battery earned, and the hour you lost the most, from simulate()'s own earnings per
// interval; and Hard's add-ons, off by default, the first a rooftop solar array that follows the level's real solar shape.
import Link from "next/link";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  ADDON_KEYS, ADDONS, DEFAULT_SETTINGS, DIFFICULTIES, EMERGENCY, emergencyOf, eventPageFor, explain, FLEET, isPerfect, LIGHTS_OUT, optimum, perfectShare, presetLabel, presetOf, rulesOf, SETTINGS,
  shownPrices, simulate, SOLAR, solarKwh, SPIKE_LABEL, START_MONEY, validAddons, validSettings, validSolar, vppHour, worstHour,
  type Action, type AddonKey, type Difficulty, type Result, type Rules, type Settings, type ShownPrice,
} from "@/lib/battery";
import type { PresetCount, ScoreRow } from "@/lib/game";

// session 56: a level names its grid and its operating day's time zone (the California days are Pacific), and the
// California days their selection rule
// session 66: and, where the warehouse holds it, the day's solar shape (the grid's solar fleet, output per MW installed,
// one value per interval) with its source: the rooftop add-on needs it and is unavailable without it
export type GameLevel = { slug: string; date: string; title: string; why: string; ts_utc: string[]; price: number[]; grid: "ERCOT" | "CAISO"; tz: string; rule?: string; solar?: number[]; solar_source?: string };

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
  // session 66: on Hard the dearest hour's price is the game's, and the share says so wherever it says "real prices"
  const hard = preset.startsWith("hard:");
  const spikeNote = `On Hard the dearest hour's price is a ${SPIKE_LABEL}.`;
  const text = () => `${lines.join(" ")} ${presetLabel(preset)}. Real ${GRIDS[level.grid].prices} prices; ${hard ? `${spikeNote} ` : ""}the battery and the fleet are fictional. ${window.location.origin}/play/battery`;
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
    if (hard) ctx.fillText(spikeNote, 60, 600);
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
  "On Hard the battery keeps a backup reserve, every kWh you discharge wears it (a cost), and a grid emergency ends in an outage: keep the house lit, because a dark house costs money. After the day, replay the perfect battery's day beside yours.",
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
function Replay({ level, rules, mine, perfect, sun }: { level: GameLevel; rules: Rules; mine: Action[]; perfect: Action[]; sun?: number[] }) {
  const n = level.price.length;
  const hours = useMemo(() => level.ts_utc.map((t) => Number(clock(level.tz, t).slice(0, 2))), [level]);
  const segs = useMemo(() => explain(level.price, hours, perfect, rules, (i) => clock(level.tz, level.ts_utc[i]), sun), [level, hours, perfect, rules, sun]);
  const a = useMemo(() => simulate(level.price, mine, rules, sun).soc, [level, mine, rules, sun]);
  const b = useMemo(() => simulate(level.price, perfect, rules, sun).soc, [level, perfect, rules, sun]);
  const shown = useMemo(() => shownPrices(level.price, rules), [level, rules]);  // session 66: the price at the cursor, a spiked one labeled
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
      <p className="mb-2 text-xs text-muted">The same battery and rules, with every price known in advance. Its state of charge (accent) and yours (ink), kWh, over the day; the day&apos;s real price is the faint line behind, on its own scale{shown.some((s) => s.spike) ? ` (the emergency's prices are a ${SPIKE_LABEL}, so they are not drawn; the line below names them)` : ""}.</p>
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
        <strong>{clock(level.tz, level.ts_utc[cur])}</strong>: the perfect battery {seg ? `is ${verb(seg.a)} (${seg.text})` : ""}; you were {verb(mine[cur] ?? 0)}.{" "}
        <span className={shown[cur].spike ? "text-accent" : "text-muted"}>The price: {shown[cur].text}.</span>
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
function SettingsPanel({ draft, setDraft, difficulty, setDifficulty, addonsOn, setAddonsOn, available, level }: {
  draft: Record<keyof Settings, string>; setDraft: (d: Record<keyof Settings, string>) => void; difficulty: Difficulty; setDifficulty: (d: Difficulty) => void;
  addonsOn: AddonKey[]; setAddonsOn: (a: AddonKey[]) => void; available: Record<AddonKey, boolean>; level: GameLevel;
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
      {/* session 66: Hard's add-ons, optional switches, off by default; one that needs data the level does not hold is
          unavailable for it and says so */}
      {DIFFICULTIES[difficulty].addons ? (
        <fieldset className="mb-2 border-t border-rule pt-2">
          <legend className="float-left mr-2 font-semibold">Add-ons</legend>
          <p className="mb-1 text-xs text-muted">Optional, off by default, on Hard only. Each is a game rule, and a leaderboard ranks only plays with the same add-ons.</p>
          {ADDON_KEYS.map((k) => {
            const can = available[k], on = can && addonsOn.includes(k);
            return (
              <label key={k} className={`flex items-start gap-2 ${can ? "" : "opacity-70"}`}>
                <input type="checkbox" role="switch" aria-checked={on} checked={on} disabled={!can} className="mt-1"
                  onChange={(e) => setAddonsOn(e.target.checked ? [...addonsOn.filter((x) => x !== k), k] : addonsOn.filter((x) => x !== k))} />
                <span>
                  <strong>{ADDONS[k].label}</strong>: {ADDONS[k].what}.
                  {can && level.solar_source ? <span className="block text-xs text-muted">The shape for {level.date}: {level.solar_source}</span> : null}
                  {can ? null : <span className="block text-xs text-accent">Not available for {level.date}: the warehouse holds no solar shape for this day, and the game never fills one in.</span>}
                </span>
              </label>
            );
          })}
        </fieldset>
      ) : null}
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

/** Session 66: after a play, three plain lines: what you earned, what the perfect battery earned on the same day under
 * the same rules, and the one hour where you lost the most against it, with what it did then and at what price. Every
 * number is simulate()'s (the play's and the perfect plan's results, and worstHour over their earnings per interval). */
function EndLines({ level, rules, mine, perfect, big }: { level: GameLevel; rules: Rules; mine: Result; perfect: Result; big: boolean }) {
  const w = worstHour(level.price, mine, perfect, rules);
  const from = (i: number) => clock(level.tz, level.ts_utc[i]);
  const to = (i: number) => clock(level.tz, new Date(Date.parse(level.ts_utc[i]) + 15 * 60_000).toISOString());
  const did = !w ? "" : w.did === -1 ? "sold power" : w.did === 1 ? "charged up (bought power)" : w.outage ? "kept the house running, because the grid was down," : "waited";
  return (
    <ol className={`list-decimal space-y-1 pl-6 ${big ? "text-lg" : "text-base"}`} aria-label="Your day in three lines">
      <li>You {mine.score >= 0 ? "earned" : "lost"} <strong>{usd(Math.abs(mine.score))}</strong>.</li>
      <li>The perfect battery, which knew every price ahead of time, earned <strong>{usd(perfect.score)}</strong> on the same day with the same rules.</li>
      <li>
        {w ? (
          <>
            The hour you lost the most was {from(w.first)} to {to(w.last)}. The perfect battery {did} then, at an average price of{" "}
            <span className={w.price.spike ? "text-accent" : ""}>{w.price.text}</span>, and made {usd(w.perfect)} in that hour; you made {usd(w.mine)}.
          </>
        ) : "You matched the perfect battery in every hour."}
      </li>
    </ol>
  );
}

/** Why a play ended early, in words. Session 66: lights out costs money, and the note says what and why. */
function EarlyEnd({ mine, at }: { mine: Result; at: string }) {
  if (mine.why === "bankrupt") {
    return <p className="mt-1 text-sm text-accent" role="status">Out of money at {at}: below $0 the game ends (a game rule). Buying when power is dear costs more than the battery can earn back.</p>;
  }
  if (mine.why !== "lights_out") return null;
  return (
    <p className="mt-1 text-sm text-accent" role="status">
      Lights out at {at}: the battery ran dry in the outage, so the round ended there. A dark house costs money (a game rule): if the lights
      go out at any moment of the outage, you pay for the power the house needed in the whole outage, not only the part it missed. That is{" "}
      {mine.unservedKwh.toFixed(2)} kWh at USD {LIGHTS_OUT.usdPerMwh.toLocaleString("en-US")} per MWh, the value Texas&apos;s utility commission puts on power that is not delivered:{" "}
      {usd(mine.penalty)}. A home without power in a grid emergency is the outcome the battery exists to prevent. The outage needed{" "}
      {mine.outageNeedKwh.toFixed(2)} kWh from the battery; at its start the battery held {(mine.outageStartKwh ?? 0).toFixed(2)} kWh.
      {mine.money < 0 ? " The charge took your money below $0." : ""}
    </p>
  );
}

/** The price now, as a big number. Session 66: a spiked price carries its label and the real price beside it, on the
 * number itself (the text is lib/battery.ts's shownPrices). */
function PriceNow({ s, big }: { s: ShownPrice; big: boolean }) {
  const cut = s.text.indexOf(" ");
  return (
    <div className="mb-1 text-center">
      <span className={`tabular-nums ${big ? "text-3xl" : "text-xl"} ${s.spike ? "text-accent" : ""}`}>{s.text.slice(0, cut)}</span>{" "}
      <span className={`text-sm ${s.spike ? "text-accent" : "text-muted"}`}>{s.text.slice(cut + 1)}{s.spike ? "" : " now"}</span>
    </div>
  );
}

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
  // session 66: Hard's add-ons. One is on when it is switched on, the difficulty has add-ons, and the level holds what it
  // needs (rooftop solar: the day's solar shape); otherwise it is off, and the panel says why
  const [addonsOn, setAddonsOn] = useState<AddonKey[]>([]);
  const available: Record<AddonKey, boolean> = { solar: validSolar(level.solar, n) };
  const addonsKey = (DIFFICULTIES[difficulty].addons ? ADDON_KEYS.filter((k) => addonsOn.includes(k) && available[k]) : []).join(",");
  const addons = useMemo(() => (addonsKey ? addonsKey.split(",") : []) as AddonKey[], [addonsKey]);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  const rules = useMemo(() => rulesOf(settings, difficulty, addons), [settingsKey, difficulty, addons]);
  const preset = presetOf(settings, difficulty, addons);
  const sun = rules.solarKw > 0 ? level.solar : undefined;
  // session 63: on Hard the emergency's prices are the ones played and scored (a game rule); elsewhere the real prices
  const em = useMemo(() => emergencyOf(level.price, rules), [level, rules]);
  const P = em.prices;
  const vpp = useMemo(() => vppHour(P), [P]);
  // session 66: every price as it may be shown: a spiked one carries its label and the real price
  const labeled = useMemo(() => shownPrices(level.price, rules), [level, rules]);
  const best = useMemo(() => optimum(level.price, rules, sun), [level, rules, sun]);
  const perfect = useMemo(() => simulate(level.price, best.actions, rules, sun), [level, best, rules, sun]);
  const [tutorial, setTutorial] = useState(false);

  // the viewer's conveniences, from browser storage after the first render (absent or refused: the defaults)
  useEffect(() => {
    if (simple) return;  // session 63: the simple page always plays Normal with the default battery, and skips the tutorial
    const seen = load(TUTORIAL_KEY) === "seen";
    let saved: { settings?: unknown; difficulty?: unknown; addons?: unknown } | null = null;
    try { saved = JSON.parse(load(SETTINGS_KEY) ?? "null"); } catch { saved = null; }
    queueMicrotask(() => {
      if (!seen) setTutorial(true);
      if (saved && validSettings(saved.settings)) setDraft(toDraft(saved.settings));
      if (saved && (saved.difficulty === "easy" || saved.difficulty === "normal" || saved.difficulty === "hard")) setDifficulty(saved.difficulty);
      if (saved && validAddons(saved.addons, "hard")) setAddonsOn(saved.addons);
    });
  }, [simple]);
  const addonsOnKey = addonsOn.join(",");
  useEffect(() => { if (ok && !simple) save(SETTINGS_KEY, JSON.stringify({ settings, difficulty, addons: addonsOn })); }, [ok, settingsKey, difficulty, simple, addonsOnKey]); // eslint-disable-line react-hooks/exhaustive-deps
  const endTutorial = useCallback(() => { save(TUTORIAL_KEY, "seen"); setTutorial(false); }, []);

  // mutable game state, read by the animation loop
  const g = useRef({ t0: 0, idx: 0, held: [0, 0, 0], last: 0, soc: 0, money: START_MONEY, wear: 0, solar: 0, vppKwh: 0, actions: [] as Action[], control: 0 as Control, ended: false });
  const [hud, setHud] = useState({ idx: 0, soc: rules.start, money: START_MONEY, wear: 0, solar: 0, vppKwh: 0, control: 0 as Control });
  // session 66: the finished play is simulate()'s own result (the end screen reads every number from it)
  const [result, setResult] = useState<{
    mine: Result; actions: Action[]; rules: Rules; preset: string; settings: Settings; difficulty: Difficulty; addons: AddonKey[]; sun?: number[];
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
    ctx.stroke();
    // session 66: a spiked price is the game's, not the market's: it is drawn in the accent color, the real price
    // dashed beneath it, and the band says so
    let anySpike = false;
    for (let i = 0; i < shown; i++) {
      if (!labeled[i].spike) continue;
      anySpike = true;
      const x0 = x(i), x1 = Math.min(x0 + dx, nowX);
      ctx.strokeStyle = css("accent"); ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(x0, y(P[i])); ctx.lineTo(x1, y(P[i])); ctx.stroke();
      ctx.strokeStyle = css("ink"); ctx.lineWidth = 1.5; ctx.setLineDash([4, 3]); ctx.beginPath(); ctx.moveTo(x0, y(labeled[i].real)); ctx.lineTo(x1, y(labeled[i].real)); ctx.stroke(); ctx.setLineDash([]);
    }
    ctx.restore();
    if (anySpike && em.spike && pos >= em.spike.last + 1) {  // while the spike lasts, the label at the now line says it
      ctx.font = "11px system-ui, sans-serif";
      const notes = [SPIKE_LABEL, "dashed: the real price"];
      const nx = Math.max(42, x(em.spike.first) + 4), nw = Math.max(...notes.map((t) => ctx.measureText(t).width));
      ctx.fillStyle = css("panel"); ctx.fillRect(nx - 3, top + 15, nw + 6, 29);  // a plain ground, so the words do not cross the price line
      ctx.fillStyle = css("accent");
      notes.forEach((t, k) => ctx.fillText(t, nx, top + 26 + k * 13));
    }
    // the now line and the current price
    ctx.strokeStyle = css("accent"); ctx.lineWidth = 1.5; ctx.beginPath(); ctx.moveTo(nowX, top - 8); ctx.lineTo(nowX, bottom); ctx.stroke();
    const now = labeled[Math.min(n - 1, Math.floor(pos))];
    ctx.fillStyle = css("accent"); ctx.beginPath(); ctx.arc(nowX, y(now.value), 4, 0, Math.PI * 2); ctx.fill();
    ctx.font = "12px system-ui, sans-serif";
    // the label right of the now line where it fits, else left of it (narrow screens), never over the line. Session 66:
    // the label is the library's text; a spiked price's label and its real price go on the lines under the number
    const cut = now.text.indexOf(" ("), semi = now.text.indexOf("; ");
    const lines = cut < 0 ? [now.text] : [now.text.slice(0, cut), now.text.slice(cut + 1, semi + 1), now.text.slice(semi + 2)];
    const lw = Math.max(...lines.map((t) => ctx.measureText(t).width));
    const lx = nowX + 8 + lw <= w - 2 && !forecast ? nowX + 8 : nowX - 8 - lw;
    const ly = Math.max(top + 10, y(now.value) - 8) + (lines.length > 1 ? 44 : 0);
    if (lines.length > 1) { ctx.fillStyle = css("panel"); ctx.fillRect(lx - 3, ly - 12, lw + 6, lines.length * 14 + 4); }
    lines.forEach((t, k) => { ctx.fillStyle = k === 0 ? css("ink") : css("accent"); ctx.fillText(t, lx, ly + k * 14); });
  }, [level, n, vpp, forecast, P, em, labeled]);

  const finish = useCallback(async () => {
    cancelAnimationFrame(raf.current);
    const played = g.current.actions.slice(0, n);
    const actions: Action[] = [...played, ...new Array(Math.max(0, n - played.length)).fill(0)];  // after an early end nothing counts
    const r = simulate(level.price, actions, rules, sun);
    setResult({ mine: r, actions, rules, preset, settings, difficulty, addons, sun });
    setPhase("done");
    setControl(0);
    try {
      const res = await fetch("/api/play/finish", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ level: level.date, actions, settings, difficulty, addons }) });
      const j = await res.json();
      setServer(res.ok ? (Math.abs(j.score - Math.round(r.score * 10_000) / 10_000) < 1e-6 ? "Score verified by the server." : `The server scored this game ${usd(j.score)}.`) : `Not stored: ${j.error ?? res.status}`);
    } catch {
      setServer("Not stored: the server could not be reached.");
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [level, n, setControl, rules, preset, settingsKey, difficulty, addons, sun]);

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
      // session 66: only the intervals played so far (the rest of the day is not scored as idle before it happens)
      const r = simulate(level.price, s.actions, rules, sun, s.idx);
      s.soc = r.soc[r.soc.length - 1]; s.money = r.money; s.wear = r.wear; s.solar = r.solar; s.vppKwh = r.vppKwh;
      if (r.end !== null) s.ended = true;
    }
    draw(Math.min(n - 0.001, elapsed / per));
    setHud((h) => (h.idx !== s.idx || Math.abs(h.soc - s.soc) > 1e-9 ? { idx: s.idx, soc: s.soc, money: s.money, wear: s.wear, solar: s.solar, vppKwh: s.vppKwh, control: s.control } : h));
    if (s.idx >= n || s.ended) { finish(); return; }
    raf.current = requestAnimationFrame((t) => next.current(t));
  }, [n, level, draw, finish, rules, em, sun]);
  useEffect(() => { next.current = loop; }, [loop]);

  const start = () => {
    if (!ok) return;
    const t = performance.now();
    g.current = { t0: t, idx: 0, held: [0, 0, 0], last: t, soc: rules.start, money: START_MONEY, wear: 0, solar: 0, vppKwh: 0, actions: [], control: 0, ended: false };
    setHud({ idx: 0, soc: rules.start, money: START_MONEY, wear: 0, solar: 0, vppKwh: 0, control: 0 });
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
  const money = hud.money;  // session 66: simulate()'s own money: the roof's sales and a lights-out charge included
  const roof = useMemo(() => solarKwh(level.price, rules, sun), [level, rules, sun]);
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
      body: JSON.stringify({ level: level.date, actions: result.actions, nickname: nick.trim() || undefined, settings: result.settings, difficulty: result.difficulty, addons: result.addons }),
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
          <SettingsPanel draft={draft} setDraft={setDraft} difficulty={difficulty} setDifficulty={setDifficulty} addonsOn={addonsOn} setAddonsOn={setAddonsOn} available={available} level={level} />
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
            <button onClick={start} disabled={!ok} className="border border-accent bg-accent px-4 py-2 text-paper disabled:opacity-50">Play {level.date}, {DIFFICULTIES[difficulty].label}{addons.map((k) => `, with ${ADDONS[k].label.toLowerCase()}`).join("")}</button>
            {!tutorial ? <button onClick={() => setTutorial(true)} className="text-sm underline">How to play (30 seconds)</button> : null}
          </div>
        </div>
      ) : null}

      {phase !== "pick" ? (
        <div ref={board} className="scroll-mt-2">
          <div className="mb-1 flex flex-wrap items-baseline justify-between gap-2 text-sm">
            <span><strong>{level.title}</strong>, {level.date} ({GRIDS[level.grid].name}, {GRIDS[level.grid].zone} time), {DIFFICULTIES[difficulty].label}{addons.map((k) => `, with ${ADDONS[k].label.toLowerCase()}`).join("")}</span>
            <span aria-live="polite">{playing && hud.idx < n ? `${clock(level.tz, level.ts_utc[Math.min(n - 1, hud.idx)])}` : "end of day"}</span>
          </div>
          {inOutage ? (
            <div className="mb-1 border border-ink bg-panel px-2 py-1 text-sm" role="status">
              Outage (a game rule): the grid is down. Your house runs on its battery, {EMERGENCY.houseKw} kW{rules.solarKw > 0 ? " (the roof's power first)" : ""}. If the battery runs dry, the lights go out, the round ends,
              and you pay for the power the house needed in the whole outage ({usd((perfect.outageNeedKwh * rules.eta * LIGHTS_OUT.usdPerMwh) / 1000)}): a dark house in a grid emergency is what the battery is there to prevent.
            </div>
          ) : inSpike ? (
            <div className="mb-1 border border-accent bg-panel px-2 py-1 text-sm text-accent" role="status">
              Grid emergency (a game rule): the price is climbing toward the {usd(EMERGENCY.cap).replace(".00", "")}/MWh cap. This hour&apos;s price is a {SPIKE_LABEL}. Next the grid goes down for two hours: keep charge for the house.
            </div>
          ) : notice ? (
            <div className="mb-1 border border-accent px-2 py-1 text-sm text-accent" role="status">Fleet call in 15 minutes: the grid&apos;s dearest hour of the day. Keep charge to sell then.</div>
          ) : inVpp ? (
            <div className="mb-1 border border-accent bg-panel px-2 py-1 text-sm text-accent" role="status">
              Fleet call: discharge now to earn the bonus (a game rule modeled on ERCOT&apos;s ADER pilot; see the rules below).
            </div>
          ) : null}
          {simple || playing ? <PriceNow s={labeled[Math.min(n - 1, hud.idx)]} big={simple} /> : null}
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
                {rules.solarKw > 0 ? <div className="text-xs text-muted">roof: {(roof[Math.min(n - 1, hud.idx)] * 4).toFixed(1)} of {SOLAR.kw} kW now{playing && !inOutage && labeled[Math.min(n - 1, hud.idx)].value < 0 && hud.control !== 1 ? " (switched off: the price is below zero)" : ""}, {usd(hud.solar)} so far</div> : null}
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
          <EndLines level={level} rules={result.rules} mine={result.mine} perfect={perfect} big />
          <EarlyEnd mine={result.mine} at={at(result.mine.end)} />
          <div className="mt-3 flex flex-wrap gap-3">
            <button onClick={() => setPhase("pick")} className="border border-accent bg-accent px-5 py-3 text-lg text-paper">Play again</button>
            <Link href="/play/battery?more=1" className="self-center text-sm">More: the replay, the settings, Hard&apos;s emergency and the leaderboard</Link>
          </div>
        </div>
      ) : phase === "done" && result ? (
        <div className="mt-4 border border-rule p-3">
          <EndLines level={level} rules={result.rules} mine={result.mine} perfect={perfect} big={false} />
          <EarlyEnd mine={result.mine} at={at(result.mine.end)} />
          <p className="mt-2 text-sm">
            In detail: {usd(result.mine.cash)} in the market{result.mine.wear > 0 ? `, less ${usd(result.mine.wear)} of wear` : ""}{result.mine.bonus > 0 ? `, plus the fleet bonus ${usd(result.mine.bonus)}` : ""}{result.rules.solarKw > 0 ? `, plus ${usd(result.mine.solar)} for the roof's power` : ""}{result.mine.penalty > 0 ? `, less the lights-out charge ${usd(result.mine.penalty)}` : ""}.
            Your fleet of {FLEET.toLocaleString("en-US")} homes: <strong>{usd(result.mine.score * FLEET)}</strong>.
            The rules: {presetLabel(result.preset)}{perfect.score > 0 ? `; you made ${Math.round((result.mine.score / perfect.score) * 100)} percent of the perfect battery's earnings` : ""}. <span className="text-muted">{server}</span>
          </p>
          <p className="mt-2 max-w-3xl text-sm">
            On {level.date} the real-time price at {G.hub} peaked at {level.price[peak].toLocaleString("en-US", { maximumFractionDigits: 2 })} USD/MWh at {clock(level.tz, level.ts_utc[peak])} {G.zone} time and
            was lowest, {level.price[low].toLocaleString("en-US", { maximumFractionDigits: 2 })} USD/MWh, at {clock(level.tz, level.ts_utc[low])}. The dearest hour, the fleet call, began at {clock(level.tz, level.ts_utc[vpp.first])}. Knowing every
            price in advance, this battery would have {charged.length ? `charged ${list(charged)}` : "never charged"} and {discharged.length ? `discharged ${list(discharged)}` : "never discharged"}: buy when power is cheap,
            sell when it is dear, within {result.rules.kwh} kWh and {result.rules.kw} kW, losing {Math.round((1 - result.rules.eta ** 2) * 100)} percent of the energy on the round trip{result.rules.reserveKwh > 0 ? `, never below its ${result.rules.reserveKwh.toFixed(2)} kWh reserve` : ""}{result.rules.deg > 0 ? `, and paying ${usd(result.rules.deg)} of wear for each kWh it discharges` : ""}.
            The grid: {G.name}. Real batteries on the grid do this every day: see <Link href="/storage">storage</Link> and <Link href={G.href}>{G.page}</Link>.
            {level.grid === "ERCOT" && eventPageFor(level.date) ? <> What happened that day on the grid: <Link href={eventPageFor(level.date)!.href}>{eventPageFor(level.date)!.label}</Link>.</> : null}
          </p>
          <Replay level={level} rules={result.rules} mine={result.actions} perfect={best.actions} sun={result.sun} />
          <ShareCard level={level} score={result.mine.score} optimal={perfect.score} preset={result.preset} />
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
