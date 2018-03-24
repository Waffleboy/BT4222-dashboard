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

def index(request):
	context = {}
	return render(request, 'dashboard.html', context)

def customers(request):
	context = {}
	return render(request, 'customers.html', context)
