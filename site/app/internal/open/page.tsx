import type { Metadata } from "next";

// Session 177: the internal view's door without a token in any address (docs/release-gate.md). A form that POSTs the
// token in the request's body to /internal/unlock, which sets the same two cookies the link sets. The old link,
// /internal/unlock?token=<INTERNAL_COSTS_TOKEN>, works exactly as it did. This page holds no secret and says nothing
// about what the internal view opens; it is not indexed, never cached, and sends no referrer (next.config.ts gives
// every /internal address those headers).
export const metadata: Metadata = { title: "Internal view", robots: { index: false, follow: false }, referrer: "no-referrer" };
export const dynamic = "force-dynamic";

const SAID: Record<string, string> = {
  no: "That token was not accepted. Nothing was changed.",
  wait: "Too many tries from this address in an hour. The link you were given still works; or try again later.",
};

export default async function Open({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const sp = await searchParams;
  const said = typeof sp.state === "string" ? SAID[sp.state] : undefined;
  return (
    <div className="max-w-md" data-internal-open="1" data-no-usage>
      <h1 className="mb-2 text-3xl">Internal view</h1>
      <p className="mb-4 text-sm text-muted">For the people reviewing the site. Paste the token you were given.</p>
      {said ? <p className="mb-4 border border-rule bg-panel p-2 text-sm" role="status" data-open-state="1">{said}</p> : null}
      <form method="post" action="/internal/unlock" className="space-y-3 text-sm" autoComplete="off">
        <label className="block">
          <span className="mb-1 block text-xs text-muted">Token</span>
          <input name="token" type="password" required minLength={24} maxLength={200} autoComplete="off" spellCheck={false}
            className="w-full border border-rule bg-paper px-2 py-2 font-mono" />
        </label>
        {/* a field people do not see; a form that fills it is a bot, and nothing is checked */}
        <div aria-hidden="true" style={{ position: "absolute", left: "-10000px", width: "1px", height: "1px", overflow: "hidden" }}>
          <label>Website <input name="website" type="text" tabIndex={-1} autoComplete="off" /></label>
        </div>
        <button type="submit" className="border border-rule bg-panel px-4 py-2">Open the internal view</button>
      </form>
      <p className="mt-4 text-xs text-muted">Sets two cookies in this browser for 90 days, used only to show the pages in review. <a href="/internal/lock">Lock</a> removes them.</p>
    </div>
  );
}
