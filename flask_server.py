#!_*_coding:utf-8_*_
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import os

from collections import defaultdict
import json
import requests
import numpy as np
import tensorflow as tf

from model.data_utils import CoNLLDataset
from model.ner_model import NERModel
from model.config import Config
import tokenization
from sent_utils import cut4iob, iob2dict
import conf

from flask import Flask, request, jsonify
from waitress import serve

app=Flask(__name__)
config = Config()
tokenizer = tokenization.FullTokenizer(vocab_file='vocab.txt')
errordict = defaultdict(str)

@app.route('/', methods=['POST'])
def main():
    """
    给个句子,返回所有NER结果,字典形式
    """
    global errordict
    try:
        newmtime = os.path.getmtime(conf.errordictfile)
        if newmtime > conf.mtime:
            conf.mtime = newmtime
            try:
                errordict = json.loads(open(conf.errordictfile).read())
            except Exception as e:
                conf.logger.exception(e)
        sent = request.json.get("sentence")
        if len(sent) == 0:
            return jsonify({})
        t, rawlist = cut4iob(tokenizer.tokenize, sent)
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
        ioblist = [model.idx_to_tag[i] for i in viterbi_seq]
        res = iob2dict(rawlist, ioblist)
        conf.logger.info("sentence: {}, result: {}".format(sent, json.dumps(res, ensure_ascii=False)))

        for key in res.keys(): #EXPRESS-N
            k = key
            if k.endswith('-N'):
                k = k[:-2]
            for i in range(len(res[key])):
                if res[key][i] in errordict[k].keys():
                    res[key][i] = errordict[k][res[key][i]]
        return jsonify(res)
    except Exception as e:
        conf.logger.exception(e)
        return jsonify({})


if __name__ == "__main__":
    #app.run(host=conf.host, port=conf.port)
    serve(app, host=conf.host, port=conf.port)
