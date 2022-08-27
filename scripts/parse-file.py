#!/usr/bin/env python3

from io import StringIO, TextIOBase
import re
import sys
from typing import Iterable, Iterator

TEMPLATE_DIR = "templates"

DIRECTIVE_PAT = re.compile("{([^}]+)}")
OPEN_PAT = re.compile("{(\**)")


def comb_rem(rem: str, src: Iterator[str]):
    if rem:
        yield rem
    for line in src:
        yield line


def parse_file(src: Iterator[str], dest: TextIOBase = sys.stdout,
               subs: dict[str, str] = {}, exit_pat: str = None,
               rem: str = None):

    exit_found = False

    for line in comb_rem(rem, src):
        # Breaking this while implies that we've consumed the whole line
        while line:
            if exit_pat:
                exit_idx = line.find(exit_pat)
                exit_found = exit_idx != -1

            match = DIRECTIVE_PAT.search(line)

            if not exit_found and not match:
                dest.write(line)
                break

            if exit_found and not (match and match.start() < exit_idx):
                dest.write(line[:exit_idx])
                dest.flush()
                return line[exit_idx + len(exit_pat):]

            if match.start() > 0:
                dest.write(line[:match.start()])

            line = line[match.end():]

            match match.group(1).split():
                case ["include", filename]:
                    with open(f"{TEMPLATE_DIR}/{filename}") as file:
                        parse_file(file, dest)

                case ["include", filename, "with"]:
                    incl_subs: dict[str, str] = {}
                    line = parse_subs(src, incl_subs, subs, line)

                    with open(f"{TEMPLATE_DIR}/{filename}") as file:
                        parse_file(file, dest, incl_subs)

                case [key] if key in subs:
                    dest.write(subs[key])

                case _:
                    dest.write(match[0])
    dest.flush()


def parse_subs(src: Iterator[str], incl_subs: dict[str, str],
               subs: dict[str, str], rem: str):
    for line in comb_rem(rem, src):
        while line:
            exit_idx = line.find("{endwith}")
            exit_found = exit_idx != -1

            colon_idx = line.find(":")
            colon_found = colon_idx != -1

            if not exit_found and not colon_found:
                break

            if exit_found and not (colon_found and colon_idx < exit_idx):
                return line[exit_idx + len("{endwith}"):]

            key = line[:colon_idx].strip()
            match = OPEN_PAT.search(line, colon_idx + 1)
            strbuf = StringIO()

            if match:
                line = parse_file(src, strbuf, subs, match[1] + "}",
                                  line[match.end():])
            else:
                parse_file(iter([line[colon_idx + 1:]]), strbuf, subs)
                line = ""   # Force exit

            incl_subs[key] = strbuf.getvalue().strip()


with open(sys.argv[1]) as file:
    parse_file(file)
