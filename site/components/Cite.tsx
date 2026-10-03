import { SiteLink as Link } from "@/components/SiteLink";  // session 46: no prefetch on /severance/lease
import { catalogue } from "@/lib/data";
import { attempt } from "@/lib/supabase";
import { TIER_LABEL, TIER_TITLE, isModelExtracted } from "@/lib/tiers";

// Supabase tables that are not ERW tables (they have no row in the coverage table)
const LIVE_ONLY: Record<string, string> = {
  latest_prices: "warehouse/connectors/latest_prices.py, every 15 minutes",
  catalogue: "warehouse/metadata/coverage.csv",
};

// The citation under every chart and table: the ERW tables it reads and, from the
// catalogue, the source report behind each. Session 28: a table whose provenance tier is
// model_extracted carries a short label, so a reader can tell a model's reading from a source. Session 71: while /data is
// in review (lib/release.ts) a visitor sees each table name as plain text, with no "in review" label.
export async function Cite({ tables, note }: { tables: string[]; note?: string }) {
  const cat = await attempt(catalogue);
  const byName = new Map(cat.ok ? cat.data.map((r) => [r.table_name, r]) : []);
  const uniq = Array.from(new Set(tables));
  return (
    <p className="mt-2 text-xs text-muted">
      Source:{" "}
      {uniq.map((t, i) => {
        const r = byName.get(t);
        return (
          <span key={t}>
            {i > 0 ? "; " : ""}
            {LIVE_ONLY[t] ? (
              <>
                Supabase table <code className="font-mono">{t}</code> ({LIVE_ONLY[t]})
              </>
            ) : (
              <>
                ERW table{" "}
                <Link href={`/data#${t}`} className="font-mono" gate="plain">
                  {t}
                </Link>
                {isModelExtracted(r?.tier) ? (
                  <Link href="/data/standard" title={TIER_TITLE.model_extracted} className="ml-1 rounded border border-rule px-1 font-sans not-italic" gate="plain">
                    {TIER_LABEL.model_extracted}
                  </Link>
                ) : null}
                {r?.source_report ? (
                  <>
                    {" "}
                    (source report <code className="font-mono">{r.source_report}</code>)
                  </>
                ) : null}
              </>
            )}
          </span>
        );
      })}
      {note ? <>. {note}</> : null}.
    </p>
  );
}
