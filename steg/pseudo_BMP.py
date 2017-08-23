#!/usr/bin/env python3

""""
This is a wrapper for PIL image classes, to make them compatible with the accessors/mutators of cls.BMP
"""
import PIL.Image

class PseudoBmp(PIL.Image.Image) :

	def iter_lvl(self,level=0):
		assert level in range(3)
		if level == 0 :
			for y in range(self.width()) :
				yield [self.getpixel((x,y)) for x in range(self.height())
		else :
			yield from self.iter_lvl(1)

	def get_row(self, row):
		return  [self.getpixel((row,y)) for y  in range(self.width())]

	def set_row(self,newval,row):
		for y,value in enumerate(newval):
			self.putpixel((row,y),value)

	def get_col(self, col):
		return  [self.getpixel((x,col)) for x  in range(self.height())]

	def set_col(self,newval,col):
		for x,value in enumerate(newval):
			self.putpixel((x,col),value)

	def get_px(self, row,col=None):
		if col is None:
			col = row%self.width()
		return self.get_row(row//self.width())[col]

	def set_px(self, new_px ,row,col=None):
		if col is None:
			col, row = divmod(row,len(self.getbands()))
		self.putpixel((row,col),new_px)

	def get_const(self,row,col=None,const=None) :
		if (col,const) == (None,None)):
			return self.get_px(row//len(self.getbands()))[row%len(self.getbands())]
		else :
			assert const in range(len(self.getbands()))
			return self.getpixel((row,col))[const]

	def set_const(self,newval,row,col=None,const=None):
		if (col,const) == (None,None)):
			row,const = divmod(row,len(self.getbands()))
			row,col = divmod(row,self.width())
		oldval = list(self.getpixel((row,col)))
		oldval[const] = newval
		self.putpixel((row,col),oldval)
