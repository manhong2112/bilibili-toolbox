from collections import namedtuple
import urllib.request as request
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import json
import time
from pushbullet import PushBullet


def POST(url, header=dict(), data=dict()):
   request = Request(url, urlencode(data).encode())
   if "referer" not in header or "Referer" not in header:
      header["Referer"] = url
   for k in header:
      request.add_header(k, header[k])
   return urlopen(request)


def post_json(url, header=dict(), data=dict()):
   return json.loads(POST(url, header, data).read().decode())


def get_html(url):
   return urlopen(url).read().decode("utf-8")


def get_json(url):
   return json.loads(
       urlopen(url).read().decode("utf-8").replace('\r', '').replace('\n', ''))


ReplyData = namedtuple('ReplyData', ['floor', 'user', 'message', 'reply'])


def json2ReplyData(json, subreply=None):
   return ReplyData(floor=json['floor'],\
                    user=json["member"]["uname"],\
                    message=json['content']['message'],\
                    reply=subreply)


def json2subReplyData(json, subreply=None):
   subreply = {}
   for each_subreply in json:
      subreply_data = json2ReplyData(each_subreply)
      subreply[subreply_data.floor] = subreply_data
   return subreply


class Reply(object):

   def __init__(self, aid):
      self.aid = aid

   def getReplyCount(self):
      url = "https://api.bilibili.com/x/v2/reply?type=1&oid={}&pn={}"  # aid, page number
      res = get_json(url.format(self.aid, 1))
      self.last_reply_count = res["data"]["page"]["count"]
      return self.last_reply_count

   def getReplyaCount(self):
      url = "https://api.bilibili.com/x/v2/reply?type=1&oid={}&pn={}"  # aid, page number
      res = get_json(url.format(self.aid, 1))
      self.last_reply_acount = res["data"]["page"]["acount"]
      return self.last_reply_acount

   def getReply(self):
      url = "https://api.bilibili.com/x/v2/reply?type=1&oid={}&pn={}"  # aid, page number

      res = [get_json(url.format(self.aid, 1))]
      reply = {}

      if res[0]["data"]["upper"]["top"]:
         upper_subreply_data = json2subReplyData(
             res[0]["data"]["upper"]["top"]["replies"])
         upper_reply_data = json2ReplyData(res[0]["data"]["upper"]["top"],
                                           upper_subreply_data)
         reply[upper_reply_data.floor] = upper_reply_data

      reply_count = self.last_reply_count = res[0]["data"]["page"]["count"]
      self.last_reply_acount = res[0]["data"]["page"]["acount"]
      for pn in range(2, reply_count // 20 + 2):
         res.append(get_json(url.format(self.aid, pn)))

      for each_page in res:
         for each_reply in each_page["data"]["replies"]:
            subreply_data = json2subReplyData(each_reply["replies"])
            reply_data = json2ReplyData(each_reply, subreply_data)
            reply[reply_data.floor] = reply_data
      self.last_reply = reply
      return reply

   def getReplyByPageNumber(self, pn):
      url = "https://api.bilibili.com/x/v2/reply?type=1&oid={}&pn={}"  # aid, page number
      res = get_json(url.format(self.aid, pn))
      reply = {}
      for each_reply in res["data"]["replies"]:
         subreply_data = json2subReplyData(each_reply["replies"])
         reply_data = json2ReplyData(each_reply, subreply_data)
         reply[reply_data.floor] = reply_data
      return reply

   def getLastReplyNumber(self):
      return self.last_reply_count

   def getLastReply(self):
      return self.last_reply


def push_notication(PB, title, message):
   for i in PB.getDevices():
      if i["pushable"]:
         PB.pushNote(i["iden"], title, message)


def main(aid, pb):
   k = Reply(aid)
   last_reply_count = 0
   count = 0
   while True:
      l = k.getReplyaCount()
      while l == last_reply_count:
         time.sleep(60)
         l = k.getReplyaCount()
      if l > last_reply_count:
         raw = k.getReply()
         s = "\n".join(repr(raw[i]) for i in raw)
         open(f"reply.{count}", "w", encoding="utf-8").write(s)
         count += 1
      last_reply_count = l


if __name__ == "__main__":
   import sys
   main(int(sys.argv[1]), None)
