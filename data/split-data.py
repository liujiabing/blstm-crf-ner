
import codecs
import re
import numpy as np

"""
Load sentences. A line must contain at least a word and its tag.
Sentences are separated by empty lines.

<class 'list'>: [['@tolgaballik', 'O'], ['Başkanım', 'O'], ['misafirperverliğiniz', 'O'], ['için', 'O'], ['teşekkür', 'O'], ['ederiz', 'O'], [':)', 'O']]
<class 'list'>: [['@pulmonerdamar', 'O'], ['kanki', 'O'], ['ben', 'O'], ['de', 'O'], ['senin', 'O'], ['tipini', 'O'], ['coh', 'O'], ['seviyoom', 'O'], [':D', 'O'], ['mucuk', 'O'], ['kanki', 'O']]
...
"""
lower = False
zeros = True

sentences = []
sentence = []


def _zero_digits(s):
    """
    Replace every digit in a string by a zero.
    """
    return re.sub('\d', '0', s)


def write(path, sts):
    f = open(path, 'w')
    for s in sts:
        for w in s:
            f.write(w[0] + ' ' + w[1])
            f.write('\n')
        f.write('\n')
    f.close()

for line in codecs.open('input.txt', 'r', 'utf8'):
    line = _zero_digits(line.rstrip()) if zeros else line.rstrip()
    if not line:
        if len(sentence) > 0:
            sentences.append(sentence)
            sentence = []
    else:
        word = line.split()
        assert len(word) >= 2
        word[0] = str(word[0]).lower if lower else word[0]
        sentence.append(word)
if len(sentence) > 0:
    sentences.append(sentence)
num_sentences = len(sentences)
print("Found %i sentences" % num_sentences)

# Randomly shuffle sentences
np.random.shuffle(sentences)
# Split into train, dev and test sets
num_train = int(round(int(num_sentences) * (float(80) / 100)))
num_dev = int(round(int(num_sentences) * (float(10) / 100)))
num_test = int(round(int(num_sentences) * (float(10) / 100)))

train_sentences = sentences[:num_train]
dev_sentences = sentences[num_train:num_train+num_dev]
test_sentences = sentences[num_train+num_dev:]

# Write to corresponding files
write('tr.train.iobes', train_sentences)
write('tr.testa.iobes', dev_sentences)
write('tr.testb.iobes', test_sentences)

