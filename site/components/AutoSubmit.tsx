"use client";
// A select that submits its GET form when it changes (session 18). The form still has a submit
// button, so it works without JavaScript.
//
// Session 9601 (chain 620, the browser read of 20 November 2026): after the browser's back button the list reads what
// the page shows. A browser puts a form's last state back when a page of its history is shown again, and this list
// takes its value from the page only once (defaultValue), so after two choices and one step back the address and the
// page went back and the list kept the later choice (on /queues/places: the table PacifiCorp, the list Duke). When the
// page is shown, which "pageshow" says both for a page loaded again and for one that comes back whole from the
// browser's cache, the list is set to the value the page was drawn with.
import { useEffect, useRef } from "react";

export function AutoSubmitSelect({ name, value, options, label }: { name: string; value: string; options: { value: string; label: string }[]; label: string }) {
  const ref = useRef<HTMLSelectElement>(null);
  useEffect(() => {
    const put = () => { const s = ref.current; if (s && s.value !== value) s.value = value; };
    put();
    window.addEventListener("pageshow", put);
    return () => window.removeEventListener("pageshow", put);
  }, [value]);
  return (
    <label className="flex flex-col text-xs text-muted">
      {label}
      <select
        ref={ref}
        name={name}
        defaultValue={value}
        onChange={(e) => e.currentTarget.form?.requestSubmit()}
        className="mt-1 border border-rule bg-panel px-2 py-1 text-sm text-ink"
      >
        {options.map((o) => (
          <option key={o.value} value={o.value}>
            {o.label}
          </option>
        ))}
      </select>
    </label>
  );
}
