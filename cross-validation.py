import codecs
import numpy as np
from sklearn.model_selection import ShuffleSplit
from shutil import copyfile
import subprocess

sentences = []
sentence = []


def write(path, sts):
    f = open(path, 'w', encoding='utf-8')
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

rs = ShuffleSplit(n_splits=10, train_size=0.8, test_size=0.1)
count = rs.get_n_splits()

# Generate n-fold CV files & build, train, eval
for train_index, test_index in rs.split(sentences):
    # Find dev index as well...
    temp = list()
    temp.extend(train_index)
    temp.extend(test_index)
    dev_index = list(set(range(0, len(sentences))) - set(temp))

    # Extract sentences from indices
    train_sentences = sentences[train_index]
    dev_sentences = sentences[dev_index]
    test_sentences = sentences[test_index]

    print("Splitted dataset into 3 parts.")

    # Write to respective files
    filename_train = 'data/tr.train{}.tmp'.format(count)
    filename_dev = 'data/tr.testa{}.tmp'.format(count)
    filename_test = 'data/tr.testb{}.tmp'.format(count)

    write(filename_train, train_sentences)
    write(filename_dev, dev_sentences)
    write(filename_test, test_sentences)

    print("Created train, dev and test sets of iteration: %i" % count)

    copyfile(filename_train, 'data/train.tmp')
    copyfile(filename_dev, 'data/dev.tmp')
    copyfile(filename_test, 'data/test.tmp')

    # Build
    with open('output.log', 'a+') as out:
        out.write("Beginning building for CV iteration:{}".format(str(count)))
        p = subprocess.Popen('python3 build_data.py', shell=True, stdout=subprocess.PIPE, universal_newlines = True,
                             stderr=subprocess.STDOUT)
        while True:
            output = p.stdout.readline()
            if output == '' and p.poll() is not None:
                break
            if output:
                out.write(output.strip() + '\n')
                out.flush()
        retval = p.poll()
        out.write("Finished building. exit code:{}\n".format(str(retval)))
        out.flush()
    print("Built model.")

    # Train
    with open('results/output.log', 'a+') as out:
        out.write("Beginning training for CV iteration:{}".format(str(count)))
        p = subprocess.Popen('python3 train.py', shell=True, stdout=subprocess.PIPE, universal_newlines = True,
                             stderr=subprocess.STDOUT)
        while True:
            output = p.stdout.readline()
            if output == '' and p.poll() is not None:
                break
            if output:
                out.write(output.strip() + '\n')
                out.flush()
        retval = p.poll()
        out.write("Finished training. exit code:{}\n".format(str(retval)))
        out.flush()
    print("Trained model.")

    # Evaluate
    with open('results/output.log', 'a+') as out:
        out.write("Beginning eval for CV iteration:{}".format(str(count)))
        p = subprocess.Popen('python3 evaluate.py', shell=True, stdout=subprocess.PIPE, universal_newlines = True,
                             stderr=subprocess.STDOUT)
        while True:
            output = p.stdout.readline()
            if output == '' and p.poll() is not None:
                break
            if output:
                out.write(output.strip() + '\n')
                out.flush()
        retval = p.poll()
        out.write("Finished eval. exit code:{}\n".format(str(retval)))
        out.flush()
    print("Evaluated model.")

    count -= 1
