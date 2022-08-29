#!/usr/bin/perl

use strict;
use warnings;
use lib "scripts";
use SmartyPants;
use open qw(:std :encoding(UTF-8));
use Encode "decode";

my $TEMPLATE_DIR = "templates";

my $DIRECT_PAT = qr/\$?{([^}]+)}/;
my $OPEN_PAT = qr/{(\**)/;

sub parse_file;
sub parse_with;

sub trim {
    $_[0] =~ s/^\s+|\s+$//g;
}

sub file_iter {
    my $file = shift;
    sub { <$file> }
}

sub str_iter {
    my @lines = split /\n/, shift;
    sub { shift @lines }
}

sub parse_file {
    my ($iter, $dest, $subs, $exit_pat, $line) = @_;

    do {
        while ($line) {
            my $exit_idx = -1;
            my $exit_found = 0;
            if (defined $exit_pat) {
                $exit_idx = index $line, $exit_pat;
                $exit_found = $exit_idx != -1;
            }

            my $direct_found = $line =~ $DIRECT_PAT;
            my $direct_idx = $-[0];
            my $direct_end = $+[0];

            if (!$exit_found && !$direct_found) {
                print $dest $line;
                last;
            }

            if ($exit_found && !($direct_found && $direct_idx < $exit_idx)) {
                print $dest substr($line, 0, $exit_idx);
                return substr($line, $exit_idx + length $exit_pat);
            }

            print $dest substr($line, 0, $direct_idx) if ($direct_idx > 0);

            my $match = substr($line, $direct_idx, $direct_end - $direct_idx);
            my @tokens = split " ", $1;
            my $name = shift @tokens;
            $line = substr $line, $direct_end;

            if ($name eq "include") {
                my $filename = shift @tokens;
                if (defined $tokens[0] && $tokens[0] eq "with") {
                    my %incl_subs;

                    $line = parse_with $iter, \%incl_subs, $subs, $line;

                    open my $file, "<", "$TEMPLATE_DIR/$filename";
                    parse_file file_iter($file), $dest, \%incl_subs;
                    close $file;

                    next;
                } else {
                    # Include file with no processing
                    open my $file, "<", "$TEMPLATE_DIR/$filename";
                    parse_file file_iter($file), $dest;
                    close $file;
                }
            } elsif ($name eq "q") {
                if (substr($match, 0, 1) eq "\$") {
                    print $dest SmartyPants::SmartyPants($line);
                    last;
                } else {
                    my $str = "";

                    open my $str_io, ">", \$str;
                    $line = parse_file $iter, $str_io, $subs, "{endq}", $line;
                    close $str_io;

                    print $dest SmartyPants::SmartyPants(decode("UTF-8",
                                                                $str));
                }
            } elsif ($name eq "with") {
                $line = parse_with $iter, $subs, $subs, $line;
            } elsif (exists $$subs{$name}) {
                print $dest $$subs{$name};
            } else {
                print $dest $match;
            }
        }

        $line = &$iter;
    } while (defined $line);
}

sub parse_with {
    my ($iter, $incl_subs, $subs, $line) = @_;
    my $exit_pat = "{endwith}";

    do {
        while ($line) {
            my $exit_idx = index $line, $exit_pat;
            my $exit_found = $exit_idx != -1;

            my $colon_idx = index $line, ":";
            my $colon_found = $colon_idx != -1;

            last if !$exit_found && !$colon_found;

            if ($exit_found && !($colon_found && $colon_idx < $exit_idx)) {
                return substr($line, $exit_idx + length $exit_pat);
            }

            my $key = substr($line, 0, $colon_idx);
            trim $key;
            my $after_colon = substr $line, $colon_idx + 1;

            my $open_found = $after_colon =~ /^\s*$OPEN_PAT/;
            my $open_end = $+[0];

            open my $str_io, ">", \$$incl_subs{$key};

            # No braces, so we'll just take the rest of the line
            if (!$open_found) {
                parse_file str_iter($after_colon), $str_io, $subs;
                $line = "";
            } else {
                # Braces mean recursion
                $line = parse_file $iter, $str_io, $subs, "$1}",
                                   substr($after_colon, $open_end);
            }

            close $str_io;

            $$incl_subs{$key} = decode("UTF-8", $$incl_subs{$key});
            trim $$incl_subs{$key};
        }

        $line = &$iter;
    } while (defined $line);
}

parse_file sub { <> }, \*STDOUT;
