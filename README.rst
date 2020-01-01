mlt2
****

A simple text processing (templating) engine which allows to mix freely python
and text. Its intended use is personal text processing.  It does not have (and
will never have) security measures for usage in a web server.

Introduction
============

Motivation
----------

There are many python templating systems. They tend to be overloaded with
features and huge. There are obvious drawbacks. Systems like mako, jinja and
the like have a steep learning curve, they are not available on every system
and local installation requires quite some knowledge about pythons internals.
On our departmental computers, e.g.,  python is available, but mako and jinja
are not. 

..  At the moment not relevant.
    Also, it is fair to say that some of the main players are lacking
    good error messages. That means searching for errors in templates can be
    tedious.

I played a little with m4, which is a bit out of date, but available
everywhere. Coming from tex/latex it is easy to deal with. However, macro logic
is very cumbersome to code. To make long story short, I wrote my own templating
script.

What I want
-----------

- Small footprint with little or no dependencies
- Full mixing of text, python, and expression evaluation.
- No restrictions what a template may do or not do.
  This is intentionally unsuitable for dynamic web, but very suitable
  for daily text processing needs.
- Everything is evaluated in one global scope. It is the template
  designers responsibility to take care of scoping if she/he wishes.
- Easy commandline usage, as e.g. the m4 macro processor.  

..
    Error Messages
    --------------

    Python has great exception handling. I tried hard to catch errors and
    provide reasonable error messages. When doing macro expansion,
    tracking line numbers can be a bit dfficult. We use a simple minded
    line based recursive descent parsing technique. The benefit is that
    keeping track of line numbers in stack traces is trivial, allowing to
    give the user detailed error messages. The approach might be bad for
    performance. This program is *not* intended to compete with the big
    players in the python dynamic web templating market, so performance
    currently is not an issue.


Usage
=====

Download and install the package. Inside mlt2 there is a little script cli.py.
Copy it as, say `mlt2`, to your local directory of executables, e.g.
`/usr/local/bin`::

    mlt2 [file list]

renders the file list. If no argument is given, this doc string is
printed.

Syntax
======

Ingredients
-----------

A template consists of text, python blocks, embedded python expressions, and
comments lines. Parsing is regex driven, and the template syntax can easily be
changed by changing a few regular expressions in the core file.


1. Normal text is just rendered unaltered

2. Everything inside <? ... ?> is run as python code, within a fixed
   environment env. The environment corresponds to the globals inside the
   python code.

3. Everything inside <!...!> is evaluated as python code, also within env.
   Variables declared in previous python blocks are visible.

4. Everything inside <# ... #> is a comment.

5. Auxiliary user tag: <$ ... $>. By default it evaluates to a fixed with
   decimal expression. As syntactic sugar one may write <foo[+-]$[expression]>
   to assign the expression to the variable foo, with + or - it will be
   added/subtracted to foo.
 
The Blocks described in 1.-5. correspond to tokens of the language.
Before such a token is rendered, it is preprocessed as follows.
Depending on the value of the variable __ML_subst it is either
  
     '': rendered as is
     '$': Expressions $ followed by a python identifier must refer to a valid
     variable. They are substituted by the value of this var
     '#{}': Same but ruby type #{var} ...

The template has access to the runtime environment. This is uncommented at
the moment and may change without notice. See `core.py`.

License
-------

MIT license 2019 Matthias Lesch <ml@matthiaslesch.de>



