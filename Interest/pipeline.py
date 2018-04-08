# import libraries
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
from _pickle import dump, load
from nltk.corpus import stopwords

# api keys
api_csv = pd.read_csv(r"Interest/apikeys.csv")
accesstokenlist=[]
for row in api_csv.iterrows():
    index, data = row
    accesstokenlist.append(data.tolist())

# pre-defined functions
# extract tweets from a given screen name
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

# only for interest model
def processTweets(lst):
    for i in range(len(lst)):
        text = lst[i]
        text = text.lower()
        text = re.sub('RT @[\w_]+',"",text)
        text = re.sub('@[\w_]+','',text)
        text = re.sub(r"http\S+", "", text)
        lst[i] = text
    return lst

# for ensembling ML models
class ensemble_ML():
    def __init__(self, list_of_models, vect, num_class):
        self.models = list_of_models
        self.vect = vect
        self.num_class = num_class

    def preprocess_x(self, tweet):
        tweets = pd.Series(tweet)

        #convert tweets to lower case
        tweets = tweets.apply(str.lower)
        #replaces any urls with URL
        tweets = tweets.str.replace(r'((www\.[\S]+)|(https?://[\S]+))', ' URL ')
        #removes user mentions
        tweets = tweets.str.replace(r"@\S+", " MENTIONS ")
        #removes hashtags
        tweets = tweets.str.replace(r"#\S+", " HASHTAGS ")
        #removes rt
        tweets = tweets.str.replace(r'\brt\b', ' RETWEETS ')
        #removes multiple white spaces
        tweets = tweets.str.replace(r'\s+', " ")
        #strips both ends of white space
        tweets = tweets.apply(str.strip)

        #loading stopwords
        stop = stopwords.words('english')

        #removing stopwords
        tweets = tweets.str.split()
        tweets = tweets.apply(lambda x: [item for item in x if item not in stop])
        tweets = tweets.str.join(" ")

        return tweets

    def tokenize_x(self, tweet):
        tweet = vect.transform(tweet)

        return tweet

    # for age prediction
    def format_to_age_label(self, list_of_labels):
        age_mapper = pd.Series(['Middle', 'Old', 'Teenager', 'Young Adult'])
        return age_mapper[list_of_labels]

    def predict_age(self, tweet):
        tweet = self.preprocess_x(tweet)
        tweet = self.tokenize_x(tweet)

        ypred = np.zeros((tweet.shape[0], self.num_class))

        for model in self.models:
            ypred = ypred + model.predict_proba(tweet)

        ypred = np.argmax(ypred, axis = -1)
        return self.format_to_age_label(ypred)

    # for gender prediction
    def format_to_gender_label(self, list_of_labels):
        gender_mapper = pd.Series(['Female', 'Male'])

        return gender_mapper[list_of_labels]

    def predict_gender(self, tweet):
        tweet = self.preprocess_x(tweet)
        tweet = self.tokenize_x(tweet)

        ypred = np.zeros((tweet.shape[0], self.num_class))

        for model in self.models:
            ypred = ypred + model.predict_proba(tweet)

        ypred = np.argmax(ypred, axis = -1)
        return self.format_to_gender_label(ypred)


# get predictions based on screen name
global interest_maxTweetLength
interest_maxTweetLength = 141

# to decode prediction results
global predictionDic
predictionDic = {0:'Food',1:'Music',2:'News',3:'Politics',4:'Soccer',5:'Tech',6:'Fashion',7:'Gaming',8:'Pets',9:'Reading',10:'Running',11:'Travel',12:'Travel'}

# input: user screen name
# output: [interest, age, gender]
def predictUser(user,numTweets=500):

    # list of tweets
    userTweets = extractTweets(user,numTweets) # input number of tweets to pull as desired (>= 200)

    # interest
    interest_data = processTweets(userTweets)
    interest_data = interest_tokenizer.texts_to_sequences(interest_data)
    interest_data = sequence.pad_sequences(interest_data, maxlen = interest_maxTweetLength, padding = 'post')
    results = interest_model.predict(interest_data)
    results = np.argmax(results,axis=1)
    interest_key = Counter(results)
    interest_key = interest_key.most_common(1)[0][0]
    interest = predictionDic.get(interest_key)

    # age
    age_model = ensemble_ML(list_of_models = [age_lr, age_xgb, age_nb], \
                             vect = vect, num_class = 4)
    age_results = age_model.predict_age(userTweets)
    predicted_age_count = Counter(age_results.index)
    predicted_age_key = predicted_age_count.most_common(1)[0][0]
    age = age_results[predicted_age_key].iloc[0]

    # gender
    gender_model = ensemble_ML(list_of_models = [gender_lr, gender_xgb, gender_nb], \
                             vect = vect, num_class = 2)
    gender_results = gender_model.predict_gender(userTweets)
    predicted_gender_count = Counter(gender_results.index)
    predicted_gender_key = predicted_gender_count.most_common(1)[0][0]
    gender = gender_results[predicted_gender_key].iloc[0]

    return [interest, age, gender]


# functions to load models
# load interest model
def load_cnn_interest():
    global interest_tokenizer
    global interest_embeddings_matrix
    global interest_model

    # .pickle files for interest model
    with open('tokenizer30.pickle', 'rb') as handle:
        interest_tokenizer = pickle.load(handle)
    interest_tokenizer.oov_token = None
    with open('embeddings30.pickle', 'rb') as handle:
        interest_embeddings_matrix = pickle.load(handle)
    interest_model = load_model('bestmodel.h5')
    print("loaded interest model")

# load age model
def load_ML_age():
    global vect  # same vectorizer for gender
    global age_lr
    global age_xgb
    global age_nb

    # pkl files for age model
    vect = load(open('vectorizer.pkl', 'rb'))
    age_lr = load(open('age_lr.pkl', 'rb'))
    age_xgb = load(open('age_xgb.pkl', 'rb'))
    age_nb = load(open('age_nb.pkl', 'rb'))
    print("loaded age model")

# load age model
def load_ML_gender():
    global gender_lr
    global gender_xgb
    global gender_nb

    # pkl files for gender model
    gender_lr = load(open('gender_lr.pkl', 'rb'))
    gender_xgb = load(open('gender_xgb.pkl', 'rb'))
    gender_nb = load(open('gender_nb.pkl', 'rb'))
    print("loaded gender model")
