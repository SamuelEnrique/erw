// An acronym with its definition on hover (session 21). `first` links it to its entry in the
// glossary on /about: each page links the first use of each acronym.
import { SiteLink as Link } from "@/components/SiteLink";  // session 67: every link passes the release gate
import { GLOSSARY, glossaryId } from "@/lib/glossary";

export function Term({ t, first = false, children }: { t: keyof typeof GLOSSARY | string; first?: boolean; children?: React.ReactNode }) {
  const title = GLOSSARY[t];
  const text = children ?? t;
  if (!title) return <>{text}</>;
  return first ? (
    <Link href={`/about#${glossaryId(t)}`} title={title} className="underline decoration-dotted">
      {text}
    </Link>
  ) : (
    <abbr title={title} className="no-underline">
      {text}
    </abbr>
  );
}
