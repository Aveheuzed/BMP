#!/usr/bin/env python3
from pseudo_BMP import PseudoBmp
from boolstring import to_bool,to_bytes
import PIL.Image

def iter_block(list_to_iter,n):
        """Iter the list_to_iter yielding blocks of n elements"""
        list_to_iter = iter(list_to_iter)
        run = 1
        while run :
                _ = list()
                for i in range(n):
                        try :
                                _.append(next(list_to_iter))
                        except StopIteration :
                                run = 0
                                break
                if len(_) :
                        yield _


def hide_n(img,msg,n=2):
##        structure of the picture :
##        #0->#2 : flag
##        #3 : n
##        #4->#? : message on the n lsbs of each byte
##        #?+1->#?+3 : flag
        assert isinstance(img,PseudoBmp)
        assert isinstance(msg,bytes)
        assert n in range(1,9)

        msg = to_bool(msg)
        while len(msg)%n :
                msg.append("0")#"0" or "1", it has no importance

        prev = tuple()
        px_with_msg = set()

        #writing n
        const_n = img.get_const(3)
        const_n -= const_n%8
        const_n += n-1
        img.set_const(const_n,3)

        for chunk,i in zip(iter_block(msg,n), range(4,(len(msg)//n)+4)):
                chunk = "".join(str(int(x)) for x in chunk)
                const = bin(img.get_const(i))[2:].zfill(8)
                const = int(const[:-n]+chunk,base=2)
                img.set_const(const,i)

                if len(prev) == 3 :
                        prev = prev[1:] + (const,)
                        px_with_msg.add(prev)
                else :
                        prev += (const,)

        #now we just have to set the start/stop flag !

        flag = list(img.get_px(0))
        j = 0
        while tuple(flag) in px_with_msg :
                flag[j] += 1
                flag[j] %= 256
                j += 1
        img.set_px(flag,0)
        img.set_const(flag[0],i+1)
        img.set_const(flag[1],i+2)
        img.set_const(flag[2],i+3)

        return img

def show_n(img):
        assert isinstance(img,PseudoBmp)
        flag = list(img.get_px(0))
        n = (img.get_const(3)%8)+1
        prev = list()
        msg = list()
        const = None
        i = 4
        while prev != flag :
                try :
                        const = img.get_const(i)
                except :#we have reached the end of the picture
                        break
                c = (bin(const)[2:]).zfill(8)
                msg.extend(c[-n:])

                i += 1
                if len(prev) == 3 :
                        prev = prev[1:]+[const,]
                else :
                        prev.append(const)

        msg = msg[:-n*3]#this is the length of what we added from the flag, witch isn't part of the message
        if len(msg)%8 :
                msg = msg[:-(len(msg)%8)]#see the first loop in hide_n
        msg = [int("".join(oc),base=2) for oc in iter_block(msg,8)]
        return bytes(msg)
