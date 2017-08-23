#!/usr/bin/env python3
"""OS/2 version : see http://www.fileformat.info/format/os2bmp/egff.htm"""
convert = lambda x,n=4 : x.to_bytes(n,"little")

def BMP(file,x,y,px):
    assert len(px) == x*y
    
    head = b"BM"+\
           convert(0,8)+\
           convert(26)+\
           convert(12)+\
           convert(x,2)+\
           convert(y,2)+\
           convert(1,2)+\
           convert(24,2)

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
    BMP(open("testfile2.bmp","wb"),20,10,[(127,127,127),]*200)
