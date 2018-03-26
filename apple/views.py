# Create your views here.
import logging
import random, string
import sys
import json
from threading import Thread

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from apple.models import Tweet

def index(request):
	context = {}
	return render(request, 'dashboard.html', context)

def customers(request):
	context = {}
	return render(request, 'customers.html', context)


@csrf_exempt 
def stream_api_post(request):
	if request.method == 'POST':
		tweet_details = json.loads(request.body)
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