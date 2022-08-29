# HTML Preprocessor Documentation

## Usage

Directives tell the preprocessor what to do. There are currently 5 supported
directives.

### `{include <filename>}`

Parses the file `templates/<filename>` and inserts the result at the position
of this directive. `<filename>` must not have any spaces. The template
directory can be customized by modifying `TEMPLATE_DIR`.

Example:

```
{include nav.html}
```

### `{q}`

First fully parses the text, then smartly replaces straight quotes with curly
quotes, as well as a few other text patterns. Here are the currently supported
patterns:

Replaces     | With
-------------|------------------
--           | &ndash; (en-dash)
---          | &mdash; (em-dash)
... or . . . | &mldr; (ellipses)

There are two variants of this directive. As `{q}`, it replaces text until the
corresponding `{endq}`. As `${q}`, it replaces text until the end of the line.
The second variant can save a few keystrokes and indentation levels. I'm
thinking about generalizing the `$` concept to a general directive modifier,
but no other directives can make use of it yet.

The code for smart quoting is translated from an ancient Perl script called
SmartyPants by John Gruber. It has the limitation that the entire input must be
stored as a string, so be aware of the size of the text in this directive.

Example:

```
{q}
  "Sir, this is a Wendy's," she said.
{endq}
```

### `{with}`

As the preprocessor parses the file, it keeps a dictionary of keys and
associated substitution texts. This directive parses substitutions until the
corresponding `{endwith}` and adds the new entries to the dictionary.

Substitutions are declared in the form

```
key: {
    some text
}
```

which means that the preprocessor will replace any occurrences of `{key}` with
`some text`. The text between the curly braces can be multiple lines and even
include directives of its own. The newlines after the opening curly brace are
optional, but the opening curly brace must be on the same line as the key. If,
for any reason, the text contains curly braces, you can place an equal number
of asterisks after the opening delimiter and before the closing delimiter to
distinguish it from the in-text curly braces, like so:

```
key: {*
  No need to escape in-text {curly braces} !
*}
```

A shorthand form is

```
key: some text
```

Without curly braces, all and only the text on the same line after the colon is
considered the substitution for `key`. This means that the next substitution or
`{endwith}` must start on the next line.

Example:

```
{with}
  title: ${q} "Hello World!"
  arch_wiki: https://wiki.archlinux.org/
  description: {
    Here you will find the answer to life,
    the universe, and everything.
  }
{endwith}

<h1>{title}</h1>
<a href="{arch_wiki}">{description}</a>
```

Note: In the declaration of `title`, the `{q}` variant could not have been used
because the preprocessor would have interpreted the directive as substitution
text within curly braces.

### `{include <filename> with}`

Parses the file `templates/<filename>` and inserts the result. Substitutions
for the template are declared in the text until the corresponding `{endwith}`.
The substitution declared with this directive only apply to the included file,
not the current file.

### `{<key>}`

If `<key>` is a single word that does not match any other directives, it will
be looked up in the current substitution dictionary, and its value, if any,
inserted at the position of this directive.
