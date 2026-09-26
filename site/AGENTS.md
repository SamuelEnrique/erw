# site/: agent notes

The Energy Research Warehouse (ERW) public site: Next.js 16 (App Router), TypeScript, Tailwind 4. The repository's `CLAUDE.md` governs; in particular no em dashes in any file, and real data only.

- This Next.js version has breaking changes from older versions: read the guide in `node_modules/next/dist/docs/` before writing code, and heed deprecation notices.
- `next dev`, when it detects an AI coding agent, rewrites this file with its own managed block, which contains em dashes. Do not commit that change. Run the site with `npm run build` and `npm start` instead (see `README.md`).
- Data: `lib/supabase.ts` is the only reader of Supabase, with `SUPABASE_URL` and `SUPABASE_ANON_KEY`. Never the service key.
- Design tokens: `app/tokens.css` only.
