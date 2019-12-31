#!/usr/bin/python3
# vim: fileencoding=utf-8 tabstop=4 expandtab shiftwidth=4 softtabstop=4
# vim: expandtab softtabstop=0 nosmarttab guifont=Monospace\ 14 foldmethod=manual noautoindent nocin nosi indentexpr=
#mltminimal 2017-Programming/mlt

## 24.10.19 Auskopplung aus mlt. reflection part mit Exceptions

import os,re,sys
from textwrap import dedent

class Namespace(): pass

G = Namespace() # Globals
  # current env and global var passed to makros etc.

import pudb
#dbg=pudb.set_trace

def devnull(*args): pass
dbg=devnull

## Exceptions ##
class MltReflectionError(Exception):
    def __init__(self,msg):
        super().__init__(msg)
        self.msg = msg
## END Exceptions ##

## Utils ##    
def myexec(s,env):
    """ Executes python code in environment env,
    inside code the function puts is available for 
    direct output. Additional exception handling
    """
    res = []
    puts = res.append
    env['puts']=puts
    sorig = s
    newl='\n' in s
    #s = s.lstrip('py')
    s = dedent(s)
    s = s.strip('\n')
    try:
        exec(s,env)
    except Exception as e:
        print("Caught:",e.msg)
        raise MltReflectionError( "Code:\n" + s )
    res = ''.join([str(i) for i in res])
    if env.get('__keepcode__',False):
        if newl:
            return ''.join(['<?',sorig,'?>\n',res])
        else:
            return ''.join(['<?',sorig,'?>',res])
    else:
        return res

def myeval(s,env):
    s=s.strip()
    width=env.get('__width__',0)
    fmt = '{:>' + str(width) + 's}'
    try:
        res=str( eval(s,env) )
    except Exception as e:
        print("Caught:",e)
        raise MltReflectionError( "Code:\n" + s )
    return fmt.format(res)


# Testing
env={}
