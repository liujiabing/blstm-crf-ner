
word_list = set()

with open("input.txt", "r") as inp, open("words.txt", "w+") as out:
    for c, line in enumerate(inp):
        # Skip handles and empty lines
        if "#HANDLE#" in line or not line:
            continue
        if len(line.split()) == 0:
            continue
        word = str(line.strip().split()[0]).lower()
        if not word.isalnum():
            continue
        if word in word_list:
            continue
        if len(word) < 4:
            continue
        word_list.add(word)
        out.write("{}:{}+###+###+###+###+###+###+###+###+{}\n".format(word,
                                                                      word[:-3] + "-" + word[-3:],
                                                                      "-".join([char for char in word])))
