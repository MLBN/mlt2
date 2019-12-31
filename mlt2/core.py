# mlt2/core.py
# Copyright 2019 Matthias Lesch <ml@matthiaslesch.de>
# MIT License: http://www.opensource.org/licenses/mit-license.php
"""
    mlt2.core
    ---------

    The core functionality.

    :copyright: 2014-2020 by Matthias Lesch <ml@matthiaslesch.de>
    :license:   MIT license
"""
import os,re,sys
from collections import deque

from .reflection import myexec as _myexec,myeval as _myeval,MltReflectionError
from .fixed import Fixed2


# Parsing #

## Regexes ##
# RE muss eine Gruppe haben, wegen 3 split.
RE_py = re.compile(r'<\?(.*?)\?>[\t ]*?\n{0,1}', re.S|re.M)
RE_eval = re.compile(r'<\!(.*?)\!([^\!]*?)>',re.S|re.M)
RE_comment = re.compile(r'^<\#(.*?)^\#>.*?\n', re.S|re.M)
RE_aux = re.compile(r'<\$(.*?)\$>', re.S|re.M)
RE_ipol = re.compile(r'#\{(.*?)\}')
RE_bezeichner = re.compile(r'\$([a-zA-Z_]\w*)')
RE_start = re.compile(r'<(\w*?[+-]{0,1})([\?\!\#\$])',re.S|re.M)
RE_endpy = re.compile(r'(\?>)[\t ]*?\n{0,1}', re.S|re.M)
RE_endeval = re.compile(r'(\!>)',re.S|re.M)
RE_endcomment = re.compile(r'(\#>).*?\n{0,1}', re.S|re.M)
RE_endaux = re.compile(r'(\${0,1}>)', re.S|re.M)

redict={
    '!': RE_endeval,
    '?': RE_endpy,
    '#': RE_endcomment,
    '$': RE_endaux
}


## Tokenizer
tokenqueue=deque()
push=tokenqueue.append
pop=tokenqueue.popleft

# tokentypen
TOKRAW='0'
TOKPY='1'
TOKEVAL='2'
TOKTXT='3'
TOKAUX='4'

#borrowed from interpolate.py
def partition(s):
    """partitions string s into left, token, right
    left: string
    token: mlt token
    right: remainder
    mlt symbols hardcoded
    """
    mo = RE_start.search(s)
    if not mo:
        return (s,'', TOKTXT), ("",'',TOKTXT), ""
    left = s[:mo.start()]
    end_RE = redict[ mo.group(2) ]
    mo1 = end_RE.search(s,mo.end() )

    # it is an error if mo1 is None ....
    return (left, '',TOKTXT),\
            ( s[mo.end():mo1.start()],mo.group(1), mo.group(2) ),s[mo1.end():]

def tokenize(s):
    remainder=s
    toks=deque()
    push=toks.append
    while remainder:
         tokleft,tokmid,remainder = partition(remainder)
         push( tokleft )
         push( tokmid )
    return toks


# Runtime

def myexec(s,env,*args,**kwargs):
    return _myexec(s,env)

def myeval(s,env,*args,**kwargs):
    return _myeval(s,env)

def nothing(s,env,**args):
    return ''

def noop(s,env,**args):
    return s

## For reasons I don't understand, the following function cannot be
## defined inside a script, too much fiddling with the environment
## dict ...
## conveniences for numeval
def idfunc(x): return x

## z.Zt. ohne Funktion
class Alu():
    def __init__(self):
        self.list = list()
    def clear(self):
        self.list.clear()
    @property
    def last(self):
        return self.list[-1]
    def append(self,x):
        return self.list.append(x)
    def sum(self):
        return sum(self.list)

alu=Alu()

class Runtime():
    # exchange vars between script and mlt
    pass

runtime="""
<?
from fixed import Fixed2 as Euro
?>
"""

def setsumvar(s):
    env=Runtime.env
    env['sumvar']=s
    env[s] = Fixed2(0)

def parselabel(label,res,env):
    if not label: return res
    
    symbol = label[-1]
    if not symbol in '+-': 
        env[label]=res
        return res
    label=label[:-1]

    if symbol=='+':
        env[label] = env[label] + res
    elif symbol=='-':
        env[label] = env[label] - res
 
    return res
      
    

def numeval(s,env,**args):
    # evaluates to a currency format ...
    s=s.strip()
    width=env.get('__width__',10)
    fmt = '{:>' + str(width) + '.2f}'
    try:
        res=Fixed2( eval(s,env) )
    except Exception as e:
        print("Caught:",repr(e))
        raise MltReflectionError( "Code:\n" + s )
    #res = Fixed2( fmt.format(res) )
    #alu.append(res)
    # tke care of summation
    sumvar = env['sumvar']
    if sumvar is not None and s!=sumvar:
        env[sumvar] = env[sumvar]+res  
    if 'label' in args:
        label=args['label']
        parselabel(label,res,env)
    return fmt.format(res)

def ipol(s,env):
    method=env.get('__ML_subst','')
    if not method:
        return s
    elif method=='$':
        RE=RE_bezeichner
        def _sub(mo):
            return env[mo.group(1)]
    elif method=='#{}':
        RE=RE_ipol
        def _sub(mo):
            return myeval(mo.group(1),env)
    # substitution of variables in s using in env
    # syntax "Hello #{var}" substitutes var for its value
    # if var is undefined ERROR
    return RE.sub(_sub,s)
    

symboltable={
'?': 'exec',
'!': 'eval',
'#': 'comment',
'$': 'aux',
'3': 'txt'
}

def mltminimal(s,env):
    res = deque()
    puts=res.append
    s = runtime + '\n' + s
    toks=tokenize(s)
    env['__ML_exec'] = myexec
    env['__ML_eval'] = myeval
    env['__ML_comment'] = nothing
    env['__ML_aux'] = numeval
    env['__ML_txt'] = noop
    env['__ML_symboltable'] = symboltable
    env['__ML_numhook'] = idfunc
    #env['alu'] = alu
    Runtime.env = env
    env['runtime'] = Runtime
    env['sumvar'] = None
    env['setsumvar'] = setsumvar

    for tok,label,ttype in toks:
        f = env['__ML_'+symboltable[ttype] ]
        ## PREPROCESSING
        tok = ipol(tok,env)
        puts( f(tok,env,label=label) )
        '''        
#if ttype=='#':
        #    continue
        elif ttype=='!':
            puts( myeval(tok,env) )
        elif ttype=='?':
            puts( myexec(tok,env) )
        elif ttype=='$':
            f = env.get('__ML_user',None)
            if f:
                puts( f(tok,env) )
        else:
            puts( tok )
        '''
    return ''.join( res )
            
def mlt(s):
    print(mltminimal(s,{}))
          


test="""Hello world
<?     
_puts=puts

def puts(*args):
    for s in args: _puts(s)

a=9
def hello(s):
    return "Hello: \\n"+s

def user(s,env):
    return "USER"+s+"USER"

__ML_aux=user
puts( __ML_symboltable, '\\n' )
?>
Vorher1+1=<!a+1!>Wei
<#ter
#>
User:<$FUCK$>
<!hello('world')   !>."""


# -*- coding: utf-8 -*-
## vim: tabstop=4 softtabstop=4 shiftwidth=4 expandtab autoindent tw=79 ft=python fenc=utf-8
