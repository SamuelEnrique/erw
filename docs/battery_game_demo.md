# The battery game: a five-minute demonstration

The game is in review. On the machine you will show it from, open the internal view first:
`https://erw-flame.vercel.app/internal/unlock?token=<your internal token>`, then `https://erw-flame.vercel.app/play/battery`.

**Say this first:** you own a home battery; a real day of Texas power prices goes past in ninety seconds; buy when power is cheap, sell when it is dear; then the page shows what a battery that knew every price would have made.

**Controls.** Laptop: hold **C** (or the down arrow) to charge, **S** (or the up arrow) to sell; let go to wait. Phone: hold one of the two big buttons. A day takes 90 seconds whatever you do, so two plays fit in five minutes, not three.

## Minute 0 to 2: the simple page

1. In "The day" pick **A summer scarcity day, 2023-08-10**. Press **Start**.
2. Name what is on the screen: the price now, the day so far, the battery's charge, the money ($5 to start; below $0 the game ends). The future is hidden. The clock is at the top right.
3. Play it: the battery starts half full. Charge in the morning (the price is lowest, 24.90 USD/MWh, at 08:45). From about 13:00 hold Sell: the price climbs to 3,842.89 USD/MWh at 15:30.
4. **Read the end screen's three lines aloud.** They are the point: what you earned; what the perfect battery earned on the same day with the same rules, **$60.97**; and the one hour you lost the most against it, with what it did then and at what price.
5. Add one sentence: nobody knows the day's prices ahead, so the perfect battery is a ceiling, not a target.

## Minute 2 to 5: Hard, and the grid emergency

1. Follow **More** under the end screen. Choose **Hard**, pick the same day. The button reads "Play 2023-08-10, Hard".
2. Before you press it, say what Hard adds. The page labels each as a game rule:
   - a **backup reserve** the battery will not sell below (the line on the charge bar) and **wear** (each kWh sold costs money);
   - a **grid emergency**: in the day's dearest hour the price climbs toward the $5,000 cap, and the number carries the label "game rule, not a real price" with the real price beside it;
   - then **the grid goes down for two hours**: the buttons go grey and the house runs on the battery. If it runs dry the lights go out, the round ends, and the house is charged for the whole outage.
3. Play it: the emergency is the hour from 15:00, the outage 16:00 to 18:00. Sell into the climb, and **stop while the battery still holds more than 3.2 kWh, about a quarter full.** The banner gives the number: the house needs 3.16 kWh from the battery, and the reserve line is at 2.70 kWh, which is not enough by itself. Hold Sell until the battery stops at the reserve and the lights go out late in the outage, at a cost of $105.
4. The perfect battery earns **$49.01** on Hard: less than on Normal, because it keeps charge for the house. The money is in the emergency, and so is the risk.

**With a sixth minute:** on Hard, switch on **Rooftop solar**. A 5 kW roof follows the real shape of Texas's solar fleet that day; in the outage the house takes the roof's power first. The perfect battery earns **$89.17**; doing nothing at all earns $34.32, the roof alone.

## What the room asks

- **Are the prices real?** Yes: ERCOT's real-time price at the hub average, every fifteen minutes of that day. Only Hard's emergency hour is the game's, and it is labeled on the number.
- **Is the battery real?** No. The battery, the home, the $5 and the fleet are made up; the page says which numbers are assumptions.
- **Why did I lose money?** Buying when power is dear costs more than the battery earns back, and a tenth of the energy is lost on each round trip.
- **Where does the lights-out charge come from?** Texas's value of lost load, USD 35,000 per MWh, adopted by its utility commission in 2024.

## If something goes wrong

- **"In review" instead of the game:** the internal view is not open in this browser. Open the unlock address again.
- **Blank or stuck:** reload. The prices are part of the page; the network is needed only to load it and to store the score.
- **A quieter day:** "A calm spring day" (2026-04-26). The perfect battery earns 44 cents on Normal: most days there is little to arbitrage.

Checked on production at a phone's width and a laptop's, 4 October 2026 (`site/scripts/check-battery-game.mjs`; session 111's report).
