# mlt2/lexer
# Copyright 2019 Matthias Lesch <ml@matthiaslesch.de>
# MIT License: http://www.opensource.org/licenses/mit-license.php
"""
    mlt2.lexer
    ---------

    The class based lexer for mlt2

    :copyright: 2014-2020 by Matthias Lesch <ml@matthiaslesch.de>
    :license:   MIT license
"""
import os,re,sys
from collections import deque

import pudb
debug=pudb.set_trace

# Parsing #
# without handling of whitespace after the mlt command.
RE_mlt=re.compile(r"""
        <(?P<cmd>\w*?[+-]{0,1})  # befehlssequenz
        (?P<sym>[\?\!\#\$])      # identifier
        (?P<cnt>.*?)             # content
        (?P=sym){0,1}            # backref to identifyer
        (?P<trim>[-]{0,1})       # white space trimming symbol.
        >
        """,re.S|re.M|re.VERBOSE)

## too ambiguous. Don't.
#RE_aux_simple=re.compile(r'(?P<cmd>\w*?[+-]{0,1})(?P<sym>\$)(?P<cnt>\S*)_*')

RE_ipol = re.compile(r'#\{(.*?)\}')
RE_bezeichner = re.compile(r'\$([a-zA-Z_]\w*)')

# tokentypen
# not really used
TOKRAW='0'
TOKPY='?'
TOKEVAL='!'
TOKTXT='3'
TOKAUX='$'
TOKCOMMENT='#'
TOKOTHER=99

class Token():
    def __init__(self,mo,ttype):
        self.type = ttype
        self.mo = mo
        if ttype == TOKTXT:
            self.cnt = mo
            self.trim = ''
            self.cmd = ''
        else: 
            self.d = mo.groupdict()
            self.cnt = self.d['cnt']
            self.trim = self.d['trim']
            self.cmd = self.d['cmd']

def specialtoken(            
# attribute holder

## splits s as follows:
## text,mo,text,mo,text
## according to the matches found.
def resplit(RE,s):
    last = 0
    for mo in RE.finditer(s):
        yield s[last:mo.start()]
        yield mo
        last = mo.end()
    yield s[last:]


def mlt_basic_tokenizer(s):
    i=0
    for mo in resplit(RE_mlt,s):
        if i%2==0:
            yield (mo,TOKTXT)
        else:
            yield (mo,mo.groupdict()['sym'])
        i+=1


## mlt lexer
## obsolete
'''
class Lexer():
    def __init__(self,s):
        self.source = s
        self.stack = deque()

    def push(self,x): return self.stack.append(x)
    def pop(self): return self.stack.pop()
    def __bool__(self): return self.stack.__bool__()
'''

TEST="""Hallo
<py?thon
?->

Text fuck$you weiter.
<# this is a comment
further#>"""

g = mlt_basic_tokenizer(TEST)
# -*- coding: utf-8 -*-
## vim: tabstop=4 softtabstop=4 shiftwidth=4 expandtab autoindent tw=79 ft=python fenc=utf-8
