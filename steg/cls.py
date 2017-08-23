from io import BytesIO
from math import ceil
import PIL.BmpImagePlugin

num = lambda x : int.from_bytes(x,"little")#bytes string => int
byt = lambda x,l=1 : int.to_bytes(x,l,"little")
def readnext(type,buffer):
	"""read and return the next <type> in the buffer ;
type in WORD,DWORD,SHORT,LONG"""
	if type.startswith(("W","S")) :
		next = buffer.read(2)
	else :
		next = buffer.read(4)
	if type.startswith(("W","D")) :
		return int.from_bytes(next,"little",signed=False)
	else :
		return int.from_bytes(next,"little",signed=True)



class BMP :

	def __init__(self,img):
		"""Standard attributes :
-self.ver : 2 or 3
-self.filehead
-self.imghead
-self.px (containing a list for each row ; each list is containing a a tuple (B,G,R) (B/G/R are single bytes)
img may be a readable file, or a bytes or io.BytesIO object"""

		if isinstance(img, PIL.Image.Image):
			self.ver = 3
			self.filehead = [19778,
					54+3*img.size[0]*img.size[1],
					0,
					0,
					54 ]
			self.imghead = [40,
                                       img.size[0],
                                       img.size[1],
                                       1,
                                       24,
                                       0,
                                       0,
                                       0,
                                       0,
                                       0,
                                       0,]
			img = PIL.BmpImagePlugin.Image.Image.convert(img)
			img = img.convert("RGB")
			self.px = list()
			for y in range(self.imghead[2]) :
				row = list()
				for x in range(self.imghead[1]):
					row.append(list(img.getpixel((x,y))))
				self.px.append(row)
			return

		if isinstance(img,(bytes,bytearray)) :
			img = BytesIO(img)
		elif not hasattr(img,"read") :
			raise TypeError("Bad type for img : expected a binary flow or bytes, not "+type(img).__name__)
		elif not img.mode.endswith("b"):
			raise TypeError("Bad type for img : expected a binary flow or bytes, not a textual flow")

		self.filehead = [readnext("WORD",img)]

		assert self.filehead[0] == 19778, "cannot read this as a BMP file"

		self.filehead += [readnext("DWORD",img),
				  readnext("WORD",img),readnext("WORD",img),
				  readnext("DWORD",img)]
		##self.filehead = [signature,
		##                 file length,
		##                 reserved_0,reserved_1,
		##                 offset (index from where the pixel data are set)]


		self.imghead = [readnext("DWORD",img)]
		assert self.imghead[0] in (12,40),  "Cannot open this as a BMP"
		if self.imghead[0] == 12 :
			self.ver = 2
			self.imghead.extend([readnext("SHORT",img),
						 readnext("SHORT",img),
						 readnext("WORD",img),
						 readnext("WORD",img)])
			##    header's size
			##    img's width (px)
			##    img's height (px)
			##    number of planes (normally 1)
			##    bpp
		else :
			self.ver = 3
			self.imghead.extend([abs(readnext("LONG",img)),
						 abs(readnext("LONG",img)),
						 readnext("WORD",img),
						 readnext("WORD",img),
						 readnext("DWORD",img),
						 readnext("DWORD",img),
						 readnext("LONG",img),
						 readnext("LONG",img),
						 readnext("DWORD",img),
						 readnext("DWORD",img)])
		##    header's size
		##    img's width (px) (abs(...) shouldn't be considered correct)
		##    img's height (px) (abs(...) shouldn't be considered correct)
		##    number of planes (normally 1)
		##    bpp
		##    compression
		##    bitmap's size (o)
		##    horizontal res (px/m)
		##    vertical res (px/m)
		##    number of colours
		##      //   // important //

		assert self.imghead[3] == 1

		#we won't consider palette as a standard attribute, because it will be helpful only to interpret the pixels
		palette = list()
		pal = self.filehead[4] - self.imghead[0] - 14
		if pal : # there is a palette
			if self.ver == 2 :
				LEN_PAL_ELT = 3
			else :
				LEN_PAL_ELT = 4
			assert not pal%LEN_PAL_ELT
			pal //= LEN_PAL_ELT
			# pal is now the number of palette entries

			for elt in range(pal) :
				block = (img.read(1),
					 img.read(1),
					 img.read(1))
				if LEN_PAL_ELT  == 4 :
					img.read(1)
				palette.append(block)
		#now we'we finished with the metadata ; let's attack pixels ;)

		self.px = list()
		#strucure : a list containing a list for each row of the picture
		#each sub-list is containing triples (one per pixel) of the form (Blue_constant,Green_constant,Red_constant)

		row_len = self.imghead[1]#this value is in pixels
		bytes_per_row = ceil(row_len*self.imghead[4]/8)#this value is in bytes
		added = (4-(bytes_per_row%4))%4#each row is completed to have a multiple-of-4 length
		num_rows = self.imghead[2]
		bytesperpx = self.imghead[4]

		if bytesperpx == 32 :
			for r in range(num_rows):
				self.px.append([(img.read(1),img.read(1),img.read(1),img.read(1)) for x in range(row_len)])
				img.read(added)
			#now we will delete transparency (it's a shame, but it's easier than implementing it)
			self.px = [[px[:-1] for px in row] for row in self.px]
		elif bytesperpx == 24 :
			for r in range(num_rows):
				self.px.append([(img.read(1),img.read(1),img.read(1)) for x in range(row_len)])
				img.read(added)
		elif bytesperpx == 8 :
			if not palette :
				raise ValueError("Can't interpret a 8-bits BMP without palette")
				for r in range(num_rows):
					row = img.read(bytes_per_row)
					img.read(added)
					self.px.append([palette[x] for x in row])

		elif bytesperpx == 4 :
			if not palette :
				raise ValueError("Can't interpret a 4-bits BMP without palette")
			for r in range(num_rows):
				row = list()
				for i in range(row_len//2):#//2 bc each byte is containing 2 pixels
					px = bin(ord(img.read(1)))[2:]
					px = [px[:4],px[4:]]
					px = [int(x,base=2) for x in px]
					row.extend(palette[x] for x in px)
				if row_len%2 :#witch means that we have forgotten a pixel
					px = row.append(palette[int(bin(ord(img.read(1)))[2:4],base=2)])
				img.read(added)
				self.px.append(row)

		elif bytesperpx == 1 :
			if not palette :
				raise ValueError("Can't interpret a 1-bit BMP without palette")
			for r in range(num_rows):
				row = list()
				for i in range(row_len//8):#//8 bc each byte is containing 8 pixels
					px = bin(ord(img.read(1)))[2:]
					px = [int(x) for x in px]
					row.extend(palette[x] for x in px)

				_ = row_len%8
				if _ :#we missed at least one pixel
					px = bin(ord(img.read(1)))[2:]
					px = [int(x) for x in px[:8-_]]
					row.extend(palette[x] for x in px)

				img.read(added)
				self.px.append(row)
		else :
			raise ValueError("Error in header's data (picture coded with {} bytes per pixel)".format(bytesperpx))

		img.close()

		#let's reset some header's entries
		self.imghead[4] = 24
		if self.ver == 3 :
			self.imghead[5] = 0
			self.imghead[6] = 0
			self.imghead[9] = 0
			self.imghead[10] = 0

		self.px = [[list(map(num,px)) for px in row] for row in self.px]

	def copy(self):
		c = BMP.__new__(BMP)
		c.__dict__ = self.__dict__
		return c

	def __eq__(self,other) :
		return (self.__dict__ == other.__dict__)

	def __getitem__(self,item):
		"""Used to access to the header's data.
Available keywords : version, signature, file_length, reserved0, reserved1, \
offset, header_length, img_width, img_height, planes, bytes_per_px,
compression, bitmap_len, x_res, y_res, palette_len, important_colours.
Constants :
signature = 19778
header_length = 12 or 40 (depending on the version)
version = 2 or 3
planes = 1
bytes_per_px = 24
compression = 0
The following keywords may be incorrect, or set to 0 :
bitmap_len, x_res, y_res, palette_len, important_colours, \
reserved0, reserved1"""
		if item == "version" :
			return self.ver
		elif item == "signature" :
			return self.filehead[0]
		elif item == "file_length" :
			return self.filehead[1]
		elif item == "reserved0":
			return self.filehead[2]
		elif item == "reserved1":
			return self.filehead[3]
		elif item == "offset":
			return self.filehead[4]

		elif item == "header_length":
			return self.imghead[0]
		elif item == "img_width":
			return self.imghead[1]
		elif item == "img_height":
			return self.imghead[2]
		elif item == "planes":
			return self.imghead[3]
		elif item == "bytes_per_px":
			return self.imghead[4]
		elif item == "compression" :
			return self.imghead[5]
		elif item == "bitmap_len" :
			return self.imghead[6]
		elif item == "x_res" :
			return self.imghead[7]
		elif item == "y_res" :
			return self.imghead[8]
		elif item == "palette_len" :
			return self.imghead[9]
		elif item == "important_colours":
			return self.imghead[10]

		else :
			raise ValueError("bad keyword : "+str(item))

	def turninto(item,type):
		"""Turn item (int) into bytes,\
according to type specifications.
type in WORD,DWORD,SHORT,LONG"""
		if isinstance(item,bytes) :
			return item
		if type.startswith(("W","S")) :
			length = 2
		else :
			length = 4
		if type.startswith(("W","D")) :
			signed=False
		else :
			signed=True
		return item.to_bytes(length,"little",signed=signed)


	def to_bytes(self=None,**kwargs) :
		"""Makes a version-3 BMP.
	Any keyword allowed by __getitem__ is allowed, except :
version, signature, file_length*, offset*, header_length*, img_width, \
img_height, planes, compression, bitmap_len, palette_len*
*automatically computed
	A 'palette' keyword may be added, \
as a list of at most 2**bytes_per_px (B,G,R) triples
	If a 'px' keyword is specified as a list of lists of (B,G,R) triples,
each list of the same length, then self may be None, \
and the function can be called alone (not as a method ;  see int.from_bytes)
	The other keywords are bytes or int instances \
(please refer to the source code for details)"""

		def get(item):
			try :
				return kwargs[item]
			except KeyError :
				try :
					return self[item]
				except ValueError :
					return getattr(self,item)
		turninto = BMP.turninto

		file = BytesIO()

		pal = kwargs.get("palette",list()) #/!\ palette is a list of (B,G,R) triples (B,G,R integers in range(256))
		assert len(pal) <= 2**get("bytes_per_px")
		bpp = get("bytes_per_px")
		assert bpp in  (1,4,8,24)

		offset = (4*len(pal))+54
		_ = ceil(bpp*get("img_width")/8)
		file_len = offset + self["img_height"]*(_+4-_%4)

		px_data = get("px")

		#generating file header
		file.write(b"BM")
		file.write(byt(file_len,4))
		file.write(turninto(get("reserved0"),"WORD"))
		file.write(turninto(get("reserved1"),"WORD"))
		file.write(turninto(offset,"DWORD"))

		#generating image header
		file.write(turninto(40,"DWORD"))
		file.write(turninto(len(px_data[0]),"LONG"))#width
		file.write(turninto(len(px_data),"LONG"))#height
		file.write(turninto(1,"WORD"))
		file.write(turninto(bpp,"WORD"))
		file.write(turninto(0,"DWORD"))
		file.write(turninto(0,"DWORD"))
		file.write(turninto(get("x_res"),"LONG"))
		file.write(turninto(get("y_res"),"LONG"))
		file.write(turninto(len(pal),"DWORD"))
		file.write(turninto(get("important_colours"),"DWORD"))

		#generating (optional) palette
		for x,y,z in pal :
			file.write(byt(x,1))
			file.write(byt(y,1))
			file.write(byt(z,1))
			file.write(b"\x00")

		#generating px
		if bpp != 24 :
			assert len(pal)
			if bpp == 1 :
				for row in px_data :
					array = [str(pal.index(px)) for px in row]
					final_row = int(array,base=2).to_bytes(ceil(len(array)/8),"little")
					while len(final_row)%4 :
						final_row += b"\x00"
					file.write(final_row)
			elif bpp == 4 :
				for row in px_data :
					array = [hex(pal.index(px))[2:] for px in row]
					final_row = int(array,base=16).to_bytes(ceil(len(array)/8),"little")
					while len(final_row)%4 :
						final_row += b"\x00"
					file.write(final_row)
			else :
				for row in px_data :
					array = b"".join(pal.index(px).to_bytes(1,"little") for px in row)
					final_row = array
					while len(final_row)%4 :
						final_row += b"\x00"
					file.write(final_row)
		else :
			if len(pal) :
				for row in px_data :
					array = b"".join(pal.index(px).to_bytes(3,"little") for px in row)
					final_row = array
					while len(final_row)%4 :
						final_row += b"\x00"
					file.write(final_row)
			else :
				for row in px_data :
					array = b"".join(bytes([x,y,z]) for x,y,z in row)
					final_row = array
					while len(final_row)%4 :
						final_row += b"\x00"
					file.write(final_row)
		return file.getvalue()



	def iter_lvl(self,level=0):
		"""level = 0 : yields the rows in the picture ;
level = 1 : yields the pixels in each row ;
level = 2 : yields the R/G/B constants in each pixel"""
		assert level in range(3)
		if level == 0 :
			yield from self.px
		else :
			for item in self.iter_lvl(level-1):
				yield from item

	__iter__ = iter_lvl

	"""Accessors / Mutators :
 - get_const is depending on get_px, witch is depending on get_row
 - set_row                   set_px                        set_const
 - get_col is depending on get_px ; set_col is depending on set_px
del_row, del_col, mk_row, mk_col are independent.
Beware : for row and column mutators, if the replacement row/column is smaller than the picture's ones,
the row/column in the picture will be replaced only in their beginning. If the replacement is too long, an exeption will occur.
"""

	def get_const(self,row,col=None,const=None) :
		"""Two ways :
- either ask for a row, column, constant (0=R, 1=G, 2=B)
- or ask for the nth constant of the picture"""
		if (col,const) == (None,None) :
			return self.get_px(row//3)[row%3]#3 bc of the 3 constants per pixel
		else :
			assert const in range(3)
		return self.get_px(row,col)[const]

	def set_const(self,newval,row,col=None,const=None):
		#newval : int in range(256) or single byte
		if isinstance(newval,(bytes,bytearray)):
			assert len(newval) == 1
			newval = ord(newval)
		elif not isinstance(newval,int) :
			try :
				newval = int(newval)
			except :
				raise ValueError("Bad type for newval : "+type(newval).__qualname__)
		assert newval in range(256)

		if (col,const) == (None,None) :
			row, const = divmod(row,3)
			row, col = divmod(row,self["img_width"])
		self.px[row][col][const] = newval



	def get_px(self,row,col=None) :
		"""Two ways :
- either ask for a row, column
- or ask for the nth pixel the picture"""
		if col is None :
			col = row%self["img_width"]
		return self.get_row(row//self["img_width"])[col]

	def set_px(self,triple,row,col=None):
		if col is None :
			row *= 3
			for const in triple :
				self.set_const(const,row)
				row += 1
		else :
			i = 0
			for const in triple :
				self.set_const(const,row,col,i)
				i += 1

	def get_row(self,row):
		return self.px[row]
	def set_row(self,row,replace):
		for i,px in enumerate(replace):
			self.set_px(px,row,i)

	def del_row(self,row):
		del self.px[row]
		self.imghead[2] -= 1

	def mk_row(self,new,index=None):
		"""Insert a row before index. Let index=None to append the row."""
		assert all(all(x in range(256) for x in triple) for triple in new) and \
		       len(new) == self["img_width"], "Bad value for a row"
		if index is None :
			self.px.append(new)
		else :
			self.px.insert(index,new)
		self.imghead[2] += 1


	def get_col(self,col):
		return [self.get_px(row,col)  for row in range(self["img_height"])]

	def set_col(self,col,replace):
		for i,px in enumerate(replace):
			self.set_px(px,i,col)

	def del_col(self,col):
		col_1 = col + 1#to avoid making many times the same calculation
		self.px = [row[:col]+row[col_1:] for row in self.px]
		self.imghead[1] -= 1

	def mk_col(self,new,index=None):
		"""Insert a column before index. Let index=None to append the column."""
		assert all(all(x in range(256) for x in triple) for triple in new) and \
		       len(new) == self["img_height"], "Bad value for a column"
		if index is None :
			[row.append(px) for row,px in zip(self.px,new)]
		else :
			[row.insert(index,px) for row,px in zip(self.px,new)]
		self.imghead[1] += 1

if __name__ == "__main__" :
	from os import chdir
	chdir("..")
	I = 0
	def save(img):
		global I
		open("picture{}.bmp".format(I),"wb").write(img.to_bytes())
		I += 1
	a = BMP(open("testfile.bmp","rb"))
