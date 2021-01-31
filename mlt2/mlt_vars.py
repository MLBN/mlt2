# variable management for numerical vars in mlt2
import os,pickle
# Fixed2 kann nicht gepickelt werden, deshalb workaround via Decimal
# Fixed2 in mlt2 ist ziemlich obsolet, da am Ende formateuro verwendet wird
from decimal import Decimal
from mlt2.fixed import Fixed2

# Variablentypen
DEC = 'decimal'
INT = 'integer'
STR = 'string'
import pudb

class Var():
    def __init__(v,name):
        v.name = name
        v.val = None

    #@staticmethod
    def format(v,val):
        return val

    def __str__(v):
        return v.format(v.val)

class Str(Var):
    #@staticmethod
    def format(v,val):
        return str(val)

    def set(v,val):
        v.val = str(val)

class Dec(Var):
    def __init__(v,name,digs=2):
        super().__init__(name)
        v.val = Decimal('0.00')
        v.digs = digs
        v.fstr = '{:10.'+f'{digs}f'+'}'

    def set(v,val):
        if val is None: val = '0.00'
        v.val = Decimal(val)

    def format(v,val):
        return v.fstr.format(val)

class MltVars():
    def __init__(mv,slave_dict):
        mv.sd = slave_dict

    def init(mv,fname):
        # this MUST be called on the instance BEFORE USE
        mv.fname = fname
        if os.path.exists(fname):
            with open(fname,"rb") as f:
                mv.md = pickle.load(f)
            mv.update_slave()
        else:
            mv.md = dict()

    def update_slave(mv):
        for key in mv.md:
            mv.sd[key] = Fixed2( mv.md[key].val )

    def update_master(mv):
        for key in mv.md:
            mv.md[key].set( mv.sd[key] )

    def save_and_close(mv):
        mv.update_master()
        with open(mv.fname,"wb") as f:
            pickle.dump(mv.md,f)

    def Var(mv,vname,default=None,Typ=DEC,**kwargs):
        pudb.set_trace()
        if vname in mv.sd:
            mv.md[vname].set( mv.sd[vname] )
        elif vname in mv.md:
            mv.sd[vname] = mv.md[vname].val
        else:
            if Typ==DEC:
                mv.md[vname] = Dec(vname, digs=kwargs.get("digs",2) )
            else:
                raise Exception("not implemented")

            if default is not None:
                mv.sd[vname] = default
            else:
                mv.md[vname].set( default )

    def dump_vars(mv,f):
        f.write("Saved Variables:\n")
        for var in mv.md.values():
            f.write(f"{var.name:10s}: {var.val:10.2f}\n")

#M = MltVars(globals(),"test.db")            
#M.Var("fuck")
##fuck=23
#M.save_and_close()
