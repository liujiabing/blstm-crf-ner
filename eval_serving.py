#!_*_coding:utf-8_*_
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import os

import json
import requests
import numpy as np
import tensorflow as tf

from model.data_utils import CoNLLDataset
from model.ner_model import NERModel
from model.config import Config
import tokenization
from sent_utils import cut4iob, iob2dict


def align_data(data):
    """Given dict with lists, creates aligned strings

    Adapted from Assignment 3 of CS224N

    Args:
        data: (dict) data["x"] = ["I", "love", "you"]
              (dict) data["y"] = ["O", "O", "O"]

    Returns:
        data_aligned: (dict) data_align["x"] = "I love you"
                           data_align["y"] = "O O    O  "

    """
    spacings = [max([len(seq[i]) for seq in data.values()])
                for i in range(len(data[list(data.keys())[0]]))]
    data_aligned = dict()

    # for each entry, create aligned string
    for key, seq in data.items():
        str_aligned = ""
        for token, spacing in zip(seq, spacings):
            str_aligned += token + " " * (spacing - len(token) + 1)

        data_aligned[key] = str_aligned

    return data_aligned



def interactive_shell(model):
    """Creates interactive shell to play with model

    Args:
        model: instance of NERModel

    """
    model.logger.info("""
This is an interactive mode.
To exit, enter 'exit'.
You can enter a sentence like
input> I love Paris""")

    while True:
        try:
            # for python 2
            sentence = raw_input("input> ")
        except NameError:
            # for python 3
            sentence = input("input> ")

        words_raw = sentence.strip().split(" ")

        if words_raw == ["exit"]:
            break

        preds = model.predict(words_raw)
        to_print = align_data({"input": words_raw, "output": preds})

        for key, seq in to_print.items():
            model.logger.info(seq)


def main(interactive=False):
    """
    给个句子,返回所有NER结果,字典形式
    """
    config = Config()
    tokenizer = tokenization.FullTokenizer(vocab_file='vocab.txt')

    sent = "不要发顺丰帮我发顺丰"
    if len(sent) == 0:
        return {}
    t, rawlist = cut4iob(tokenizer.tokenize, sent)
    print ' '.join(t), ' '.join(rawlist)
    words = [config.processing_word(w.encode("utf-8")) for w in t]
    if type(words[0]) == tuple:
        words = zip(*words)
    model = NERModel(config)
    fd, sequence_length = model.get_fd_serving([words])
    url = "http://10.85.32.218:8501/v1/models/blstm_crf:predict"
    r = requests.post(url, data='{{"inputs":{}}}'.format(json.dumps(fd)))
    trans_params = r.json()["outputs"]["trans_params"]
    logit = r.json()["outputs"]["logits"][0]
    logit = np.array(logit[:sequence_length[0]])
    viterbi_seq, viterbi_score = tf.contrib.crf.viterbi_decode(logit, trans_params)
    print viterbi_seq
    ioblist = [model.idx_to_tag[i] for i in viterbi_seq]
    res = iob2dict(rawlist, ioblist)
    print json.dumps(res, ensure_ascii=False)


    # interact
    if interactive:
        interactive_shell(config)


if __name__ == "__main__":
    main()
