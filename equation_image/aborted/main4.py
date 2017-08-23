#!/usr/bin/env python3
from pseudo_BMP import PseudoBmp
from Polynome import Polynome
import PIL.Image

"""
The goal of this script is to reduce a picture to Polynomes ;
unlike the other script, we will have up to 2nd-degree Polynome
parted in 2 lists per channel (R,G,B for each row)
We should obtain a very heavy compression, but with very much loss.
"""

picture = PIL.Image.open(input("Path : "))
picture = PseudoBmp(picture)
new_picture = list()
for row in picture.iter_lvl(0) :
        polys_row = list()
        recombined = [list(),list(),list()]#one for R, one for G, one for B
        [[recombined[i].append(const) for i,const in enumerate(pixel)] for pixel in row]
        for serie in recombined :
                polys_serie = list()
                #deg.0
                polys_serie.append(Polynome(sum(serie)//len(serie)))

                #deg.1
                #N.I.


                #deg.2
                minimas = dict()#here a=1
                maximas = dict()#here a=-1
                #alpha as key, beta as value
                lastdelta = 0
                for i,x in enumerate(serie[:-1]):
                        delta = serie[i+1]-serie[i]#deta is not the discriminant of anything !

                        if delta*lastdelta <= 0 :
                                if delta > 0 :
                                        minimas[i] = serie[i]
                                if delta < 0 :
                                        maximas[i] = serie[i]

                        lastdelta = delta

                print(minimas,maximas,sep="\n",end="\n\n")
                minimas = [Polynome(value+key**2,-2*key,1) for key,value in minimas.items()]
                maximas = [Polynome(value-key**2,2*key,-1) for key,value in maximas.items()]
                polys_serie.append((minimas,maximas))

                polys_row.append(polys_serie)
        new_picture.append(polys_row)

# IDEA: we should also create degree-0 and -1 functions ;
#if degree-1 decreasing, then it overrides degree-0 when smaller.
#if degree-1 increasing, then it overrides degree-0 when greater
#degree-2 : if a=1, then overrides degree-1 when smaller
#degree-2 : if a=-1, then overrides degree-1 when greater

#the degree-0 function(s) would replace 0 and 255 l.55-57

#recreating  !
img = PIL.Image.new("RGB",picture.size)
for y in range(img.height) :
        (r0,(r2,R2)),(g0,(g2,G2)),(b0,(b2,B2)) = new_picture[y]
        for x in range(img.width) :
                red = max([-1,*[f(x) for f in r2]])
                if red > 255 :
                        red = min([256,*[f(x) for f in R2]])
                if red < 0 :
                        red = r0(x)

                green = max([-1,*[f(x) for f in g2]])
                if green > 255 :
                        green = min([256,*[f(x) for f in G2]])
                if green < 0 :
                        green = g0(x)
                blue = max([-1,*[f(x) for f in b2]])
                if blue > 255 :
                        blue = min([256,*[f(x) for f in B2]])
                if blue < 0 :
                        blue = b0(x)
                img.putpixel((x,y),(red,green,blue))
img.save("/home/aveheuzed/test.bmp")


"""
/home/aveheuzed/Python/ressources/bmp_images/python.bmp
"""
