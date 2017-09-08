# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod
import xml.etree.ElementTree as ET
import time
import menu
import manager
import json
from models import *


class Msg:
    def __init__(self, toUser = None, fromUser = None, createTime = None):
        self.toUser = toUser
        self.fromUser = fromUser
        self.createTime = createTime

    @abstractmethod
    def parseXML(self, msgXMLTree):
        pass

    @abstractmethod
    def reply(self):
        pass

class TextMsg(Msg):

    msgType = 'text'

    def __init__(self, toUser = None, fromUser = None, createTime = None, content = None):
        Msg.__init__(self, toUser, fromUser, createTime)
        self.content = content

    def parseXML(self, msgXMLTree):
        toUser = msgXMLTree.find('ToUserName').text
        fromUser = msgXMLTree.find('FromUserName').text
        createTime = msgXMLTree.find('CreateTime').text
        content = msgXMLTree.find('Content').text
        self.__init__(toUser, fromUser, createTime, content)

        return self

    def reply(self):
        responseMsg = TextMsg(self.fromUser, self.toUser, int(time.time()), self.content)
        if manager.check(self.fromUser):
            if self.content.strip().encode('utf-8') == '更新菜单':
                error = menu.create()
                if error['errcode'] == 0:
                    responseMsg.content = '更新成功'
                else:
                    responseMsg.content = '更新失败\n原因: ' + error['errmsg'].encode('utf-8')
            if self.content.strip().encode('utf-8') == '座位信息':
                seating = Seating.objects.get(id=1)
                seating = json.loads(seating.seating)
                content = '\n'.join([str(seat) for seat in seating])
                if content == '':
                    content = '没人入座'
                responseMsg.content = content
        if self.content.strip().encode('utf-8') == '用户信息':
            responseMsg.content = self.fromUser

        return responseMsg

class Event(Msg):
    msgType = 'event'

    def parseXML(self, msgXMLTree):

        types = {
            'CLICK': ClickEvent
        }

        event = types.get(msgXMLTree.find('Event').text)

        return event().parseXML(msgXMLTree)

class ClickEvent(Event):

    event = 'CLICK'

    def __init__(self, toUser = None, fromUser = None, createTime = None, eventKey = None):
        Event.__init__(self, toUser, fromUser, createTime)
        self.eventKey = eventKey

    def parseXML(self, msgXMLTree):
        toUser = msgXMLTree.find('ToUserName').text
        fromUser = msgXMLTree.find('FromUserName').text
        createTime = msgXMLTree.find('CreateTime').text
        eventKey = msgXMLTree.find('EventKey').text
        self.__init__(toUser, fromUser, createTime, eventKey)

        return self

    def reply(self):
        responseMsg = TextMsg(self.fromUser, self.toUser, int(time.time()), 'clicked')
        if self.eventKey == 'MENU_INFO':
            responseMsg.content = '地址: 张家港市杨舍镇暨阳湖商业街4幢一层102室\n\n营业时间: 10:00 - 凌晨3:00\n\n电话: 0512-58213777'
        # elif self.eventKey == 'MENU_CONTACT':
        #     responseMsg.content = '0512-58213777'
        return responseMsg

def parseMsg(msgXML):
    msgXMLTree = ET.XML(msgXML)
    msgType = msgXMLTree.find('MsgType').text

    types = {
        'text': TextMsg,
        'event': Event
    }

    msg = types.get(msgType)

    return msg().parseXML(msgXMLTree)
