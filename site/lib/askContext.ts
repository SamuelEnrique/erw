// Energy Research Warehouse (ERW) site, session 92: how a view of the site opens Ask ERCOT with its period and
// settings. A view links to /ask/ercot?from=<its path>&title=<its name>&s_<setting>=<value>...; the page reads the
// address back into the context it sends with each question (lib/chat/ercot.ts cleans it again on the server).
// No imports: the page, the link component and the tests read this file as it is.

export type AskContext = { view: string; title?: string; settings?: Record<string, string> };

const clean = (v: string, n: number) => v.replace(/[^\x20-\x7E]/g, " ").replace(/\s+/g, " ").trim().slice(0, n);

/** The address that opens Ask ERCOT from a view. Settings with an empty value are left out. */
export function askHref(c: AskContext, question?: string): string {
  const p = new URLSearchParams({ from: c.view });
  if (c.title) p.set("title", c.title);
  for (const [k, v] of Object.entries(c.settings ?? {})) if (String(v).trim()) p.set(`s_${k}`, String(v));
  if (question) p.set("q", question);
  return `/ask/ercot?${p.toString()}`;
}

/** The context an address carries; null when it names no view (or a view that is not a path of the site). */
export function contextOf(sp: Record<string, string | string[] | undefined>): AskContext | null {
  const from = typeof sp.from === "string" ? sp.from : "";
  if (!/^\/[A-Za-z0-9/_-]{0,80}$/.test(from)) return null;
  const settings: Record<string, string> = {};
  for (const [k, v] of Object.entries(sp)) {
    if (!k.startsWith("s_") || typeof v !== "string") continue;
    const key = clean(k.slice(2), 24).replace(/[^A-Za-z0-9 _-]/g, ""), val = clean(v, 60);
    if (key && val && Object.keys(settings).length < 10) settings[key] = val;
  }
  const title = typeof sp.title === "string" ? clean(sp.title, 80) : "";
  return { view: from, ...(title ? { title } : {}), ...(Object.keys(settings).length ? { settings } : {}) };
}
