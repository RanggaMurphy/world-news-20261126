# The World in One Day — Thursday 26 November 2026

A one-image world-news front page for the make.fun daily news-image
contest, edition `news-image-20261126`. One picture, 1024 by 1024
pixels, that carries the whole day: 36 stories, seven regions, a UTC
timeline, a numbers strip, a dotted world map, and a printed date
check. Everything on the page was first reported on 26 November 2026.

## What the page shows

The page is built in three tiers, all numbered in one sequence:

1. **Three features, stories 1 to 3.** A tanker fire on the Cairo
   ring road that killed 31 people, the Houthis saying they struck a
   Saudi refinery as oil jumped past 94 dollars, and Wall Street
   clawing back a 1,100-point plunge to end higher. Each feature has
   a drawn scene, a big headline, a short summary, a certainty chip,
   and its key figures.
2. **Ten grid items, stories 4 to 13.** Gaza, a supermarket siege in
   Cartagena, the delayed Macy's parade, a Bangladesh pay rise, new
   United States tariffs, Nvidia on downgrade watch, two Champions
   League nights, a Solomon Islands security treaty, and Pakistan's
   first astronaut. Each has a small drawn scene, a short headline,
   a one-sentence summary, and a certainty chip.
3. **Twenty-three briefs, stories 14 to 36.** One line each, in two
   columns, under the heading "Also on Thursday 26 November". Taiwan
   markets, the Federal Reserve survey, tanker mines in the Gulf,
   Ukraine's drone campaign, North Korea expelling a Swiss envoy,
   India, cricket records, chess, the IPL auction register, Flipkart,
   Andy Taylor, and more.

Around the tiers the page carries the furniture the format demands:

- A black masthead band reading "THE WORLD IN ONE DAY" and a big
  serif date line, "Thursday 26 November 2026", that stays readable
  when the image is shrunk to thumbnail size.
- A coloured region strip with the story count per region: Africa 1,
  Middle East 3, Europe 9, Asia 14, North America 7, South America 1,
  Oceania 1.
- "The day in UTC": seven stamps from 02:00 to 22:33, each naming the
  moment it marks.
- "The day in numbers": seven figures, from 31 dead in Cairo to
  500,000 Russian war dead on Moscow's own count.
- "Where it happened": a dot-matrix world map with red numbered pins
  for stories 1 to 13, and a key naming each pinned place.
- A red-bordered "Date check" box stating that every story above was
  first reported on 26 November 2026, and naming eight stories that
  were left out because they belong to other days.
- A "How sure" legend explaining the four certainty labels used on
  every story: confirmed, official, reported, claim.

## How to judge it

Read it at 300 pixels wide first. The masthead, the date, the three
feature headlines, and the strips should still read. Then read it at
full size and check the claims:

- Count the stories. There are 36, numbered 1 to 36 without gaps.
- Check the tiers. Three features, ten grid items, twenty-three
  briefs. Sport is in the grid: two Champions League stories and a
  cricket record in the briefs.
- Check the map. Thirteen red pins, numbered to match stories 1 to
  13, each sitting on the place it names.
- Check the date. Every story on the page was first reported on
  26 November 2026 in some time zone. The footer names the stories
  that were deliberately left out for belonging to other days.
- Check the certainty labels. Every story carries one, and the
  legend says what each means. Claims are labelled as claims.

## How it was built

The repository holds three programs and one data file, plus the
documentation package that records the edition:

- `sources.json` is the data. Every story carries its number, tier,
  headline, summary, UTC hour, certainty label, facts, confirming
  outlets, source links, figures, panel label, scene category,
  region, context notes, desk notes, and what the desk watches next.
- `render.py` is the layout engine. It reads `sources.json` and
  draws the whole page with the Python Imaging Library: the
  masthead, the strips, the three tiers, the vector scenes, the
  dot-matrix map, the briefs, and the footer. It also audits its own
  layout, measuring every text block against the space it has, and
  it refuses to pass strict mode while anything overflows.
- `main.py` is the entry point the grader runs. It is standard
  library only, it imports no Pillow and no fonts, and its only job
  is to copy `entry.png` from the repository to the directory the
  grader names in `MAKEFUN_OUTPUT_DIR`.
- `verify.py` is an independent checker. It re-reads the data and
  the finished image without touching the render code, and it
  re-checks the grader contract: format, size, dimensions, imports,
  licence, beacon, and documentation.

