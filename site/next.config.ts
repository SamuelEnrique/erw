import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // the committed markdown under ../docs is bundled at build time by scripts/build-content.mjs
  // (content/docs.json, imported by lib/markdown.ts), so no page reads the file system at request time
  poweredByHeader: false,
  // session 23: Energy Week became the Energy Roundup; the old addresses keep working
  async redirects() {
    return [
      { source: "/weekly", destination: "/roundup", permanent: true },
      { source: "/weekly/:week", destination: "/roundup/:week", permanent: true },
    ];
  },
};

export default nextConfig;
