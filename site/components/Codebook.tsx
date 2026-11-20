// Chain 630 (part D1): the variables of each table a method note documents, from the codebook's metadata
// (warehouse/metadata/variables/, drawn into site/data/codebook_methods.json by warehouse/codebook/build_docs.py --site).
// Public tables only. At 768 px and wider a table; narrower, one block a column, so the page never scrolls sideways.
import codebook from "@/data/codebook_methods.json";

type Entry = { table: string; row: string; read: string; columns: [string, string, string, string, string][] };
const BOOK = codebook as unknown as Record<string, Entry[]>;

export function codebookFor(slug: string): Entry[] {
  return BOOK[slug] ?? [];
}

export function Codebook({ slug }: { slug: string }) {
  const entries = codebookFor(slug);
  if (!entries.length) return null;
  return (
    <section className="mt-10" aria-labelledby="codebook-heading" data-codebook>
      <h2 id="codebook-heading" className="mb-2 border-b border-rule pb-1 text-xl">Variables</h2>
      {entries.map((e) => (
        <div key={e.table} className="mb-8" data-codebook-table={e.table}>
          <h3 className="mt-6 mb-1 text-base font-semibold">
            <code className="font-mono">{e.table}</code>
          </h3>
          {e.row ? <p className="mb-2 text-sm">{e.row}</p> : null}
          <table className="hidden w-full border-collapse text-sm md:table">
            <thead>
              <tr className="bg-panel text-left">
                <th className="border border-rule px-2 py-1">Name</th>
                <th className="border border-rule px-2 py-1">Label</th>
                <th className="border border-rule px-2 py-1">Unit</th>
                <th className="border border-rule px-2 py-1">Type</th>
                <th className="border border-rule px-2 py-1">
                  <span title={e.read ? `Read from the table on ${e.read}` : undefined}>Values</span>
                </th>
              </tr>
            </thead>
            <tbody>
              {e.columns.map(([name, label, unit, type, values]) => (
                <tr key={name} className="align-top">
                  <td className="border border-rule px-2 py-1"><code className="font-mono">{name}</code></td>
                  <td className="border border-rule px-2 py-1">{label}</td>
                  <td className="border border-rule px-2 py-1">{unit}</td>
                  <td className="border border-rule px-2 py-1">{type}</td>
                  <td className="border border-rule px-2 py-1 [overflow-wrap:anywhere]">{values}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <dl className="md:hidden">
            {e.columns.map(([name, label, unit, type, values]) => (
              <div key={name} className="border-t border-rule py-2 text-sm">
                <dt>
                  <code className="font-mono">{name}</code>
                  <span className="ml-2 text-xs">{[type, unit && unit !== "none" ? unit : ""].filter(Boolean).join(", ")}</span>
                </dt>
                <dd>{label}</dd>
                {values ? <dd className="[overflow-wrap:anywhere] text-xs">{values}</dd> : null}
              </div>
            ))}
          </dl>
        </div>
      ))}
    </section>
  );
}
