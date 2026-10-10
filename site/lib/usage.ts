// track("scenario compared") records one usage count for the page in view: the path, the tool's name, the event and
// the UTC day, with no cookie and nothing that identifies a person (docs/methods/usage_counts.md). It never blocks and
// never throws; call it from a click or change handler: import { track } from "@/lib/usage".
// (Do not call it from inside a box that tells the reader nothing typed there is sent: a count is a request.)
//
// Energy Research Warehouse (ERW) site, session 177. The four events: "tool opened" (a page view, sent by
// components/Usage.tsx), "input changed" (a form control inside a tool changed, sent by the same component, once a
// control a page view), "scenario compared" (a tool compared two cases: the tool calls track itself) and "download".
//
// What is sent: POST /api/usage {"event": ..., "path": the address's path}. No query string, no referrer, no
// identifier, no value of any input. The server names the tool from the path. Nothing is read from or written to a
// cookie, localStorage or any other browser storage.
//
// Nothing is sent at all when the browser says not to be tracked: Do Not Track ("1") or Global Privacy Control.

export type UsageEvent = "tool opened" | "input changed" | "scenario compared" | "download";

/** Does this browser ask not to be tracked? Then nothing is sent. */
export function optedOut(nav: { doNotTrack?: string | null; globalPrivacyControl?: boolean; msDoNotTrack?: string | null } | undefined, win?: { doNotTrack?: string | null }): boolean {
  if (!nav) return true;
  const dnt = nav.doNotTrack ?? win?.doNotTrack ?? nav.msDoNotTrack;
  return dnt === "1" || dnt === "yes" || nav.globalPrivacyControl === true;
}

/** Record one event. `detail.path` names another page of this site than the one in view (rarely needed). */
export function track(event: UsageEvent, detail?: { path?: string }): void {
  try {
    if (typeof window === "undefined" || typeof navigator === "undefined") return;
    if (optedOut(navigator as Parameters<typeof optedOut>[0], window as unknown as { doNotTrack?: string | null })) return;
    const body = JSON.stringify({ event, path: detail?.path ?? window.location.pathname });
    if (typeof navigator.sendBeacon === "function") {
      if (navigator.sendBeacon("/api/usage", new Blob([body], { type: "text/plain;charset=UTF-8" }))) return;
    }
    void fetch("/api/usage", { method: "POST", body, headers: { "Content-Type": "text/plain;charset=UTF-8" }, keepalive: true, credentials: "same-origin", referrerPolicy: "no-referrer" }).catch(() => {});
  } catch {
    /* a count that cannot be sent is not sent */
  }
}

// The pages that tell the reader nothing typed is sent. On them only the page view is counted: no "input changed", no
// "download", so no request follows anything the reader does there (scripts/check-no-request.mjs proves it for
// /battery/customer). QUIET names the pages whose whole tool makes that promise; PROMISE is the sentence itself, so a
// page that carries it in a box (the contract boxes of the cost-of-power pages) is treated the same way without a list.
export const QUIET = ["/battery/customer", "/severance", "/learn/bill"];
export const PROMISE = /sent or stored|never sent|nothing is uploaded/i;
export const quiet = (path: string) => QUIET.some((q) => path === q || path.startsWith(q + "/"));

const FILE = /\.(csv|do|py)$/i;
/** Is this link a download? One that carries `download`, goes to /api/download or a download route, or names a .csv,
 * .do or .py file. */
export function isDownload(a: { hasDownload: boolean; href: string }, origin: string): boolean {
  if (a.hasDownload) return true;
  try {
    const u = new URL(a.href, origin);
    return u.pathname.startsWith("/api/download") || u.pathname.endsWith("/download") || FILE.test(u.pathname);
  } catch {
    return false;
  }
}
