# -*- coding: utf-8 -*-
from django.http import HttpResponse
import urllib2
import json

accessTokenUrl = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=wxb1424a0a2eb49689&secret=f5745f2b9724446361e8947034f12ac2'
createMenuUrl = 'https://api.weixin.qq.com/cgi-bin/menu/create?access_token='
getMenuUrl = 'https://api.weixin.qq.com/cgi-bin/menu/get?access_token='

def getAccessToken():
    request = urllib2.Request(accessTokenUrl)
    response = urllib2.urlopen(request)
    accessToken = json.loads(response.read())['access_token']
    return accessToken

def create():
    menu = '''
            {
                "button":[
                    {
                        "type":"click",
                        "name":"特色",
                        "key":"MENU_SPECIAL"
                    },
                    {
                        "type":"click",
                        "name":"活动",
                        "key":"MENU_PROMO"
                    },
                    {
                        "type":"click",
                        "name":"门店信息",
                        "key":"MENU_INFO"
                    }
                ]
            }
         '''
    response = urllib2.urlopen(createMenuUrl + getAccessToken(), menu)
    error = json.load(response)
    return error
