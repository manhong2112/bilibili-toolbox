import sys
import urllib.request as request
import json
import time
import traceback
import subprocess
import logging

import live_tool as live
from pushbullet import PushBullet


def log(msg, prefix="", err=None, end="\n"):
   t = time.localtime()
   tm = f"[{t.tm_year}/{t.tm_mon:02d}/{t.tm_mday:02d} {t.tm_hour:02d}:{t.tm_min:02d}:{t.tm_sec:02d}]"
   if err and "log" in ARGS:
      logging.exception(f"{tm} {msg}")
   elif err:
      traceback.print_exception(*sys.exc_info())
   print(f"{prefix}{tm} {msg}", end=end)
   sys.stdout.flush()


def push_notication(PB, LIVE_DAO):
   for i in PB.getDevices():
      if i["pushable"]:
         PB.pushLink(i["iden"], f'{LIVE_DAO.get_name()}直播中...',
                     f'{live.LIVE_HOST}/{LIVE_DAO.get_url()}')


ARIA2_RPC = "http://localhost:6800/jsonrpc"


def download(dao, *url):
   t = time.localtime()
   ts = int(time.mktime(t))
   request.urlopen(
       ARIA2_RPC,
       bytes(
           json.dumps({
               "id":
               "live",
               "method":
               "aria2.addUri",
               "jsonrpc":
               "2.0",
               "params": [
                   url, {
                       "out":
                       f"{dao.get_name()}-{t.tm_year}-{t.tm_mon:02d}-{t.tm_mday:02d}.{ts}.flv"
                   }, 0
               ]
           }), "utf-8"))


def argsProcess(LIVE_DAO, ARGS):
   if "push" in ARGS:
      log(f'正在推送...')
      try:
         push_notication(ARGS["push"], LIVE_DAO)
      except Exception as e:
         log(f'推送失敗...', err=True)
   if "download" in ARGS:
      log(f'正在下載...')
      try:
         download(LIVE_DAO, *LIVE_DAO.get_url())
      except Exception as e:
         log(f'下載失敗...', err=True)
   if "player" in ARGS:
      log(f'正在調用指定的播放器...')
      try:
         subprocess.Popen([ARGS["player"], LIVE_DAO.get_url()[2]])
      except Exception as e:
         log(f'調用失敗...', err=True)


def main(LIVE_ID, **ARGS):
   LIVE_DAO = live.Live(LIVE_ID)
   NAME = LIVE_DAO.get_name()
   if "log" in ARGS:
      logging.basicConfig(filename=ARGS["log"], level=logging.ERROR)
   while True:
      try:
         log(f"正在監聽{NAME}直播...")
         while True:
            log("heartbeat", prefix="\b" * 100, end="")
            try:
               if LIVE_DAO.get_live_status() == live.LIVE_STATUS["LIVE"]:
                  break
               time.sleep(2)
            except Exception as e:
               time.sleep(5)
         print()
         log(f'{NAME}直播中...')
         argsProcess(LIVE_DAO, ARGS)
         log(f"正在監聽{NAME}結束直播...")
         while True:
            log("heartbeat", prefix="\b" * 100, end="")
            try:
               if LIVE_DAO.get_live_status() == live.LIVE_STATUS["PREPARING"]:
                  break
               time.sleep(2)
            except Exception as e:
               time.sleep(5)
         print()
         log(f"{NAME}直播結束...")
      except Exception as e:
         log("未知錯誤, 重啟中...", err=True)


if __name__ == "__main__":
   LIVE_ID = sys.argv[1]
   ARGS = {}
   if len(sys.argv) > 2:
      for i in sys.argv[2:]:
         x = i.split("=")
         if len(x) == 1:
            ARGS[x[0]] = True
         else:
            ARGS[x[0]] = x[1]
   if "push" in ARGS:
      ARGS["push"] = PushBullet(ARGS["push"])
   main(LIVE_ID, **ARGS)
