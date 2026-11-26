"""Independent checker for the finished news-image entry.

This program checks the built entry against the grader contract and
the desk's own rules without importing or calling any render code. It
reads sources.json and entry.png directly, parses main.py with the
standard library ast module, and probes the rendered pixels for the
page furniture the format requires: masthead, strips, map, footer.

Usage: python3 verify.py [--report]

Exit code 0 means every check passed; 1 means at least one failed.
"""

import ast
import hashlib
import json
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCES_PATH = os.path.join(HERE, "sources.json")
ENTRY_PATH = os.path.join(HERE, "entry.png")
MAIN_PATH = os.path.join(HERE, "main.py")
LICENSE_PATH = os.path.join(HERE, "LICENSE")
FRESHNESS_PATH = os.path.join(HERE, ".makefun", "freshness.json")

WIDTH = 1024
HEIGHT = 1024
MAX_BYTES = 1048576

CERTAINTY_LABELS = {"CONFIRMED", "OFFICIAL", "REPORTED", "CLAIM"}

REQUIRED_DOCS = [
    "README.md",
    "SOURCES.md",
    "DESIGN.md",
    "OUTLETS.md",
    "TIMELINE.md",
    "GAZETTEER.md",
    "BUILDLOG.md",
    "EDITION.md",
    "DOSSIER.md",
    "PRESS.md",
]

REQUIRED_STORIES = [
    "cairo-tanker-fire",
    "houthi-ras-tanura",
    "wall-street-comeback",
    "gaza-strike",
    "colombia-siege",
    "macys-parade",
    "bangladesh-wage",
    "us-tariffs-14",
    "nvidia-creditwatch",
    "champions-liverpool-barca",
    "champions-psg-bayern",
    "solomon-australia-pact",
    "pakistan-astronaut",
]

REQUIRED_BACKGROUND = [
    "energy-shock",
    "markets-ai",
    "trade-war-2026",
    "south-asia",
    "pacific-shift",
    "europe-courts",
]

# Palette probes: (x, y, expected RGB, what it proves)
PIXEL_PROBES = [
    (8, 29, (18, 16, 14), "masthead band is black"),
    (1016, 29, (18, 16, 14), "masthead band reaches the right edge"),
    (8, 151, (31, 58, 95), "region strip is blue"),
    (8, 213, (46, 94, 60), "numbers strip is green"),
    (24, 960, (178, 34, 34), "date check box has a red border"),
]


