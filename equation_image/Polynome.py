#!/usr/bin/env python3
from itertools import zip_longest
from fractions import Fraction
from math import sqrt


class Polynome :

    def _wrapper(f):
        """Makes sure the second arg is an instance of Polynome"""
        def f_(self,other):
            if not isinstance(other,Polynome):
                other = Polynome(other)
            return f(self,other)
        return f_

    def __init__(self, *args,coeffs=None):
        """Two ways to build :
    -either fill *args with numbers (any number allowed, float, int, fraction.Fraction...).
    The first number will multiply x**0, the second x**1, etc.
    -either use coeffs (kwarg-only) with a dict as : {k:v} with k as x's power, and v the multiplier (as given in args)
    This method is useful when you have only big powers for x : istead of 0,0,0,0,0,0,0,0,0,0,0,0,1,-1 you can type {12:1,13:-1}
-Do not use both syntaxes in the same call !"""
        #part 1 : setting self.coeffs
        if coeffs is not None :
            assert not len(args), "You must specify either args or coeffs, not both"
            self.coeffs = [0,]*(max(coeffs.keys())+1)
            for k,v in coeffs.items():
                self.coeffs[k] = v
        elif not len(args):
            self.coeffs = [0,]
        else :
            if len(args) == 1 :
                if hasattr(args[0],"__iter__"):
                    args = list(args[0])
            self.coeffs = list(args)

        while len(self.coeffs)>1 and (not self.coeffs[-1]) :
            self.coeffs = self.coeffs[:-1]

    def __repr__(self):
        rep = list()
        if self.coeffs[0] or len(self.coeffs)==1:
            rep.append(str(self.coeffs[0]))

        if len(self.coeffs)>1:
            if self.coeffs[1] :
                if self.coeffs[1] not in (1, -1) :
                    rep.append(str(self.coeffs[1])+"x")
                elif self.coeffs[1] == 1 :
                    rep.append("x")
                else :
                    rep.append("-x")
            for b,a in enumerate(self.coeffs[2:],2):
                if a :
                    if a not  in (1, -1):
                        rep.append("{a}x**{b}".format(a=a,b=b))
                    elif a == 1 :
                        rep.append("x**{b}".format(b=b))
                    else :
                        rep.append("-x**{b}".format(b=b))
        return " + ".join(rep)

    @_wrapper
    def __add__(self,other):
        return Polynome(*[a+b for a,b in zip_longest(self.coeffs,
                                                     other.coeffs,
                                                     fillvalue=0)])

    def __neg__(self):
        return self*(-1)

    @_wrapper
    def __sub__(self,other):
        return Polynome(*[a-b for a,b in zip_longest(self.coeffs,
                                                     other.coeffs,
                                                     fillvalue=0)])

    @_wrapper
    def __mul__(self,other):
        coeffs = [0,]*(len(other.coeffs)+len(self.coeffs)-1)
        for i,x in enumerate(other.coeffs):
            for j,y in enumerate(self.coeffs):
                coeffs[i+j] += x*y
        return Polynome(*coeffs)

    def __pow__(self,x):
        if not isinstance(x,int) and x >= 0:
            return NotImplemented
        else :
            p = Polynome(1)
            for _ in range(x):
                p *= self
        return p


    @_wrapper
    def __divmod__(self,other):
        _self = self
        rep = Polynome()
        dmaxcoeff, dmaxpow = other[-1], other.maxdegree()
        i = self.maxdegree()
        while i>=dmaxpow :
            _ = Fraction(_self[i],dmaxcoeff)
            _ = Polynome(coeffs={i-dmaxpow:_})
            _self -= (_*other)
            rep += _
            i -= 1
        return (rep,_self)

    def __floordiv__(self,other):
        return divmod(self,other)[0]

    def __mod__(self,other):
        return divmod(self,other)[1]

    def __call__(self,xval):#using the Horner method
        s = self.coeffs[-1]
        for coeff in reversed(self.coeffs[:-1]):
            s *= xval
            s += coeff
        return s

    @_wrapper
    def __eq__(self,other):
        return self.coeffs.__eq__(other.coeffs)

    def __getitem__(self,degree):
        try :
            return self.coeffs.__getitem__(degree)
        except IndexError :
            return 0

    def __len__(self):
        return self.coeffs.__len__()

    def maxdegree(self):
        return len(self.coeffs)-1

    def __iter__(self):
        return self.coeffs.__iter__()

    def derivate(self):
        rep = list()
        for i,x in enumerate(self.coeffs[1:],1):
            rep.append(i*x)
        return Polynome(rep)

    def lim(self):
        """return the limit of self(x) when x is close to -inf and when x is close to inf : (lim_-inf, lim_inf)"""
        inf = float("inf")
        if self.maxdegree()%2 :
            if self[-1] > 0:
                return (inf,inf)
            else :
                return (-inf,-inf)
        else :
            if self[-1] > 0:
                return (-inf,inf)
            else :
                return (inf,-inf)

    def __bool__(self):
        return (self.coeffs==[0,])

    def __getstate__(self):
        return tuple(self.coeffs)

    __setstate__ = __init__
