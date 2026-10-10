// Energy Research Warehouse (ERW) site, session 170: human labels for a template's parameter names and values on the
// /analysis gallery ("ERCOT North Hub", not HB_NORTH). Pure: no fs, so the client gallery and the server page share it.
export const PARAM_WORDS: Record<string, string> = {
  HB_HUBAVG: "ERCOT hub average", HB_NORTH: "ERCOT North Hub", HB_SOUTH: "ERCOT South Hub", HB_WEST: "ERCOT West Hub",
  HB_HOUSTON: "ERCOT Houston Hub", HB_BUSAVG: "ERCOT bus average",
  "TH_NP15_GEN-APND": "CAISO NP15", "TH_SP15_GEN-APND": "CAISO SP15", "TH_ZP26_GEN-APND": "CAISO ZP26",
  ".H.INTERNAL_HUB": "ISO-NE internal hub", "N.Y.C.": "NYISO New York City", "LONGIL": "NYISO Long Island", "CAPITL": "NYISO Capital",
  SPPNORTH_HUB: "SPP North Hub", SPPSOUTH_HUB: "SPP South Hub", "ILLINOIS.HUB": "MISO Illinois Hub", "INDIANA.HUB": "MISO Indiana Hub",
  "MICHIGAN.HUB": "MISO Michigan Hub", "MINN.HUB": "MISO Minnesota Hub", "ARKANSAS.HUB": "MISO Arkansas Hub", "LOUISIANA.HUB": "MISO Louisiana Hub",
  "TEXAS.HUB": "MISO Texas Hub",
  ercot: "ERCOT", caiso: "CAISO", nyiso: "NYISO", isone: "ISO-NE", spp: "SPP", miso: "MISO", pjm: "PJM",
  iso: "Grid", hub: "Hub", node: "Node", months: "Months", weeks: "Weeks", years: "Years", ai_power: "AI power", all: "All",
};
export const paramWords = (v: string) => PARAM_WORDS[v] ?? v;
