"""Split timed SRT captions into one cue per word."""

import argparse
import re
from pathlib import Path

TIMING = re.compile(r"(\d{2,}:\d{2}:\d{2},\d{3})\s+-->\s+(\d{2,}:\d{2}:\d{2},\d{3})")


def milliseconds(timestamp):
    hours, minutes, seconds, fraction = map(int, re.split(r"[:,]", timestamp))
    if minutes >= 60 or seconds >= 60:
        raise ValueError(f"Invalid timestamp {timestamp}")
    return ((hours * 60 + minutes) * 60 + seconds) * 1000 + fraction


def timestamp(total):
    seconds, fraction = divmod(total, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02},{fraction:03}"


def split_srt(source):
    output = []
    source = source.strip()
    if not source:
        raise ValueError("The input contains no subtitle cues.")
    for cue_number, block in enumerate(re.split(r"\n(?:[^\S\n]*\n)+", source), 1):
        lines = block.splitlines()
        match = TIMING.fullmatch(lines[1].strip()) if len(lines) >= 3 else None
        if match is None or not lines[0].strip().isdigit():
            raise ValueError(f"Invalid SRT structure in cue {cue_number}.")
        start, end = map(milliseconds, match.groups())
        # Remove common SRT formatting tags before splitting across whitespace.
        words = re.sub(r"</?(?:b|i|u|font)\b[^>]*>", "", " ".join(lines[2:]), flags=re.I).split()
        duration = end - start
        if not words or duration < len(words):
            raise ValueError(f"Cue {cue_number} cannot allocate at least 1 ms per word.")
        for index, word in enumerate(words):
            word_start = start + duration * index // len(words)
            word_end = start + duration * (index + 1) // len(words)
            output.append(f"{len(output) + 1}\n{timestamp(word_start)} --> {timestamp(word_end)}\n{word}")
    return "\n\n".join(output) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="An existing UTF-8 SRT file")
    parser.add_argument("output", type=Path, help="A new SRT file")
    args = parser.parse_args()
    try:
        source = args.input.read_text(encoding="utf-8-sig")
        result = split_srt(source)
        with args.output.open("x", encoding="utf-8", newline="\n") as destination:
            destination.write(result)
    except (OSError, ValueError) as error:
        parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    main()
