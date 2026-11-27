# Session 10603 report (chain 730, lab-desktop second window): longer backtests and more places

27 November 2026, from 08:29 UTC, on Samuel's word (the chain had stopped after landing 20, about 06:40 UTC). Model
spend: USD 0. No warehouse table written, no data lock taken. Kept current while the session runs.

The first five items of Samuel's order (the weather forecast line, wind and solar, net demand, the real-time price, the
share inside each band) were done in session 10602 and landed with rows 7 and 8 (gate 20, `89418bdef`). The weather
forecast line still holds 13 to 21 days a place against the 30 it needs, so it stays "too few days to judge". This
session takes the next item: longer backtests and more places. Branch `wip/c730-predict-v4`, from main at `6e211cb0d`.

## What a reader will see that was not there before (once the landing row lands and window E's page reads the files)

- **35 more places for demand:** every other balancing authority whose EIA-930 demand runs to the latest day and covers
  two years (AECI to WALC; method note `predict.md` section 23), each with the same file as the 29 places.
- **The real-time price over a longer backtest:** ERCOT from 2016, scored year by year (`predict_price.md` section 8).
  The market's day-ahead price beats the ERW in ten of eleven years at North (nine or ten at the other ERCOT hubs).
- **The real-time price at four more hubs:** ERCOT Houston, South and West, CAISO NP15 (section 9). The day-ahead price
  is ahead at all four.
- **The day-ahead price at the same four hubs** (`price_hubs.json`, section 10): yesterday's price beats the ERW's
  regression at every ERCOT hub; the regression wins at NP15.
- **In the 35 new places the operator mostly wins:** the ERW is ahead of the filed forecast in 13 of 35 over two years,
  in 8 of the 32 with sound months. Many small authorities' filings fail the check (PSEI 78 of 79 months).
- **Window E's two rows mended** (chain 720's requests 11 and 12 in `data_requests_predict.md`): no rows of nulls for a
  day not forecast (the reason instead: EIA-930's gap of 18 to 20 November in the Carolinas and the Southwest), net
  demand's `tomorrow_held`, `shown_for` naming the place that shows CAISO's wind and solar, and words for every cut,
  with `cuts_price` for the price rows of `scores.json` (its `cuts` call `top10` the highest-demand days).
- **Replications:** the day-ahead price, which had none, 3,936 of 3,936; the real-time price 3,020 of 3,020; demand on
  the 64 places 48,384 figures (47,967 exactly; the 417 others in the seven smallest authorities, within the backtest
  table's 0.1 MW rounding, which the script now allows on the regressions only) and 1,024 of 1,024 refits.

## Decisions made without you

- **"Longer backtests" read as far back as the warehouse's data allows, and a request for more.** The demand forecast's
  backtest starts on 1 July 2019 because the warehouse's EIA-930 demand begins on 1 July 2018 (and its six-month history
  table holds only January to June 2018, for seven authorities); it cannot be longer without older data. Data request 9
  asks for EIA's six-month files from July 2015; the connector's header calls its span an approved pull, so it says the
  reach further back may be your word. The real-time price reads only hub prices, which ERCOT's table holds from 2015:
  its longer backtest runs from 2016. The day-ahead price reads demand, so it cannot go back further either.
- **The longer backtest is a block beside the backtest, not a replacement:** `long_backtest` in `rt_price.json`; the
  backtest, its cuts and the choice are unchanged (the file equals main's once that block is set aside). The method in
  every earlier year is the one chosen now: the earlier years test the choice, they do not make it.
- **The 35 places added by a rule, not by size:** every authority whose demand reaches the latest day and covers two
  years. Left out: SWPW and BHBA (filing only since April 2026), WACM and WAUW (no demand after 1 April 2026), AEC, NSB
  and OVEC (their filings end in 2021, 2020 and 2018). The smallest added (SPA, 23 MW on average) is in, as the rule says.
- **The forecast two to seven days ahead (`ahead.py`) keeps its 29 places:** adding 35 would double a daily step of
  window A's run that already takes about half an hour; `run.CORE_PLACES` keeps the list, and the note says so.
- **Hubs added where both markets are held two years:** ERCOT Houston, South, West and CAISO NP15. Not SPP South or CAISO
  ZP26 (day-ahead prices from 26 August 2026 only, no real-time price), not ERCOT's two averages of hubs already scored.
- **Wind and solar by authority not built:** the warehouse holds it for 91 days only. Data request 10 asks for it from
  July 2018.
- **The day-ahead price at the added hubs reads its grid's demand** (ERCO for ERCOT's hubs, CISO for NP15), as the
  grid's first hub does in the place files.

## Errors and how they were met

- **A heredoc, against the chain's rules:** a two-line `cat <<'X'` wrote a placeholder file that was deleted at once
  (no content used). Every later file went by Write or Edit.
- **A claim of session 10602 corrected:** the progress file said "every series of the forecast now has its
  replication", but the day-ahead price (the place files' `series.price`) had none: `replicate.py` checks the demand rows
  only. `replication/predict/replicate_price.py` now rebuilds the day-ahead price end to end.
- **Faults of mine found by window E** (chain 720's requests 11 and 12, filed against this window's files): 24 rows of
  nulls where a day could not be forecast, with no reason, and cut words borrowed from demand for price rows. Mended on
  the branch, with tests; rebuild 17 carries them.
- **The demand replication at first differed on 417 figures** of the seven smallest authorities, in the MAPE's third
  decimal: the regressions are read from the backtest table at 0.1 MW. The script now allows that rounding's bound on
  the regressions only and says so; the simple methods and the operator stay exact.
- **A row 1 figure out of date:** data request 1 says `run.py` takes about five minutes; the 29 places took 32 minutes in
  rebuild 15, and the 64 are about 70 alone. Data request 13 says so for window A.

## For Samuel's ruling

Nothing is taken for you.

- Data request 9 (EIA-930 from July 2015) would lengthen the demand backtest by three years; the connector's header calls
  its present span an approved pull.
- The three items of session 10602 stand (the page's lead where the operator's filing breaks; the 5 percent line; ruling
  2 and the ERCOT tables two lines read).

## Commits

- **Branch `wip/c730-predict-v4`:** `15f0e9271` the 35 places and the real-time longer backtest; `3927d1c5f` the four
  real-time hubs; `fb294cadd` the day-ahead price at four hubs and `replicate_price.py`.
- **Main:** `bb2dc07d6` progress; `daeb525ad`, `9a0ed65ce`, `bbd5efab1` `predict_price.md` sections 8 to 10; `7ad8766fc`
  and `b55b220d7` data requests 9 and 10.
