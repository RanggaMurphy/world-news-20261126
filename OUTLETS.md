# Source policy — Thursday 26 November 2026

This file records how the desk chooses outlets, how it counts
confirmation, and how it handles corrections. The policy is the same
for every edition; the outlet list is the one this edition used.

## What counts as a source

A source is a named outlet or an official document that the desk
could read in the session. A social media post is not a source on
its own. A wire carried by another outlet still counts as that wire,
not as two sources: the desk counts independent outlets, not
articles. If Reuters and the BBC both carry the same AP wire, that
is one wire and two outlets only if their reporting adds independent
confirmation, and the desk says so in the dossier when it matters.

## Wires and newspapers

Wires move first and get the facts right most often, but they also
move first with the wrong toll or the wrong count. Newspapers are
slower and add context, names, and the second source. The desk uses
both: the wire for the first report, the newspaper for the check.
When the two disagree on a number, the desk waits for the official
figure, a ministry, a police statement, a court filing, and prints
that, not the first wire.

Official documents sit above both. A USTR notice, an IPL media
advisory, a Beige Book, a cabinet statement: these are the facts
themselves, and they carry the OFFICIAL label even when only one
outlet wrote about them.

## The outlets this edition used

**Wires and agencies:** AP, Reuters, AFP via partners, Kyodo.

**International newspapers and broadcasters:** BBC, Guardian, CNN,
New York Times, Sky News, Le Monde, The Times, USA Today.

**Business and markets:** Bloomberg, Investopedia, Motley Fool,
TradingView, CBOE, Morningstar, Bloomberg Law, Investors.com,
Forbes India, Inc42, YourStory, TechCrunch.

**Regional and specialist:** CGTN America, Firstpost, Dhaka Tribune,
Democracy Now, Middle East Eye, OilPrice, IRNA, Europa Journal
News, Zot News, Yonhap, TBS News, Sowetan, AJP, The AZB, Particle
News, Developments Today, Boeing (company release), Lowy Institute,
UEFA, AP Sport, Sportradar, IPLT20, Wisden, CricTracker, Zee News,
SelfStudys, Observer Voice, StudMentor, Jagran Josh, BigGo Finance,
SimpleLife, Finwire, Bogner Chess, The Week in Chess, World Chess,
Rapporteur, Europe Says, Politico, EU Perspectives, ANI, Devdiscourse,
Parade, TMZ, People, ABC, NBC, Stocktwits, LA Post, Hourly News,
Gate TR, DefenceMENA, Atlas360, Wall Street Journal.

**Official sources:** USTR notice, IPLT20 media advisory, Federal
Reserve Beige Book, India cabinet statement, court filings.

## How confirmation is counted

The desk records, per story, the outlets it actually read. The
count in `SOURCES.md` is that list's length. A story needs two
outlets to earn CONFIRMED. One outlet earns REPORTED, unless the
single source is an official document, which earns OFFICIAL. A
claim by one party, with no independent confirmation, earns CLAIM
even if six outlets report that the claim was made: reporting a
claim is not confirming it.

Edge cases from this edition:

- The Houthi strike: six outlets reported the claim and the market
  move, none confirmed a direct hit. CLAIM, not CONFIRMED.
- The Gulf tanker mines: two outlets, one of them quoting the
  claim, and the maritime authorities saying unconfirmed. CLAIM.
- The Pakistan astronaut: three secondary outlets agreed on the
  name and the mission, no wire. REPORTED.
- The Ukraine refinery strikes: one wire in English, several local
  sources the desk could not read. REPORTED.
- The AI bust warning: an opinion built on estimates. REPORTED,
  with the estimates attributed to their sources.

## What the desk does not use

- Unattributed social media posts as the sole source of a fact.
- Aggregators that do not name their own source.
- A single outlet's "sources say" with no corroboration, unless
  the outlet is a wire and the fact is small and checkable.
- Press releases quoted as news without noting that they are press
  releases. A company release is a source for what the company
  said, not for what happened.

## Corrections

