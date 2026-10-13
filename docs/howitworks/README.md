# How it works: the five tools

One document a tool, written on 2026-10-13 (session 249) for the person who shows the tool and has to answer for it. Each has the same seven parts, in the same order, and a last part that says where every number in it was read.

| Tool | Address | Document | Written from |
|---|---|---|---|
| What a battery earns | `/cost-of-power/battery` | [battery.md](battery.md) | `main` (the page landed in session 234, commit `80aa2362`) |
| What a generator earns | `/cost-of-power/seller` | [generator.md](generator.md) | the branch `origin/wip/235-generator` at `c7ce17de`; it landed during the writing (`aa3addbc`, 09:14 UTC), the page's files unchanged |
| What a datacenter pays | `/cost-of-power` | [datacenter.md](datacenter.md) | the branch `origin/wip/236-datacenter` at `d4eaec68`; it landed during the writing (`aa3addbc`) with two sentences reworded, which the document gives |
| The Grid tool | `/grid` | [grid.md](grid.md) | the branch `origin/wip/237-grid` at `13dfe385`, not on `main` |
| Research | `/research` | [research.md](research.md) | the branch `origin/wip/238-research` at `f95bb129`, not on `main` |

## The seven parts

1. What it is for, and for whom.
2. The model, in numbered steps.
3. Every assumption, its default and its source.
4. The cross-checks.
5. What it cannot see, ranked by how much it moves the answer.
6. The ten hardest questions, each with the honest answer and the number.
7. A five-minute demo, click by click.

## How to read them

- **Every number is one the repository already holds:** a methods document, a session report, a check script, a card's own file. The last part of each document names the file and the place. Where the repository holds no number the document says "no number held"; nothing was estimated to fill a line. One exception, marked where it stands: some figures of the battery document carry **[c]**. No method or report prints them; they were computed with the page's own library from the table of 2026-10-13, and the script and its output are in [`computed/`](computed/).
- **Four of the five were written from a branch.** The code machine rebuilt those pages on the night of 12 to 13 October 2026 and had landed none of the four when the writing began. Two landed before it ended (the generator and the datacenter pages, together, as `aa3addbc`) and their documents were read again against what landed. The Grid tool and Research were still on their branches: until a branch lands, production shows the page as it stood before, and each document says what differs. When one lands with changes, its document is read again against the landed page.
- **No demo path was clicked through in a browser.** Each was written from the page's code, its check scripts and its data. Every page is in review (`site/lib/release.ts`), so a demo starts by opening the internal view.
- **The screen is newer than the page.** Prices and the live set are rebuilt daily. A figure here names its months; when the screen differs, the screen is right and the document is due an edit.
- **A number that moves is fixed in its source first** (the method, the code), then here. `tests/test_session249.py` holds the form of these documents, not their numbers.
