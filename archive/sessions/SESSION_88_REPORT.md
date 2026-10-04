# Session 88 report: what a battery saves a customer

**Built.** The review page `/battery/customer`: the reader types a peak demand, a demand charge, two energy rates and a battery's size, and the page works out the bill saved by shaving the peak and by shifting energy. Everything is computed in the browser. Nothing typed is sent or stored, and a test proves it with a real browser. The page says plainly that it uses the reader's own numbers, not ERW data. One deploy, with snapshots before and after: no number changed; the home page's battery tile was absent again for about a quarter of an hour after the deploy, as in session 87, and came back by itself (a second snapshot confirms it).

**Read these three first:**

1. **The proof found a real fault, and I fixed the page, not the test.** The first run of the browser proof counted 4 requests after typing. None carried anything typed: when the result appeared the page grew taller, the footer's links came into view, and the site's framework fetched those links' pages in advance. But the page says "nothing is sent", so 4 is a failure. The shared links no longer prefetch on this page (the list session 46 made for the lease tool). Second run: **0 requests** in the six seconds after typing, the address unchanged, no cookie, no stored key, and the result on the page equal to what the arithmetic gives.
2. **The proof runs on every push.** `site/scripts/check-no-request.mjs` is a step of the workflow's site check. On the runner a missing browser fails the step, so a green run means the proof was made there too. It was (run 37179333295).
3. **The home page's battery tile blanked again after the deploy** (05:22 UTC, "not held" where USD 81.40 per kW stands), the second deploy in a row. The value did not change and it returned when the page's cache turned, a quarter of an hour later; a second snapshot at 05:40 UTC shows 81.40 and no number different. This is the fault described in session 87's report; it needs a fix before the next deploy, and so **session 89, which is documents only, is not merged to main tonight.**