If a figure on the page turns out wrong, the desk corrects it in
`EDITION.md` under "Corrections and clarifications", with the old
figure, the new figure, and the source of the correction. No
correction has been needed for this edition at the time of writing.
The desk re-checks the two numbers most likely to move after press
time, the Cairo toll and the Brent price, before the next edition.

## Paraphrase rule

Every line in this repository is the desk's own wording. The desk
never copies a headline or a fact line verbatim from a wire or an
outlet into a repo file. Where the original phrasing was striking,
the desk paraphrases it. Headlines in the dossiers are broken into
phrases across lines for the same reason. Source links are kept in
`sources.json` so any reader can check the original reporting. This
rule is not only about honesty: it is how the desk keeps its work
its own, and it is enforced by the reproduction check in `PRESS.md`.

## Language

The page is in English, the language of the contest and of the
wires the desk read. The dossiers and the record are in English
too. The build log and the working notes are the desk's own and
follow the same rule.

## Reliability notes on the main outlets

A short note on each outlet the desk relied on most in this
edition, so that a reader can see why the desk trusts them and
where it stays cautious.

- **AP.** The wire the desk trusts first for breaking facts. Its
  tolls and counts are usually right, and when they are wrong it
  corrects quickly. Used for Cairo, the parade, Bangladesh, and the
  chess and football results.
- **Reuters.** The wire the desk trusts first for markets and for
  the Gulf. Its timestamps are the ones the UTC strip uses. Used for
  the Houthi claim, the Nvidia watch, the tariffs, and the treaty.
- **BBC.** The broadcaster the desk trusts for confirmation. It is
  slower than the wires and more careful with names and ages. Used
  for Cairo, Gaza, Colombia, the parade, and the Markle charge.
- **Guardian.** The newspaper the desk trusts for context and for
  the second source. Used for Cairo, the parade, and the Jolie-Pitt
  settlement.
- **USTR notice.** An official document, not an outlet. It is the
  source of the tariff facts, and it is public, so any reader can
  check it.
- **Federal Reserve Beige Book.** An official document. It is the
  source of the survey facts, and it is public.
- **IPLT20 media advisory.** An official document. It is the source
  of the auction register figures.
- **UEFA.** The source of the football scores. Scores are matters of
  record, and UEFA is the record.
- **Yonhap.** The wire the desk trusts for North Korea, because it
  is closest to the story and has the best sourcing in Seoul.
- **SelfStudys, Observer Voice, StudMentor.** Secondary outlets the
  desk used for South Asian stories where no wire was available in
  English. The desk treats them as reliable for facts and cautious
  about labels, which is why the stories they carry are REPORTED
  rather than CONFIRMED.

## What the desk does when outlets disagree

When two outlets disagree on a number, the desk waits for the
official figure. When they disagree on a fact, the desk prints the
fact both agree on and records the disagreement in the dossier.
When an outlet corrects itself, the desk follows the correction and
records it in `EDITION.md`. In this edition no outlet disagreed
with another on any number the page prints, except for the early
Cairo tolls, where the desk waited for the ministry.

## Outlets not used, and why

Sources the desk saw and did not use, recorded so that the next
edition does not have to re-check them.

- **Unattributed social media posts.** Several posts carried the
  Houthi claim and the tanker-mine claim before the wires did. The
  desk did not use them as sources, because a post is not a source
  on its own. The wires that later carried the claims are the
  sources on the record.
- **Aggregators that do not name their source.** Two aggregators
  carried the Taiwan market fall without naming their source. The
  desk used BigGo Finance, SimpleLife, and Finwire instead, which
  name theirs.
- **A single outlet's "sources say".** One outlet reported that
  Walmart asked the Flipkart chief to leave, citing unnamed sources.
  The desk prints the departure as a fact and the reason as
  "sources said", because that is what the reporting supports, and
  records the attribution in the dossier.
- **Press releases quoted as news.** The Boeing release about the
  F-15EX display is a source for what Boeing said, not for what
  happened. The desk used it alongside Kyodo and the other outlets,
  not on its own.
