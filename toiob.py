#!/usr/bin/env python
#_*_coding:utf-8_*_

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import re
import tokenization
from sent_utils import regularization, str_fw2hw

"""
IOB规则
1. ||表示两个并列，如“到了打1345或者打12222”，“我这边只有邮政，邮政可以发嘛！”
2. &&表示两个拼接，如“吉林省四平市铁东区七马路街道 详细地址: 北一委六马路东升嘉园小区B区”
3. 使用||时，后面可以使用另一套逻辑判断每个entity是什么或者使用时间差，尽量降低NER成本，如“今天买明天能不能发货”
4. 否定!，如“明天发货且不是从广州发的”，后续可以新增个意图属性；&&遇到否定需要将两个都添加!
5. --N表示对应第N个关键词（从0开始），如“为什么发邮政，跟你说不要发邮政”，可以标注“快递：!邮政--0||!邮政--1”，避免巧合产生实体词，但是情况比较少
"""

IOB = ('ADDRESS', 'NAME', 'PHONE', 'EXPRESS', 'DATE', 'LAST', 'EXCHANGE')
tokenizer = tokenization.FullTokenizer(vocab_file='vocab.txt')
cutf = tokenizer.tokenize

def process_and(sent, label, subentity, iobtag, iobindex, s):
    if subentity.startswith('!'):
        subentity = subentity[1:]
        iobtag += '-N'
    subentity = subentity.split('--')
    if len(subentity) == 2:
        iobindex = int(subentity[1])
    #print iobindex
    subentity = subentity[0]
    #print subentity

    tmp = cutf(regularization(str_fw2hw(subentity)))
    #iob = ' '.join(tmp)
    iob = tmp
    iobseq = ["I-"+iobtag for _ in range(len(tmp))]
    #print iobseq, iobindex
    if s and len(iobseq):
        iobseq[0] = 'B-' + iobtag
    #start = [i.start() for i in re.finditer(iob, sent)][iobindex]
    start = []
    for i in range(len(sent)):
        if iob == sent[i:i+len(iob)]:
            start.append(i)
    #print sent, start, iobindex
    end = start[iobindex] + len(iob)
    start = start[iobindex]
    label = label[0:start] + iobseq + label[end:]
    return label

def process_or(sent, label, entity, iobtag, iobindex):
    for i, item in enumerate(entity.split('&&')):
        if i == 0:
            s = True
        else:
            s = False
        label = process_and(sent, label, item, iobtag, iobindex, s)
    return label

def process(line):
    split = line.lower().rstrip('\n').split('\t')
    t = cutf(regularization(split[0]))
    if len(t) > 0 and t[0].startswith("tag"):
        return None
    label = ["O" for _ in range(len(t))]
    #if len(''.join([_.lstrip('##') for _ in t])) != len(split[0].replace(' ', '').decode('utf-8')):
    #    print ''.join([_.lstrip('##') for _ in t]), split[0]
    if len(split) > 1:
        iobs = split[1:]
        assert len(IOB) == len(iobs)
        for i, iob in enumerate(iobs):
            iobsplit = iob.split('||')
            for j, item in enumerate(iobsplit):
                c = 0
                for k in range(len(iobsplit[0:j])):
                    if iobsplit[k] == item:
                        c += 1
                label = process_or(t, label, item, IOB[i], c)
        #    tmp = cutf(iob)
        #    iob = ' '.join(tmp)
        #    iobseq = ' '.join(['I-{}'.format(IOB[i]) for _ in range(len(tmp))])
        #    start = sent.index(iob)
        #    end = start + len(iob)
        #    label = label[0:start] + iobseq + label[end:]
        #[i.start() for i in re.finditer('12',x)]
        #print line.rstrip('\n')
        #print label
    raw = regularization(split[0]).replace(' ', '').decode('utf-8')
    r = ''.join(t).replace('(', '\(').replace(')', '\)').replace('[UNK]', '(.+)').replace('?', '\?').replace('##', '').replace('[', '\[').replace(']', '\]')
    c = ''.join(t).count('[UNK]')
    #print raw, r
    if c == 0:
        allunk = None
    elif c == 1:
        allunk = re.findall(r, raw)
        #print allunk
        if len(allunk) != c:
            print >>sys.stderr, "{}\t{}\t{}".format(raw, r, split[0])
            return "DONT RET"
    else:
        allunk = re.findall(r, raw)[0]
        assert len(allunk) == c
    cur = 0
    for e, (i, l) in enumerate(zip(t, label)):
        if i == '[UNK]':
            print i, allunk[cur], l
            cur += 1
        else:
            print i, i[2:] if i.startswith('##') else i, l
    return ""

def main():
    for line in sys.stdin.readlines():
        #print line
        if process(line) != "DONT RET":
            print ''

if __name__ == "__main__":
    main()
