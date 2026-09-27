"use client";
// A select that submits its GET form when it changes (session 18). The form still has a submit
// button, so it works without JavaScript.
export function AutoSubmitSelect({ name, value, options, label }: { name: string; value: string; options: { value: string; label: string }[]; label: string }) {
  return (
    <label className="flex flex-col text-xs text-muted">
      {label}
      <select
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
