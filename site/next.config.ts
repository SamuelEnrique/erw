import type { NextConfig } from "next";

// Session 177 (docs/reviews/2026-10-10-security.md): the security headers of every answer.
//   Strict-Transport-Security   Vercel sends it already; named here so the site does not depend on the host for it
//   X-Content-Type-Options      a file is what its type says
//   X-Frame-Options, frame-ancestors   no other site may frame a page (the site frames nothing of its own)
//   Referrer-Policy             another site learns the origin, never the path or the query
//   Permissions-Policy          the site uses no camera, microphone, location, payment or sensors
// Session 177 sent the full policy (where scripts, styles, images and requests may come from) as
// Content-Security-Policy-Report-Only, and enforced only the four directives that cannot break a page (base-uri,
// object-src, frame-ancestors, form-action: the site has no <base>, no <object> or <embed>, no frame, and every form
// posts to the site itself). Session 301 (the security review's M4, the chain prompt of 19 October 2026): the full
// policy is ENFORCED, after scripts/check-csp.mjs opened every page of the release list in a real browser on the
// built site and found 0 violations (89 pages, 19 October 2026). The report-only header stays beside it for a week,
// with the same value, so a violation after a click would still be reported where the enforced one blocks it. It
// allows what the site is known to use: its own files, inline scripts and styles (Next writes both), the chart
// library from cdnjs (components/echarts.ts), the database's storage for the network's hourly file, blob: for the
// map's worker and the pages' own downloads, and data: images. To go back: CSP_ENFORCED = CSP_MINIMAL.
const CSP_MINIMAL = "base-uri 'self'; object-src 'none'; frame-ancestors 'none'; form-action 'self'";
const CSP_FULL = [
  "default-src 'self'",
  "script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com",
  "style-src 'self' 'unsafe-inline'",
  "img-src 'self' data: blob:",
  "font-src 'self' data:",
  "connect-src 'self' https://*.supabase.co",
  "worker-src 'self' blob:",
  "frame-src 'none'",
  "base-uri 'self'", "object-src 'none'", "frame-ancestors 'none'", "form-action 'self'",
].join("; ");
const CSP_ENFORCED = CSP_FULL;          // session 301; until then CSP_MINIMAL
const CSP_REPORT_ONLY = CSP_FULL;       // beside it for a week (session 301)
void CSP_MINIMAL;
const SECURITY_HEADERS = [
  { key: "Strict-Transport-Security", value: "max-age=63072000; includeSubDomains; preload" },
  { key: "X-Content-Type-Options", value: "nosniff" },
  { key: "X-Frame-Options", value: "DENY" },
  { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
  { key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=(), payment=(), usb=(), accelerometer=(), gyroscope=(), magnetometer=(), browsing-topics=()" },
  { key: "Content-Security-Policy", value: CSP_ENFORCED },
  { key: "Content-Security-Policy-Report-Only", value: CSP_REPORT_ONLY },
];

const nextConfig: NextConfig = {
  async headers() {
    return [
      { source: "/:path*", headers: SECURITY_HEADERS },
      // every internal address: never indexed, never cached, and no referrer leaves it (a token may be in an old link)
      { source: "/internal/:path*", headers: [
        { key: "Referrer-Policy", value: "no-referrer" },
        { key: "Cache-Control", value: "private, no-store" },
        { key: "X-Robots-Tag", value: "noindex" },
      ] },
      // the form of the internal view holds no token in its address, and it must post to this site: under no-referrer a
      // browser writes "Origin: null" on a posted form (the Fetch standard), which a same-origin check cannot tell from
      // another site's. With same-origin the form's post names this site, and nothing is sent to any other site.
      { source: "/internal/open", headers: [{ key: "Referrer-Policy", value: "same-origin" }] },
    ];
  },
  // the committed markdown under ../docs is bundled at build time by scripts/build-content.mjs
  // (content/docs.json, imported by lib/markdown.ts), so no page reads the file system at request time
  poweredByHeader: false,
  // session 90: while the site is built its reads take turns (lib/supabase.ts, BUILD_READS), so a page may wait for the
  // database longer than the default 60 seconds a page is given; a page waiting for its turn is not a page that hangs
  staticPageGenerationTimeout: 300,
  // session 138: /cost-of-power reads a grid's years of hourly prices from data/datacenter when a request asks for that
  // grid (lib/datacenterdata.ts); the file names are built at request time, so the folder is named for the server trace
  // session 183: the seller page reads one hub's model by a name taken from data/seller/hubs/index.json
  // session 467: /datacenters reads the same price files for its power-side section (app/datacenters/PowerSide.tsx)
  outputFileTracingIncludes: { "/cost-of-power": ["./data/datacenter/*.json"], "/datacenters": ["./data/datacenter/*.json"], "/cost-of-power/seller": ["./data/seller/hubs/**/*.json"],
    // session 1170: the replay's daily files, read on the server for a replayed day's figures (lib/gridReplayFile.ts)
    "/grid": ["./public/network/daily_*.json"] },
  // session 23: Energy Week became the Energy Roundup; the old addresses keep working
  async redirects() {
    return [
      // session 239 (the owner's instruction of 12 October 2026; docs/reviews/erw-review-2026-10-12.md, section B): six
      // pages hold what thirteen held, each as tabs of one address (lib/tabs.ts). Every old address redirects to the tab
      // it became (a query is carried over, so /storage/buildout?grid=ercot opens the build-out tab on ERCOT). Only the
      // address itself is redirected: /resources/layer and /resources/overlay (the resource map's files),
      // /severance/lease/real and /severance/finder answer as before.
      { source: "/storage/buildout", destination: "/storage?tab=buildout", permanent: true },
      { source: "/storage/owners", destination: "/storage?tab=owners", permanent: true },
      { source: "/severance/lease", destination: "/severance?tab=lease", permanent: true },
      { source: "/consumption", destination: "/demand?view=consumption", permanent: true },
      { source: "/deals/v2", destination: "/deals?tab=tracker", permanent: true },
      { source: "/companies", destination: "/deals?tab=companies", permanent: true },
      { source: "/resources", destination: "/map?tab=resources", permanent: true },
      // session 239: the versioned addresses. /board/v3, /board/v4, /map/v2, /network/v3, /curtailment/v2 and
      // /cost-of-power/seller/v2 redirect already (below); /deals/v2 is the tracker tab (above). /seller/v2 never was
      // an address of the site (the page was /cost-of-power/seller/v2); it redirects with it, so a link written short
      // answers. /datacenters/v2 (session 106: ERCOT's large-load status beside the facilities held) redirects too
      // since session 241. Session 239 held the line back because /datacenters did not draw its blocks; it draws them now
      // (app/datacenters/LargeLoad.tsx), and the old page's file stands in app/_retired/datacenters-v2.
      { source: "/datacenters/v2", destination: "/datacenters", permanent: true },
      { source: "/seller/v2", destination: "/cost-of-power/seller", permanent: true },
      { source: "/explorer/ercot-peak-premium", destination: "/prices?tab=ercot", permanent: true },
      // session 237 (the roadmap's item 2): one tool, one page, one address. The Grid tool is /grid; the network, the
      // energy mix, the emissions page and the seven grid pages are views of that page now, and their addresses redirect
      // to the view each became. A query is carried over; where an old page's own word is one of the tool's two (view,
      // grid), it is read by the tool (lib/gridtool.ts): the network's view is written as net, the mix's as mix, and a
      // grid named by its EIA-930 code (grid=ERCO) chooses that grid. The finishing pass of sessions 237 and 238: /network/v3,
      // /mix/v2, /mix/clean and /mix/stress (below) go to their view in one step, no longer through /network and /mix.
      { source: "/network", has: [{ type: "query", key: "view", value: "(?<net>[a-z0-9_]+)" }], destination: "/grid?view=network&net=:net", permanent: true },
      { source: "/network", destination: "/grid?view=network", permanent: true },
      { source: "/mix", has: [{ type: "query", key: "view", value: "clean" }], destination: "/grid?view=clean", permanent: true },
      { source: "/mix", has: [{ type: "query", key: "view", value: "(?<mix>[a-z]+)" }], destination: "/grid?view=mix&mix=:mix", permanent: true },
      { source: "/mix", destination: "/grid?view=mix", permanent: true },
      { source: "/emissions", destination: "/grid?view=clean", permanent: true },
      // the seven grid pages, each by its own line (tests/test_session53.py reads a folded page's line here); a longer
      // address under one of them (/grid/caiso/alerts, the Flex Alert scorecard) is its own page and is not redirected
      { source: "/grid/ercot", destination: "/grid?grid=ercot", permanent: true },
      { source: "/grid/caiso", destination: "/grid?grid=caiso", permanent: true },
      { source: "/grid/pjm", destination: "/grid?grid=pjm", permanent: true },
      { source: "/grid/nyiso", destination: "/grid?grid=nyiso", permanent: true },
      { source: "/grid/isone", destination: "/grid?grid=isone", permanent: true },
      { source: "/grid/miso", destination: "/grid?grid=miso", permanent: true },
      { source: "/grid/spp", destination: "/grid?grid=spp", permanent: true },
      // session 238 (the owner's task of 12 October 2026): Automated Analysis is Research, at /research. The old address and
      // the addresses under it (a week's chart, a finding's card) redirect to the same place under /research (a query is
      // carried over, so a card's chart form or a request's link opens as it did)
      { source: "/analysis", destination: "/research", permanent: true },
      { source: "/analysis/:path*", destination: "/research/:path*", permanent: true },
      // session 145: one tool, one page, one address. What a generator earns is /cost-of-power/seller; its second version
      // is folded into it and its address redirects there (a query is carried over)
      { source: "/cost-of-power/seller/v2", destination: "/cost-of-power/seller", permanent: true },
      // session 133: one tool, one page, one address. The energy mix is /mix; its second version and the two pages beside
      // it are views of that page now, and their addresses redirect to the view each became (a query is carried over)
      // session 237, the finishing pass: /mix is the Mix view of /grid, so each goes there in one step (it went to
      // /mix?view=day, /mix?view=clean and /mix?view=stress, and from there to /grid)
      { source: "/mix/v2", destination: "/grid?view=mix&mix=day", permanent: true },
      { source: "/mix/clean", destination: "/grid?view=clean", permanent: true },
      { source: "/mix/stress", destination: "/grid?view=mix&mix=stress", permanent: true },
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
      // session 168: one tool, one page, one address. The grid network is /network; version 3 is that page now, and its
      // address redirects to it (a query is carried over, so a view shared from /network/v3 opens the same view)
      // session 237, the finishing pass: /network is the Network view of /grid, so version 3's address goes there in one
      // step, its view written as net as /network's is (it went to /network, and from there to /grid)
      { source: "/network/v3", has: [{ type: "query", key: "view", value: "(?<net>[a-z0-9_]+)" }], destination: "/grid?view=network&net=:net", permanent: true },
      { source: "/network/v3", destination: "/grid?view=network", permanent: true },
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
