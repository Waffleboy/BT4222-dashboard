# import remaining libraries
from keras.models import Sequential
from keras.layers import Dense, Flatten, LSTM, Conv1D, MaxPooling1D, Dropout, Activation
from keras.layers.embeddings import Embedding
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split
from sklearn.manifold import TSNE
from collections import Counter
import nltk
from nltk.corpus import stopwords
import string
import pickle
from _pickle import dump, load
import numpy as np
import pandas as pd

# will change this to apiKeys.csv
accesstokenlist=[]
accesstokenlist.append(['k9mZYw5Ob4F8xP7nBAD9qruWt','cISrskHBeEDCbZvPfPq7kgKD2y3f7fjCKZx0qeR5BNhdJfDpbV','2751072230-oI7GT4b5cHxiy0ztZi2UpHGFi3TB14O6Kxr0nIz','K7WckeuIRk3oRkDNOviSncYGBHChEZZPSDS8HcbtWcvyz'])
accesstokenlist.append(['Ylj8Iadlj9G6gP5NSlg1zd6jh','lpT0ayT2iRicrNmpIkUJVWXJWKgpw6xGD0oyPOd6WuoDdjLOnb','2751072230-3n2XQy7jWuATxWW8fUeQHmjPueSWJmqQMEJRO80','Ac05rHR7kvDalWzDPQG9qLe8GWD33SGVEyDJ6QuyzsuY8'])
accesstokenlist.append(['Ylj8Iadlj9G6gP5NSlg1zd6jh','lpT0ayT2iRicrNmpIkUJVWXJWKgpw6xGD0oyPOd6WuoDdjLOnb','2751072230-3n2XQy7jWuATxWW8fUeQHmjPueSWJmqQMEJRO80','Ac05rHR7kvDalWzDPQG9qLe8GWD33SGVEyDJ6QuyzsuY8'])
accesstokenlist.append(['n95HW5GEBFgvabqEAJHpfUotd','CsKcATAR6RDrjNQRfvtANAIUph0QwfiGv6pWtndOAJVRuHj1Rw','3922360932-NZsAqG12uu3f7xobVXF1VR0JQPpFoRvLjrK8OsL','atfRNC90EnJmEWeW9BkIlSkb67VjXwfK69x7hKceBUSH2'])
accesstokenlist.append(['7VzkryGJd0z8ClcWKoeImN4cb','fv0hmCRkSl8rgcnyduVM2t79A7dGBzvUTIAEXpX8IIoxOFwsgE','3922360932-HMZZneyV9DHaNbHYPHFczCxeHvvDpISPxeG1RpA','YqUgwlBrOwfWucfGC1JjRMa0e5fTwxwSlRCha7gjmFI2k'])

# api_csv = pd.read_csv(r"Interest/apikeys.csv")
# accesstokenlist=[]
# for row in api_csv.iterrows():
#     index, data = row
#     accesstokenlist.append(data.tolist())

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


global interest_maxTweetLength
interest_maxTweetLength = 141
global age_maxTweetLength
age_maxTweetLength = 30
# TO-DO create gender_maxTweetLength


# to decode prediction results
global predictionDic
global predictionAge
global predictionGender
predictionDic = {0:'Food',1:'Music',2:'News',3:'Politics',4:'Soccer',5:'Tech',6:'Fashion',7:'Gaming',8:'Pets',9:'Reading',10:'Running',11:'Travel',12:'Travel'}
predictionAge = {0:"Young", 1:"Middle Aged", 2:"Elderly"}
predictionGender = {0:"Female", 1:"Male"}

# input: user screen name
# output: [interest, age, gender]
def predictUser(user,numTweets=500):

    # list of tweets
    userTweets = extractTweets(user,numTweets) # input number of tweets to pull as desired (>= 200)
    userTweets = processTweets(userTweets)

    # interest
    interest_data = interest_tokenizer.texts_to_sequences(userTweets)
    interest_data = sequence.pad_sequences(interest_data, maxlen = interest_maxTweetLength, padding = 'post')
    results = interest_model.predict(interest_data)
    results = np.argmax(results,axis=1)
    interest_key = Counter(results)
    interest_key = interest_key.most_common(1)[0][0]
    interest = predictionDic.get(interest_key)

    # age
    age_data = age_tokenizer.texts_to_sequences(userTweets)
    age_data = sequence.pad_sequences(age_data, maxlen = age_maxTweetLength, padding = 'post')
    age_results = age_model.predict(age_data)
    age_results = np.argmax(age_results, axis=1)
    predicted_age_count = Counter(age_results)
    predicted_age_key = predicted_age_count.most_common(1)[0][0]
    age = predictionAge.get(predicted_age_key)

    # gender
    # TO-DO: process input data for gender_model
    gender_results = gender_model.predict(data)
    gender_results = np.argmax(gender_results, axis=1)
    predicted_gender_count = Counter(gender_results)
    predicted_gender_key = predicted_gender_count.most_common(1)[0][0]
    age = predictionGender.get(predicted_gender_key)

    return [interest, age, gender]

# load models
# load interest model
# from dion's predict_user.py
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
def load_cnn_age():
    global age_tokenizer
    global age_embeddings_matrix
    global age_model

    # pkl files for age model
    age_tokenizer = load(open('tokenizer30age.pkl', 'rb'))
    age_embeddings_matrix = load(open('embeddings30age.pkl', 'rb'))
    age_model = load_model('bestmodelage.h5')
    print("loaded age model")
