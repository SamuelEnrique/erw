# The release gate

Energy Research Warehouse (ERW), session 67. From this session a tool on the public site is open to visitors only once Samuel has approved it. The whole menu stays visible, so a visitor sees everything that exists.

**This is a curtain for visitors, not security.** The API routes and the data are exactly as they were: Supabase's public rows are still public, the Redivis dataset is still public, and anyone who knows a table's name can read it. The gate decides what the site's pages show a visitor, nothing more. Nothing confidential may rely on it. Licensed data is kept out of the site by other means (the internal tables are never loaded for the anon key and never displayed).

## The one list

`site/lib/release.ts` gives every page a status, one line each:

- `live`: open to every visitor.
- `review`: listed in the menu, greyed and not clickable; its address answers the in-review page.

To open or lock a tool, change its one line and push. A path takes the status of the longest entry that is the path itself or a parent of it (`/grid/ercot` reads `/grid/ercot`, else `/grid`); `/` matches only the home page. A path with no entry is in review, so a new page is closed until someone opens it.

**Live at launch (session 67):** the home page `/`, `/cost-of-power/battery`, `/cost-of-power/seller`, `/network`, `/storage`, `/about`, `/terms`, and the methods pages those tools link to (`/data/methods/battery_stack`, `/data/methods/cost_of_power`, `/data/methods/grid_network`, `/data/methods/storage`).

**In review:** everything else, the price board included: `/board`, `/markets`, `/cost-of-power` (the buyer's tab), `/prices`, `/explorer/ercot-peak-premium`, `/grid` and the seven grid pages, `/mix`, `/curtailment`, `/emissions`, `/consumption`, `/map`, `/datacenters`, `/companies`, `/policy`, `/deals`, `/events`, `/tour`, `/learn/problems`, `/learn/bill`, `/play/battery`, `/severance`, `/severance/lease`, `/digest`, `/roundup`, `/subscribe`, `/data`, `/data/standard`, the other methods pages, `/analysis`, `/ask`, `/reports`.

## What a visitor sees

- **The menu and every in-page link.** A link to a page in review is drawn as greyed text with a small "in review" label. It is not a link: it cannot be clicked or reached by keyboard. A dropdown whose items are all in review still opens and shows them. Every link of the site passes through one component (`site/components/SiteLink.tsx`); links inside rendered markdown (the methods pages, the digest on the home page) are handled in `site/lib/markdown.ts`.
- **A direct address** to a page in review answers a short page at the same address: the tool's name, "This tool is in review and will open when it is approved", and links to the live tools. It is marked noindex (a robots meta tag and an `X-Robots-Tag` header) and carries none of the tool's numbers. `site/proxy.ts` does this before the page is rendered; the page is `site/app/in-review/page.tsx`.

## The internal view

Visiting `/internal/unlock?token=<INTERNAL_COSTS_TOKEN>` (the token already set on Vercel and in `.env`; no new secret) sets two cookies for 90 days and goes to the home page:

- `erw_internal`, httpOnly: a SHA-256 digest of the token, never the token. The proxy opens the pages in review only when it matches.
- `erw_view`, readable by the page's own script: it only tells the menu and the links to draw themselves as they were before the gate. It opens nothing.

In the internal view the menu is as it was, with a small "internal view" mark and a "lock" link beside it, so the difference is visible. `/internal/lock` clears both cookies. A wrong or missing token answers 404. The pages a server renders and caches are always the visitor's view; an internal browser redraws its links after the page loads.

The unlock address carries the token in its query, as `/internal/costs` does. Open it from a private note, not from a shared document, and do not post it.

**Since session 177 there is a door with no token in any address: `/internal/open`.** It is a form: paste the token, press "Open the internal view". The token goes in the request's body to `POST /internal/unlock`, which sets the same two cookies and goes to the home page. Nothing of the token is put in an address, a log or the page. A wrong token returns to the form; after ten wrong tries in an hour from one address the form asks to wait (a right token is never refused, and the link above is not limited). `/internal/costs`, `/internal/ask` and `/internal/usage` open with the internal cookie, so they need no `?token=` either (the old addresses with `?token=` still work). Every `/internal` address is sent `Cache-Control: private, no-store`, `Referrer-Policy: no-referrer` and `X-Robots-Tag: noindex`.

The link above works exactly as before until the owner confirms the form. Retiring it, and rotating the token afterwards, are the owner's steps (`docs/reviews/2026-10-10-security.md`, H1).

## Not behind the gate

- `/api/*`: the game's API (`/api/play/*`), `/api/ask`, the download and entity routes, subscribe, confirm and unsubscribe. An unsubscribe link in an email keeps working.
- `/internal/*`: each has its own token.
- `/severance/finder/download` (a route handler), Next's own files and static files.
- The scheduled jobs (the daily run, the 15-minute prices, the hourly network, the Roundup): none of them reads a page of the site, so none is affected. The hourly network job writes an object to Supabase Storage, which the live `/network` page reads.

One consequence to know: the digest and Roundup emails link to `/digest` and `/roundup`, which are in review. A subscriber who follows such a link sees the in-review page until those pages are opened.

## The checks

- `site/scripts/check-routes.mjs` runs twice. With the internal cookie it covers every page as before (status, "undefined", "no data" against the baseline). Without it, as a visitor, it asserts that each live page opens as itself, that each page in review shows the in-review page marked noindex with no number on it, that the home page's menu names every page with the ones in review greyed and not linked, and that an API route is not behind the gate.
- `site/scripts/check-values.mjs` reads the pages with the internal cookie, so it still checks the numbers of every page.
- `.github/workflows/code-branch.yml` gives the local build it tests a throwaway token of its own, so the checks can unlock it; that is not a secret and is not the production token. Against the live site as a baseline, a page that answers the in-review page is treated as having no baseline.
