# Session 2965 report: the landing request file, the tariff registry's next utilities

6 November 2026, about 08:53 to 08:56 UTC, on lab-desktop (the data machine), chain 157 (the owner's), unattended. Model spend USD 0. Pulls: 8 requests (`runs/s2965/probe.csv`; bodies in `runs/license_reads/s2965/`).

## Read these first

- **The landing request file:** not on origin's main. No laptop branch to land.
- **No utility added: each tariff book's host bars this reader or this use.** The chain's four, in its order:
  - **Duke Energy Carolinas:** www.duke-energy.com's robots file disallows `*/-/media/` and `*/_/media/` to every reader, the paths its tariff PDFs are served from. The NCUC's portal names ClaudeBot (chain 147). Not read.
  - **Entergy Texas:** www.entergy-texas.com redirects to www.entergytexas.com, whose robots file closes only `/wp-admin/`. Its terms (`/terms`) forbid any user who "uses any robot, spider, scraper or other automatic or manual means to access the Sites or copies any content or information on the Sites". Not read.
  - **Xcel Colorado:** www.xcelenergy.com has no robots file (HTTP 404), and its address redirects a reader to the account portal my.xcelenergy.com/s/ (a Salesforce site holding no tariff book; its robots file names only account paths). No tariff address was found without guessing. Not read.
  - **Evergy:** closed by chain 155's session 2937 (a bot script at its robots address). Not asked again.
- **The registry stays at 5 schedules of 4 utilities.**

## Errors

- **Two home pages were asked before their redirects' hosts' robots files:** www.entergy-texas.com to www.entergytexas.com, and www.xcelenergy.com to my.xcelenergy.com. Each new host's robots file was read immediately after, and both allow the pages asked. Nothing was taken from either home page but its links.

## Decisions made without you

- **No guessed tariff address for Xcel.**

## For Samuel's ruling

- **Hosts closed by this session:** www.duke-energy.com's tariff files (robots), www.entergytexas.com (its terms bar robots). Duke and Entergy, like SCE, National Grid, Con Edison and Eversource, would need written permission or the commission's docket copies.
