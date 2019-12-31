# vim: guifont=Monospace\ 14 linespace=2 expandtab:
## fixed width decimal types. 
## also Euro ...
## 2016-09-22 copied from /home/python at tp430
## and modified in folder 2016-Programming...
## issue: division
## Metaclass free reimplementation

__version__ = '0.4.0'
__datum__ = '01.11.2019'
__author__= 'Matthias Lesch ml@matthiaslesch.de'

__all__ = ['Fixed2','Euro','cent','euro','Decimal']

import decimal
from decimal import Decimal,getcontext

decimal.getcontext().rounding = decimal.ROUND_HALF_UP # standard rounding

# warning, Decimal adds second argument context to add, mul, sub, div
# ...
class Fixed(Decimal):
    """ Fixed width Decimal class"""
    _digits = 2
    _tick = Decimal(10) ** (-2)

    # this is needed tue to the implementation of Decimal, which has
    # __new__ instead of __init__
    # Man kann bei der Instantiierung auch die Zahl der Stellen
    # angeben, diese ist aber dann lokal, siehe auch setfix unten.
    def __new__(cls, value = '0', context = None,digits=None):
        if value is None:
            value = 0
        instance= super(Fixed,cls).__new__(cls,value,context)
        if digits is not None:
            instance._digits=digits
            instance._tick = Decimal(10) ** (-digits)
        return instance    

    def __str__(self):
        return str(self.quantize(self._tick))

    def __repr__(self):
        return "%s( %s )"%(self.__class__.__name__,str(self))

    # oder nachtraeglich die Zahl der Stellen aendern
    # aendert aber nicht die Klasse bei arithmetischen Operationen
    def setfix(self,digits):
        self._digits=digits
        self._tick = Decimal(10) ** (-digits)

    def __add__(self, x, context = None):
        #return self.__class__(
        #        Decimal.__add__(self,Decimal(x), context))
        return self.__class__(
                Decimal.__add__( self, Decimal(x) ))

    __radd__ = __add__

    def __sub__(self,x, context = None):
        return self.__class__(
                Decimal.__sub__( self, Decimal(x) ))

    def __rsub__(self,other, context = None):
        tmp = self.__class__(other)
        return tmp.__sub__( self )

    def __mul__(self,x, context = None):
        return self.__class__(
                Decimal.__mul__(self,Decimal(x) ))

    __rmul__ = __mul__

    def __truediv__(self, x, context = None):
        return self.__class__(
                Decimal.__truediv__(self, Decimal(x) ))

    def __rtruediv__(self,other, context = None):
        tmp = self.__class__(other)
        return tmp.__truediv__( self )
    
def FixedCls(d):
    class foo(Fixed):
        _digits = d
        _tick = Decimal(10) ** (-d)
    foo.__name__ = 'Fixed%i'%d
    return foo

Fixed1=FixedCls(1)
Fixed2=FixedCls(2)
Fixed3=FixedCls(3)
Fixed4=FixedCls(4)


class Euro(Fixed): 
    def __repr__(self):
        return '{} €'.format( super().__str__() )

euro = Euro(1)
cent = Euro(10)**(-2)

zero = Fixed2("0.00")
one  = Fixed2(1)


## (German) Number parsing and Formatting
# see accounting, gdecimal etc....

def formateuro(x):
    """ Formatiert x als Dezimalzahl der Länge 10 (Mantisse 7, 
    2 Nachkommastellen). Zunächst im US Format. Dann werden
    Punkt und Komma einfach getauscht."""
    s = '{:10,.2f}'.format(x)  # , Tausender Separator
    s=s.replace('.','?')
    s=s.replace(',','.')
    s=s.replace('?',',')
    return s


## Submodule currency ##
## from accounting, slightly edited...
# helper, under  Decimals in accounting

### THIS NEEDS TO BE RECODED MORE NICELY, AWFUL HACK ###
def parse_decimal(s):
    ''' parses numbers of the form xx,xxx,xxx.xx (US)
    resp xx.xxx.xxx,xx (german)
    returns decimalpoint version with thousand separators removed.
    If number cannot be determined, string is returned unaltered
    '''
    s=s.strip()
    if s=='': return '0.00'
    assert len(s)>0
    separator=None
   
    try:
        assert s[0] in '+-0123456789'
        for dig in s[1:]:
            assert dig in '0123456789,.'
    except AssertionError:
        return s# ignore string which cannot be handled
    i = len(s)-1
    while i>=0:
        if s[i] in ',.':
            separator = s[i]
            break
        i -= 1   
    if separator is not None:
        if s.count(separator)>=2:
            s=s.replace( separator, '')
            separator = '!'

        s = s.replace( separator, '!')
        s = s.replace(',','')
        s = s.replace('.','')
        s = s.replace('!','.')
    #if separator is None or separator=='!':
    #    s+='.00'
    if s[0]=='+': s=s[1:]
    return s

# Convenience class
class Commodity(Fixed):
    def __str__(self):
        return '{:10.0f}'.format( self )

    #def __repr__(self):
    #    return super( self.quantize( one ) ).__repr__()

class Currency(Fixed):
    def __str__(self):
        return formateuro( self )

    #def __repr__(self):
    #    return Decimal.__repr__( self.quantize( cent ) )

def MyDecimal(s,digs=2):
    if s is None or s=='': return None
    if isinstance(s,bytes):
        s = s.decode()
    if isinstance(s,str):
        # guess commodity without decimal point:
        if (not '.' in s) and (not ',' in s):
            return Commodity(s)
        else:
            s = parse_decimal(s)
            return Currency(s)
    if isinstance(s,Commodity):
        return s
    if isinstance(s,int):
        return Commodity(s)
    #if isinstance(s,float) or isinstance(s,Decimal):
    #    return Currency(s)
    #print(repr(s))
    #print(s.__class__)
    #raise Exception("What is this?")
    # otherwise format with two decimal digs
    fmt = '{:.'+ str(digs)+'f}'
    s = fmt.format(s)
    return Currency(s)

def __fmt_currency(d):
# war deutsches Format
    tmp=d
    if isinstance(d,Decimal):
        tmp = str(d)
    elif not isinstance(d,str):
        try: 
            tmp= '{:10,.2f}'.format(d)
        except:
            import pudb
            pudb.set_trace()
    # war deutsches Format
    #tmp=tmp.replace('.',';')
    #tmp=tmp.replace(',','.')
    #return tmp.replace(';',',')
    #standard Format
    return tmp

def fmt_currency(d):
    tmp=d
    if not isinstance(d,str):
        tmp='{:10.2f}'.format(d)
    return tmp
## End of Submodule currency ##
