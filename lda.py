#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 28 16:22:45 2018

@author: thiru
"""

from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
import string
import gensim
from gensim import corpora
import pandas as pd


stop = set(stopwords.words('english'))
exclude = set(string.punctuation)
lemma = WordNetLemmatizer()


def clean(doc):
    stop_free = ' '.join([i for i in doc.lower().split() if i not in stop])
    punc_free = ''.join(ch for ch in stop_free if ch not in exclude)
    normalized = " ".join(lemma.lemmatize(word) for word in punc_free.split())
    return normalized


def run_lda(doc_clean,num_topics):
    dictionary = corpora.Dictionary(doc_clean)
    doc_term_matrix = [dictionary.doc2bow(doc) for doc in doc_clean]
    lda = gensim.models.ldamodel.LdaModel
    ldamodel = lda(doc_term_matrix,num_topics=num_topics,id2word = dictionary,passes = 60)
    return ldamodel,dictionary,doc_term_matrix

def pretty_print_results(ldamodel,num_topics,num_words):
    z = ldamodel.print_topics(num_topics=num_topics,num_words=num_words)
    group = 1
    for i in range(len(z)):
        entry = z[i][1]
        entry = ''.join([i for i in entry if not (i.isdigit() or i == '.' or i == '*')])
        entry = entry.replace('"','')
        entry = '{}. {}'.format(group,entry)
        entry = entry.replace(' + ',', ')
        z[i] = entry
        group += 1
    return z

num_topics = 2

texts = pd.Series(["this is a random sentence","random too man idgi"])

texts_cleaned = [clean(x).split() for x in texts]

ldamodel,dictionary,doc_term_matrix  = run_lda(texts_cleaned,num_topics)

results = pretty_print_results(ldamodel,num_topics,num_words = 7)
for entry in results:
    print(entry)
print('\n')

import pyLDAvis.gensim as gensimvis
import pyLDAvis

vis_data = gensimvis.prepare(ldamodel,doc_term_matrix, dictionary )
pyLDAvis.save_html(vis_data,'file.html')