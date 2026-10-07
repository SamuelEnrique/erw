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
      // session 133: one tool, one page, one address. The energy mix is /mix; its second version and the two pages beside
      // it are views of that page now, and their addresses redirect to the view each became (a query is carried over)
      { source: "/mix/v2", destination: "/mix?view=day", permanent: true },
      { source: "/mix/clean", destination: "/mix?view=clean", permanent: true },
      { source: "/mix/stress", destination: "/mix?view=stress", permanent: true },
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
