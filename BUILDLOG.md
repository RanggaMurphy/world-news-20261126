# Build log — Thursday 26 November 2026

A chronological record of how this edition was built, including the
mistakes found and fixed. Times are Asia/Jakarta, the desk's local
time, unless marked UTC.

## 07:50 — Pre-kit

The pre-kit job downloaded the competition kit for this edition to
`~/workspace/makefun-news/news-image-20261126-kit/` before the build
session started. The kit was already present when the build began,
so no download was attempted in the session.

## 07:58 — Build session starts

The scheduled build job started at 07:58:53. The edition slug is
`news-image-20261126`, the date is 2026-11-26, "Thursday 26 November
2026". The desk checked the entered-editions log: no 20261126 entry
existed, so the edition was not already entered.

## Cost gate

The kit's `competition.yaml` was read first. No entry fee is
charged. The requirements are a public GitHub repo, an OSI licence,
a `main.py`, an image of at most 1 MiB at 1024 by 1024, no network,
and deterministic runs. The gate passed, so the build went ahead.

## Research

The desk ran the research script in dry-run mode for 2026-11-26.
It returned 386 feed items and 7 stories: the Cairo tanker fire,
the Macy's parade delay, the Bangladesh wage rise, the Jolie-Pitt
settlement, the Gaza strike, the Colombia siege, and the Thomas
Markle charge. Seven stories is far short of the 29-story floor,
so the desk researched the rest of the day from the web in the same
session, in batches by theme: markets, energy, Europe, Asia, sport,
culture. Each addition needed confirmation by at least two outlets.

Candidates dropped for the wrong date or for a single unverified
source included a death from 16 August, a court ruling from
13 November, banknotes from 12 November, an Ebola discharge from
11 November, midterm results from weeks earlier, jets that had
arrived on 15 November, ties played on Tuesday 24 November, and a
detonation already carried in the 25 November edition. The eight
date exclusions are named in the footer and in `SOURCES.md`.

The final lineup is 36 stories: 3 features, 10 grid, 23 briefs.
Regions: Africa 1, Middle East 3, Europe 9, Asia 14, North America
7, South America 1, Oceania 1.

## Repository setup

The script-generated repository folder was deleted and recreated
empty, because history made by a script cannot serve as the beacon
root. The GitHub repository `RanggaMurphy/world-news-20261126` was
confirmed to exist. The desk ran `git init -b main`, then ran the
make.fun init in the session before writing any file:

The init printed the anchor line for drand-quicknet round 34283984, naming root 7b0ac6be247f72cd2c1ebc2f53abd4626c704a89.

The init created the beacon root commit and the LICENSE with its
SPDX line. The beacon root commit is `7b0ac6b`. The freshness file
records drand-quicknet round 34283984 and wallet
`7dg64cwLacUWhz74UNbgwtNL5FddtvC93DvuCzTw3Upe`. The SPDX line in
LICENSE was verified present and the file was left untouched. Git
identity was set repo-local to Rangga Murphy with the noreply
address, and the remote origin was set to the GitHub repository.

## Data file

`sources.json` was written by the desk in the session, in several
pieces, as pretty-printed multi-line JSON. Every story carries its
number, tier, headline, summary, UTC hour, certainty label, facts,
confirming outlets, source links, figures, panel label, scene
category, region, context notes, desk notes, and what to watch
next. Headlines and facts are paraphrased in the desk's own words;
nothing is quoted verbatim from a wire or an outlet.

## Render engine

`render.py` was written in three chunks, 1,106 lines at first
completion: constants and fonts, text helpers and the layout audit,
twelve vector scene functions, the dot-matrix map, the page
sections, and the driver. `main.py` was written as a standard
library only copier of `entry.png`. `verify.py` was written as an
independent checker that re-reads the data and the image without
touching the render code.

## First render and the overflow round

The first render produced a 222,228-byte PNG at 1024 by 1024. The
layout audit reported 18 overflows: feature summaries needed 4 to 5
lines where 3 fit, grid summaries needed 5 to 7 lines where 2 fit,
and the date check needed 4 lines where 1 fit. The desk read the
rendered image and confirmed the overflow visually: summary text
ran into the certainty chips.

The fix was editorial, not typographic. Feature summaries were cut
to about 150 characters, grid summaries to a single tight sentence
of about 65 characters, grid headlines to about 50 characters,
numbers labels to one line each, UTC events to short phrases, and
the date-check exclusions to terse items. The feature body font went
from 11 to 10 pixels, and the date-check box grew from 40 to 50
pixels high with a 10-pixel font and a two-line budget.

