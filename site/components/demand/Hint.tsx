// Session 152: a short placeholder with a hover. The page face of /demand carries no method or limitations prose:
// what explained a chart or a table there is the hover of a few words here, and the method itself is the Method note.
export function Hint({ words, why }: { words: string; why: string }) {
  return <span className="cursor-help border-b border-dotted border-muted text-muted" title={why} data-hint="1">{words}</span>;
}
