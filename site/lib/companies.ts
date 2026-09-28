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
