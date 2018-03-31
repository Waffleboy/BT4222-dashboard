# Create your views here.
import logging
import random, string
import sys
import json
import os
from threading import Thread

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from apple.models import Tweet,TwitterUser
from apple import views_helper 

from apple.forms import replyForm
from apple.tweet_reply import update_stat
from apple.customer_helper import get_user_info

import logging
logger = logging.getLogger(__name__)

def index(request):
	context = {}

	# get:
	# 1) daily / weekly / monthly wordcloud info. this should be a pregenerated image, not run on demand
	# 2) topic modelling, same.
	# 3) positive tweets
	# 4) negative tweets
	# 5) other tweets

	tweets = Tweet.objects.all()
	positive_tweets = tweets.filter(sentiment='positive')
	negative_tweets = tweets.filter(sentiment='negative')

	context['total_users'] = TwitterUser.objects.count()
	context['positive_tweets'] = views_helper.format_tweets_to_table(positive_tweets)
	context['negative_tweets'] = views_helper.format_tweets_to_table(negative_tweets)

	return render(request, 'dashboard.html', context)

def customers(request):
	context = {}

	all_users = TwitterUser.objects.all()
	user_info = get_user_info(all_users)

	context['users'] = user_info
	return render(request, 'customers.html', context)

def profile(request):
	context = {}
	
	if request.method == "GET":
		request_dict = list(dict(request.GET).keys())
		form = replyForm()

		if len(request_dict) != 0:
			dict_content = request_dict[0]
			screenname = dict_content.split('?')[0]
			tweet_id = dict_content.split('?')[1]

	else:
		form = replyForm(request.POST)

		tweet_id = request.POST['tweet_id']
		screenname = request.POST['screen_name']

		if form.is_valid():
			reply = form.cleaned_data['reply']
			update_stat(screenname, reply, tweet_id)

			form = replyForm()
	#To hide errors from multiple get requests when loading new page
	try:
		user = TwitterUser.objects.get(screen_name = screenname)
		tweet = Tweet.objects.get(tweet_id = tweet_id)

		context['profile_pic'] = user.profile_picture
		context['screen_name'] = user.screen_name
		context['followers'] = user.followers_count
		context['friends'] = user.friends_count
		context['tweet_id'] = tweet.tweet_id
		context['tweet'] = tweet.text
		context['form'] = form
		#context['age'] = user.age
		#context['gender'] = user.gender
	except:
		pass
	return render(request, 'profile.html', context)

##TODO: Move to seperate thread
@csrf_exempt 
def stream_api_post(request):
	if request.method == 'POST':
		logger.info("Got a stream API post")
		tweet_details = json.loads(request.body)
		if not tweet_details["AUTH_KEY"] == os.environ["DJANGO_POST_KEY"]:
			return HttpResponse("Invalid Auth key")

		tweet = Tweet.find_or_create(tweet_details)
		response = {'status':'fail'}

		if tweet:
			response['status'] = 'success'
			response['tweet_id'] = tweet.tweet_id
			response['user_id'] = tweet.user.twitter_id
			response['screen_name'] = tweet.user.screen_name
		
		return HttpResponse(json.dumps(response))

	else: #GET
		return HttpResponse("Invalid operands")