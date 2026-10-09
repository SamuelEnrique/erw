import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // the committed markdown under ../docs is bundled at build time by scripts/build-content.mjs
  // (content/docs.json, imported by lib/markdown.ts), so no page reads the file system at request time
  poweredByHeader: false,
  // session 90: while the site is built its reads take turns (lib/supabase.ts, BUILD_READS), so a page may wait for the
  // database longer than the default 60 seconds a page is given; a page waiting for its turn is not a page that hangs
  staticPageGenerationTimeout: 300,
  // session 138: /cost-of-power reads a grid's years of hourly prices from data/datacenter when a request asks for that
  // grid (lib/datacenterdata.ts); the file names are built at request time, so the folder is named for the server trace
  outputFileTracingIncludes: { "/cost-of-power": ["./data/datacenter/*.json"] },
  // session 23: Energy Week became the Energy Roundup; the old addresses keep working
  async redirects() {
    return [
      // session 145: one tool, one page, one address. What a generator earns is /cost-of-power/seller; its second version
      // is folded into it and its address redirects there (a query is carried over)
      { source: "/cost-of-power/seller/v2", destination: "/cost-of-power/seller", permanent: true },
      // session 133: one tool, one page, one address. The energy mix is /mix; its second version and the two pages beside
      // it are views of that page now, and their addresses redirect to the view each became (a query is carried over)
      { source: "/mix/v2", destination: "/mix?view=day", permanent: true },
      { source: "/mix/clean", destination: "/mix?view=clean", permanent: true },
      { source: "/mix/stress", destination: "/mix?view=stress", permanent: true },
      // session 144: one tool, one page, one address. Curtailment is /curtailment; its second version (California by the
      // hour, against battery charging) is part of that page now, and its address redirects to it (a query is carried over)
      { source: "/curtailment/v2", destination: "/curtailment", permanent: true },
      // session 152: one tool, one page, one address. Demand growth is /demand; the page built at /demand/weather (demand
      // growth with the weather taken out, sessions 126 and 129) is the second view of that page, and its address
      // redirects to it (a query is carried over)
      { source: "/demand/weather", destination: "/demand?view=weather", permanent: true },
      // session 167: one tool, one page, one address. The project map is /map; its second version is the base of that page
      // now, and its address redirects to it (a query is carried over)
      { source: "/map/v2", destination: "/map", permanent: true },
      { source: "/weekly", destination: "/roundup", permanent: true },
      { source: "/weekly/:week", destination: "/roundup/:week", permanent: true },
      // session 132: one tool, one page, one address. The price board is /board; its earlier versions and the markets
      // page (now the board's workbench) redirect to it, and so does the method note of version 4
      { source: "/markets", destination: "/board", permanent: true },
      { source: "/board/v3", destination: "/board", permanent: true },
      { source: "/board/v4", destination: "/board", permanent: true },
      { source: "/data/methods/price_board_v4", destination: "/data/methods/price_board", permanent: true },
    ];
  },
};

export default nextConfig;
