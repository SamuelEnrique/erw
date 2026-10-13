// Session 212: the three lines the seller page's two CSV downloads share (months.csv/route.ts, tables.csv/route.ts).
export const text = (msg: string, status: number) => new Response(msg + "\n", { status, headers: { "Content-Type": "text/plain; charset=utf-8" } });
export const cell = (v: unknown): string => {
  if (v === null || v === undefined) return "";
  const s = String(v);
  return /[",\n\r]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
};
export const csv = (lines: string[], name: string) => new Response(lines.join("\n") + "\n", {
  status: 200,
  headers: { "Content-Type": "text/csv; charset=utf-8", "Content-Disposition": `attachment; filename="${name}"`, "Cache-Control": "no-store" },
});