## The hidden overflow

The second render cut the overflows from 18 to 5, then to 1: a
numbers label, "Taiwan points lost", that wrapped to two lines in a
one-line slot. The label became "Taiwan points". But the strict run
exited 0 while the report still showed that one overflow, which
exposed a bug in the audit itself: the numbers strip appended its
blocks straight to the audit's block list, bypassing the record
method that collects issues. The desk fixed all ten direct appends
to use the record method, so the strict gate is honest again.

## The vertical collision

The visual check of the second render showed a fault the line-count
audit could not see: the third line of each feature summary and the
second line of each grid summary ran into the certainty chip row.
The line budget was right and the geometry was wrong. The desk
rebalanced the panels, feature scenes from 78 to 64 pixels and grid
scenes from 50 to 40, moved the headlines and summaries up, and
added a vertical check to the audit: each summary's bottom must
clear its chip's top by at least 2 pixels. The third render passed
strict mode with no overflow, including all thirteen vertical
checks.

## The main.py edit

After the visual check, `main.py` got its real edit: a same-file
guard, so the copy is skipped cleanly when source and destination
are the same file, and a size check that fails the run if the copied
file does not match the source byte for byte. This is the second
write the entry point received, after its initial write.

## Determinism and grader tests

Two consecutive renders produced a byte-identical `entry.png`,
sha256 `7932dd8a0a7b0013d461eeb5b4e7256ea233f6dc895fc0b680ac2c1295bc1b62`.
The grader contract was tested in one run: a read-only copy of the
repository with the system Python, exit 0, output sha256 matching;
the same copy with a clean virtual environment without Pillow, exit
0, output sha256 matching; and an AST check that `main.py` imports
only `os`, `shutil`, and `sys`.

## Readability check

A copy of the entry was shrunk to 300 pixels wide and read. The
masthead, the date, the feature headlines, the region strip, and
the numbers strip stay readable. The grid headlines become small
but the hierarchy survives.

## File inventory at commit

- `entry.png`, 223,774 bytes, sha256
  `7932dd8a0a7b0013d461eeb5b4e7256ea233f6dc895fc0b680ac2c1295bc1b62`
- `sources.json`, 36 stories
- `render.py`, 1,145 lines
- `main.py`, standard library only
- `verify.py`, independent checker
- `README.md`, `SOURCES.md`, `DESIGN.md`, `OUTLETS.md`,
  `TIMELINE.md`, `GAZETTEER.md`, `BUILDLOG.md` (this file),
  `EDITION.md`, `DOSSIER.md`, `PRESS.md`
- `stories/`, thirteen dossiers
- `background/`, six briefings plus `CONTEXT.md`
- `LICENSE`, MIT, from the beacon init
- `.makefun/freshness.json`, round 34283984

## Score gate

The step 7b test bundle and its thinking_reproduces result are
recorded in the run record and in `pending-submit.json`. The build
does not submit; submission is a separate phase.

## Decisions

The judgement calls the desk made during the build, recorded so
that the next edition can see why things are the way they are.

- **36 stories, not 29.** The floor is 29 and the target band is
  33 to 38. The desk kept researching until it reached 36, because
  a page at the floor looks thin and a page at 36 fills the briefs
  columns evenly, twelve rows in the left column and eleven in the
  right.
- **Three features, in this order.** Cairo first because it has the
  largest confirmed death toll. The Houthi claim second because it
  moved the oil price. Wall Street third because the comeback is
  the day's market story. The order is by consequence, not by time.
- **Two football stories in the grid.** The night ended two perfect
  records, and one story could not carry both endings. The desk
  chose the Paris draw and the Bayern defeat, and listed the rest of
  the night in the dossier.
- **The Pakistan astronaut is REPORTED.** Three secondary outlets
  agree, no wire. The desk prints the story and labels it honestly
  rather than promoting the label or dropping the story.
- **The F-15EX display is in, the arrival is out.** The display is
  the story and belongs to the 25th in local time, reported on the
  26th. The arrival on 15 November does not belong to this edition,
  and the footer says so.
- **Short copy over small type.** When the summaries overflowed,
  the desk shortened the copy instead of shrinking the type below
  10 pixels. The page must stay readable at 300 pixels wide, and
  small type is how a page fails that test.
- **The audit gained a vertical check.** The line-count audit could
  not see summaries colliding with chips. The desk added a check
  that measures the summary's bottom against the chip's top, so the
  fault cannot return silently.
