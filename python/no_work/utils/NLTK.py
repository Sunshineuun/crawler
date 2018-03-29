#!/usr/bin/env python
# encoding: utf-8
# qiushengming-minnie
import urllib
import string

import jieba
import nltk
from urllib import request
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.book import text2
from nltk import *

# 语句
statement = '天天基金网络是上市公司东方财富旗下专业的基金网站,证监会核准的首批独立基金销售机构。'

"""
    三种模式
    1.精确模式：试图将句子最精确地切开，适合文本分析
        jieba.cut(statement, cut_all=False)
    2.全模式：把句子中所有的可以成词的词语都扫描出来（速度快）
        jieba.cut(statement, cut_all=True)
    3.搜索引擎模式：在精确模式的基础上，对长词再次切分，提高召回率，适合用于搜索引擎分词
        jieba.cut_for_search(statement)

"""


# print(
#     list(jieba.cut(statement, cut_all=False)),
#     '\n',
#     list(jieba.cut(statement, cut_all=True)),
#     '\n',
#     list(jieba.cut_for_search(statement))
# )

# 关键字提取
# print(
#     jieba.analyse.extract_tags(statement, topK=20)
# )

# 词性标注
# words = jieba.posseg.cut(statement)
# for word in words:
#     print(word.flag, ' ', word.word)

# 词语定位
# index = jieba.tokenize(statement)
# for i in index:
#     print(i[0], 'from', i[1], 'to', i[2])

# 近义词
# print('人脸: %s' % (synonyms.nearby('人脸')))  # 获取近义词
# print('识别: %s' % (synonyms.nearby('识别')))
# print('NOT_EXIST: %s' % (synonyms.nearby('NOT_EXIST')))

# 反义词英文
# antonyms = []
# for syn in wordnet.synsets("small"):
#     for l in syn.lemmas():
#         if l.antonyms():
#             antonyms.append(l.antonyms()[0].name())
# print(antonyms)

# import nltk
# import jieba.analyse
# from nltk.tokenize import word_tokenize
#
# document = statement
# texts_tokenized = []
# for word in word_tokenize(document):
#     texts_tokenized += jieba.analyse.extract_tags(word, 10)
# print(texts_tokenized)
#
# english_punctuations = [',', '.', ':', ';', '?', '(', ')', '[', ']', '&', '!', '*', '@', '#', '$', '%']
# texts_filtered_stopwords = texts_tokenized
# texts_filtered = [[word for word in document if not word in english_punctuations] for document in
#                   texts_filtered_stopwords]
#
# # 词干化
# from nltk.stem.lancaster import LancasterStemmer
#
# st = LancasterStemmer()
# texts_stemmed = [[st.stem(word) for word in docment] for docment in texts_filtered]
#
# # 去除过低频词
# all_stems = sum(texts_stemmed, [])
# stems_once = set(stem for stem in set(all_stems) if all_stems.count(stem) == 1)
# texts = [[stem for stem in text if stem not in stems_once] for text in texts_stemmed]
#
# print(texts)

# response = urllib.request.urlopen('http://php.net/')
# html = response.read()
# soup = BeautifulSoup(html, "html5lib")
# # 这需要安装html5lib模块
# text = soup.get_text(strip=True)
# tokens = text.split()
# filtered = [w for w in tokens if w not in stopwords.words('english')]
# freq = nltk.FreqDist(filtered)
# for key, val in freq.items():
#     print(str(key) + ':' + str(val))
# freq.plot(30, cumulative=False)
#
# print(
#     filtered
# )
def stopWrodMinnie():
    minnieStopWord = ['，', '：', '；', '’', '‘', '“', '”', '？', '！', '、', '【', '】']
    minnieStopWord += list(string.digits) + list(string.ascii_letters) + list(string.punctuation) + list(
        string.whitespace)
    return minnieStopWord


def NLTK():
    minnieStopWord = stopWrodMinnie()

    response = urllib.request.urlopen('https://www.jianshu.com/p/aea87adee163')
    html = response.read()
    soup = BeautifulSoup(html, "html5lib")
    # 这需要安装html5lib模块
    text = soup.get_text(strip=True)
    tokens = jieba.cut(text)
    filtered = [w for w in tokens if w not in stopwords.words('english') and w not in minnieStopWord]
    freq = nltk.FreqDist(filtered)
    freq.plot(30, cumulative=False)
    # for key, val in freq.items():
    #     print(str(key) + ':' + str(val))


# def function_20171228():
#     freq = FreqDist(text1)
#     sorted([w for w in set(text5) if len(w) > 7 and freq[w] > 7])


if __name__ == '__main__':
    import itertools

    # for index, _text in enumerate(itertools.product(string.ascii_lowercase, repeat=5)):
    #     if index < 100:
    #         print(str(index) + '-' + "".join(_text))
    #     else:
    #         break

    # print(3 * 'minnie')

    # print(
    #     'text2有{n}个词\n'.format(n=len(text2)),
    #     'text2有{n}个不同的词\n'.format(n=len(set(text2)))
    # )

    sample = ['Elinor', 'Marianne', 'Willoughby', 'Edward']
    words = [w for w in text2 if len(w) == 5]
    freq = FreqDist(words)
    # freq.tabulate(5, samples=sample)
    freq.plot(30, cumulative=True)

