# Session 1129 report: a conversation on /ask

23 October 2026, 20:00 to 20:10 UTC, on samueloldlaptop, unattended, on `wip/1129-ask` (cut from `wip/1126-ask`, while the landing gate ran on it). Chain `queue/done/076-day-24-october-code-ask-board-2.md`. Model spend USD 0.

## What was done

- **Checked first**: Ask ERCOT holds the last three turns (session 121); the general chat and the grids' scoped chats did not: the panel sent no history for them and the route called the general loop without one.
- **Now they do** (`site/lib/chat/history.ts`): the last three turns, each its question, its answer (to 1,500 characters) and what its queries read (session 1115's `reads`), go into the first message before the new question, in Ask ERCOT's own words (`spec_ercot.json`'s `history_head` and `history_turn`). An earlier answer's numbers count as given (they were checked when it was written) and its cited tables as read; every new number is still fetched and checked. With no earlier turn the first message is byte for byte what it was (a test). The panel sends the turns for every chat; the route passes them to the general loop.
- The Python CLI's general chat is unchanged (it takes `history` only under a profile).

## Checks

- `node --import ./scripts/alias-register.mjs scripts/test-ask-1129.mjs`: exit 0, 4 of 4.
- The Ask tests: exit 0 after three old tests' literals moved with the call they read (sessions 92, 121: the route's general call now passes `history`; session 137: the panel's general body carries it).
- Em dashes: 0.

## Decisions made without you

1. **The history's words are Ask ERCOT's**, not new ones, so the two chats read a conversation the same way. Reversible.

## For Samuel's ruling

- None new.
