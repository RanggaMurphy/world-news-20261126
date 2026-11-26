# Gazetteer — places on the page

Every place named on the page, with its story number, its region,
and the pin coordinates used by the world map. Coordinates are
in decimal degrees. Pins are numbered to match stories 1 to 13; the
briefs name places too, and those are listed after the pinned
places with their coordinates for the record.

## Pinned places, stories 1 to 13

### 1. Cairo, Egypt

Story 1, the tanker fire. Region: Africa. Pin: 30.04 N, 31.24 E.
The ring road around the capital, where the tanker overturned.
The map pin sits on the Nile delta, at the eastern edge of the
Mediterranean coast of the African landmass.

### 2. Ras Tanura, Saudi Arabia

Story 2, the Houthi claim. Region: Middle East. Pin: 26.65 N,
50.16 E. The refinery on the Gulf coast, capacity 550,000 barrels
a day. The pin sits on the western shore of the Gulf, just below
the Strait of Hormuz band.

### 3. New York, United States

Story 3, the Wall Street comeback. Region: North America. Pin:
40.71 N, 74.01 W. The New York Stock Exchange, where the Dow closed
at 50,183 after erasing a 1,100-point loss. The pin sits on the
eastern seaboard of the North American landmass.

### 4. Gaza City

Story 4, the strike. Region: Middle East. Pin: 31.50 N, 34.47 E.
The strike on Gaza City that killed the Hamas internal security
chief and his family. The pin sits on the eastern Mediterranean
coast, just west of the Jordan valley.

### 5. Cartagena, Colombia

Story 5, the supermarket siege. Region: South America. Pin:
10.39 N, 75.51 W. The supermarket where 76 people were held for
17 hours. The pin sits on Colombia's Caribbean coast, the only
South American pin on the map.

### 6. New York, United States

Story 6, the delayed parade. Region: North America. Pin: 40.71 N,
74.01 W. The same city as story 3: the parade route and the stock
exchange share a place, so their pins sit a few pixels apart on
the map, nudged just far enough that both numbers stay readable.
Two stories, one city, two pins, and the key names both.

### 7. Dhaka, Bangladesh

Story 7, the garment pay rise. Region: Asia. Pin: 23.81 N,
90.41 E. The capital where the minimum wage decision was announced
after weeks of street protests. The pin sits on the Ganges delta,
east of the Indian landmass.

### 8. Taipei, Taiwan

Story 8, the tariff proposal. Region: Asia. Pin: 25.03 N,
121.56 E. The proposal came from the trade office in Washington,
which announced Section 301 duties on 14 economies; the desk
pinned the story at Taipei, whose proposed cap of 15 percent is
one of the announcement's headline figures.

### 9. Santa Clara, United States

Story 9, Nvidia on downgrade watch. Region: North America. Pin:
37.35 N, 121.95 W. Nvidia's headquarters in Silicon Valley. The
pin sits on the Pacific coast of the North American landmass, far west
of the New York and Washington pins.

### 10. Bruges, Belgium

Story 10, Liverpool and Barcelona in Europe. Region: Europe. Pin:
51.21 N, 3.22 E. Club Brugge's ground, where Liverpool won 3-0.
The pin sits on the North Sea coast of the European landmass. Barcelona
played at Sabah, whose ground is not pinned: one pin per story, and
the desk chose the match the headline leads with.

### 11. Paris, France

Story 11, PSG's perfect run ends. Region: Europe. Pin: 48.86 N,
2.35 E. The Parc des Princes, where Paris were held 2-2 by Roma.
The pin sits on the northern French plain, just south of the
Channel coast.

### 12. Honiara, Solomon Islands

Story 12, the security treaty. Region: Oceania. Pin: 9.65 S,
160.06 E. The capital where the treaty was signed in Canberra's
shadow: the signing itself happened in Canberra, but the story
belongs to the islands, so the pin sits on the islands. The pin is
the easternmost on the map, near the right edge.

### 13. Beijing, China

Story 13, Pakistan's first astronaut. Region: Asia. Pin: 39.90 N,
116.40 E. The space programme's capital, where the Shenzhou-24
crew was announced. The astronaut is Pakistani, the station is
Chinese, and the pin sits on the programme that flies him.

## Places in the briefs

These places are named in the briefs but carry no pin, because the
map pins only stories 1 to 13. Their coordinates are recorded here
so the next edition can pin them if the format changes.

- Taipei, Taiwan, 25.03 N, 121.56 E. Story 14, the market fall.
- Washington, United States, 38.91 N, 77.04 W. Story 15, the Beige
  Book.
