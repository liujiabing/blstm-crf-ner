import codecs
import numpy as np
from sklearn.model_selection import ShuffleSplit
from build_data import main as build
from train import main as train
from evaluate import main as eval

"""

<class 'list'>: [['@tolgaballik', 'O'], ['Başkanım', 'O'], ['misafirperverliğiniz', 'O'], ['için', 'O'], ['teşekkür', 'O'], ['ederiz', 'O'], [':)', 'O']]
<class 'list'>: [['@pulmonerdamar', 'O'], ['kanki', 'O'], ['ben', 'O'], ['de', 'O'], ['senin', 'O'], ['tipini', 'O'], ['coh', 'O'], ['seviyoom', 'O'], [':D', 'O'], ['mucuk', 'O'], ['kanki', 'O']]
...
"""

sentences = []
sentence = []

def write(path, sts):
    f = open(path, 'w')
    for s in sts:
        for w in s:
            f.write(w[0] + ' ' + w[1])
            f.write('\n')
        f.write('\n')
    f.close()

for line in codecs.open('data/celikkaya2013/input.txt', 'r', 'utf8'):
    line = line.rstrip()
    if not line:
        if len(sentence) > 0:
            sentences.append(sentence)
            sentence = []
    else:
        word = line.split()
        assert len(word) >= 2
        sentence.append(word)
if len(sentence) > 0:
    sentences.append(sentence)
num_sentences = len(sentences)
print("Found %i sentences" % num_sentences)

# Randomly shuffle sentences
np.random.shuffle(sentences)

# Need numpy array so that we can 'extract' using indices
sentences = np.array(sentences)

rs = ShuffleSplit(n_splits=5, train_size=0.8, test_size=0.1)
count = rs.get_n_splits()

# Generate n-fold CV files
for train_index, test_index in rs.split(sentences):
    # Find dev index as well...
    temp = list()
    temp.extend(train_index)
    temp.extend(test_index)
    print(temp)
    dev_index = list(set(range(0, len(sentences))) - set(temp))

    # Extract sentences from indices
    train_sentences = sentences[train_index]
    dev_sentences = sentences[dev_index]
    test_sentences = sentences[test_index]

    # Write to respective files
    filename_train = 'data/celikkaya2013/tr.train{}.iobes'.format(count)
    filename_dev = 'data/celikkaya2013/tr.testa{}.iobes'.format(count)
    filename_test = 'data/celikkaya2013/tr.testb{}.iobes'.format(count)

    write(filename_train, train_sentences)
    write(filename_dev, dev_sentences)
    write(filename_test, test_sentences)

    # Build
    kwargs = {
        "filename_train": filename_train,
        "filename_dev": filename_dev,
        "filename_test": filename_test
    }
    build(**kwargs)

    # Train
    train(**kwargs)

    # Evaluate
    eval(interactive=False, **kwargs)

    count -= 1
