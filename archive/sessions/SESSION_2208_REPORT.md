# Session 2208 report: chain 087's build, checks and gate, not started for want of memory

Energy Research Warehouse (ERW), chain 087 (`queue/done/087-day-24-october-portable-explorers-gate.md`, its session "2206", run as 2208 because 2206 and 2207 were taken by the periodicals' sessions on `wip/2206-periodicals-fixes`), portable-laptop, 23 October 2026, 22:23 to 22:30 UTC. Model Fable 5.1. Model spend USD 0. No warehouse data written; no web request but GitHub; nothing built, nothing landed.

## Read these first

- Chain 087 was taken by session 2207's queue step (`92e943f7`, pushed); the other session on this machine had not taken it.
- **The chain's own rule stopped it before any build.** Its first step reads the free memory and the build lock every two minutes for at most 20 minutes and starts nothing under 4,000,000 KB free. The first read, at 22:24 UTC: 1,663,972 KB free, the lock free. The read itself was then stopped by Claude Code at 22:26, with the periodicals' gate beside it, because the machine was critically low on memory (801,844 KB free at 22:26; the other Claude Code session on this laptop was building). Claude Code's notice says not to start the stopped work again unasked, so neither the read nor a build was restarted.
- Nothing of chain 086's branch `wip/2204-explorers` was built, checked or shot. The "To finish" of `docs/state/review_2026-10-29_portable.md` and of sessions 2203 and 2204's reports stands word for word.

## Checks

| Check | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 2208"` | 0 | on duty |
| free memory at 22:24 UTC | | 1,663,972 KB: under the line |
| `scripts/buildlock.py status` at 22:24 | 0 | free |
| free memory at 22:26 UTC | | 801,844 KB |

## The landing

Not run. `wip/2204-explorers` stands at `c21c8d0d`, merged with main as of 23 October 20:43 UTC; main has moved since (the data chain's `task/2070-2083-data` merged), so the merge is the first command when the gate runs.

## Decisions made without you

1. The session numbers: 2208 and 2209 for chain 087's two sessions, 2206 and 2207 being taken.
2. The 20-minute read was not restarted after the system stopped it: Claude Code's notice asks for that, and the one read already stood under the line by 2.3 GB.

## For Samuel's ruling

- Nothing new. Chain 087 needs a machine with 4 GB free and the database answering under 3 s: this laptop with the other session closed, or the desktop with the file's `machine:` line changed.

## To finish

Chain 087's session "2206", word for word, from its first command: the memory and the lock, the merge of main into `wip/2204-explorers`, the probe, the gate with `--keep-worktree`, the after checks and shots on the build, the push commands only on a gate that passes outright.