- Okinawa, Japan, 26.21 N, 127.68 E. Story 16, the fighter jet.
- Gulf of Oman, 25.00 N, 59.00 E. Story 17, the tanker mines.
- Samara, Russia, 53.20 N, 50.15 E. Story 18, the refineries.
- Rostov-on-Don, Russia, 47.24 N, 39.71 E. Story 18, Novoshakhtinsk.
- Pyongyang, North Korea, 39.03 N, 125.75 E. Story 20, the envoy.
- New Delhi, India, 28.61 N, 77.21 E. Stories 21, 22, 23, 35.
- Mumbai, India, 19.08 N, 72.88 E. Story 21, the 26/11 anniversary.
- Kathmandu, Nepal, 27.72 N, 85.32 E. Story 22, the package.
- Doha, Qatar, 25.29 N, 51.53 E. Story 24, the cricket record.
- Geneva, Switzerland, 46.20 N, 6.14 E. Story 25, the chess match.
- Goa, India, 15.30 N, 74.12 E. Story 26, the IPL auction.
- Los Angeles, United States, 34.05 N, 118.24 W. Stories 30 and 36.
- Luxembourg, 49.61 N, 6.13 E. Story 33, the General Court.

## How pins are projected

The map box runs x 24 to 604 and y 684 to 778 in page pixels. A
pin's page position is computed from its longitude and latitude by
a straight equirectangular projection: longitude plus 180, divided
by 360, times the box width, plus the box's left edge; and 78 minus
latitude, divided by 136, times the box height, plus the box's top
edge. The latitude range is cropped, 78 north to 58 south, so the
continents get more vertical room and the empty far north and the
ocean-only far south do not eat the box. A few pins are then nudged
a few pixels by hand, where two true positions would print on top
of each other. The projection is a locator, not a survey: the
decimal coordinates in this file are the precise record.

## Regions on the page

How the seven regions are represented, and what each region's
stories have in common on this day.

- **Africa, 1 story.** The Cairo tanker fire, the day's largest
  confirmed death toll. One story, and it leads the page.
- **Middle East, 3 stories.** The Houthi claim, the Gaza strike,
  and the tanker mines in the Gulf. All three are about claims and
  strikes, and two of the three are claims.
- **Europe, 9 stories.** Two Champions League nights, the cage
  ruling, the chess match, the guitarist's death, and four briefs.
  Europe's day was made of institutions doing their work.
- **Asia, 14 stories.** The largest region on the page. Bangladesh,
  Taiwan, India, Pakistan, North Korea, Japan, China, and the Gulf.
  Asia's day was made of markets, wages, packages, and a space
  station.
- **North America, 7 stories.** Wall Street, Nvidia, the parade,
  the Beige Book, the AI-bust warning, and two briefs from Los
  Angeles. The region's day was made of markets and government.
- **South America, 1 story.** The Colombia siege, 76 freed after
  17 hours. One story, and it is the day's longest by the clock.
- **Oceania, 1 story.** The Solomon Islands treaty, signed in
  Canberra at 02:00 UTC. One story, and it is the day's most
  consequential diplomatic news.

The region strip on the page carries these counts in the same order:
Africa 1, Middle East 3, Europe 9, Asia 14, North America 7, South
America 1, Oceania 1. The counts sum to 36, and the desk's checker
verifies the sum before every commit.

## How the map was drawn

The map is drawn from hand-written continent outlines stored in
`render.py` as lists of longitude and latitude pairs, one polygon
per continent or island group. Each polygon is projected with the
same rule as the pins and filled in slate blue-grey with a darker
coastline, so the page carries a real world map: the Americas on
the left, Africa and Eurasia in the middle, Indonesia and
Australia on the right.

The outlines were written from a world map, keeping each
continent's real shape and neighbours with a dozen to forty points
per outline. The desk checked them by rendering and reading the
result: the continents must be recognisable at a glance, and the
pins must sit on the right countries. The first filled render hid
two pins under their neighbours, the second New York pin under the
first and the Cairo pin under the Gaza pin, and Bruges and Paris
overlapped the same way. Those pins are now nudged a few pixels
inside their own city areas, by hand, so every number from 1 to 13
stays readable.

Each pin is filled with its country's colour, and the same colour
prints the country name in the key beside the map and the place
names inside the briefs, so one country's colour can be followed
across the whole lower half of the page.

The projection is equirectangular with a cropped latitude range:
longitude maps linearly across the box, latitude maps linearly
down the span from 78 north to 58 south. The desk knows this
stretches the far north. The distortion does not matter, because
the map is a locator, not a survey. A reader who wants exact
positions will find the decimal coordinates in this file.
