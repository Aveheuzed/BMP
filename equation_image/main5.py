#!/usr/bin/env python3
from pseudo_BMP import PseudoBmp
from Polynome import Polynome
import PIL.Image
import pickle,pickletools

def get_model(i,modelization) :
        while i not in modelization.keys() :
                i -= 1
        return modelization[i]

picture = PIL.Image.open(input("Path : "))
picture = PseudoBmp(picture)
new_picture = list()
for row in picture.iter_lvl(0) :
        polys_row = list()
        recombined = [list(),list(),list()]#one for R, one for G, one for B
        [[recombined[i].append(const) for i,const in enumerate(pixel)] for pixel in row]
        for serie in recombined :
                derivate = list()
                _ = serie[0]
                for elt in serie[1:]:
                        derivate.append(elt-_)
                        _ = elt

                modelization = {0:Polynome(serie[0],derivate[0])}
                modelizationp = {0:(serie[0],derivate[0])}
                #key := available from index _ (included)
                #value := Polynome modelizing

                derivate.insert(0,0)
                i = 2
                while i<len(serie) :
                        if serie[i] - get_model(i,modelization)(i) not in range(-7,0):
                                modelization[i] = Polynome((serie[i]-i*derivate[i])%256,\
                                derivate[i]%256)

                                modelizationp[i] = (serie[i]-i*derivate[i]%256, derivate[i]%256)
#set modelization[i-1] (or another value, maybe it works) to get funny pictures !
                        i += 1

                polys_row.append(modelizationp)
        new_picture.append(polys_row)
# RECREATING !
# img = PIL.Image.new("RGB",picture.size)
# for y in range(img.height) :
#         R,G,B = new_picture[y]
#         for x in range(img.width) :
#                 img.putpixel((x,y),(get_model(x,R)(x)%256,\
#                 get_model(x,G)(x)%256,\
#                 get_model(x,B)(x)%256))
# img.save(input("Path (saving) : "))
img = open(input("Path (saving) : "),"wb")
img.write(int.to_bytes(picture.width,2,"big"))
img.write(int.to_bytes(picture.height,2,"big"))
img.write(pickletools.optimize(pickle.dumps(\
tuple([tuple(row) for row in new_picture]))))
#tuples are better at serializing than lists
img.close()
