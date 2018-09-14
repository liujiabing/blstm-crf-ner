with open("../data/wnut17/emerging.train.conll.preproc.url", "r") as inp, open("train-pos.txt", "w+") as out:
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