#!/usr/bin/env python
#_*_coding:utf-8_*_

import logging
import logging.handlers
import os
from flask import Flask

port = 8002
host = '0.0.0.0'

os.putenv('OPENBLAS_NUM_THREADS', '1')
os.putenv('CUDA_VISIBLE_DEVICES', '')

if not os.path.exists('log'):
    os.makedirs('./log')

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.handlers.RotatingFileHandler('log/flask.log', mode='a', \
        maxBytes=100*1024*1024, backupCount=10, encoding='utf-8')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(filename)s: ' + \
        '%(lineno)s - %(name)s - %(levelname)s - %(thread)s - %(message)s'))
logger.addHandler(file_handler)

errordictfile = "error.dic"
mtime = 0

if __name__ == "__main__":
    pass
