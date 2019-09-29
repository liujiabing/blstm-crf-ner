#!/usr/bin/env python
#_*_coding:utf-8_*_

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from collections import defaultdict
import json

IOB = ('ADDRESS', 'NAME', 'PHONE', 'EXPRESS', 'DATE', 'LAST', 'EXCHANGE')

sent, lbls = '', defaultdict(list)
key = 'ERROR'
for i, line in enumerate(sys.stdin.readlines()):
    if line.strip() == '':
        print '\t'.join((sent, '\t'.join(['||'.join(lbls[k]) for k in IOB])))
        sent, lbls = '', defaultdict(list)
        key = 'ERROR'
        continue
    left, right = line.rstrip().split('\t')
    l = left.split(' ')[-1]
    w = right.split(' ')[1]
    #print l, w
    sent += w
    if l.startswith('B'):
        key = l.split('-')[1]
        if l.endswith('-N'):
            lbls[key].append('!'+w)
        else:
            lbls[key].append(w)
    elif l.startswith('I'):
        if key == "ERROR":
            key = l.split('-')[1]
            if l.endswith('-N'):
                lbls[key].append('!'+w)
            else:
                lbls[key].append(w)
        else:
            lbls[key][-1] += w
    else:
        key = "ERROR"
