// Session 10231 (tests/test_audit_explore_7.py): one interconnection figure's hover words, as lib/explore/source.ts
// writes them. Run from site/: node --import ./scripts/tsx-register.mjs ../tests/audit_explore_7_source.mjs
import path from "node:path";
import { pathToFileURL } from "node:url";

const { sourceOf } = await import(pathToFileURL(path.join(process.cwd(), "lib", "explore", "source.ts")).href);
console.log(sourceOf("series|iso_queue_statistics|caiso:queue_2023|positions_entered|2023-01-01T00:00:00Z", "CAISO's queue, entry year 2023"));
