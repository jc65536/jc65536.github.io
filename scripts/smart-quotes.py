import re
import sys

_depth = 6

_TEXT = 0
_TAG = 1

_nested_tags = "|".join(["(?:<(?:[^<>]"] * _depth) + ")*>)" * _depth

_tag_pat = re.compile(fr"""
    (?s: <! ( -- .*? -- \s* )+ > ) |  # comment
    (?s: <\? .*? \?> ) |              # processing instruction
    {_nested_tags}
""", re.VERBOSE)

_tags_to_skip = re.compile("<(/?)(?:pre|code|kbd|script|math)[\s>]")

_escapes = [(r"\\", "&#92;"),
            (r"\"", "&#34;"),
            (r"\'", "&#39;"),
            (r"\.", "&#46;"),
            (r"\-", "&#45;")]

_replacements = [("---",   "\u2014"),
                 ("--",    "\u2013"),
                 ("...",   "\u2026"),
                 (". . .", "\u2026")]

_first_squote_pat, _first_dquote_pat = [re.compile(fr"^{q}(?=[\W_]\B)")
                                        for q in "\'\""]

_sdquotes_pat = re.compile("\"'(?=\\w)")
_dsquotes_pat = re.compile("'\"(?=\\w)")

_decade_pat = re.compile(r"'(?=\d{2}s)")

_close_class = r"[^ \t\r\n[{(-]"
_dec_dashes = "\u2013|\u2014"

_open_squote_pat, _open_dquote_pat = [re.compile(fr"""
    (
        \s            |   # a whitespace char, or
        &nbsp;        |   # a non-breaking space entity, or
        --            |   # dashes, or
        &[mn]dash;    |   # named dash entities
        {_dec_dashes} |   # or decimal entities
        &\#x201[34];      # or hex
    )
    {q}                   # the quote
    (?=\w)                # followed by a word character
""", re.VERBOSE) for q in "\'\""]

_close_squote_pat = re.compile(fr"""
    ({_close_class})?
    '
    (?(1)|          # If $1 captured, then do nothing;
      (?=\s | s\b)  # otherwise, positive lookahead for a whitespace
    )               # char or an 's' at a word ending position. This
                    # is a special case to handle something like:
                    # "<i>Custer</i>'s Last Stand."
""", re.VERBOSE | re.IGNORECASE)

_close_dquote_pat = re.compile(fr"""
    ({_close_class})?
    "
    (?(1)|(?=\s))   # If $1 captured, then do nothing;
                       # if not, then make sure the next char is whitespace.
""", re.VERBOSE)

def smart_quotes(text: str):
    result = ""
    in_pre = False
    prev_token_last_char = ""

    for token in _tokenize(text):
        if token[0] == _TAG:
            result += token[1]
            match = _tags_to_skip.match(token[1])
            if match:
                in_pre = match[1] != "/"
        else:
            t = token[1]
            last_char = t[-1:]

            if not in_pre:
                for esc, ent in _escapes:
                    t = t.replace(esc, ent)

                for pat, char in _replacements:
                    t = t.replace(pat, char)

                if t == "'":
                    if not prev_token_last_char.isspace() and prev_token_last_char:
                        t = "\u2019"
                    else:
                        t = "\u2018"
                elif t == '"':
                    if not prev_token_last_char.isspace() and prev_token_last_char:
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
                    t = t.replace(ent, esc[1:])

            prev_token_last_char = last_char
            result += t
    
    return result


def _tokenize(text: str):
    pos = 0

    while match := _tag_pat.search(text, pos):
        if pos < match.start():
            yield (_TEXT, text[pos:match.start()])
        yield (_TAG, match[0])
        pos = match.end()

    if pos < len(text):
        yield (_TEXT, text[pos:])

print(smart_quotes(sys.stdin.read()), end="")
