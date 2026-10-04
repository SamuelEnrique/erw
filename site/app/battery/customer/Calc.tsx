"use client";
// Session 88: the calculator of /battery/customer. Everything here happens in the reader's browser. The fields live in
// this component's memory only: no form is submitted, nothing is put in the address, no request is made and nothing
// is stored (scripts/check-no-request.mjs drives a real browser through this page and counts the requests: none).
// The arithmetic is lib/customerbattery.ts, which imports nothing.
import { useState } from "react";
import { FIELDS, qty, readAll, saving, usd } from "@/lib/customerbattery";

const field = "w-full border border-rule bg-white px-2 py-1 text-sm";

export function Calc() {
  const [text, setText] = useState<Record<string, string>>(() => Object.fromEntries(FIELDS.map((f) => [f.key, f.start ?? ""])));
  const r = readAll(text);
  const s = r.ok ? saving(r.x) : null;
  const x = r.ok ? r.x : null;
  const bad = (k: string) => !r.ok && r.missing.includes(k) && text[k].trim() !== "";
  return (
    <div className="grid gap-8 lg:grid-cols-[300px_minmax(0,1fr)]">
      <aside>
        <section className="mb-4 bg-paper px-4 py-4" aria-label="Your numbers">
          <h2 className="mb-1 font-serif text-lg text-accent">Your numbers</h2>
          <p className="mb-3 text-xs text-muted">From your own bill and your own battery quote. Nothing here leaves this page.</p>
          <div className="space-y-3 text-sm">
            {FIELDS.map((f) => (
              <label key={f.key} className="block">
                <span className="font-semibold">{f.label}</span> <span className="text-xs text-muted">{f.unit}</span>
                <input
                  type="text" inputMode="decimal" autoComplete="off" name={f.key} data-field={f.key} value={text[f.key]} className={field}
                  aria-invalid={bad(f.key) ? "true" : undefined}
                  onChange={(e) => setText((t) => ({ ...t, [f.key]: e.target.value }))}
                />
                <span className={`block text-xs ${bad(f.key) ? "text-accent" : "text-muted"}`}>{bad(f.key) ? `Not a number this page can use (${f.min} to ${qty(f.max)}).` : f.hint}</span>
              </label>
            ))}
          </div>
        </section>
      </aside>

      <div className="min-w-0" aria-live="polite">
        {!s || !x ? (
          <p className="mb-6 border border-rule bg-paper px-3 py-2 text-sm" role="status" data-result="waiting">
            Fill in every field to see what the battery saves. {!r.ok ? `${r.missing.length} of ${FIELDS.length} still needed.` : ""} No number is assumed for you.
          </p>
        ) : (
          <>
            <p className="mb-6 max-w-3xl font-serif text-xl leading-snug" data-result="summary">
              On your numbers, a {qty(x.batteryKw)} kW battery holding {qty(x.batteryKwh)} kWh ({qty(s.hours, 1)} hours) lowers the bill by{" "}
              <span data-n="month">{usd(s.monthSaved)}</span> a month, <span data-n="year">{usd(s.yearSaved)}</span> a year:{" "}
              <span data-n="demand">{usd(s.demandSaved)}</span> a month from a lower peak and <span data-n="energy">{usd(s.energySaved)}</span> a month from moving energy.
            </p>
            <div className="mb-10 grid gap-6 sm:grid-cols-3">
              <div className="border-t-2 border-accent pt-2">
                <div className="text-xs uppercase tracking-wide text-muted">Saved a year</div>
                <div className="font-serif text-3xl">{usd(s.yearSaved)}</div>
                <div className="text-xs text-muted">{usd(s.monthSaved)} a month, twelve months alike.</div>
              </div>
              <div className="border-t-2 border-accent pt-2">
                <div className="text-xs uppercase tracking-wide text-muted">From shaving the peak</div>
                <div className="font-serif text-3xl">{usd(s.demandSaved)}<span className="text-base text-muted"> a month</span></div>
                <div className="text-xs text-muted">{qty(s.shavedKw, 1)} kW off a {qty(x.peakKw)} kW peak; the demand charge was {usd(s.demandBefore)} a month.</div>
              </div>
              <div className="border-t-2 border-accent pt-2">
                <div className="text-xs uppercase tracking-wide text-muted">From shifting energy</div>
                <div className="font-serif text-3xl">{usd(s.energySaved)}<span className="text-base text-muted"> a month</span></div>
                <div className="text-xs text-muted">{qty(s.dischargedKwh)} kWh a day out at the peak rate, {qty(s.chargedKwh)} kWh a day in at the off-peak rate, {qty(x.days)} days.</div>
              </div>
            </div>

            <section className="mb-10">
              <h2 className="mb-3 border-b border-rule pb-1 font-serif text-xl text-accent">How the two numbers are made</h2>
              <ul className="max-w-3xl list-disc space-y-2 pl-5 text-sm">
                <li>
                  <strong>The peak.</strong> To lower your peak the battery must discharge through all {qty(x.peakHours, 1)} hours of it. Its power allows {qty(x.batteryKw)} kW;
                  its energy allows {qty(x.batteryKwh / x.peakHours, 1)} kW for that long; your peak is {qty(x.peakKw)} kW. The smallest of the three is what comes off:{" "}
                  <strong>{qty(s.shavedKw, 1)} kW</strong>, set by {s.limit === "power" ? "the battery's power" : s.limit === "energy" ? "the battery's energy" : "your peak itself"}.
                  At {usd(x.demandCharge)} per kW that is {usd(s.demandSaved)} a month.
                </li>
                <li>
                  <strong>The energy.</strong>{" "}
                  {s.shifts ? (
                    <>Each day it runs, the battery puts out {qty(s.dischargedKwh)} kWh in the peak hours and takes in {qty(s.chargedKwh)} kWh off-peak (more, because of the round
                      trip). That is {usd(s.shiftPerDay)} a day, {usd(s.energySaved)} over {qty(x.days)} days.</>
                  ) : (
                    <>At your rates moving energy does not pay: each kWh out at the peak rate costs more than it saves once the round trip is counted (the peak rate would
                      have to pass ${qty(s.breakEvenRate, 3)} per kWh). So the battery is run only for the peak, {qty(s.cyclesForPeak)} kWh a day, and the energy it loses
                      on the way is a cost: {usd(s.energySaved)} a month.</>
                  )}
                </li>
                <li><strong>The year</strong> is the month twelve times. It knows no season.</li>
              </ul>
            </section>
          </>
        )}
      </div>
    </div>
  );
}
