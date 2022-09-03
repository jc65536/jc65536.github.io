from curses.ascii import isspace
from io import TextIOBase
import re
import sys

_depth = 6

_TEXT = 0
_TAG = 1

_nested_tags = "|".join([r"(?:<(?:[^<>]"] * _depth) + r")*>)" * _depth

_tag_pat = re.compile(fr"""
    (?s: <! ( -- .*? -- \s* )+ > ) |  # comment
    (?s: <\? .*? \?> ) |              # processing instruction
    {_nested_tags}
""", re.VERBOSE)

_tags_to_skip = re.compile(r"<(/?)(?:pre|code|kbd|script|math)[\s>]")

# These aren't regex. The keys are directly substituted.
_escapes = ((r"\\", "&#92;"),
            (r"\"", "&#34;"),
            (r"\'", "&#39;"),
            (r"\.", "&#46;"),
            (r"\-", "&#45;"))

_replacements = (("---",   "\u2014"),
                 ("--",    "\u2013"),
                 ("...",   "\u2026"),
                 (". . .", "\u2026"))

# Special case if the very first character is a quote followed by punctuation
# at a non-word break. Close the quotes by brute force.
_first_squote_pat = re.compile(r"^'(?=[\W_]\B)")
_first_dquote_pat = re.compile(r'^"(?=[\W_]\B)')

# Special case for double sets of quotes, e.g. "'Quoted'"
_sdquotes_pat = re.compile("\"'(?=\\w)")
_dsquotes_pat = re.compile("'\"(?=\\w)")

# Special case for decade abbreviations (the '80s)
_decade_pat = re.compile(r"'(?=\d{2}s)")

_close_class = r"[^ \t\r\n[{(-]"
_dashes = "\u2013|\u2014"

# Most opening single/double quotes
_open_squote_pat, _open_dquote_pat = [re.compile(fr"""
    (
        \s          |   # a whitespace char, or
        &nbsp;      |   # a non-breaking space entity, or
        --          |   # dashes, or
        &[mn]dash;  |   # named dash entities
        {_dashes}   |   # or decimal entities
        &\#x201[34];    # or hex
    )
    {q}                 # the quote
    (?=\w)              # followed by a word character
""", re.VERBOSE) for q in "\'\""]

# Most closing single quotes
_close_squote_pat = re.compile(fr"""
    ({_close_class})?
    '
    (?(1)|          # If $1 captured, then do nothing;
      (?=\s | s\b)  # otherwise, positive lookahead for a whitespace
    )               # char or an 's' at a word ending position. This
                    # is a special case to handle something like:
                    # "<i>Custer</i>'s Last Stand."
""", re.VERBOSE | re.IGNORECASE)

# Most closing double quotes
_close_dquote_pat = re.compile(fr"""
    ({_close_class})?
    "
    (?(1)|(?=\s))   # If $1 captured, then do nothing;
                    # if not, then make sure the next char is whitespace.
""", re.VERBOSE)


def smart_quotify(text: str, dest: TextIOBase):
    in_pre = False  # Keep track of when we're inside <pre> or <code> tags.

    prev_token_last = ""    # This is a cheat, used to get some context
                            # for one-character tokens that consist of 
                            # just a quote char. What we do is remember
                            # the last character of the previous text
                            # token, to use as context to curl single-
                            # character quote tokens correctly.

    for token in _tokenize(text):
        if token[0] == _TAG:
            dest.write(token[1])
            match = _tags_to_skip.match(token[1])
            if match:
                in_pre = match[1] != "/"
        else:
            t = token[1]
            last = t[-1:]

            if not in_pre:
                for esc, ent in _escapes:
                    t = t.replace(esc, ent)

                for pat, char in _replacements:
                    t = t.replace(pat, char)

                if t == "'":
                    if not prev_token_last.isspace() and prev_token_last:
                        t = "\u2019"
                    else:
                        t = "\u2018"
                elif t == '"':
                    if not prev_token_last.isspace() and prev_token_last:
                        t = "\u201d"
                    else:
                        t = "\u201c"
                else:
                    t = _first_squote_pat.sub("\u2019", t, 1)
                    t = _first_dquote_pat.sub("\u201d", t, 1)
                    t = _dsquotes_pat.sub("\u201c\u2018", t)
                    t = _sdquotes_pat.sub("\u2018\u201c", t)
                    t = _decade_pat.sub("\u2019", t)
                    t = _open_squote_pat.sub("\\1\u2018", t)
                    t = _close_squote_pat.sub("\\1\u2019", t)
                    t = t.replace("'", "\u2018")
                    t = _open_dquote_pat.sub("\\1\u201c", t)
                    t = _close_dquote_pat.sub("\\1\u201d", t)
                    t = t.replace('"', "\u201c")

                for esc, ent in _escapes:
                    t = t.replace(ent, esc[1])

            prev_token_last = last
            dest.write(t)
    
    dest.flush()


def _tokenize(text: str):
    while match := _tag_pat.search(text):
        if match.start() > 0:
            yield (_TEXT, text[:match.start()])
        yield (_TAG, match[0])
        text = text[match.end():]

    if text:
        yield (_TEXT, text)
