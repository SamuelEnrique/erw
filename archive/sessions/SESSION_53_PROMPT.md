# SESSION 53: Home page v2, tools by audience, and a guided tour

## Read first
CLAUDE.md, the site's home page, nav and every route under site/app (list them), the
session reports 35 to 52 for what each tool does.

## Budget and rules
USD 0, no model calls, no data pulls, no Supabase table. Every number on the home page
read from a table with a check key, as the rest of the site. Target about an hour.
Pull and merge if the daily job lands, never force push, commit after every step.

## The work
1. Inventory: docs/tools.md listing every live tool with its route, one line on the
   question it answers, its audience, and its data sources.
2. Home page v2: a one-sentence statement of what the ERW is (the whole US energy
   system, AI's power demand as the sharpest lens), then three audience sections:
   Students and teachers (grid pages, the network, bill explainer, problem sets, the
   battery game, events), Investors and lenders (price board, cost of power both
   tabs, deals, datacenters, severance and the lease tool, Thesis Builder), Researchers
   (data and downloads, event studies and the notebook, methods, Ask the ERW). Each
   tool a card: its name, the question it answers, one live number from the warehouse
   where natural (checked), a link. Keep the existing live-price strip at the top.
   Stanford palette, mobile-safe, fast.
3. /tour: a five-stop guided tour for a first-time visitor (about three minutes),
   each stop a sentence and a link: the network, a grid page, the price board, an event
   study, the cost-of-power seller's tab. A "start the tour" link on the home page.
4. The nav: group items so no menu holds more than eight; nothing removed.
5. check-values, check-routes (every card's link resolves), tests/, deploy, live
   checks.

## Report: archive/sessions/SESSION_53_REPORT.md
The inventory count, what the home page now shows, the tour stops, nav changes, wall
time, spend USD 0 confirmed. Push. Stop.