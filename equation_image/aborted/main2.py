#!/usr/bin/env python3
from pseudo_BMP import PseudoBmp
from Polynome import Polynome
import PIL.Image

"""
The goal of this script is to reduce a picture to Polynomes ;
unlike the other script, we will have only 2nd-degree Polynome ( ax²+bx+c = a(x-alpha)²+beta )
parted in 2 lists per channel (R,G,B for each row), one with a=1, the other with a=-1.
We should obtain a very heavy compression, but with very much loss.
"""

picture = PIL.Image.open(input("Path : "))
picture = PseudoBmp(picture)
new_picture = list()
for row in picture.iter_lvl(0) :
        polys = list()
        recombined = [list(),list(),list()]#one for R, one for G, one for B
        [[recombined[i].append(const) for i,const in enumerate(pixel)] for pixel in row]
        for serie in recombined :
                minimas = dict()#here a=1
                maximas = dict()#here a=-1
                #alpha as key, beta as value
                lastdelta = 0
                for i,x in enumerate(serie[:-1]):
                        delta = serie[i+1]-serie[i]#deta is not the discriminant of anything !
                        if delta*lastdelta < 0 :
                                lastdelta = delta
                                continue
                        elif delta > 0 :
                                minimas[i] = serie[i]
                        else :
                                maximas[i] = serie[i]
#WARNING :if delta = 0, strange things could occur !!!

                minimas = [Polynome(value+key**2,-2*key,1) for key,value in minimas.items()]
                maximas = [Polynome(value-key**2,2*key,-1) for key,value in maximas.items()]
                polys.append((minimas,maximas))
        new_picture.append(polys)

# IDEA: we should also create degree-0 and -1 functions ;
#if degree-1 decreasing, then it overrides degree-0 when smaller.
#if degree-1 increasing, then it overrides degree-0 when greater
#degree-2 : if a=1, then overrides degree-1 when smaller
#degree-2 : if a=-1, then overrides degree-1 when greater

#the degree-0 function(s) would replace 0 and 255 l.55-57

#recreating  !
img = PIL.Image.new("RGB",picture.size)
for y in range(img.height) :
        (r,R),(g,G),(b,B) = new_picture[y]
        for x in range(img.width) :
                img.putpixel((x,y),
                             (max([0,*[f(x) for f in r]])+min([255,*[f(x) for f in R]]),
                              max([0,*[f(x) for f in g]])+min([255,*[f(x) for f in G]]),
                              max([0,*[f(x) for f in b]])+min([255,*[f(x) for f in B]])))
img.save("/home/aveheuzed/test.bmp")
