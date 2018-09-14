with open("../data/wnut17/emerging.train.conll.preproc.url", "r") as inp, open("train-pos-tagged.txt", "r") as inp2, open("wnut17.train.txt", "w+") as out:
    d = dict()
    for line2 in inp2:
        toks = line2.strip().split()
        for t in toks:
            _t = t.split('/')[-1]
            if _t.isalpha():
                d[t.split('/')[0]] = _t
    print(d)
    for line in inp:
        if "#HANDLE#" in line or not line:
            out.write("\n")
            continue
        if len(line.split()) == 0:
            out.write("\n")
            continue
        word = str(line.strip().split()[0]).lower()
        pos = d[word] if word in d else "0"
        _line = line.strip() + " " + pos
        out.write(_line + "\n")

"""
with open("../data/wnut16/train", "r") as inp, open("train-pos16.txt", "w+") as out:
    l = ""
    for line in inp:
        if "#HANDLE#" in line or not line:
            out.write(l + "\n")
            l = ""
            continue
        if len(line.split()) == 0:
            out.write(l + "\n")
            l = ""
            continue
        word = str(line.strip().split()[0]).lower()
        try:
            word = word.encode('utf-8')
            l += " " + word.decode('utf-8')
        except UnicodeError:
            print("string is not UTF-8")
            l += " #ERR#"
"""



"""
if len(l) > 0 and word.isalnum():
    if not l[-1].isalnum():
        l += word
    else:
        l += " " + word
elif len(l) > 0 and not word.isalnum():
    l += word
elif not l:
    l += word
"""