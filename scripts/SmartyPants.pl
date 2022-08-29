#!/usr/bin/perl -w

#
# SmartyPants  -  A Plug-In for Movable Type, Blosxom, and BBEdit
# by John Gruber
# http://daringfireball.net
#

package SmartyPants;
use strict;
use open qw( :std :encoding(UTF-8) );


# Globals:
my $tags_to_skip = qr!<(/?)(?:pre|code|kbd|script|math)[\s>]!;


#### Process incoming text: #####################################
my $old = $/;
undef $/;               # slurp the whole file
my $text = <>;
$/ = $old;
print SmartyPants($text);


sub SmartyPants {
    my $text = shift;   # text to be parsed

    my $tokens ||= _tokenize($text);
    my $result = '';
    my $in_pre = 0;  # Keep track of when we're inside <pre> or <code> tags.

    my $prev_token_last_char = "";  # This is a cheat, used to get some context
                                    # for one-character tokens that consist of 
                                    # just a quote char. What we do is remember
                                    # the last character of the previous text
                                    # token, to use as context to curl single-
                                    # character quote tokens correctly.

    foreach my $cur_token (@$tokens) {
        if ($cur_token->[0] eq "tag") {
            # Don't mess with quotes inside tags.
            $result .= $cur_token->[1];
            if ($cur_token->[1] =~ m/$tags_to_skip/) {
                $in_pre = defined $1 && $1 eq '/' ? 0 : 1;
            }
        } else {
            my $t = $cur_token->[1];
            my $last_char = substr($t, -1); # Remember last char of this token before processing.
            if (! $in_pre) {
                $t = ProcessEscapes($t);

                $t = EducateDashes($t);

                $t = EducateEllipses($t);

                if ($t eq q/'/) {
                    # Special case: single-character ' token
                    if ($prev_token_last_char =~ m/\S/) {
                        $t = "\N{U+2019}";
                    }
                    else {
                        $t = "\N{U+2018}";
                    }
                }
                elsif ($t eq q/"/) {
                    # Special case: single-character " token
                    if ($prev_token_last_char =~ m/\S/) {
                        $t = "\N{U+201D}";
                    }
                    else {
                        $t = "\N{U+201C}";
                    }
                }
                else {
                    # Normal case:
                    $t = EducateQuotes($t);
                }

                $t = UndoEscapes($t);
            }
            $prev_token_last_char = $last_char;
            $result .= $t;
        }
    }

    return $result;
}


