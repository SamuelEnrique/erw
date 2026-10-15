"use client";
// Session 293: the teacher's copy prints as it is shown (the browser's own print; nothing is sent).
export function PrintButton({ label = "Print" }: { label?: string }) {
  return <button type="button" onClick={() => window.print()} className="border px-3 py-1 text-sm print:hidden">{label}</button>;
}
