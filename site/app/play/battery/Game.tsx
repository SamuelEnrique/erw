"use client";
// Session 38: the home battery game. One canvas for the prices, plain React for the rest; mouse, touch and keys.
// The prices are real (ERCOT HB_HUBAVG, every 15-minute interval of one operating day); the battery, the home, the
// brand and the fleet are fictional and say so. Each interval's action is the control held for most of its time.
import Link from "next/link";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { BATTERY, FLEET, optimum, simulate, step, vppHour, type Action } from "@/lib/battery";
import type { ScoreRow } from "@/lib/game";

export type GameLevel = { slug: string; date: string; title: string; why: string; ts_utc: string[]; price: number[] };

const DURATION_MS = 90_000;
const TZ = "America/Chicago";
const HHMM = new Intl.DateTimeFormat("en-US", { timeZone: TZ, hour: "2-digit", minute: "2-digit", hourCycle: "h23" });
const clock = (ts: string) => HHMM.format(new Date(ts));
const usd = (v: number) => `${v < 0 ? "-" : ""}$${Math.abs(v).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
const css = (name: string) => (typeof window === "undefined" ? "#6B665E" : getComputedStyle(document.documentElement).getPropertyValue(`--color-${name}`).trim() || "#6B665E");

type Phase = "pick" | "play" | "done";
type Control = 1 | 0 | -1;

/** Runs of one action in a list of intervals, as "HH:MM to HH:MM" (the end is the last interval's end). */
function runs(actions: Action[], ts: string[], which: Action): string[] {
  const out: string[] = [];
  let i = 0;
  while (i < actions.length) {
    if (actions[i] !== which) { i++; continue; }
    let j = i;
    while (j + 1 < actions.length && actions[j + 1] === which) j++;
    const end = new Date(Date.parse(ts[j]) + 15 * 60_000).toISOString();
    out.push(`${clock(ts[i])} to ${clock(end)}`);
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

export function Game({ levels, top: firstTop }: { levels: GameLevel[]; top: ScoreRow[] }) {
  const [phase, setPhase] = useState<Phase>("pick");
  const [pick, setPick] = useState(0);
  const level = levels[pick];
  const n = level.price.length;
  const vpp = useMemo(() => vppHour(level.price), [level]);
  const best = useMemo(() => optimum(level.price), [level]);

  // mutable game state, read by the animation loop
  const g = useRef({ t0: 0, idx: 0, held: [0, 0, 0], last: 0, soc: BATTERY.kwh * BATTERY.startShare, cash: 0, vppKwh: 0, actions: [] as Action[], control: 0 as Control });
  const [hud, setHud] = useState({ idx: 0, soc: BATTERY.kwh * BATTERY.startShare, cash: 0, vppKwh: 0, control: 0 as Control });
  const [result, setResult] = useState<{ score: number; cash: number; bonus: number; actions: Action[] } | null>(null);
  const [server, setServer] = useState<string>("");
  const [top, setTop] = useState<ScoreRow[]>(firstTop);
  const [topFor, setTopFor] = useState<string>(levels[0].date);
  const [nick, setNick] = useState("");
  const [posted, setPosted] = useState<string>("");
  const canvas = useRef<HTMLCanvasElement>(null);
  const raf = useRef(0);

  const setControl = useCallback((c: Control) => { g.current.control = c; setHud((h) => ({ ...h, control: c })); }, []);

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
    const seen = level.price.slice(0, shown);
    let lo = Math.min(0, ...seen), hi = Math.max(10, ...seen);
    const pad = (hi - lo) * 0.12; lo -= pad; hi += pad;
    const top = 18, bottom = h - 34;
    const y = (v: number) => bottom - ((v - lo) / (hi - lo)) * (bottom - top);
    const span = 24; // intervals visible behind the now line (six hours)
    const nowX = w * 0.72;
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
    // the VPP hour, once it has started
    if (pos >= vpp.first) {
      ctx.fillStyle = "rgba(140, 21, 21, 0.08)";
      ctx.fillRect(x(vpp.first), top, (vpp.last + 1 - vpp.first) * dx, bottom - top);
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
      if (xx < 40 || xx > w - 20 || i > pos + 1) continue;
      ctx.fillText(clock(level.ts_utc[i]).slice(0, 2), xx - 6, h - 6);
    }
    // the price line so far
    ctx.save(); ctx.beginPath(); ctx.rect(40, 0, w - 40, h); ctx.clip();
    ctx.strokeStyle = css("ink"); ctx.lineWidth = 2; ctx.beginPath();
    for (let i = 0; i < shown; i++) {
      const x0 = x(i), yy = y(level.price[i]);
      if (i === 0) ctx.moveTo(x0, yy); else ctx.lineTo(x0, yy);
      ctx.lineTo(x0 + dx, yy);
    }
    ctx.stroke(); ctx.restore();
    // the now line and the current price
    ctx.strokeStyle = css("accent"); ctx.lineWidth = 1.5; ctx.beginPath(); ctx.moveTo(nowX, top - 8); ctx.lineTo(nowX, bottom); ctx.stroke();
    const cur = level.price[Math.min(n - 1, Math.floor(pos))];
    ctx.fillStyle = css("accent"); ctx.beginPath(); ctx.arc(nowX, y(cur), 4, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = css("ink"); ctx.font = "12px system-ui, sans-serif";
    ctx.fillText(`${cur.toLocaleString("en-US", { maximumFractionDigits: 2 })} USD/MWh`, Math.min(nowX + 8, w - 120), Math.max(top + 10, y(cur) - 8));
  }, [level, n, vpp]);

  const finish = useCallback(async () => {
    cancelAnimationFrame(raf.current);
    const actions = g.current.actions.slice(0, n);
    const r = simulate(level.price, actions);
    setResult({ score: r.score, cash: r.cash, bonus: r.bonus, actions });
    setPhase("done");
    setControl(0);
    try {
      const res = await fetch("/api/play/finish", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ level: level.date, actions }) });
      const j = await res.json();
      setServer(res.ok ? (Math.abs(j.score - Math.round(r.score * 10_000) / 10_000) < 1e-6 ? "Score verified by the server." : `The server scored this game ${usd(j.score)}.`) : `Not stored: ${j.error ?? res.status}`);
    } catch {
      setServer("Not stored: the server could not be reached.");
    }
  }, [level, n, setControl]);

  const loop = useCallback((now: number) => {
    const s = g.current;
    const per = DURATION_MS / n;
    const elapsed = now - s.t0;
    const dt = Math.min(100, now - s.last);
    s.last = now;
    s.held[s.control + 1] += dt; // [discharge, idle, charge]
    const target = Math.min(n, Math.floor(elapsed / per));
    while (s.idx < target) {
      const [dis, idle, chg] = s.held;
      const a: Action = chg > idle && chg > dis ? 1 : dis > idle && dis > chg ? -1 : 0;
      const r = step(s.soc, a, level.price[s.idx]);
      s.soc = r.soc; s.cash += r.cash;
      if (s.idx >= vpp.first && s.idx <= vpp.last) s.vppKwh += r.delivered;
      s.actions.push(a);
      s.idx++;
      s.held = [0, 0, 0];
    }
    draw(Math.min(n - 0.001, elapsed / per));
    setHud((h) => (h.idx !== s.idx || Math.abs(h.soc - s.soc) > 1e-9 ? { idx: s.idx, soc: s.soc, cash: s.cash, vppKwh: s.vppKwh, control: s.control } : h));
    if (s.idx >= n) { finish(); return; }
    raf.current = requestAnimationFrame(loop);
  }, [n, level, vpp, draw, finish]);

  const start = () => {
    const t = performance.now();
    g.current = { t0: t, idx: 0, held: [0, 0, 0], last: t, soc: BATTERY.kwh * BATTERY.startShare, cash: 0, vppKwh: 0, actions: [], control: 0 };
    setHud({ idx: 0, soc: g.current.soc, cash: 0, vppKwh: 0, control: 0 });
    setResult(null); setServer(""); setPosted("");
    setPhase("play");
    raf.current = requestAnimationFrame(loop);
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

  const inVpp = phase === "play" && hud.idx >= vpp.first && hud.idx <= vpp.last;
  const vppDone = hud.idx > vpp.last;
  const lit = hud.vppKwh > 0;
  const post = async () => {
    if (!result) return;
    setPosted("Posting...");
    const res = await fetch("/api/play/score", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ level: level.date, actions: result.actions, nickname: nick.trim() || undefined }) });
    const j = await res.json();
    if (!res.ok) { setPosted(j.error ?? `HTTP ${res.status}`); return; }
    setTop(j.top); setTopFor(level.date); setPosted("Posted.");
  };

  // the debrief, from the level's prices and the optimum
  const peak = level.price.indexOf(Math.max(...level.price)), low = level.price.indexOf(Math.min(...level.price));
  const charged = runs(best.actions, level.ts_utc, 1), discharged = runs(best.actions, level.ts_utc, -1);

  return (
    <div className="select-none">
      {phase === "pick" ? (
        <div>
          <p className="mb-2 text-sm">Pick a day. Everyone plays the same level on the same day.</p>
          <div className="mb-3 grid gap-2 sm:grid-cols-2">
            {levels.map((l, i) => (
              <button key={l.slug} onClick={() => setPick(i)} className={`border p-2 text-left text-sm ${i === pick ? "border-accent" : "border-rule"}`}>
                <span className="font-semibold">{l.title}</span> <span className="text-muted">{l.date}</span>
                <span className="block text-xs text-muted">{l.why}</span>
              </button>
            ))}
          </div>
          <button onClick={start} className="border border-accent bg-accent px-4 py-2 text-paper">Play {level.date}</button>
        </div>
      ) : null}

      {phase !== "pick" ? (
        <div>
          <div className="mb-1 flex flex-wrap items-baseline justify-between gap-2 text-sm">
            <span><strong>{level.title}</strong>, {level.date} (Central time)</span>
            <span aria-live="polite">{phase === "play" && hud.idx < n ? `${clock(level.ts_utc[Math.min(n - 1, hud.idx)])}` : "end of day"}</span>
          </div>
          {inVpp ? (
            <div className="mb-1 border border-accent bg-panel px-2 py-1 text-sm text-accent" role="status">
              Fleet call: the grid is at its dearest hour. Discharge now to earn a bonus (a game rule, not a real program&apos;s terms).
            </div>
          ) : null}
          <canvas ref={canvas} className="block h-[260px] w-full touch-none" aria-label="The day's real-time price so far; the future is hidden" />
          <div className="mt-2 grid grid-cols-[1fr_auto] items-center gap-3 text-sm">
            <div>
              <div className="mb-1 flex justify-between text-xs text-muted"><span>State of charge</span><span>{hud.soc.toFixed(2)} of {BATTERY.kwh} kWh</span></div>
              <div className="h-3 w-full border border-rule bg-panel"><div className="h-full bg-[var(--color-down)]" style={{ width: `${(hud.soc / BATTERY.kwh) * 100}%` }} /></div>
            </div>
            <div className="text-right"><span className="text-xs text-muted">Cash</span><div className="font-mono text-lg" aria-live="off">{usd(hud.cash)}</div></div>
          </div>
          <div className="mt-2 flex items-center gap-3">
            <div className="grid grid-cols-10 gap-[3px]" aria-label={lit ? "The fleet map is lit: your battery answered the call" : "The fleet map"} role="img">
              {Array.from({ length: 50 }, (_, i) => <span key={i} className="block h-2 w-2 rounded-full" style={{ background: lit ? "var(--color-accent)" : "var(--color-rule)" }} />)}
            </div>
            <span className="text-xs text-muted">{lit ? `Fleet lit: ${hud.vppKwh.toFixed(2)} kWh delivered in the call hour.` : vppDone ? "The fleet call has passed." : "The fleet map lights when your battery answers the call."}</span>
          </div>
          {phase === "play" ? (
            <div className="mt-3 grid grid-cols-2 gap-3">
              <button {...hold(1)} className={`touch-none border px-3 py-4 text-base ${hud.control === 1 ? "border-[var(--color-down)] bg-[var(--color-down)] text-paper" : "border-[var(--color-down)] text-[var(--color-down)]"}`}>Hold to charge (buy)</button>
              <button {...hold(-1)} className={`touch-none border px-3 py-4 text-base ${hud.control === -1 ? "border-accent bg-accent text-paper" : "border-accent text-accent"}`}>Hold to discharge (sell)</button>
              <p className="col-span-2 text-xs text-muted">Keys: C or the down arrow to charge, S or the up arrow to sell. Let go to idle.</p>
            </div>
          ) : null}
        </div>
      ) : null}

      {phase === "done" && result ? (
        <div className="mt-4 border border-rule p-3">
          <p className="text-lg">You earned <strong>{usd(result.score)}</strong>{result.bonus > 0 ? <> (the fleet bonus {usd(result.bonus)})</> : null}. Your fleet of {FLEET.toLocaleString("en-US")} homes: <strong>{usd(result.score * FLEET)}</strong>.</p>
          <p className="text-sm">With perfect foresight the same battery would have earned {usd(best.score)}{best.score > 0 ? `; you made ${Math.round((result.score / best.score) * 100)} percent of it` : ""}. <span className="text-muted">{server}</span></p>
          <p className="mt-2 max-w-3xl text-sm">
            On {level.date} the real-time price at ERCOT&apos;s hub average peaked at {level.price[peak].toLocaleString("en-US", { maximumFractionDigits: 2 })} USD/MWh at {clock(level.ts_utc[peak])} Central time and
            was lowest, {level.price[low].toLocaleString("en-US", { maximumFractionDigits: 2 })} USD/MWh, at {clock(level.ts_utc[low])}. The dearest hour, the fleet call, began at {clock(level.ts_utc[vpp.first])}. Knowing every
            price in advance, this battery would have {charged.length ? `charged ${list(charged)}` : "never charged"} and {discharged.length ? `discharged ${list(discharged)}` : "never discharged"}: buy when power is cheap,
            sell when it is dear, within 13.5 kWh and 5 kW, losing a tenth of the energy on the round trip. Real batteries on the grid do this every day: see <Link href="/storage">storage</Link> and <Link href="/grid/ercot">ERCOT&apos;s grid page</Link>.
          </p>
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

      <div className="mt-6">
        <h3 className="mb-1 text-base">Leaderboard, {topFor}</h3>
        {top.length ? (
          <ol className="list-decimal pl-6 text-sm">
            {top.map((r, i) => (
              <li key={i}>{r.nickname ?? <span className="text-muted">anonymous</span>}: {usd(r.score)}{r.optimal_score > 0 ? <span className="text-muted"> ({Math.round((r.score / r.optimal_score) * 100)} percent of perfect)</span> : null}</li>
            ))}
          </ol>
        ) : <p className="text-sm text-muted">No scores yet for this level.</p>}
      </div>
    </div>
  );
}
