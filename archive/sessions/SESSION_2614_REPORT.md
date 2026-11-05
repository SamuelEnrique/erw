# Session 2614 report: a third own choice, none taken (Aruba: WEB Aruba's figures are an image and its terms allow personal use only; CBS Aruba serves a script challenge)

25 October 2026, about 05:43 to 05:52 UTC, on lab-desktop (the data machine), chain 129, unattended. Precheck passed (`runs/c129/pre2614.out`). Model spend USD 0. Pulls: 6 requests of 20. Run before session 2613, as chain 128 ran its session 2600 before 2599.

## Why Aruba

- **The record, the queue and the unlanded chains' branches hold none of Bermuda, the Cayman Islands, Aruba or Puerto Rico.** Puerto Rico was set aside because `eia_state_generation_monthly` already holds its monthly generation by fuel (`eia:generation:PR:*`, to August 2026). Aruba was tried first: its generator, WEB Aruba, has a production figures page.

## Read these first

- **No table.**
  - **WEB Aruba N.V.:** its robots file closes only system paths (read 1216). Its Power Production Figures page (read 1218) gives the figures only as an image, a JPG "awareness sheet", and earlier chains took no figures from images (NBS China, chain 125).
  - Its Terms of Use (read 1219): "It must not be copied, reproduced, republished, downloaded, posted, broadcast or transmitted in any way except for your own personal, non-commercial use." **Verdict: needs written permission** (NEPCO's form, session 2374).
  - **CBS Aruba:** cbs.aw has no robots file (HTTP 404, read 1220), and its site answers with a Sucuri script challenge (HTTP 307, read 1221). Not asked again.
- **Bermuda** was searched (no request): only press reports and EIA's figures republished by third parties came up, and no first-hand table within the ceiling. So nothing was taken.

## Requests (6 of 20)

| n | What | Outcome |
|---|---|---|
| 1 | webaruba.com's robots file | 200 |
| 2, 3 | WEB Aruba's Energy Production and Power Production Figures pages | 200, the figures an image |
| 4 | WEB Aruba's Terms of Use | 200 |
| 5 | cbs.aw's robots file | 404 |
| 6 | cbs.aw's site | 307, a Sucuri challenge |

Reads recorded: 1216 to 1221.

## Decisions made without you

- **Puerto Rico not chosen,** as EIA's state table holds its generation already.
- **No figure read from an image,** and none from the press or a secondary source.
- **WEB Aruba's verdict recorded,** with no table, so that a later chain needs no new read.

## For Samuel's ruling

- None new.

## Files

- New: this report.
- Changed: the license record (reads 1216 to 1221, WEB Aruba's verdict) and `docs/licenses.md`.
- On the data machine only: `runs/c129/s2614/`, `runs/license_reads/s2614/`.
