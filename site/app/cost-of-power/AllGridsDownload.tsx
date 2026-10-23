"use client";
// Session 793 (chain 065): the hub table's rows, as shown (the sort and the filters as set), downloaded as a CSV made here
// from the page's own figures, as session 724 gave the node list. A cell the page draws in words ("license needed", "not
// held", "no capacity market") is written as those words, never a number. No new route, no read.
export type HubDownloadRow = (string | number | null)[];
export function AllGridsDownload({ head, columns, rows }: { head: string[]; columns: string[]; rows: HubDownloadRow[] }) {
  const download = () => {
    const cell = (v: string | number | null) => (v === null ? "" : typeof v === "number" ? String(v) : /[",]/.test(v) ? `"${v.replace(/"/g, '""')}"` : v);
    const lines = [...head.map((h) => `# ${h}`), columns.join(","), ...rows.map((r) => r.map(cell).join(","))];
    const url = URL.createObjectURL(new Blob([lines.join("\n") + "\n"], { type: "text/csv" }));
    const a = document.createElement("a");
    a.href = url; a.download = "erw_allgrids_hubs_and_zones.csv";
    document.body.appendChild(a); a.click(); a.remove(); URL.revokeObjectURL(url);
  };
  return (
    <button type="button" onClick={download} className="mb-2 border border-rule px-2 py-1 text-sm" data-hub-download="1">
      Download these {rows.length.toLocaleString("en-US")} rows (CSV)
    </button>
  );
}
