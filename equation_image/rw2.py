#!/usr/bin/env python3
from pseudo_BMP import PseudoBmp
from Polynome import Polynome
import PIL.Image

def get_model(i,modelization) :
        while i not in modelization.keys() :
                i -= 1
        return modelization[i]

def turninto(item,type):
        """Turn item (int) into bytes,\
according to type specifications.
type in WORD,DWORD,SHORT,LONG"""
        if isinstance(item,bytes) :
                return item
        if type.startswith(("W","S")) :
                length = 1#not the real value (?)
        else :
                length = 2#not the real value (?)
        if type.startswith(("W","D")) :
                signed=False
        else :
                signed=True
        return item.to_bytes(length,"little",signed=signed)

def readnext(type,buffer):
	"""read and return the next <type> in the buffer ;
type in WORD,DWORD,SHORT,LONG"""
	if type.startswith(("W","S")) :
		next = buffer.read(1)#not the real value (?)
	else :
		next = buffer.read(2)#not the real value (?)
	if type.startswith(("W","D")) :
		return int.from_bytes(next,"little",signed=False)
	else :
		return int.from_bytes(next,"little",signed=True)

def build_image(path_from,path_to) :
        picture = PIL.Image.open(path_from)
        picture = PseudoBmp(picture)
        new_picture = open(path_to,"wb")
        new_picture.write(turninto(picture.width,"DWORD"))
        new_picture.write(turninto(picture.height,"DWORD"))

        for row in picture.iter_lvl(0) :
                recombined = [list(),list(),list()]#one for R, one for G, one for B
                [[recombined[i].append(const) for i,const in enumerate(pixel)] for pixel in row]
                for serie in recombined :
                        derivate = list()
                        _ = serie[0]
                        for elt in serie[1:]:
                                derivate.append(elt-_)
                                _ = elt

                        modelization = {0:(serie[0],derivate[0])}
                        #key := available from index _ (included)
                        #value := Polynome modelizing
                        new_picture.write(turninto(0,"DWORD"))
                        new_picture.write(turninto(serie[0]%256,"WORD"))
                        new_picture.write(turninto(derivate[0]%256,"WORD"))

                        derivate.insert(0,0)
                        i = 2
                        while i<len(serie) :
                                model = get_model(i,modelization)
                                model = model[0] + model[1]*i
                                if serie[i] - model not in range(-7,8):#the params of the range are to be re-worked
                                        modelization[i] = (serie[i]-i*derivate[i]%256, derivate[i]%256)
                                        new_picture.write(turninto(i,"DWORD"))
                                        new_picture.write(turninto((serie[i]-i*derivate[i])%256,"WORD"))
                                        new_picture.write(turninto(derivate[i]%256,"WORD"))
                                i += 1
        new_picture.close()


def read_image(path_from,path_to=None):
        picture = open(path_from,"rb")
        width,height = readnext("DWORD",picture),readnext("DWORD",picture)
        new_picture = PIL.Image.new("RGB",(width,height))

        channel = dict()
        for y in range(height):
                i = -1
                row = list()
                while len(row) < 3 :
                        new = {readnext("DWORD",picture) : (readnext("WORD",picture),readnext("WORD",picture))}
                        #i.e. (model_from,(,b,a))
                        j = list(new.keys())[0]
                        if j <= i :
                                row.append(channel)
                                channel = dict()
                        channel.update(new)
                        i = j

                for x in range(width) :
                        model = [get_model(x,chan) for chan in row]
                        new_picture.putpixel((x,y),tuple((m[0]+m[1]*x)%256 for m in model))


        if path_to is None :
                new_picture.show()
        else :
                new_picture.save(path_to)

# BUG: if a model is available for more than 255 px, build_image will fail
"""
picture's structure :
______________________
DWORD width
DOWRD height

DWORD model_from
WORD b
WORD a
______________________
a and b => model : y = ax+b (y=value of R,G,B for one px ; x= place of the px in the row)
- order of the data : row1,row2,row3 without separator
- in a row : R, then G, then B
"""
