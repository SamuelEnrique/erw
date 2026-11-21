// Energy Research Warehouse (ERW) site, session 9601 (chain 620, the browser read of 20 November 2026): after the
// browser's back button, a list that submits itself reads what the page shows.
//
//   node scripts/check-back-button.mjs <base-url>
//
// On each page named below two choices are made one after the other, as a reader makes them (the list's own change
// handler submits the form), then the browser goes back once and forward once. At each step every list of the form
// must read the value its own address gives it (or the page's default where the address names none, read from a
// fresh load of the same address). Before the session's mend the list kept the later choice: on /queues/places the
// table went back to PacifiCorp and the list "Queue B" read Duke.
// Needs the internal view (INTERNAL_COSTS_TOKEN): every page is in review.
import { withBrowser } from "./browser.mjs";

const base = (process.argv[2] ?? "").replace(/\/$/, "");
if (!base) { console.error("usage: node scripts/check-back-button.mjs <base-url>"); process.exit(2); }

// page, then two choices: [the list's name, the place of the option to take among its options]
const PAGES = [
  ["/queues/places", ["a", 8], ["b", 6]],
  ["/storage/places", ["a", 5], ["b", 9]],
  ["/curtailment/where-when", ["fuel", 1], ["year", 3]],
  ["/ai-energy", ["sort", 2], ["m", 3]],
];
let failed = 0, passed = 0;
const check = (ok, what) => { if (ok) passed += 1; else failed += 1; console.log(`${ok ? "ok  " : "FAIL"} ${what}`); };

const code = await withBrowser(async ({ go, evaluate, unlock, sleep }) => {
  await unlock(base);
  const lists = () => evaluate(`Object.fromEntries([...document.querySelectorAll('main form select[name]')].map((s) => [s.name, s.value]))`);
  const where = () => evaluate("location.pathname + location.search");
  const settled = async (before) => { for (let i = 0; i < 80; i += 1) { await sleep(150); const now = await where().catch(() => before); if (now !== before && (await evaluate("document.readyState").catch(() => "")) === "complete") break; } await sleep(700); };
  const choose = async (name, place) => {
    const before = await where();
    const took = await evaluate(`(() => { const s = document.querySelector('main form select[name=${JSON.stringify(name)}]'); if (!s) return null; const o = s.options[Math.min(${place}, s.options.length - 1)]; if (o.value === s.value) return 'same'; Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype, 'value').set.call(s, o.value); s.dispatchEvent(new Event('change', { bubbles: true })); return o.value; })()`);
    if (took && took !== "same") await settled(before);
    return took;
  };
  // what a fresh load of an address gives each list: the page's own word on what it shows
  const fresh = async (address) => { await go("about:blank"); await go(`${base}${address}`); await sleep(900); return lists(); };
  const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);

  for (const [page, one, two] of PAGES) {
    await go("about:blank");
    await go(`${base}${page}`);
    await sleep(900);
    const first = await choose(one[0], one[1]);
    const after1 = await where();
    const second = await choose(two[0], two[1]);
    const after2 = await where();
    check(first && second && after1 !== after2, `${page}: two choices made, each moving the address (${one[0]}=${first}, ${two[0]}=${second})`);
    await evaluate("history.back()");
    await settled(after2);
    const backAt = await where(), backLists = await lists();
    await evaluate("history.forward()");
    await settled(backAt);
    const fwdAt = await where(), fwdLists = await lists();
    const wantBack = await fresh(backAt), wantFwd = await fresh(fwdAt);
    check(backAt === after1, `${page}: back once returns to the first choice's address`);
    check(same(backLists, wantBack), `${page}: after the back button the lists read what the page shows (${JSON.stringify(wantBack)}); seen ${JSON.stringify(backLists)}`);
    check(fwdAt === after2 && same(fwdLists, wantFwd), `${page}: after forward the lists read what the page shows; seen ${JSON.stringify(fwdLists)}`);
  }
  return failed ? 1 : 0;
});
if (code === null) { console.log("not proven here: no Chrome or Edge on this machine"); process.exit(0); }
console.log(failed ? `${failed} of ${failed + passed} failed` : `the back button: ${passed} of ${passed} checks pass`);
process.exit(code);
