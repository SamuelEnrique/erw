"use client";
// Chain 302 (session 7201): a download made when it is asked for. The rows shown, as CSV, are built in the browser on
// the click and handed over as a file: no request, and nothing of the file in the page until then. (Drawn as a link
// whose address holds the file, the 122 rules' CSV put about a megabyte into the tab's HTML: scripts/
// test-large-load-render.mjs measures the section.) The Python and the Stata reader of that file are a few lines each,
// and are made the same way.
import type { ReactNode } from "react";

export function Download({ make, name, type = "text/csv", mark, children }: { make: () => string; name: string; type?: string; mark: Record<string, string>; children: ReactNode }) {
  const go = () => {
    const url = URL.createObjectURL(new Blob([make()], { type }));
    const a = document.createElement("a");
    a.href = url; a.download = name;
    document.body.appendChild(a); a.click(); a.remove(); URL.revokeObjectURL(url);
  };
  return <button type="button" onClick={go} className="underline" data-llr-download={name} {...mark}>{children}</button>;
}
