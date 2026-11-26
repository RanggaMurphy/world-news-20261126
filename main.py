"""Entry point for the make.fun news-image entry.

The repository holds the finished front page as entry.png. This program
only copies that image to the output directory the grader provides.

It uses nothing but the Python standard library, so it runs in a stock
python:3.13-slim image with no Pillow and no system fonts. It never reads
the network and it never writes into the repository itself, because the
grader mounts the repository read-only.
"""

import os
import shutil
import sys


def find_source():
    """Return the directory that holds entry.png for this run."""
    bot_dir = os.environ.get("MAKEFUN_BOT_DIR")
    if bot_dir:
        candidate = os.path.join(bot_dir, "entry.png")
        if os.path.isfile(candidate):
            return bot_dir
    here = os.path.dirname(os.path.abspath(__file__))
    return here


def main():
    source_dir = find_source()
    source = os.path.join(source_dir, "entry.png")
    if not os.path.isfile(source):
        print("entry.png not found in %s" % source_dir, file=sys.stderr)
        return 1
    output_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not output_dir:
        output_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(output_dir, exist_ok=True)
    destination = os.path.join(output_dir, "entry.png")
    if os.path.abspath(source) == os.path.abspath(destination):
        print("entry.png is already in place at %s" % destination)
        return 0
    shutil.copyfile(source, destination)
    if os.path.getsize(destination) != os.path.getsize(source):
        print("copied entry.png is %d bytes, source is %d bytes"
              % (os.path.getsize(destination), os.path.getsize(source)),
              file=sys.stderr)
        return 1
    print("copied entry.png to %s" % destination)
    return 0


if __name__ == "__main__":
    sys.exit(main())
