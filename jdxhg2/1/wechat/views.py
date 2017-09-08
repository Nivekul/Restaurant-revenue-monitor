# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
import xml.etree.ElementTree as ET
import time
import hashlib
from msg import *
import urllib2
from urllib import urlencode
import json
from models import *
from django import forms


@csrf_exempt
def index(request):
    if request.method == 'GET':
        data        = request.GET
        echostr     = data.get('echostr', None)

        if echostr:
            if checkSignature(data):
                return HttpResponse(echostr, content_type="text/plain")
        else:
            raise Http404


    else:
        msgXML = request.body

        receivedMsg = parseMsg(msgXML)
        responseMsg = receivedMsg.reply()

        return render(request,
                      'wechat/textResponse.xml',
                      {'responseMsg': responseMsg},
                      content_type='text/xml')

    return HttpResponse(type(echostr) is str)

def checkSignature(data):
    signature   = data.get('signature', None)
    timestamp   = data.get('timestamp', None)
    nonce       = data.get('nonce', None)
    token       = 'ixjW7dSjnQq8UbZF8xjavn1J3XjfOOg'

    tmpArr = [token, timestamp, nonce]
    tmpArr.sort()
    tmpStr = ''.join([str(i) for i in tmpArr])
    tmpStr = hashlib.sha1(tmpStr).hexdigest()

    return tmpStr == signature

def auth(request):
    return HttpResponse('TolmmqaRQQYV54az', content_type='text/plain')

def lineup(request):
    codeRequestData = {
        "appid" : "wxb1424a0a2eb49689",
        "redirect_uri" : "http://jdxhg2.applinzi.com/wechat/lineup",
        "response_type" : "code",
        "scope" : "snsapi_base",
        "state" : "888"
    }
    codeUrl = "https://open.weixin.qq.com/connect/oauth2/authorize?" + urlencode(codeRequestData) + "#wechat_redirect"

    if request.method == 'GET':
        data    = request.GET
        code    = data.get('code', None)
        userID  = data.get('userID', None)
        if code:
            userID = getUserID(code)
            return redirect("http://jdxhg2.applinzi.com/wechat/lineup?" + urlencode({"userID":userID}))
        elif userID:
            try:
                user = User.objects.get(openid = userID)
                name = user.name
                phone = user.phone
                userid = user.id
            except User.DoesNotExist:
                raise Http404
            form = LineupForm()
            return render(request, "wechat/lineup.html", {'form':form, 'userid':userid})
    else:
        form = LineupForm(request.POST or None)
        return render(request, "wechat/lineup.html", {'form':form})


    return redirect(codeUrl)

def queue(request):
    if request.method == "POST":
        data = request.POST
        userid = data.get('userid')
        count = data.get('count')
        name = data.get('name')
        phone = data.get('phone')
        gender = data.get('gender')
        user = User.objects.get(id = userid)
        user.name = name
        user.phone = phone
        user.gender = gender
        user.save()
        queue = Queue(count=count, userid=user)
        queue.save()
        return HttpResponse('success '+str(queue.id))
    else:
        raise Http404

class TelInput(forms.widgets.Input):
    input_type = "tel"

class LineupForm(forms.Form):
    openid = forms.IntegerField(required=True, widget=forms.HiddenInput)
    count = forms.ChoiceField(required=True, widget=forms.Select, choices=((1,1),(2,2),(3,3),(4,4),(5,5),(6,6),(7,7),(8,8),(9,9),(10,10),(11,11),(12,12)))
    name = forms.CharField(max_length=5, required=True, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'姓名'}))
    phone = forms.CharField(max_length=11, required=True, widget=TelInput(attrs={'class':'form-control', 'placeholder':'联系电话'}))
    gender = forms.ChoiceField(required=True, widget=forms.RadioSelect, choices=(('m','先生'),('f','女士')))

def getUserID(code):
    userIDRequestData = {
        "appid" : "wxb1424a0a2eb49689",
        "secret" : "f5745f2b9724446361e8947034f12ac2",
        "code" : code,
        "grant_type" : "authorization_code"
    }
    accessTokenUrl = 'https://api.weixin.qq.com/sns/oauth2/access_token?' + urlencode(userIDRequestData)
    codeRequest = urllib2.Request(accessTokenUrl.replace('CODE', code))
    response = urllib2.urlopen(codeRequest)
    userID = json.load(response)['openid']
    return userID

@csrf_exempt
def updateSeating(request):
    if request.method == "POST":
        data = request.POST
        access_token = data.get('access_token', None)
        if access_token == 'Sd78fNuehRaSd78we_ug':
            seating = Seating.objects.get(id=1)
            seating.seating = data.get('seating')
            seating.save()
            return HttpResponse('Upload success!')
        else:
            raise Http404