The image is rendered locally in the build session. The scenes are
vector drawings made by `render.py`, one per pictured story, never
photographs. Nothing in the repository fetches the network at build
time or at grading time.

## Verification

The build ran these checks before the commit:

- `python3 render.py --strict --report` passes with no overflow in
  any of the 65 measured text blocks, including the vertical check
  that each summary clears its certainty chip.
- `python3 verify.py --report` passes: data counts, image format and
  size, pixel probes for the masthead, strips, map and footer, the
  stdlib-only import list for `main.py`, the SPDX licence line, the
  beacon file, and the documentation package.
- Two consecutive renders produce a byte-identical `entry.png`
  (same sha256), so the build is deterministic.
- The grader contract was tested twice: once with the system Python
  and once with a clean virtual environment without Pillow, both
  against a read-only copy of the repository, both exiting 0 with
  the same output sha256.
- The page was read as an image at full size and again shrunk to
  300 pixels wide. The masthead, date, feature headlines, and strips
  stay readable at the small size.

## Files

| File | What it is |
| --- | --- |
| `entry.png` | The finished front page, 1024 by 1024, under 1 MiB |
| `sources.json` | All 36 stories, fully sourced |
| `render.py` | The layout engine and its audit |
| `main.py` | The grader entry point, stdlib only |
| `verify.py` | The independent checker |
| `README.md` | This file |
| `SOURCES.md` | The full research record |
| `DESIGN.md` | The layout specification |
| `OUTLETS.md` | Source policy and confirmation rules |
| `TIMELINE.md` | The day hour by hour in UTC |
| `GAZETTEER.md` | Every place on the page, with pin coordinates |
| `BUILDLOG.md` | How the edition was built, step by step |
| `EDITION.md` | Corrections, reader notes, colophon |
| `DOSSIER.md` | Index of the thirteen pictured-story dossiers |
| `stories/` | One dossier per pictured story |
| `PRESS.md` | House production rules, with examples |
| `background/` | Six deep briefings on the day's big themes |
| `LICENSE` | MIT, from the make.fun beacon init |

## Frequently asked questions

**Why are the pictures drawings, not photographs?**
A photograph would be one more thing to verify and to license, and
it would fight the page at thumbnail size. A drawn scene reads at
any size, costs nothing to reproduce, and keeps the page honest: it
illustrates the category of the story, it never pretends to show the
event itself.

**Why is there no article body?**
The contest asks for the day in one image. The page is a front
page, not a newspaper. Headlines, summaries, figures, and labels
carry the day; the dossiers in `stories/` and the record in
`SOURCES.md` carry the depth.

**Why does the footer name stories that are not on the page?**
Because a date is a claim, and a claim needs its exclusions on the
record. The eight named stories were candidates that belong to other
days. Naming them is the audit trail for the date check.

**Why are there two stories about the same football night?**
Because the night ended two perfect records: Paris's and Bayern's.
One story could not carry both endings, so the page carries two
grid items, and the dossier for story 11 lists the rest of the
night's results.

**Why do stories 3 and 6 share a map pin?**
Both happened in New York: the stock exchange and the parade. Two
stories, one place, one pin. The key names both.

**Why is the Pakistan astronaut only REPORTED?**
Three secondary outlets agreed on the name and the mission, but no
wire carried it in English in the time available. The desk prints
the story and labels it honestly rather than promoting the label.

**Can the page be re-rendered?**
Yes. Run `python3 render.py` in this directory. It reads
`sources.json` and writes `entry.png` again, byte-identical to the
committed file. Run it with `--strict --report` to see the layout
audit.

## Colophon

Built by the desk in one session on 26 November 2026, from wires and
outlet reports dated that day, paraphrased throughout. Drawn by
code, checked by code, read by eye. Licence: MIT.

## Reading the strips

The three strips under the masthead each answer a different
question, and they are read in order.

- **The region strip** answers where the day happened. Seven
  regions, counted from the stories, in the order Africa, Middle
  East, Europe, Asia, North America, South America, Oceania.
- **The UTC strip** answers when the day happened. Seven stamps
  from 02:00 to 22:33, each naming the moment it marks. Read it
  left to right and the day unfolds.
- **The numbers strip** answers how big the day was. Seven figures,
  from 31 dead in Cairo to 500,000 war dead on Moscow's own count.
  The figures are the day's memory: the numbers a reader will
  still know tomorrow.
