# variable management for numerical vars in mlt2
import os,pickle
# Fixed2 kann nicht gepickelt werden, deshalb workaround via Decimal
# Fixed2 in mlt2 ist ziemlich obsolet, da am Ende formateuro verwendet wird
from decimal import Decimal
from mlt2.fixed import Fixed2

class MltVars():
    def __init__(mv,slave_dict,fname):
        mv.sd = slave_dict
        mv.fname = fname
        if os.path.exists(fname):
            with open(fname,"rb") as f:
                mv.md = pickle.load(f)
            mv.update_slave()
        else:
            mv.md = dict()


    def update_slave(mv):
        for key in mv.md:
            mv.sd[key] = Fixed2( mv.md[key] )
        mv.sd.update(mv.md)

    def update_master(mv):
        for key in mv.md:
            mv.md[key] =  Decimal( mv.sd[key] )

    def save_and_close(mv):
        mv.update_master()
        with open(mv.fname,"wb") as f:
            pickle.dump(mv.md,f)

    def Var(mv,vname,default=None):
        if vname in mv.sd:
            mv.md[vname] = mv.sd[vname]
        elif vname in mv.md:
            mv.sd[vname] = mv.md[vname]
        elif default is not None:
            mv.md[vname] = default
            mv.sd[vname] = default
        else:
            mv.md[vname] = default

    def dump_vars(mv,f):
        f.write("Saved Variables:\n")
        for key,val in mv.md.items():
            f.write(f"{key:10s}: {val:10.2f}\n")

#M = MltVars(globals(),"test.db")            
#M.Var("fuck")
##fuck=23
#M.save_and_close()
