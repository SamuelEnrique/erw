# Session 9900: LinkedIn video posts in the approved template (chain of 24 November 2026, night)

Lab-desktop, unattended, 24 November 2026, 10:18 to about 11:05 UTC. Worktree `C:\Users\Shared\Documents\erw-posts`,
branch `wip/linkedin-posts-2026-11-24` (from origin/main `156fa60ac`). Not landed. Model spend USD 0.

## Read these first

- The review page: https://github.com/SamuelEnrique/erw/blob/wip/linkedin-posts-2026-11-24/docs/reviews/linkedin/posts-2026-11-24.md
- The note (regression, sources and terms, failures): https://github.com/SamuelEnrique/erw/blob/wip/linkedin-posts-2026-11-24/docs/state/note_2026-11-24_linkedin_posts.md

## What was done

- Template extended (optional fields only); `queue_withdrawn` renders pixel-identical to origin/main, square and tall,
  at frames 0, 90, 200, 330, 449 (10 stills, 0 differing pixels, after one fix).
- 10 posts rendered as 12 versions, 24 videos (square 2160 x 2160 and tall 2160 x 2700) with last frames: B2, B3 (A, B),
  and shortlist sections 37 (A, B), 21, 24 (A, B), 1, 8, 10, 3.
- Every version: fit checks by script on each row's peak and the last frame (0 failures); number check re-read from
  each source independently (84 rows, 0 mismatches).
- B1 (Nvidia) blocked at SEC EDGAR; sections 9 and 12 not added (they wait on all ten passing).

## What to review

- Every final frame in one image: https://github.com/SamuelEnrique/erw/blob/wip/linkedin-posts-2026-11-24/docs/reviews/linkedin/img/all_final_frames.png
- The videos: https://github.com/SamuelEnrique/erw/tree/wip/linkedin-posts-2026-11-24/docs/research/motion/posts
- The template change: https://github.com/SamuelEnrique/erw/blob/wip/linkedin-posts-2026-11-24/motion/src/Post.tsx
- The specs: https://github.com/SamuelEnrique/erw/tree/wip/linkedin-posts-2026-11-24/motion/specs/posts

## For Samuel's ruling

- B1: name a contact email for SEC's User-Agent, or decline. Also no price source cleared yet (Stooq disallows, Nasdaq
  refused).
- B3 title B ("Gasoline isn't" on sale): true against past years, but the price fell 35 cents in two weeks.
- Oil and uranium: scale A (100%) or B (largest row).
- B2: tall track about 145 px; California kept at 0 h.

## Decisions made without you

- Listed on the review page; the main ones: MISO in Central time, B2 clock times as hour ending, every drawn figure
  rounded half up from the source digits (never JavaScript's rounding), B3 on 16 November (23 November unpublished).

## Not done

- No landing, no deploy, no snapshot (no site file changed), no queue file written, no gate worktree made.

CHAIN DONE
