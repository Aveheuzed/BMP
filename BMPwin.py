#!/usr/bin/env python3
"""Windows version : see http://www.fileformat.info/format/bmp/egff.htm"""


convert = lambda x,n=4 : x.to_bytes(n,"little")

def BMP(file,x,y,px):
    assert len(px) == x*y

    #BMP version 3
    head = b"BM"+\
           convert(0,8)+\
           convert(54)+\
           convert(40)+\
           convert(x)+\
           convert(y)+\
           convert(1,2)+\
           convert(24,2)+\
           convert(0)+\
           convert(x*y)+\
           convert(0,16)
    #BMP vertsion 2
##    head = b"BM"+\
##           convert(0,8)+\
##           convert(26)+\
##           convert(12)+\
##           convert(x,2)+\
##           convert(y,2)+\
##           convert(1,2)+\
##           convert(24,2)

    i = 0
    body = bytes()
    for b,v,r in px :
        i += 1
        body += convert(b,1)+convert(v,1)+convert(r,1)
        if not i%x :
            i = 0
            m = len(body)%4
            if m :
                body += convert(0,4-m)
    file.write(head+body)

if __name__ == "__main__" :
    BMP(open("/home/aveheuzed/Python/ressources/bmp_images/chroma.bmp","wb"),254,1,\
        list(zip(range(254),range(255,1,-1),range(254))))