def sha256_file(path):
    """Return the hex sha256 of a file."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def check_sources(problems):
    """Validate the edition data: counts, order, tiers, regions, pins."""
    if not os.path.isfile(SOURCES_PATH):
        problems.append("sources.json is missing")
        return None
    with open(SOURCES_PATH, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    stories = data.get("stories", [])
    if len(stories) < 29:
        problems.append("only %d stories, need at least 29"
                        % len(stories))
    numbers = [s.get("number") for s in stories]
    if numbers != list(range(1, len(stories) + 1)):
        problems.append("story numbers are not 1..%d in order"
                        % len(stories))
    tiers = {"feature": 0, "grid": 0, "brief": 0}
    for story in stories:
        tier = story.get("tier")
        if tier not in tiers:
            problems.append("story %s has unknown tier %r"
                            % (story.get("number"), tier))
            continue
        tiers[tier] += 1
        if story.get("certainty") not in CERTAINTY_LABELS:
            problems.append("story %s has bad certainty label %r"
                            % (story.get("number"),
                               story.get("certainty")))
        if not story.get("headline"):
            problems.append("story %s has no headline"
                            % story.get("number"))
        if not story.get("summary"):
            problems.append("story %s has no summary"
                            % story.get("number"))
        if not story.get("outlets"):
            problems.append("story %s lists no confirming outlets"
                            % story.get("number"))
        if not story.get("region"):
            problems.append("story %s has no region"
                            % story.get("number"))
    if tiers["feature"] != 3:
        problems.append("need exactly 3 features, got %d"
                        % tiers["feature"])
    if tiers["grid"] != 10:
        problems.append("need exactly 10 grid items, got %d"
                        % tiers["grid"])
    regions = data.get("regions", [])
    region_total = sum(r.get("count", 0) for r in regions)
    if region_total != len(stories):
        problems.append("region counts sum to %d, stories number %d"
                        % (region_total, len(stories)))
    if len(regions) < 5:
        problems.append("only %d regions, need at least 5"
                        % len(regions))
    stamps = data.get("utc_stamps", [])
    if not 5 <= len(stamps) <= 8:
        problems.append("%d UTC stamps, need 5-8" % len(stamps))
    numbers_strip = data.get("numbers", [])
    if not 5 <= len(numbers_strip) <= 7:
        problems.append("%d numbers, need 5-7" % len(numbers_strip))
    pinned = [s for s in stories if s.get("number", 99) <= 13]
    if len(pinned) != 13:
        problems.append("need 13 pinned stories, got %d" % len(pinned))
    for story in pinned:
        pin = story.get("pin")
        if not pin:
            problems.append("story %s has no map pin"
                            % story.get("number"))
            continue
        lat = pin.get("lat")
        lon = pin.get("lon")
        if lat is None or not -90 <= lat <= 90:
            problems.append("story %s pin latitude %r out of range"
                            % (story.get("number"), lat))
        if lon is None or not -180 <= lon <= 180:
            problems.append("story %s pin longitude %r out of range"
                            % (story.get("number"), lon))
        if not pin.get("place"):
            problems.append("story %s pin has no place name"
                            % story.get("number"))
    if not data.get("date_check_excluded"):
        problems.append("date check exclusion list is empty")
    if data.get("date_line") != "Thursday 26 November 2026":
        problems.append("date line is %r, expected the edition date"
                        % data.get("date_line"))
    return {
        "stories": len(stories),
        "features": tiers["feature"],
        "grid": tiers["grid"],
        "briefs": tiers["brief"],
        "regions": len(regions),
        "utc_stamps": len(stamps),
        "numbers": len(numbers_strip),
    }


def check_image(problems):
    """Check the rendered PNG: format, size, and page furniture."""
    if not os.path.isfile(ENTRY_PATH):
        problems.append("entry.png is missing")
        return None
    size_bytes = os.path.getsize(ENTRY_PATH)
    if size_bytes > MAX_BYTES:
        problems.append("entry.png is %d bytes, over the 1 MiB limit"
                        % size_bytes)
    with Image.open(ENTRY_PATH) as image:
        if image.format != "PNG":
            problems.append("entry.png is %s, not PNG" % image.format)
        if image.size != (WIDTH, HEIGHT):
            problems.append("entry.png is %s, not 1024x1024"
                            % (image.size,))
        pixels = image.convert("RGB")
        for x, y, expected, what in PIXEL_PROBES:
            got = pixels.getpixel((x, y))
            if got != expected:
                problems.append("%s: pixel (%d, %d) is %s, expected %s"
                                % (what, x, y, got, expected))
        # The world map must actually contain filled land in its band:
        # solid continent silhouettes cover a large share of the box.
        land_colour = (104, 128, 162)
        land = 0
        for mx in range(24, 604, 4):
            for my in range(684, 778, 4):
                if pixels.getpixel((mx, my)) == land_colour:
                    land += 1
        if land < 300:
            problems.append("world map band has only %d land samples, "
                            "expected at least 300" % land)
        # Each feature scene must hold more than one colour: a drawn
        # scene, not a blank panel.
        scene_boxes = [
            (18, 238, 330, 302),
            (352, 238, 664, 302),
            (686, 238, 998, 302),
        ]
        for i, (x0, y0, x1, y1) in enumerate(scene_boxes, start=1):
            colours = set()
            for sx in range(x0, x1, 6):
                for sy in range(y0, y1, 6):
                    colours.add(pixels.getpixel((sx, sy)))
            if len(colours) < 5:
                problems.append("feature %d scene looks blank: only %d "
                                "colours sampled" % (i, len(colours)))
    return {
        "bytes": size_bytes,
        "sha256": sha256_file(ENTRY_PATH),
    }


def check_main(problems):
    """Check the grader entry point: stdlib only, copies the image."""
    if not os.path.isfile(MAIN_PATH):
        problems.append("main.py is missing")
        return None
    with open(MAIN_PATH, "r", encoding="utf-8") as handle:
        source = handle.read()
    tree = ast.parse(source, filename="main.py")
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])
    allowed = set(sys.stdlib_module_names)
    for name in sorted(imports):
        if name not in allowed:
            problems.append("main.py imports %s, which is not stdlib"
                            % name)
    if "PIL" in imports or "Pillow" in imports:
        problems.append("main.py imports PIL, forbidden in the grader")
    for banned in ("socket", "urllib", "requests", "http"):
        if banned in imports:
            problems.append("main.py imports %s, network use is not "
                            "allowed for the entry point" % banned)
    if "shutil.copyfile" not in source:
        problems.append("main.py does not copy entry.png with "
                        "shutil.copyfile")
    if "MAKEFUN_OUTPUT_DIR" not in source:
        problems.append("main.py does not honour MAKEFUN_OUTPUT_DIR")
    if "MAKEFUN_BOT_DIR" not in source:
        problems.append("main.py does not prefer MAKEFUN_BOT_DIR")
    return {"imports": sorted(imports)}


def check_license(problems):
    """The beacon LICENSE must keep its SPDX identifier."""
    if not os.path.isfile(LICENSE_PATH):
        problems.append("LICENSE is missing")
        return None
    with open(LICENSE_PATH, "r", encoding="utf-8") as handle:
        text = handle.read()
    if "SPDX-License-Identifier: MIT" not in text:
        problems.append("LICENSE lacks the SPDX MIT identifier line")
    return {"spdx": "MIT"}


def check_beacon(problems):
    """The make.fun beacon freshness file must exist and be complete."""
    if not os.path.isfile(FRESHNESS_PATH):
        problems.append(".makefun/freshness.json is missing")
        return None
    with open(FRESHNESS_PATH, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    if "round" not in data:
        problems.append("freshness.json has no drand round")
    if "wallet" not in data:
        problems.append("freshness.json has no wallet")
    return {"round": data.get("round")}


def check_docs(problems):
    """The full documentation package must be present."""
    missing = []
    for name in REQUIRED_DOCS:
        if not os.path.isfile(os.path.join(HERE, name)):
            missing.append(name)
    for slug in REQUIRED_STORIES:
        path = os.path.join(HERE, "stories", slug + ".md")
        if not os.path.isfile(path):
            missing.append("stories/%s.md" % slug)
    for slug in REQUIRED_BACKGROUND:
        path = os.path.join(HERE, "background", slug + ".md")
        if not os.path.isfile(path):
            missing.append("background/%s.md" % slug)
    if not os.path.isfile(os.path.join(HERE, "background",
                                      "CONTEXT.md")):
        missing.append("background/CONTEXT.md")
    if missing:
        problems.append("missing documentation: %s"
                        % ", ".join(missing))
    return {"missing": len(missing)}


def main(argv):
    """Run every check and report the result."""
    want_report = "--report" in argv
    problems = []
    sources = check_sources(problems)
    image = check_image(problems)
    entry = check_main(problems)
    licence = check_license(problems)
    beacon = check_beacon(problems)
    docs = check_docs(problems)
    lines = []
    if sources is not None:
        lines.append("sources: %(stories)d stories "
                     "(%(features)d features, %(grid)d grid, "
                     "%(briefs)d briefs), %(regions)d regions, "
                     "%(utc_stamps)d UTC stamps, %(numbers)d numbers"
                     % sources)
    if image is not None:
        lines.append("entry.png: %d bytes, sha256 %s"
                     % (image["bytes"], image["sha256"]))
    if entry is not None:
        lines.append("main.py imports (stdlib only): %s"
                     % ", ".join(entry["imports"]))
    if licence is not None:
        lines.append("LICENSE: SPDX %s" % licence["spdx"])
    if beacon is not None:
        lines.append("beacon: drand round %s" % beacon["round"])
    if docs is not None:
        lines.append("documentation: %d file(s) missing"
                     % docs["missing"])
    if problems:
        lines.append("verify: FAILED, %d problem(s)" % len(problems))
        for problem in problems:
            lines.append("  !! " + problem)
    else:
        lines.append("verify: PASSED, all checks green")
    if want_report:
        print("\n".join(lines))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
