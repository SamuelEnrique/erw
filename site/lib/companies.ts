// Session 26: company names as /companies anchors and /deals cross-links read them (usable on server and client).

/** A company name as the /companies anchor and the /deals cross-link read it: lower case, no punctuation or legal suffix. */
export function companyKey(name: string): string {
  return name
    .toLowerCase()
    .replace(/\(.*?\)/g, " ")
    .replace(/[^a-z0-9 ]+/g, " ")
    .replace(/\b(inc|llc|ltd|corp|corporation|co|plc|lp|sa|ag|gmbh|limited|holdings)\b/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

/** The anchor of a company's row on /companies. */
export function companyAnchor(name: string): string {
  return "co-" + companyKey(name).replace(/ /g, "-");
}

/** Session 581: a company's website as the table links it. energy_companies writes most as a bare domain ("amperon.co"),
 * which a link reads as a page of this site (/amperon.co, a 404): a bare domain is opened over https. A value that is
 * not an address ("not disclosed") is no link: null. An address with its scheme is kept as written. */
export function websiteHref(website: string): string | null {
  const w = website.trim();
  if (/^https?:\/\/\S+$/i.test(w)) return w;
  if (/^(?:www\.)?[a-z0-9-]+(?:\.[a-z0-9-]+)*\.[a-z]{2,}(?:\/\S*)?$/i.test(w)) return `https://${w}`;
  return null;
}