sub EducateQuotes {
    local $_ = shift;

    # Tell perl not to gripe when we use $1 in substitutions,
    # even when it's undefined. Use $^W instead of "no warnings"
    # for compatibility with Perl 5.005:
    local $^W = 0;


    # Make our own "punctuation" character class, because the POSIX-style
    # [:PUNCT:] is only available in Perl 5.6 or later:
    my $punct_class = qr/[!"#\$\%'()*+,-.\/:;<=>?\@\[\\\]\^_`{|}~]/;

    # Special case if the very first character is a quote
    # followed by punctuation at a non-word-break. Close the quotes by brute force:
    s/^'(?=$punct_class\B)/\N{U+2019}/;
    s/^"(?=$punct_class\B)/\N{U+201D}/;


    # Special case for double sets of quotes, e.g.:
    #   <p>He said, "'Quoted' words in a larger quote."</p>
    s/"'(?=\w)/\N{U+201C}\N{U+2018}/g;
    s/'"(?=\w)/\N{U+2018}\N{U+201C}/g;

    # Special case for decade abbreviations (the '80s):
    s/'(?=\d{2}s)/\N{U+2019}/g;

    my $close_class = qr![^\ \t\r\n\[\{\(\-]!;
    my $dec_dashes = qr/\N{U+2013}|\N{U+2014}/;

    # Get most opening single quotes:
    s {
        (
            \s          |   # a whitespace char, or
            &nbsp;      |   # a non-breaking space entity, or
            --          |   # dashes, or
            &[mn]dash;  |   # named dash entities
            $dec_dashes |   # or decimal entities
            &\#x201[34];    # or hex
        )
        '                   # the quote
        (?=\w)              # followed by a word character
    } {$1\N{U+2018}}xg;
    # Single closing quotes:
    s {
        ($close_class)?
        '
        (?(1)|          # If $1 captured, then do nothing;
          (?=\s | s\b)  # otherwise, positive lookahead for a whitespace
        )               # char or an 's' at a word ending position. This
                        # is a special case to handle something like:
                        # "<i>Custer</i>'s Last Stand."
    } {$1\N{U+2019}}xgi;

    # Any remaining single quotes should be opening ones:
    s/'/\N{U+2018}/g;


    # Get most opening double quotes:
    s {
        (
            \s          |   # a whitespace char, or
            &nbsp;      |   # a non-breaking space entity, or
            --          |   # dashes, or
            &[mn]dash;  |   # named dash entities
            $dec_dashes |   # or decimal entities
            &\#x201[34];    # or hex
        )
        "                   # the quote
        (?=\w)              # followed by a word character
    } {$1\N{U+201C}}xg;

    # Double closing quotes:
    s {
        ($close_class)?
        "
        (?(1)|(?=\s))   # If $1 captured, then do nothing;
                           # if not, then make sure the next char is whitespace.
    } {$1\N{U+201D}}xg;

    # Any remaining quotes should be opening ones.
    s/"/\N{U+201C}/g;

    return $_;
}


sub EducateDashes {
    local $_ = shift;
    s/---/\N{U+2014}/g;    # em
    s/--/\N{U+2013}/g;     # en
    return $_;
}


sub EducateEllipses {
    local $_ = shift;
    s/\.\.\./\N{U+2026}/g;
    s/\. \. \./\N{U+2026}/g;
    return $_;
}


sub ProcessEscapes {
    local $_ = shift;
    s! \\\\ !&#92;!gx;
    s! \\"  !&#34;!gx;
    s! \\'  !&#39;!gx;
    s! \\\. !&#46;!gx;
    s! \\-  !&#45;!gx;
    s! \\`  !&#96;!gx;
    return $_;
}


sub UndoEscapes {
    local $_ = shift;
    s!&#92;!\\!g;
    s!&#34;!"!g;
    s!&#39;!'!g;
    s!&#46;!.!g;
    s!&#45;!-!g;
    s!&#96;!`!g;
    return $_;
}


sub _tokenize {
#
#   Parameter:  String containing HTML markup.
#   Returns:    Reference to an array of the tokens comprising the input
#               string. Each token is either a tag (possibly with nested,
#               tags contained therein, such as <a href="<MTFoo>">, or a
#               run of text between tags. Each element of the array is a
#               two-element array; the first is either 'tag' or 'text';
#               the second is the actual value.
#
#
#   Based on the _tokenize() subroutine from Brad Choate's MTRegex plugin.
#       <http://www.bradchoate.com/past/mtregex.php>
#

    my $str = shift;
    my $pos = 0;
    my $len = length $str;
    my @tokens;

    my $depth = 6;
    my $nested_tags = join('|', ('(?:<(?:[^<>]') x $depth) . (')*>)' x  $depth);
    my $match = qr/(?s: <! ( -- .*? -- \s* )+ > ) |  # comment
                   (?s: <\? .*? \?> ) |              # processing instruction
                   $nested_tags/x;                   # nested tags

    while ($str =~ m/($match)/g) {
        my $whole_tag = $1;
        my $sec_start = pos $str;
        my $tag_start = $sec_start - length $whole_tag;
        if ($pos < $tag_start) {
            push @tokens, ['text', substr($str, $pos, $tag_start - $pos)];
        }
        push @tokens, ['tag', $whole_tag];
        $pos = pos $str;
    }
    push @tokens, ['text', substr($str, $pos, $len - $pos)] if $pos < $len;
    \@tokens;
}


1;
