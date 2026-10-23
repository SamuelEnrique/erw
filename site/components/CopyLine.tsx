"use client";
// Energy Research Warehouse (ERW) site, session 1015 (chain 070): one line of code with a control that copies it, for
// /data's "Use the ERW in your tools". The line scrolls inside its own frame on a narrow screen; the control says what it
// copies to a screen reader, and "Copied" for two seconds once it has.
import { useState } from "react";

export function CopyLine({ line }: { line: string }) {
  const [done, setDone] = useState(false);
  const copy = () => {
    void navigator.clipboard?.writeText(line).then(() => {
      setDone(true);
      window.setTimeout(() => setDone(false), 2000);
    });
  };
  return (
    <div className="flex items-start gap-2" data-copy-line="">
      <code className="block min-w-0 flex-1 overflow-x-auto whitespace-pre font-mono text-xs">{line}</code>
      <button type="button" onClick={copy} aria-label={`Copy: ${line}`} className="shrink-0 border border-muted bg-white px-1 text-xs text-ink hover:border-accent">
        {done ? "Copied" : "Copy"}
      </button>
    </div>
  );
}
