## install and import libraries
import pandas as pd
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from google.colab import auth
from oauth2client.client import GoogleCredentials
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split

# import remaining libraries
from keras.models import Sequential
from keras.layers import Dense, Flatten, LSTM, Conv1D, MaxPooling1D, Dropout, Activation
from keras.layers.embeddings import Embedding

# Others
import nltk
import string
import pickle
import numpy as np
import pandas as pd
from nltk.corpus import stopwords

from sklearn.manifold import TSNE

## authentication to Google Drive
# auth.authenticate_user()
# gauth = GoogleAuth()
# gauth.credentials = GoogleCredentials.get_application_default()
# drive = GoogleDrive(gauth)
#
# ## find all files within your own Google Drive
# listed = drive.ListFile({'q': "title contains '.csv' or title contains 'h5' or title contains 'pickle'"}).GetList()
# for file in listed:
#   print('title {}, id {}'.format(file['title'], file['id']))
#
# test_id = '16j5L_2z3vHp9ZTU2ZwQ7Qi9lggUZmb0f'
# age_model = '15sEgas1yfanq92KVFhbLyjkEk0JOn5LH'
# age_embeddings = '10_BX4TEShBsvvSh48zJXQ1-DZbSdX2uh'
# age_tokenizer = '1pFZGlZsni33W5eL06OAJbVzDevnPpNLc'
#
# download_test = drive.CreateFile({'id': test_id})
# download_model = drive.CreateFile({'id': age_model})
# download_embeddings = drive.CreateFile({'id': age_embeddings})
# download_tokenizer = drive.CreateFile({'id': age_tokenizer})
#
# download_test.GetContentFile('test.csv')
# download_model.GetContentFile('bestmodelage.h5')
# download_embeddings.GetContentFile('embeddings30age.pickle')
# download_tokenizer.GetContentFile('tokenizer30age.pickle')
#
# # list files on colab drive
# !ls
#
# """## Split testing data"""
#
# test = pd.read_csv('test.csv').loc[:, ['tweets', 'age', 'gender']]
#
# # for gender model
# test_X, test_y_gender = test['tweets'], test['gender']
#
# print(test_X.shape)
# print(test_y_gender.shape)

"""## Load models"""

# will change this to apiKeys.csv
accesstokenlist=[]
accesstokenlist.append(['k9mZYw5Ob4F8xP7nBAD9qruWt','cISrskHBeEDCbZvPfPq7kgKD2y3f7fjCKZx0qeR5BNhdJfDpbV','2751072230-oI7GT4b5cHxiy0ztZi2UpHGFi3TB14O6Kxr0nIz','K7WckeuIRk3oRkDNOviSncYGBHChEZZPSDS8HcbtWcvyz'])
accesstokenlist.append(['Ylj8Iadlj9G6gP5NSlg1zd6jh','lpT0ayT2iRicrNmpIkUJVWXJWKgpw6xGD0oyPOd6WuoDdjLOnb','2751072230-3n2XQy7jWuATxWW8fUeQHmjPueSWJmqQMEJRO80','Ac05rHR7kvDalWzDPQG9qLe8GWD33SGVEyDJ6QuyzsuY8'])
accesstokenlist.append(['Ylj8Iadlj9G6gP5NSlg1zd6jh','lpT0ayT2iRicrNmpIkUJVWXJWKgpw6xGD0oyPOd6WuoDdjLOnb','2751072230-3n2XQy7jWuATxWW8fUeQHmjPueSWJmqQMEJRO80','Ac05rHR7kvDalWzDPQG9qLe8GWD33SGVEyDJ6QuyzsuY8'])
accesstokenlist.append(['n95HW5GEBFgvabqEAJHpfUotd','CsKcATAR6RDrjNQRfvtANAIUph0QwfiGv6pWtndOAJVRuHj1Rw','3922360932-NZsAqG12uu3f7xobVXF1VR0JQPpFoRvLjrK8OsL','atfRNC90EnJmEWeW9BkIlSkb67VjXwfK69x7hKceBUSH2'])
accesstokenlist.append(['7VzkryGJd0z8ClcWKoeImN4cb','fv0hmCRkSl8rgcnyduVM2t79A7dGBzvUTIAEXpX8IIoxOFwsgE','3922360932-HMZZneyV9DHaNbHYPHFczCxeHvvDpISPxeG1RpA','YqUgwlBrOwfWucfGC1JjRMa0e5fTwxwSlRCha7gjmFI2k'])

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

global maxTweetLength
maxTweetLength = 141

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
    # tokenize and create sequence
    data = tokenizer.texts_to_sequences(userTweets)
    data = sequence.pad_sequences(data, maxlen = maxTweetLength, padding = 'post')

    # interest
    results = model.predict(data)
    results = np.argmax(results,axis=1)
    interest_key = Counter(results)
    interest_key = interest_key.most_common(1)[0][0]
    interest = predictionDic.get(interest_key)

    # age
    age = 0

    # gender
    gender = 0

    return [interest, age, gender]

# input: "","age" or "gender", "" defaults to Dion's interest model
def loadCNN(model_type):

  global tokenizer
  with open('tokenizer30{}.pickle'.format(model_type), 'rb') as handle:
      tokenizer = pickle.load(handle)
  tokenizer.oov_token = None

  global embeddings_matrix
  with open('embeddings30{}.pickle'.format(model_type), 'rb') as handle:
      embeddings_matrix = pickle.load(handle)

  if model_type=="age" or model_type=="gender":
    model_glove = Sequential()
    model_glove.add(Embedding(vocabulary_size, 50, input_length=5000, \
                              weights=[embedding_matrix], trainable=False))
    model_glove.add(Dropout(0.2))
    model_glove.add(Conv1D(64, 5, activation='relu'))
    model_glove.add(MaxPooling1D(pool_size=4))
    model_glove.add(LSTM(100))

  # load model
  global model
  model = load_model('bestmodel{}.h5'.format(model_type))
  print(model_type + " loaded")

loadCNN("age") # corrupted file
