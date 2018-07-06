import sys
import urllib.request as request
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import json
import time
import traceback
import subprocess
import logging

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


def get_submit_count(mid):
   url = f"https://space.bilibili.com/ajax/member/getSubmitVideos?mid={mid}&pagesize=1"
   res = get_json(url)
   while True:
      if res["status"]:
         return res['data']['count']
      else:
         res = get_json(url)


def get_last_submit(mid):
   url = f"https://space.bilibili.com/ajax/member/getSubmitVideos?mid={mid}&pagesize=1"
   res = get_json(url)
   return res['data']['vlist'][0]['aid']


def get_info(mid):
   url = f"https://space.bilibili.com/ajax/member/GetInfo"
   res = post_json("https://space.bilibili.com/ajax/member/GetInfo", {},
                   {"mid": mid})
   return res


def log(msg, err=None):
   t = time.localtime()
   tm = f"[{t.tm_year}/{t.tm_mon:02d}/{t.tm_mday:02d} {t.tm_hour:02d}:{t.tm_min:02d}:{t.tm_sec:02d}]"
   if err:
      traceback.print_exception(*sys.exc_info())
   print(f"{tm} {msg}")


def push_notication(PB, title, message):
   for i in PB.getDevices():
      if i["pushable"]:
         PB.pushNote(i["iden"], title, message)


def main(memberid, pb):
   NAME = get_info(memberid)["data"]["name"]
   k = last_count = get_submit_count(memberid)
   while True:
      try:
         log(f"正在監聽{NAME}投稿...")
         while k == last_count:
            time.sleep(5)
            k = get_submit_count(memberid)
         pb and push_notication(pb, "Notice",
                                f"{NAME}投/刪稿了...({last_count} -> {k})")
         if k > last_count:
            import reply
            reply.main(get_last_submit(memberid), pb)
         last_count = k
         log(f"{NAME}投/刪稿了...({last_count} -> {k})")
      except Exception as e:
         log("Error", e)
         pass


if __name__ == "__main__":
   mid = int(sys.argv[1])
   main(mid, None)
