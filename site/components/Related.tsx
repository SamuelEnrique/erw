// The "Related" line at the end of a data page (session 21), from site/lib/pages.ts.
import { SiteLink as Link } from "@/components/SiteLink";  // session 67: every link passes the release gate
import { PAGES } from "@/lib/pages";

export function Related({ href }: { href: string }) {
  const page = PAGES.find((p) => p.href === href);
  const rel = (page?.related ?? []).map((h) => PAGES.find((p) => p.href === h)).filter((p) => p !== undefined);
  if (!rel.length) return null;
  return (
    <p className="mt-10 border-t border-rule pt-3 text-sm">
      Related:{" "}
      {rel.map((p, i) => (
        <span key={p.href}>
          {i > 0 ? ", " : ""}
          <Link href={p.href}>{p.label}</Link>
        </span>
      ))}
    </p>
  );
}
