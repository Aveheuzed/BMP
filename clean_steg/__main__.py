#!/usr/bin/env python3
from sys import argv, stdout
from steg import hide_n, show_n
from pseudo_BMP import PseudoBmp
import PIL.Image


text_help = """BMP steganographer (from *.bmp to *.bmp)
Note that due to the variety of this file format, some pictures may not be supported.

Syntax :

* -h, --help : show this help and exit

* --hide <n> <picture> <output> <message> :
        hide <message> (either a text or a path to a file)  into <picture>, and put the result into <output>.
        <n> is an integer ; 1<=n<=8. The smaller n, the better the message is hidden ; The greater n, the bigger the message can be.

* --show <picture> [output] :
        show the message hiden in <picture>, and put it in [output] if specified, else in the standard output.
"""
if len(argv) <= 2 :
        print(text_help)
        exit(0)

if argv[1] == "--hide" :
        n = int(argv[2])
        picture = argv[3]
        output = argv[4]
        message = argv[5]

        picture = PseudoBmp(PIL.Image.open(picture))
        try :
                message = open(message,"rb").read()
        except :
                message = message.encode()

        hide_n(picture,message,n).save(output)

elif argv[1] == "--show" :
        picture = PseudoBmp(PIL.Image.open(argv[2]))
        if len(argv) > 3 :
                output = open(argv[3],"wb")
                output.write(show_n(picture))
        else :
                print(show_n(picture).decode(errors="replace"))
else :
        print(text_help)
