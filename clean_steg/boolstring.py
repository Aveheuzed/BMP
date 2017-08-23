def to_bool(string):
    """turns a bytes string into a list of bool"""
    rep = list()
    for x in string :
        rep.extend([bool(int(b)) for b in bin(x)[2:].zfill(8)])
    return rep

def to_bytes(string):
    """turns a list of bool into bytes"""
    while len(string)%8 :
        string.insert(0,False)
    string = "".join([str(int(x)) for x in string])
    return int(string,base=2).to_bytes(len(string)//8,"big")
