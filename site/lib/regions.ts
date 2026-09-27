// Energy Research Warehouse (ERW) site: regions the explorers select (session 18).

/** EIA-930 balancing authorities the ERW holds: table code, entity, label. */
export const BAS = [
  { code: "us48", entity: "eia930:US48", label: "US Lower 48" },
  { code: "erco", entity: "eia930:ERCO", label: "ERCOT" },
  { code: "ciso", entity: "eia930:CISO", label: "CAISO" },
  { code: "pjm", entity: "eia930:PJM", label: "PJM" },
  { code: "miso", entity: "eia930:MISO", label: "MISO" },
  { code: "swpp", entity: "eia930:SWPP", label: "SPP" },
  { code: "nyis", entity: "eia930:NYIS", label: "NYISO" },
  { code: "isne", entity: "eia930:ISNE", label: "ISO-NE" },
] as const;

/** EIA's state codes (Forms EIA-923 and EIA-861M): US, the 50 states, DC and Puerto Rico. */
export const STATES: Record<string, string> = {
  US: "United States", AL: "Alabama", AK: "Alaska", AZ: "Arizona", AR: "Arkansas", CA: "California",
  CO: "Colorado", CT: "Connecticut", DE: "Delaware", DC: "District of Columbia", FL: "Florida",
  GA: "Georgia", HI: "Hawaii", ID: "Idaho", IL: "Illinois", IN: "Indiana", IA: "Iowa", KS: "Kansas",
  KY: "Kentucky", LA: "Louisiana", ME: "Maine", MD: "Maryland", MA: "Massachusetts", MI: "Michigan",
  MN: "Minnesota", MS: "Mississippi", MO: "Missouri", MT: "Montana", NE: "Nebraska", NV: "Nevada",
  NH: "New Hampshire", NJ: "New Jersey", NM: "New Mexico", NY: "New York", NC: "North Carolina",
  ND: "North Dakota", OH: "Ohio", OK: "Oklahoma", OR: "Oregon", PA: "Pennsylvania", PR: "Puerto Rico",
  RI: "Rhode Island", SC: "South Carolina", SD: "South Dakota", TN: "Tennessee", TX: "Texas", UT: "Utah",
  VT: "Vermont", VA: "Virginia", WA: "Washington", WV: "West Virginia", WI: "Wisconsin", WY: "Wyoming",
};
