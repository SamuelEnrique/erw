import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // the committed markdown under ../docs is bundled at build time by scripts/build-content.mjs
  // (content/docs.json, imported by lib/markdown.ts), so no page reads the file system at request time
  poweredByHeader: false,
  // session 90: while the site is built its reads take turns (lib/supabase.ts, BUILD_READS), so a page may wait for the
  // database longer than the default 60 seconds a page is given; a page waiting for its turn is not a page that hangs
  staticPageGenerationTimeout: 300,
  // session 23: Energy Week became the Energy Roundup; the old addresses keep working
  async redirects() {
    return [
      { source: "/weekly", destination: "/roundup", permanent: true },
      { source: "/weekly/:week", destination: "/roundup/:week", permanent: true },
    ];
  },
};

export default nextConfig;