Energy Research Warehouse (ERW), session 88, on the old laptop (`samueloldlaptop`, data role), 2026-10-04 from about 03:42 (the arithmetic, the page and the proof script, written while session 83's pull ran) to 05:45 UTC, unattended. **Model spend: USD 0.00.** No pull, no table, no model call, no force push. No instruction arrived for session 84. The data lock was not taken.

## To finish

```bash
# Nothing is left half done. What is yours:

# 1. The page is in review. To open it: site/lib/release.ts,  "/battery/customer": "live".

# 2. The Vercel token (session 77's step, still open): until it is set the page cannot be opened on production even
#    in the internal view. I read it, and ran the browser proof, on this machine's build.

# 3. To run the proof yourself on a built site (it needs Chrome or Edge; nothing is installed for it):
cd site && npm run build && npx next start -p 3049 &
node scripts/check-no-request.mjs http://localhost:3049
```

## In plain words

### What the page does

"What a battery saves a customer." A business that pays a demand charge can lower its bill with a battery two ways: discharge through its peak, so the highest demand on the meter is lower; and charge when energy is cheap, discharge when it is dear.

Nine fields. Six are the reader's bill and battery and start empty: peak demand (kW), demand charge (USD per kW a month), the energy rate in peak hours and in off-peak hours (USD per kWh), battery power (kW) and battery energy (kWh). Three have starting values the reader can change, and the page says they are starting values, not data: how long the peak lasts (2 hours), the days a month the battery runs (21), the round trip (86 percent). **Until every field holds a number the page shows no result and says how many are missing. No number is assumed for the reader.**

The arithmetic, in `site/lib/customerbattery.ts`, which imports nothing:

- **The peak.** The battery must discharge through all the hours of the peak. What comes off the peak is the smallest of three: the battery's power, its energy over the peak's hours, and the peak itself. Times the demand charge, that is the saving, per month. The page says which of the three set it.
- **The energy.** On each day it runs, the battery puts its energy out in the peak hours and takes that much, over the round trip, back in off-peak. If that pays, it is the saving. **If it does not pay at the reader's rates, the page says so**, runs the battery only for the peak, and counts the energy lost on the round trip as a cost. It is shown as a negative number, never rounded up to nothing.
- **The year** is the month twelve times, and the page says it knows no season.

An example, the one the proof types: a 500 kW peak, USD 18 per kW, 22 and 9 cents per kWh, a 200 kW battery holding 800 kWh, a 4-hour peak, 22 days, 85 percent. The battery takes 200 kW off the peak (USD 3,600 a month) and shifts 800 kWh a day (USD 2,008 a month): USD 5,608 a month, USD 67,302 a year. Those are the example's numbers, not a finding.

Two folds state what it assumes (the peak falls in the peak-rate hours; the battery knows when the peak comes and is full; one cycle a day; one demand charge on one monthly peak; every month alike) and what it leaves out (what the battery costs, taxes and riders, solar on the same meter, the shape of the load). The source line reads: "Source: none. No ERW table is read on this page and no number on it comes from the warehouse."

### "Uses your own numbers, not ERW data", stated plainly

At the top of the page, in a box, before the fields:

> **This page uses your own numbers, not ERW data.** The warehouse holds no customer's bill and no retail tariff for this page; every figure below is arithmetic on what you type.
>
> **Nothing you type is sent or stored.** The arithmetic runs in your browser. Close or reload the page and the numbers are gone.

### The proof that nothing is sent

Three layers, each a test:

| Layer | What it shows | Result |
|---|---|---|
| In the code | The calculator and its arithmetic name no way to send or store: no fetch, no XMLHttpRequest, no beacon, no WebSocket, no storage, no cookie, no form, no link, no router. They import only React and each other. The page itself is static: it reads no table, no cookie, no address parameter | pass |
| In node | The arithmetic runs a thousand times with every sending function replaced by a counter | 0 calls |
| **In a real browser** | Edge here, Chrome on the runner, driven through the browser's own debugging protocol with no package installed. It opens the built page, waits until the page has gone quiet, types a number into each of the nine fields as a person would, presses Enter and Tab, waits five more seconds, and counts | **0 requests, 0 WebSockets; the address, the cookies and the stored keys unchanged; the result on the page is the arithmetic's** |

The first run of the third layer, before the fix:

```
requests while typing and for 6.3 s after: 4
  Fetch http://localhost:3049/terms?_rsc=...
  Fetch http://localhost:3049/data?_rsc=...
  Fetch http://localhost:3049/terms?_rsc=...
  Fetch http://localhost:3049/data?_rsc=...
check-no-request: FAILED: 4 request(s) were made after typing began
```

After it:

```
before typing: the result block read "waiting"; 28 requests had loaded the page
typed: {"peakKw":"500","demandCharge":"18","peakRate":"0.22","offPeakRate":"0.09","batteryKw":"200","batteryKwh":"800","peakHours":"4","days":"22","roundTrip":"85"}
shown: {"month":"$5,608","year":"$67,302","demand":"$3,600","energy":"$2,008"}
requests while typing and for 6.3 s after: 0
address, cookies and stored keys unchanged: http://localhost:3049/battery/customer, 0 localStorage keys, 0 sessionStorage keys
check-no-request: passed: typing into the page made no request and stored nothing
```

What the proof does not cover: a browser extension, or the network between the reader and the site, can see a page; and the 28 requests that load the page (its code and styles) happen before anything is typed.

### The deploy, and every difference

One push, `task/088-battery-customer`; the checks passed (run 37179333295: tests, site build, the route check, the browser proof) and the workflow merged it into `main` as `7fd3da7`. Snapshots of the 20 live pages before (05:14 UTC) and after (05:22 UTC).

**55 differences. No number changed; one was absent.**

| Where | Differences | What |
|---|---|---|
| All 20 pages | 20 | The menu gains one greyed item: "What a battery saves a customer in review" |
| `/` | 5 | **The battery tile: its checked number `bs|grid=ercot&dur=4&strat=foresight&mw=100&fom=22&ds=6783357|l12_kw:total` (81.40) gone, "USD 81.40 per kW" became "not held per kW", and the tile's sentence lost its dates** (one number key and four lines of text, each changed line counted as it was and as it is) |
| `/` | 30 | The six latest real-time prices and their lines of text: the site's own 15-minute refresh (12 number keys, 18 lines of text) |

**The confirming snapshot, 05:40 UTC, after the page's cache turned: 50 differences, and the battery tile is not among them.** It reads 81.40 again; the count of checked numbers is 4,098, as before the deploy. The 50 are the greyed menu item on the 20 pages and the home page's own refresh of the six latest prices (12 number keys, 18 lines of text). The tile was absent from the deploy at 05:21 until the cache turned, between 05:36 and 05:39 UTC.

## Tests and checks

| Check | Result |
|---|---|
| `tests/test_session88.py` | 11 tests pass: the saving on known numbers; what limits the peak shaved; when shifting does not pay; a field is a number or it is nothing (a rate typed in cents, a negative size, "1e3", "NaN" give no result); the three layers above; the page's plain statements; the shared links do not prefetch on this page |
| The browser proof, here | pass, 0 requests (Edge) |
| The browser proof, on the runner | pass (a missing browser would have failed the step) |
| The whole suite, here | 545 tests; one old failure (`test_session49`, known since session 82) |
| Site: types, build, route check on this machine | exit 0 each; `/battery/customer` answers 200 in the internal view and the in-review page to a visitor |

## Errors and decisions

- **The proof failed first** (above). The fix is one word in a list that already existed for this purpose (`NO_PREFETCH` in `site/components/SiteLink.tsx`).
- **Decision: the proof drives a real browser with nothing installed.** The site has no browser-testing package and adding one is a dependency for one check. Node speaks the browser's debugging protocol directly.
- **Decision: strict on the runner, plain elsewhere.** On a machine with no browser the script says "NOT PROVEN" and exits 0; on the runner it fails. So no green run can hide an unmade proof.
- **Decision: the six fields of the reader's own bill start empty.** A filled-in example would sit on the page looking like data.
- **Decision: in the Tools menu**, beside the severance calculators: it is a calculator on the reader's inputs, like them.

## For Samuel

1. **The home tile on deploy** (session 87's report, "For Samuel", 1). Two deploys in a row now. I would fix it before anything else is pushed to main.
2. **What is the page for?** As built it answers "what is this battery worth on my bill". It does not say whether the battery pays for itself: it knows no cost. One more field (the battery's price) and one line (years to pay back) would; I left it out because you asked for the bill saved.
