#!/usr/bin/env python3
from pseudo_BMP import PseudoBmp
from Polynome import Polynome
import PIL.Image

"""
The goal of this script is to reduce a picture to Polynomes ;
there will be 3 Polynome per line, one for the R constant, one for G and one for B.
We should obtain a very heavy compression, but with very much loss.

example :
the picture starts with :
0-0-0, 10-10-20, 40-40-80
then we will get :
R : y=10x²
G := R
B : y = 20x²
"""

picture = PIL.Image.open(input("Path : "))
deg = int(input("Degré maximal : "))
picture = PseudoBmp(picture)
new_picture = list()
for row in picture.iter_lvl(0) :
        polys = list()
        recombined = [list(),list(),list()]#one for R, one for G, one for B
        [[recombined[i].append(const) for i,const in enumerate(pixel)] for pixel in row]
        for serie in recombined :
                #sur un polynome de degré X, il y a jusqu'à X-1 changements de variation
                #On va d'abord déterminer le degré minimal du polynôme
                #On va pour cela 'dériver' la série,
                #pour identifier, à partir de son signe, les changements de variation de la série
##                degree = 0
##                lastdelta = 0
##                for i,x in enumerate(serie[:-1]):
##                        delta = serie[i+1]-serie[i]
##                        if lastdelta*delta < 0 :
##                                degree += 1
##                        lastdelta = delta

                poly = Polynome()#serie[0])
                ##indicator = sum(abs(moy-x)**2 for x in serie_model)#i.e. l'écart-type au carré
                #each coeff in range(-128,128)
                for rank in range(deg):#1,degree+1) :
                        indicator = sum(abs(serie[i]-(poly(i)%256))%256 for i in range(len(serie)))
                        if indicator <= 8*len(serie) :
                                break
                        for i in range(0,1024):
                                m = Polynome(coeffs={rank:i})
                                poly_ = poly+m
                                _ = sum(abs(serie[j]-(poly_(j)%256))%256 for j in range(len(serie)))
                                if indicator<_ :
                                        i -= 1
                                        break
                                else :
                                        indicator = _
                        poly += Polynome(coeffs={rank:i})
                polys.append(poly)
                print(poly)
        print()
        new_picture.append(polys)

#let's see what we have done !
img = PIL.Image.new("RGB",picture.size)
for y in range(img.height) :
        R,G,B = new_picture[y]
        for x in range(img.width) :
                img.putpixel((x,y),(R(x)%256,G(x)%256,B(x)%256))
img.save("/home/aveheuzed/test.bmp")
