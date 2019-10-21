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

emoji_pattern = re.compile(
    u"(\ud83d[\ude00-\ude4f])|"  # emoticons
    u"(\ud83d[\u0000-\uddff])|"  # symbols & pictographs (2 of 2)
    u"(\ud83d[\ude80-\udeff])|"  # transport & map symbols
    u"(\uD83E[\uDD00-\uDDFF])|"
    u"(\ud83c[\udf00-\uffff])|"  # symbols & pictographs (1 of 2)
    u"(\ud83c[\udde0-\uddff])|"  # flags (iOS)
    u"([\u2934\u2935]\uFE0F?)|"
    u"([\u3030\u303D]\uFE0F?)|"
    u"([\u3297\u3299]\uFE0F?)|"
    u"([\u203C\u2049]\uFE0F?)|"
    u"([\u00A9\u00AE]\uFE0F?)|"
    u"([\u2122\u2139]\uFE0F?)|"
    u"(\uD83C\uDC04\uFE0F?)|"
    u"(\uD83C\uDCCF\uFE0F?)|"
    u"([\u0023\u002A\u0030-\u0039]\uFE0F?\u20E3)|"
    u"(\u24C2\uFE0F?|[\u2B05-\u2B07\u2B1B\u2B1C\u2B50\u2B55]\uFE0F?)|"
    u"([\u2600-\u26FF]\uFE0F?)|"
    u"([\u2700-\u27BF]\uFE0F?)"
    "+", flags=re.UNICODE)


def remove_emoji(text):
    text = text.decode('utf8')
    return emoji_pattern.sub(r'', text).encode('utf8')

if __name__ == "__main__":
    finished = 0
    tokenizer = tokenization.FullTokenizer(vocab_file='vocab.txt')
    for line in sys.stdin.readlines():
        finished += 1
        t = tokenizer.tokenize(regularization(line.split('\t')[0].strip()))
        print ' '.join(t)
        if finished % 10000 == 0:
            print >>sys.stderr, "{} lines finished".format(finished)
