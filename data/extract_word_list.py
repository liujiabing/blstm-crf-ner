from gensim.models.keyedvectors import KeyedVectors
import os

# https://groups.google.com/forum/#!topic/gensim/JRYhCt10AMw
# https://radimrehurek.com/gensim/models/keyedvectors.html
# https://stackoverflow.com/questions/44693241/how-to-extract-a-word-vector-from-the-google-pre-trained-model-for-word2vec
"""
model = KeyedVectors.load_word2vec_format('../other/TweetNER/TweetNER/newfile.txt', binary=True, limit=200000, encoding='utf-8', unicode_errors='ignore')
print(model['*UNKNOWN*'])
with open('../other/TweetNER/TweetNER/word-list.txt', 'w+', encoding='utf-8') as f:
    for key in model.vocab.keys():
        f.write(key + "\n")
"""

print("Building vocab...")
count = 0
with open('../other/TweetNER/TweetNER/newfile.txt', encoding='utf-8') as f:
    with open('../other/TweetNER/TweetNER/word-list.txt', 'w+', encoding='utf-8') as f2:
        for line in f:
            if count == 200001:
                break
            word = line.strip().split(' ')[0]
            f2.write(word + "\n")
            count += 1



"""
with open('../other/TweetNER/TweetNER/pretrained.txt', 'r', encoding='utf-8') as f:
    with open('../other/TweetNER/TweetNER/newfile.txt', 'w+', encoding='utf-8') as f2:
        f2.write('200000 200\n')
        while True:
            line = f.readline()
            f2.write(line)
            if not line:
                break
"""