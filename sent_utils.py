#!/usr/bin/env python
#_*_coding:utf-8_*_

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import re
import json
import tokenization

def str_fw2hw(ustr):
    """
    全角转半角
    """
    retstr = ''
    normal = u'"" ,0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&()*+,-./:;<=>?@[\\]^_`{|}~'
    wide = u'”“　，０１２３４５６７８９ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ！゛＃＄％＆（）＊＋、ー。／：；〈＝〉？＠［\\］＾＿‘｛｜｝～'
    widemap = dict((x[0], x[1]) for x in zip(wide, normal))
    for cht in ustr.decode("utf8"):
        if cht in widemap.keys():
            retstr += widemap[cht]
        else:
            retstr += cht
    return retstr

def str_filter(ustr):
    """
    过滤特殊字符
    """
    return ustr.replace('ヾ', '')

def regularization(ustr):
    """
    url/表情/商品等处理
    """
    ustr = str_fw2hw(ustr)
    ustr = str_filter(ustr)
    if ustr.startswith('{') and ustr.endswith('}'):
        try:
            sj = json.loads(ustr)
        except Exception as e:
            sent = "tagothers"
            return sent
        if sj.has_key("title"):
            sent = "taggoods"
        elif sj.has_key("userMsg"):
            sent = "taghello"
        elif sj.has_key("emotionTag"):
            sent = "tagemotion"
        elif sj.has_key("couponCount"):
            sent = "tagcoupon"
        elif sj.has_key("senderId"):
            sent = "tagsenderid"
        elif sj.has_key("groupid"):
            sent = "taggroupid"
        elif sj.has_key("conversationId"):
            sent = "tagconversationid"
        elif sj.has_key('msg') and sj.has_key("senderType"):
            sent = 'tagzrg'
        elif sj.has_key('liveTitle'):
            sent = 'taglive'
        elif sj.has_key("url") and len(sj.keys()) == 1:
            sent = "tagimage"
        elif sj.has_key('launch_rec_request'):
            sent = 'tagothers'
        else:
            sent = 'tagothers'
    else:
        sent = ustr
    if sent.startswith('&$#@~^@[{:') and sent.endswith("}]&$~@#@"):
        sent = "tagimage"
    sent = re.sub("http[:/a-zA-Z0-9\?\.=_\-&]+", " tagurl ", sent.strip())
    return sent


if __name__ == "__main__":
    finished = 0
    tokenizer = tokenization.FullTokenizer(vocab_file='vocab.txt')
    for line in sys.stdin.readlines():
        finished += 1
        t = tokenizer.tokenize(regularization(line.split('\t')[0].strip()))
        print ' '.join(t)
        if finished % 10000 == 0:
            print >>sys.stderr, "{} lines finished".format(finished)
