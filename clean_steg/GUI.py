#!/usr/bin/env python3
import tkinter as tk
from tkinter import filedialog
from tkinter.scrolledtext import ScrolledText
from tkinter.messagebox import showerror
from PIL import Image,ImageTk
from steg import  PseudoBmp, hide_n, show_n

PICTURE = None
TK_PICTURE = None

"""Our GUI is split into 2 parts :
        - on the top, we have a frame containing 3 items :
                - the image on witch we are working (stocked in PICTURE)
                - a scale to modify the stegano's deepness
                 (the argument is directly passed to steg.hide_n)
                 - 2 buttons to load the picture to work on, and to export it
        - in the middle, we have 3 main parts :
                - a first frame is containing widgets to browse a file to hide
                - the second part is a ScrolledText widget, to hide a typed text
        both parts are activable through RadioButton widgets ;
        both can't be activated nor desactivated at the same time
                - the last part is containing the command to export the message contained in the picture
        Note that those commands are available through keyboard shortcuts (Alt-E and Alt-S)
"""

def put_photo(*args,**kwargs):
        global PICTURE, TK_PICTURE
        photo = filedialog.askopenfilename()#mode="rb") if tk.filedialog.askopenfile()
        if photo :
                photo = Image.open(photo)
                PICTURE = PseudoBmp(photo)
                TK_PICTURE = ImageTk.PhotoImage(photo)
                canvas.configure(scrollregion=(0,0,PICTURE.width,PICTURE.height))
                canvas.create_image(0,0,image=TK_PICTURE,anchor="nw")

                msg = show_n(PICTURE)
                msg.decode(errors="replace")
                text.delete("1.0","end")
                text.insert("1.0",msg)


def update_photo(deepness):#this function will hide the message into the picture, on <deepness> bits per byte
        global PICTURE, TK_PICTURE
        if PICTURE is None :
                return
        if not  choice.get() :#means file
                if not path.get() :
                        return
                msg = open(path.get(),"rb").read()
                text.delete("1.0","end")
                text.insert("1.0",msg.decode(errors="replace"))
        else :
                msg = text.get("1.0","end")[:-1].encode()
        try :
                PICTURE = hide_n(PICTURE,msg,int(deepness))
        except :
                showerror("Impossible de cacher ce contenu",
                "Ce contenu est trop plong pour être caché dans cette image.\nEssayez peut-être d'augmenter la profondeur de l'encodage.")
                _ = int(scale.get())
                if _ < 8 :
                        scale.set(_+1)
        else :
                TK_PICTURE = ImageTk.PhotoImage(PICTURE.kern)
                canvas.create_image(0,0,image=TK_PICTURE,anchor="nw")

def promptfile(*args,**kwargs):
        filename = filedialog.askopenfilename()
        if filename :
                path.delete(0,"end")
                path.insert(0,filename)
                update_photo(scale.get())

def export_msg(*args,**kwargs):
        if not choice.get() :#means file
                with open(path.get(),"ab") as file :
                        file.write(text.get("1.0","end").encode())
                        tk.messagebox.showwarning("Succès !","Le contenu du message a été écrit à la fin du fichier")
        else :
                main.clipboard_clear()
                main.clipboard_append(text.get("1.0","end"))
                tk.messagebox.showwarning("Succès !","Le contenu du message a été collé dans le presse-papier")

def export_picture(*args,**kwargs):
        update_photo(scale.get())
        f = filedialog.asksaveasfilename()
        if f :
                PICTURE.save(f)

#_____________________________________________

main = tk.Tk()
main.title("steganographer")

#_____________________________________________
display = tk.Frame(main)

_ = tk.Frame(display)
_.pack(side="top",fill="both",expand=True)
canvas = tk.Canvas(_)

scrollbary = tk.Scrollbar(_,orient="vertical",command=canvas.yview)
scrollbarx = tk.Scrollbar(_,orient="horizontal",command=canvas.xview)
canvas.configure(yscrollcommand=scrollbary.set, xscrollcommand=scrollbarx.set)#, scrollregion=canvas.bbox("all"))

scrollbary.pack(side="right",fill="y")
scrollbarx.pack(side="bottom",fill="x")
canvas.pack(fill="both",expand=True)

scale = tk.Scale(display,{"from":1,"to":8},orient="horizontal",digits=1,command=update_photo)
scale.set(8)
scale.pack(side="right")

tk.Button(display,text="Parcourir",command=put_photo).pack(side="left")
tk.Button(display,text="Exporter l'image",command=export_picture).pack(side="left")

display.pack(side="top",fill="both",expand=True)

#_____________________________________________
msg = tk.Frame(main)

#there is a choice to be done bw hiding a file, or a text typed in this window.
#False => file
#True => text
choice = tk.BooleanVar(msg,value=True)

file = tk.Frame(msg)
tk.Label(file,text="Chemin du fichier : ").pack(side="left")
path = tk.Entry(file) ; path.pack(side="left")
export = tk.Button(file,text="Exporter le message",command=export_msg)
export.pack(side="right")
browse = tk.Button(file,text="Parcourir",command=promptfile)
browse.pack(side="right")

text = ScrolledText(msg)
text.bind("<KeyPress>",lambda x:update_photo(scale.get()))

choose_file = tk.Radiobutton(msg,variable=choice,text="Cacher/Exporter un fichier",value=False,
        command=lambda : (path.configure(state="normal"),
        browse.configure(state="normal"),
        text.config(state="disabled"),
        export.configure(state="normal")))
choose_text = tk.Radiobutton(msg,variable=choice,text="Cacher/Exporter un texte",value=True,
        command=lambda : (path.configure(state="disabled"),
        browse.configure(state="disabled"),
        text.config(state="normal"),
        export.configure(state="disabled")))

choose_file.grid(row=0)
file.grid(row=1)
choose_text.grid(row=2)
text.grid(row=3)

msg.pack(side="bottom")

#_____________________________________________
main.bind("<Control-o>",put_photo)
main.bind("<Alt-E>",export_msg)
main.bind("<Alt-S>",export_picture)


main.mainloop()
