// Energy Research Warehouse (ERW) site, session 1007 (chain 070): the lines of /data's "Use the ERW in your tools", the
// three packages of docs/methods/packages.md. Every line here is the specification's or a package README's, word for
// word, so the page never says a call a second way (tests/test_session1007.py holds each line to its source).

export type PackagePanel = {
  /** the language */
  name: string;
  /** the install line(s), from the package's README */
  install: string[];
  /** the six calls, from the package's README */
  calls: string[];
  /** the package's README on GitHub */
  readme: string;
  /** the README in the repository, the source of its lines */
  source: string;
};

/** The specification's first sentence ("What a reader gets"). */
export const PACKAGES_LEAD =
  "A researcher who works in Python, Stata or R reads any public table of the Energy Research Warehouse (ERW) with the same six calls, gets the same rows in the same column types, and cites the same line.";

/** The citation line, as the specification writes it ("cite(table)"). */
export const PACKAGES_CITATION =
  "<publishers>. <reports>. Via the Energy Research Warehouse (ERW), table `<table>`, Redivis dataset `datapages.erw`, version <tag> (released <YYYY-MM-DD>).";

/** The specification's sentence on a table that is not public ("What a held table does"). */
export const PACKAGES_HELD =
  "A table whose verdict is not `public` is never served by Redivis or the live set.";

export const PANELS: PackagePanel[] = [
  {
    name: "Python",
    install: ['pip install "git+https://github.com/SamuelEnrique/erw.git#subdirectory=package"'],
    calls: [
      "erw.tables()",
      'erw.coverage("eia_fuel_spot_prices")',
      'df = erw.fetch("eia_fuel_spot_prices", entity="eia:henry_hub", start="2025-01-01", end="2026-01-01")',
      'erw.cite("eia_fuel_spot_prices")',
      'erw.license("eia_fuel_spot_prices")["verdict"]',
      'erw.standard("eia_fuel_spot_prices")["columns"]',
    ],
    readme: "https://github.com/SamuelEnrique/erw/tree/main/package",
    source: "package/README.md",
  },
  {
    name: "Stata",
    install: ['net install erw, from("https://raw.githubusercontent.com/SamuelEnrique/erw/main/packages/stata/") replace'],
    calls: [
      "erw tables, clear",
      "erw coverage eia_fuel_spot_prices, clear",
      "erw fetch eia_fuel_spot_prices, entity(eia:henry_hub) start(2025-01-01) end(2026-01-01) clear",
      "erw cite eia_fuel_spot_prices",
      "erw license iso_rtm_hub_prices",
      "erw standard eia860m_retired_generators, clear",
    ],
    readme: "https://github.com/SamuelEnrique/erw/tree/main/packages/stata",
    source: "packages/stata/README.md",
  },
  {
    name: "R",
    install: ['remotes::install_github("SamuelEnrique/erw", subdir = "packages/r/erw")'],
    calls: [
      "erw_tables()",
      'erw_coverage("eia_fuel_spot_prices")',
      'h <- erw_fetch("eia_fuel_spot_prices", entity = "eia:henry_hub", start = "2025-01-01", end = "2026-01-01")',
      'erw_cite("eia_fuel_spot_prices", h)',
      'erw_license("iso_rtm_hub_prices")$words',
      'erw_standard("eia860m_retired_generators")$columns',
    ],
    readme: "https://github.com/SamuelEnrique/erw/tree/main/packages/r/erw",
    source: "packages/r/erw/README.md",
  },
];
