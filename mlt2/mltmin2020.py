#!/usr/bin/python3
# vim: fileencoding=utf-8 tabstop=4 expandtab shiftwidth=4 softtabstop=4
# vim: expandtab softtabstop=0 nosmarttab guifont=Monospace\ 14 foldmethod=manual noautoindent nocin nosi indentexpr=

# 2020 reimplementation of minimal mlt
""" Language
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
"""
import os,re,sys

def noop(s,env):
    return ''

def verb(s,env):
    return s


## Regexes ##
RE_py = re.compile(r'<\?(.*?)\?>[\t ]*?\n{0,1}', re.S|re.M)
RE_eval = re.compile(r'<\!(.*?)\!([^\!]*?)>',re.S|re.M)
RE_comment = re.compile(r'^<\#(.*?)^\#>.*?\n', re.S|re.M)
RE_aux = re.compile(r'<\$(.*?)\$>', re.S|re.M)
RE_ipol = re.compile(r'#\{(.*?)\}')
RE_bezeichner = re.compile(r'\$([a-zA-Z_]\w*)')
## END Regexes

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
# RE muss eine Gruppe haben, wegen 3 split.
#utils

from collections import deque
tokenqueue=deque()
push=tokenqueue.append
pop=tokenqueue.popleft

# tokentypen
TOKRAW='0'
TOKPY='1'
TOKEVAL='2'
TOKTXT='3'
TOKAUX='4'

def partition(s):
    #borrowed from interpolate.py
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
    return (left, '',TOKTXT), ( s[mo.end():mo1.start()],mo.group(1), mo.group(2) ),s[mo1.end():]

def tokenize(s):
    remainder=s
    toks=deque()
    push=toks.append
    while remainder:
         tokleft,tokmid,remainder = partition(remainder)
         push( tokleft )
         push( tokmid )
    return toks

from reflection import myexec as _myexec,myeval as _myeval,MltReflectionError
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

class Runtime():
    # exchange vars between script and mlt
    pass

runtime="""
<?
from fixed import Fixed2 as Euro
?>
"""

from fixed import Fixed2
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
      
    
alu=Alu()

def numeval(s,env,**args):
    # evaluates to a currency format ...
    s=s.strip()
    width=env.get('__width__',10)
    fmt = '{:>' + str(width) + '.2f}'
    try:
        res=Fixed2( eval(s,env) )
    except Exception as e:
        print("Caught:",e)
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
    env['alu'] = alu
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

doc = """
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


if __name__=='__main__':
    #fix: templates can now import pymods from their directory
    sys.path.insert(0,os.path.realpath('.'))
    print(repr(sys.path))
    if len( sys.argv )<=1:
       #print(__file__)
       #os.system("less /usr/local/bin/mltmin")
       print( mltminimal( doc, {} ) )
       sys.exit()
    with open( sys.argv[1],'r') as f:
        print( mltminimal( f.read(), {} ) )    
