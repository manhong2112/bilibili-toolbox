import json
import re
import urllib.request as request
from threading import Thread, Timer
from urllib.parse import urlencode

import websocket
from bs4 import BeautifulSoup
import queue
import time

import live_chat as lchat

LIVE_HOST = "http://live.bilibili.com"
API_HOST = "http://api.live.bilibili.com"
USERINFO_API = "http://space.bilibili.com/ajax/member/GetInfo"
PLAYURL_API = f"{API_HOST}/api/playurl"
GETINFO_API = f"{API_HOST}/room/v1/Room/get_info"
ROOMINIT_API = f"{API_HOST}/room/v1/Room/room_init"
LIVE_STATUS = {"PREPARING": 0, "LIVE": 1, "ROUND": 2}
SUB_TYPE = {"DANMU_MSG": 0, "GUARD_MSG": 1, "SYS_MSG": 2}

def get_roomid(shortid):
   url = f"{ROOMINIT_API}?id={shortid}"
   data = get_json(url)
   return data["data"]["room_id"]


def get_userinfo(uid):
   return json.loads(post(USERINFO_API, {"mid": uid}, {"referer": USERINFO_API}))


def get_roominfo(roomid):
   return get_json(f"{GETINFO_API}?room_id={roomid}")


def post(url, data={}, headers={}):
   return request.urlopen(\
            request.Request(url, urlencode(data).encode(), headers=headers)\
          ).read().decode()


class Live():

   def __init__(self, live_id):
      self.LIVE_ID = live_id
      self.ROOM_ID = get_roomid(self.LIVE_ID)

      self.raw = get_roominfo(self.ROOM_ID)
      self.userinfo = get_userinfo(self.raw["data"]["uid"])

      self.PLAYURL_URL = f"{PLAYURL_API}?cid={self.ROOM_ID}&quality=4&otype=json&platform=web"

      self.sub = Live.Sub(self.ROOM_ID)

   def get_live_status(self):
      self.raw = get_roominfo(self.ROOM_ID)
      return self.raw["data"]["live_status"]

   def get_url(self):
      tmp = get_json(self.PLAYURL_URL)
      return [i["url"] for i in tmp["durl"]]

   def get_name(self):
      return self.userinfo["data"]["name"]

   def get_title(self):
      self.raw = self.raw = get_roominfo(self.ROOM_ID)
      return self.raw["data"]["title"]

   def get_recently_rawdata(self):
      return self.raw

   class Sub(object):

      @staticmethod
      def __connect(roomid):
         conn = websocket.create_connection("wss://tx-live-dmcmt-sel-01.chat.bilibili.com/sub")
         data =(f'{{"uid":0,"roomid":{roomid},"protover":1,"platform":"web","clientver":"1.2.8"}}').encode()
         d = lchat.chatEncode(7, data)
         conn.send(bytes(d))
         return conn

      def reconnect(self):
         self.conn = self.__connect(self.roomid)
         return self.conn

      def __init__(self, roomid):
         self.roomid = roomid
         self.msgQueue = {}
         self.msgCallback = {}

         self.conn = self.__connect(roomid)

         def send(data):
            # with auto reconnect
            try:
               self.conn.send(data)
            except websocket._exceptions.WebSocketConnectionClosedException:
               self.reconnect()
            except ConnectionResetError:
               self.reconnect()
            except TimeoutError:
               self.reconnect()
            self.conn.send(data)

         def recv_frame():
            try:
               return self.conn.recv_frame()
            except websocket._exceptions.WebSocketConnectionClosedException:
               self.reconnect()
            except ConnectionResetError:
               self.reconnect()
            except TimeoutError:
               self.reconnect()
            return self.conn.recv_frame()

         def recvMsg():
            while True:
               data = lchat.chatDecode(recv_frame().data)
               for i in data:
                  try:
                     cmd = json.loads(i["content"])["cmd"]
                  except Exception:
                     continue
                  if cmd in self.msgCallback:
                     self.msgCallback[cmd](json.loads(i["content"]))
                  else:
                     if cmd not in self.msgQueue:
                        self.msgQueue[cmd] = queue.Queue()
                     self.msgQueue[cmd].put(json.loads(i["content"]))

         def keepSocketLife():
            while True:
               send(bytes(lchat.chatEncode(2, b'[object Object]')))
               time.sleep(30)

         self.msgThread = Thread(target=recvMsg)
         self.keepSocketLifeThread = Thread(target=keepSocketLife)

         self.msgThread.start()
         self.keepSocketLifeThread.start()

      def hasNext(self, msgType="DANMU_MSG"):
         return msgType in self.msgQueue and not self.msgQueue[msgType].empty()

      def next(self, block=True, msgType="DANMU_MSG"):
         if msgType not in self.msgQueue:
            self.msgQueue[cmd] = queue.Queue()
         return self.msgQueue[cmd].get(block)

      def cleanQueue(self, msgType="DANMU_MSG"):
         return

      def setCallback(self, msgType, func):
         self.msgCallback[msgType] = func

      def __get__(self, index):
         return self.danmakuList[index]

      def __exit__(self):
         self.conn.close()

   def get_chat_room(self):
      return self.sub


def get_html(url):
   return request.urlopen(url).read().decode("utf-8")


def get_json(url):
   return json.loads(request.urlopen(url).read())


def get_url(live_id):
   return Live(live_id).get_url()


def get_live_status(live_id):
   return Live(live_id).get_live_status()
