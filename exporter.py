#!_*_coding:utf-8_*_
import os

from model.data_utils import CoNLLDataset
from model.ner_model import NERModel
from model.config import Config


def main():
    # create instance of config
    config = Config()

    # build model
    model = NERModel(config)
    model.build()
    model.restore_session(config.dir_model)
    model.simple_save()

    # create dataset
    #test  = CoNLLDataset(config.filename_test, config.processing_word,
    #                     config.processing_tag, config.max_iter)

    # evaluate
    #model.evaluate(test)


if __name__ == "__main__":
    main()
