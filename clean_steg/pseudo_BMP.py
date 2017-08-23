#!/usr/bin/env python3

""""
This is a wrapper for PIL image classes,to make them compatible with the accessors/mutators of cls.BMP
"""
import PIL.Image

class PseudoBmp(PIL.Image.Image) :

        def __init__(self,kern):
                self.kern = kern.convert(mode="RGB")

        def __getattr__(self,attr):
                return getattr(self.kern,attr)

        def iter_lvl(self,level=0):
                assert level in range(3)
                if level == 0 :
                        for y in range(self.kern.width) :
                                yield [self.kern.getpixel((x,y)) for x in range(self.kern.height)]
                else :
                        yield from self.iter_lvl(1)

        def get_row(self,row):
                return  [self.kern.getpixel((x,row)) for x in range(self.kern.width)]

        def set_row(self,newval,row):
                for x,value in enumerate(newval):
                        self.kern.putpixel((x,row),tuple(value))

        def get_col(self,col):
                return  [self.kern.getpixel((col,y)) for y in range(self.kern.height)]

        def set_col(self,newval,col):
                for y,value in enumerate(newval):
                        self.kern.putpixel((col,y),tuple(value))

        def get_px(self,row,col=None):
                if col is None:
                        col = row%self.kern.width
                return self.get_row(row//self.kern.width)[col]

        def set_px(self,new_px ,row,col=None):
                if col is None:
                        col,row = divmod(row,len(self.kern.getbands()))
                self.kern.putpixel((col,row),tuple(new_px))

        def get_const(self,row,col=None,const=None) :
                if (col,const) == (None,None):
                        return self.get_px(row//len(self.kern.getbands()))[row%len(self.kern.getbands())]
                else :
                        assert const in range(len(self.kern.getbands()))
                        return self.kern.getpixel((col,row))[const]

        def set_const(self,newval,row,col=None,const=None):
                if (col,const) == (None,None):
                        row,const = divmod(row,len(self.kern.getbands()))
                        col,row = divmod(row,self.kern.width)
                        row,col = col,row
                oldval = list(self.kern.getpixel((col,row)))
                oldval[const] = newval
                self.kern.putpixel((col,row),tuple(oldval))
