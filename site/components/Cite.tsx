import Link from "next/link";
import { catalogue } from "@/lib/data";
import { attempt } from "@/lib/supabase";

// Supabase tables that are not ERW tables (they have no row in the coverage table)
const LIVE_ONLY: Record<string, string> = {
  latest_prices: "warehouse/connectors/latest_prices.py, every 15 minutes",
  catalogue: "warehouse/metadata/coverage.csv",
};

// The citation under every chart and table: the ERW tables it reads and, from the
// catalogue, the source report behind each.
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
                <Link href={`/data#${t}`} className="font-mono">
                  {t}
                </Link>
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
