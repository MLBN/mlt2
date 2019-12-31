# mlt2/__init__.py
# Copyright 2019 Matthias Lesch <ml@matthiaslesch.de>
# MIT License: http://www.opensource.org/licenses/mit-license.php
"""
    mlt2
    ----

    The mltmin2020 python template language
    =======================================

    <?
    __ML_subst='$'
    pyopen='<'+'?'
    pyclose='?'+'>'
    evalopen='<'+'!'
    evalclose='!'+'>'
    commentopen='<'+'#'
    commentclose='#'+'>'
    ?>

    The t in mlt stands for "template", it goes back
    to an old hack. The language embeds python into normal text,
    and is very versatile. The interpreter is written in python and
    has an extremely small footprint, just a few kb of code.

    Language description:

    1. Normal text is just rendered unaltered

    2. Everything inside $pyopen ... $pyclose is run as python code,
    within a fixed environment env. The environment corresponds to 
    the globals inside the python code.

    3. Everything inside $evalopen...$evalclose is evaluated as python
    code, also within env. Variables declared in previous python blocks
    are visible.

    4. Everything inside $commentopen ... $commentclose is a comment.
    <# obsolete: $commentopen must be at the beginning of a line #>

    5. Auxiliary user tag: <Dollar ... Dollar>. By default it is
    a comment.
     
    The Blocks described in 1.-5. correspond to tokens of the language.
    Before such a token is rendered, it is preprocessed as follows.
    Depending on the value of the variable __ML_subst it is either
      
         '': rendered as is
         '$': Expressions $ followed by a python name must refer to
              a valid variable. They are substituted by the value of this var
         '#{}': Same but ruby type #{var} ...

    Special variables:

        env['__ML_exec'] = myexec
        env['__ML_eval'] = myeval
        env['__ML_comment'] = nothing
        env['__ML_aux'] = nothing
        env['__ML_txt'] = noop
        env['__ML_symboltable'] = symboltable

    These variable refer to the processing functions. They my be altered
    inside the python blocks.
"""

"""
OLD
    Language
    <? ... ?> embedded python
    <# comment #>
    <! expression !> expression
    or <! expression ! format string >
    so far format string may only be a number. output will be formatted in
    this length rechtsbuendig.

    ## new feature
    ## before processing any tag, it is interpolated according to
    ## #{var} a la ruby or $ a la bash/perl.
    ## to choose the method, set the variable __ML_subst to
    ## either '',$ or #{}

    <$ $> auxiliary user Tag.

    ??
    #Inside python block one can access the environment under env.
    #This is the only variable which is provided.

    # special variables in environment:
    __clean__, __keepcode__
    ??

    :copyright: 2014-2020 by Matthias Lesch <ml@matthiaslesch.de>
    :license:   MIT license
"""

import os,sys
from textwrap import dedent

from .core import mltminimal

def cli():
    #fix: templates can now import pymods from their directory
    sys.path.insert(0,os.path.realpath('.'))
    if len( sys.argv )<=1:
       print( mltminimal( dedent(__doc__), {} ) )
       sys.exit()
    with open( sys.argv[1],'r') as f:
        print( mltminimal( f.read(), {} ) )    

# -*- coding: utf-8 -*-
## vim: tabstop=4 softtabstop=4 shiftwidth=4 expandtab autoindent tw=79 ft=python fenc=utf-8
