// Session 28 (Ben Domingue's review, item 6): the provenance tier of a table, as coverage.csv and the
// catalogue give it (docs/datastandard.md, "Provenance tiers"). One place for the words the site uses.
export const TIER_LABEL: Record<string, string> = {
  source: "source",
  derived: "derived",
  model_extracted: "model-extracted",
};

export const TIER_TITLE: Record<string, string> = {
  source: "As the publisher published it, reshaped only",
  derived: "Computed by the ERW from other tables; method in the methods pages",
  model_extracted: "At least one field was written by a model reading news, filings or the web, not published by a source; check it against the linked source",
};

export const isModelExtracted = (tier: string | null | undefined) => tier === "model_extracted";
