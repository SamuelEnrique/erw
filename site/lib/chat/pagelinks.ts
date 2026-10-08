// Energy Research Warehouse (ERW) site, session 153: the files behind four pages that Ask ERCOT reads with its tool
// page_file (lib/chat/pagefiles.ts), each by the name an answer cites it by, and where each is shown on this site.
// Pure, no imports: the server's tool and the answer panel in the browser (components/ask/AskPanel.tsx) read the one list.

/** The file each page's figures are read from, as a citation names it (a "table" of the answer's sources). */
export const PAGE_FILES = {
  cost: "site/data/datacenter/index.json",
  capture: "site/data/seller/capture.json",
  shares: "site/data/curtailment/shares.json",
  texas: "site/data/curtailment/ercot.json",
  free: "site/data/curtailment/free_energy.json",
  worth: "site/data/curtailment/worth.json",
  resources: "site/data/resources/manifest.json",
} as const;
/** Where each of those files is shown on this site, for the link under an answer (components/ask/AskPanel.tsx). */
export const PAGE_FILE_HREF: Record<string, { href: string; what: string }> = {
  [PAGE_FILES.cost]: { href: "/cost-of-power", what: "What a datacenter pays" },
  [PAGE_FILES.capture]: { href: "/cost-of-power/seller", what: "What a generator earns" },
  [PAGE_FILES.shares]: { href: "/curtailment", what: "Curtailment" },
  [PAGE_FILES.texas]: { href: "/curtailment?grid=ercot", what: "Curtailment" },
  [PAGE_FILES.free]: { href: "/curtailment#free-energy", what: "Curtailment" },
  [PAGE_FILES.worth]: { href: "/curtailment#worth", what: "Curtailment" },
  [PAGE_FILES.resources]: { href: "/resources", what: "Where the resources are" },
};
