import csv,re,random,tweepy,datetime
import pandas as pd
import numpy as np
import os
import pickle
from keras.models import Sequential, load_model
from keras.layers import Dense, Activation, Embedding, Flatten, Dropout, TimeDistributed, Reshape, Lambda
from keras.layers import LSTM
from keras.optimizers import RMSprop, Adam, SGD
from keras import backend as K
from keras.utils import to_categorical
from keras.callbacks import ModelCheckpoint
from keras.preprocessing.text import Tokenizer
from keras.layers.embeddings import Embedding
from keras.preprocessing import sequence
from keras.preprocessing.text import one_hot
from keras.preprocessing.text import text_to_word_sequence
from collections import Counter
import tensorflow as tf

api_csv = pd.read_csv(r"Interest/apikeys.csv")
accesstokenlist=[]
for row in api_csv.iterrows():
    index, data = row
    accesstokenlist.append(data.tolist())


global maxTweetLength
global predictionDic
#For decoding the results
predictionDic = {0:'Food',1:'Music',2:'News',3:'Politics',4:'Soccer',5:'Tech',6:'Fashion',7:'Gaming',8:'Pets',9:'Reading',10:'Running',11:'Travel',12:'Travel'}
##Dont remove this
maxTweetLength = 141

def extractTweets(user,numOfTweets=500):
    ##Extract tweets from user (cycles api)
    currKeyIndex = 0
    currKeyList = accesstokenlist[currKeyIndex]
    totalKeys = len(accesstokenlist) #Number of twitter keys
    
    def set_auth(currKeyList):
        auth = tweepy.auth.OAuthHandler(currKeyList[0], currKeyList[1])
        auth.set_access_token(currKeyList[2], currKeyList[3])
        api = tweepy.API(auth)
        return api

    api = set_auth(currKeyList)
    rateID = 0   
    
    def cycleKey():
        nonlocal currKeyIndex
        nonlocal currKeyList
        nonlocal totalKeys
        nonlocal api
        currKeyIndex = (currKeyIndex+1)%totalKeys
        currKeyList = accesstokenlist[currKeyIndex]
        api = set_auth(currKeyList)
        
    def updateAPIRate():
        nonlocal rateID
        x = api.rate_limit_status()
        rateID = x['resources']['statuses']['/statuses/user_timeline']['remaining']
        print(rateID)
        
    def checkRateID():
        nonlocal rateID
        if rateID <= 5:
            cycleKey()
            updateAPIRate()
            
    listOfTweets = []
    counter = numOfTweets // 200 #200 per request
    print('Extracting tweets from: ' + user) 
    batch = api.user_timeline(screen_name = user,count=200)
    listOfTweets.extend(batch)
    listLen = listOfTweets[-1].id - 1
    while len(batch) > 0 and counter > 1:
        batch = api.user_timeline(screen_name = user,count=200,max_id=listLen)
        listOfTweets.extend(batch)
        listLen = listOfTweets[-1].id - 1
        counter -= 1
        updateAPIRate()
        checkRateID()
    listOfTweets = [tweet.text for tweet in listOfTweets]
    return listOfTweets


def processTweets(lst):
    for i in range(len(lst)):
        text = lst[i]
        text = text.lower()
        text = re.sub('RT @[\w_]+',"",text)
        text = re.sub('@[\w_]+','',text)
        text = re.sub(r"http\S+", "", text)
        lst[i] = text
    return lst

def predictUser(user,numTweets=500):
    userTweets = extractTweets(user,numTweets) # input number of tweets to pull as desired (>= 200)
    userTweets = processTweets(userTweets)
    data = tokenizer.texts_to_sequences(userTweets)
    data = sequence.pad_sequences(data, maxlen = maxTweetLength, padding = 'post')

    with graph.as_default():
        results = model.predict(data)

    results = np.argmax(results,axis=1)
    interest_key = Counter(results)
    interest_key = interest_key.most_common(1)[0][0]
    interest = predictionDic.get(interest_key)
    return interest

def load_cnn():
    global tokenizer
    with open('Interest/tokenizer30.pickle', 'rb') as handle:
        tokenizer = pickle.load(handle)
    tokenizer.oov_token = None
    global embeddings_matrix    
    with open('Interest/embeddings30.pickle', 'rb') as handle:
        embeddings_matrix = pickle.load(handle)
    global model
    model = load_model('Interest/bestmodel.h5')
    model._make_predict_function()
    global graph
    graph = tf.get_default_graph()
    
load_cnn()

if __name__ == '__main__':
    res = predictUser('mikaimcdermott',10000)
    print(res)


