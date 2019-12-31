# mlt2/reflection.py
# Copyright 2019 Matthias Lesch <ml@matthiaslesch.de>
# MIT License: http://www.opensource.org/licenses/mit-license.php
"""
    mlt2.reflection
    ---------------

    This module provides slightly modified exec and eval functions.

    :copyright: 2014-2020 by Matthias Lesch <ml@matthiaslesch.de>
    :license:   MIT license
"""
import os,re,sys
from textwrap import dedent

## Exceptions ##
class MltReflectionError(Exception):
    def __init__(self,msg):
        super().__init__(msg)
        self.msg = msg
## END Exceptions ##

def myexec(s,env):
    """ Executes python code in environment env. Inside code the function
puts is available for direct output. Additional exception handling.
    """
    res = []
    puts = res.append
    env['puts']=puts
    sorig = s
    newl='\n' in s
    s = dedent(s)
    s = s.strip('\n')
    try:
        exec(s,env)
    except Exception as e:
        print("Caught:",repr(e))
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
        print("Caught:",repr(e))
        raise MltReflectionError( "Code:\n" + s )
    return fmt.format(res)

# -*- coding: utf-8 -*-
## vim: tabstop=4 softtabstop=4 shiftwidth=4 expandtab autoindent tw=79 ft=python fenc=utf-8
