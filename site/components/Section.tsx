// A titled block of a page.
export function Section({ title, children, id, aside }: { title: string; children: React.ReactNode; id?: string; aside?: React.ReactNode }) {
  return (
    <section id={id} className="mb-10">
      <div className="mb-3 flex flex-wrap items-baseline justify-between gap-2 border-b border-rule pb-1">
        <h2 className="text-xl">{title}</h2>
        {aside ? <div className="text-xs text-muted">{aside}</div> : null}
      </div>
      {children}
    </section>
  );
}
