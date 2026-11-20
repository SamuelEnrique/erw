// Energy Research Warehouse (ERW) site, ruling alternatives of /supply (session 7726, 17 November 2026; wip/alt-supply-*
// branches, not a default on main). The page's own library (lib/supply.ts) run on its committed file (data/supply.json),
// so that the figures under the other choice are pinned with the site's code. On wip/alt-supply-2: PJM against MISO,
// their burn rows over the weeks both hold (burnPair), and each grid's own newest week as main's one column shows it.
//   node --import ./scripts/tsx-register.mjs scripts/alt-supply-figures.mjs
import fs from "node:fs";

const S = await import("../lib/supply.ts");
const file = JSON.parse(fs.readFileSync(new URL("../data/supply.json", import.meta.url), "utf8"));
const own = (id) => { const r = file.rows.find((x) => x.id === id); return r?.last ?? null; };
process.stdout.write(JSON.stringify({
  built: file.built, pair: S.burnPair(file, "pjm", "miso"),
  main: { pjm_gas: own("burn-pjm-natural-gas"), miso_gas: own("burn-miso-natural-gas"), pjm_coal: own("burn-pjm-coal"), miso_coal: own("burn-miso-coal") },
}));
