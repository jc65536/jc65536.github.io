#!/usr/bin/env python3

import re
import sys
from typing import Iterable, Iterator

TEMPLATE_DIR = "templates"

DIRECTIVE_PAT = re.compile("{([^}]+)}")
OPEN_PAT = re.compile("{(\**)")

remainder = ""


def join_strip(lines: Iterable[str]):
    return "".join(lines).strip()


def get_rem():
    return remainder


def set_rem(s: str):
    global remainder
    remainder = s


def comb_rem(src: Iterator[str]):
    if remainder:
        yield remainder
    for line in src:
        yield line


def parse_file(src: Iterator[str], subs: dict[str, str] = {},
               exit_pat: str = None):

    exit_found = False

    for line in comb_rem(src):
        # Breaking this while implies that we've consumed the whole line
        while line:
            if exit_pat:
                exit_idx = line.find(exit_pat)
                exit_found = exit_idx != -1

            match = DIRECTIVE_PAT.search(line)

            if not exit_found and not match:
                yield line
                break

            if exit_found and not (match and match.start() < exit_idx):
                yield line[:exit_idx]
                set_rem(line[exit_idx + len(exit_pat):])
                return

            if match.start() > 0:
                yield line[:match.start()]

            line = line[match.end():]

            match match.group(1).split():
                case ["include", filename]:
                    with open(f"{TEMPLATE_DIR}/{filename}") as file:
                        yield from parse_file(file)

                case ["include", filename, "with"]:
                    incl_subs = {}
                    parse_subs(src, incl_subs, subs)
                    line = get_rem()

                    with open(f"{TEMPLATE_DIR}/{filename}") as file:
                        yield from parse_file(file, incl_subs)

                case [key] if key in subs:
                    yield subs[key]

                case _:
                    yield match[0]


def parse_subs(src: Iterator[str], incl_subs: dict[str, str],
               subs: dict[str, str]):

    for line in comb_rem(src):
        while line:
            exit_idx = line.find("{endwith}")
            exit_found = exit_idx != -1

            colon_idx = line.find(":")
            colon_found = colon_idx != -1

            if not exit_found and not colon_found:
                break

            if exit_found and not (colon_found and colon_idx < exit_idx):
                set_rem(line[exit_idx + len("{endwith}"):])
                return

            key = line[:colon_idx].strip()
            match = OPEN_PAT.search(line, colon_idx + 1)

            if match:
                set_rem(line[match.end():])
                incl_subs[key] = join_strip(
                    parse_file(src, subs, match[1] + "}"))
                line = get_rem()
            else:
                incl_subs[key] = join_strip(parse_file(
                    iter([line[colon_idx + 1:]]), subs))
                break


with open(sys.argv[1]) as file:
    for line in parse_file(file):
        print(line, end="")
