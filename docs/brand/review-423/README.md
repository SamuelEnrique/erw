# Session 423: the footer's links and the touch targets

Before: production (`https://erw-flame.vercel.app`, main at 13:58 UTC on 21 October), in the internal view. After: the local build of `wip/423-footer-targets` (`http://localhost:3423`), in the internal view. Each at 1280 and 390 px.

| Shot | What to look at |
|---|---|
| `home-footer_*` | The footer's three links (Data and methods, Terms, Privacy): cardinal only before, cardinal and underlined after |
| `home-header_*` | At 390 px, the row of Energy Digest, Roundup and Email: 20 px tall before, 24 px after (4 px lower); the internal line's "lock" underlined after. At 1280 px the aside shares the menus' row |
| `about_*` | The site's list: "Power contracts", "What a battery saves a customer" and "The shoulder hours" (names alone on their line) are 24 px tall after; the other names, followed by their line, are unchanged |

A visitor sees a page in review as greyed text, not a link (`components/SiteLink.tsx`): the footer's rule names the element `a` and does not touch that text.
