#!/usr/bin/env python
#_*_coding:utf-8_*_

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

for line in sys.stdin.readlines():
    items = line.rstrip('\n').split('\t')
    for item in items[1:]:
        if item != '':
            print line.rstrip('\n')
            break
