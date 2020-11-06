from stanfordcorenlp import StanfordCoreNLP
import json, re
import sys

my_nlp = StanfordCoreNLP('http://localhost',port=9000,timeout=30000)


def analyse(sentence):
    '''
    Connect to StanfordCoreNLP to get the sentiment analysis for each tweet
    :param sentence:
    :return:
    '''
    res = my_nlp.annotate(sentence, properties={
        'annotators': 'sentiment',
        'outputFormat': 'json',
        'timeout': '50000'
    }).strip()
    if not res:
        return "None"
    else:
        res = json.loads(res)
        if res['sentences']:
            return res['sentences'][0]['sentiment']
        else:
            return "None"
