import base64
import random
import time
from threading import Thread

from utils import Int16, Int32

HeaderLen = 16


def chatEncode(op, content, ver=1, seq=1):
   # Assume content is bytearray or list
   # [0, 0, 0, 0] + [0, 0]    + [0, 0] + [0, 0, 0, 0] + [0, 0, 0, 0]
   # contentLen   + headerLen + ver    + op           + seq
   ver = 1
   seq = 1
   return arrayPadTo(4, Int32.toUInt8arr(len(content) + HeaderLen)) + \
          arrayPadTo(2, Int16.toUInt8arr(HeaderLen)) + \
          arrayPadTo(2, Int16.toUInt8arr(ver)) + \
          arrayPadTo(4, Int32.toUInt8arr(op)) + \
          arrayPadTo(4, Int32.toUInt8arr(seq)) + \
          list(content)


def chatDecode(bytearr):
   # [0, 0, 0, 0] + [0, 0]    + [0, 0] + [0, 0, 0, 0] + [0, 0, 0, 0]
   # contentLen   + headerLen + ver    + op           + seq
   if not bytearr:
      return []
   contentLen = Int32.fromUInt8arr(bytearr[:4])
   return [{
       "raw": bytearr,
       "contentLen": Int32.fromUInt8arr(bytearr[:4]),
       "headerLen": Int16.fromUInt8arr(bytearr[4:6]),
       "ver": Int16.fromUInt8arr(bytearr[6:8]),
       "op": Int32.fromUInt8arr(bytearr[8:12]),
       "seq": Int32.fromUInt8arr(bytearr[12:16]),
       "content": bytearr[16:contentLen],
   }] + chatDecode(bytearr[contentLen:])


def arrayPadTo(length, arr):
   assert length >= len(arr)
   return ([0] * (length - len(arr))) + arr


def keepSocketLife(socket):
   while True:
      time.sleep(30)
      socket.send(chatEncode(2, b'[object Object]'))  # ??? i don't know why, maybe it is a bug?


def main(roomid):
   import websocket
   conn = websocket.create_connection("wss://tx-live-dmcmt-hk-01.chat.bilibili.com/sub")
   data = chatEncode(7, (
       f'{{"uid":0,"roomid":{roomid},"protover":1,"platform":"web","clientver":"1.2.8"}}').encode())
   conn.send(data)
   thread = Thread(target=keepSocketLife, args=(conn,))
   thread.start()
   while True:
      data = chatDecode(conn.recv_frame().data)
      for i in data:
         print(i)
         print(decodeUnicodeEscape(i["content"].decode("utf-8", errors="ignore")))


def decodeUnicodeEscape(string):
   result = []
   buff = ""
   unicodeEscape = 0
   escape = False
   for i in string:
      if unicodeEscape > 0:
         unicodeEscape -= 1
         buff += i
         if unicodeEscape == 0:
            result.append((b"\\u" + buff.encode()).decode("unicode-escape"))
            buff = ""
      elif escape:
         escape = False
         if i == "u":
            unicodeEscape = 4
         else:
            result.append(i)
      elif i == "\\":
         escape = True
      else:
         result.append(i)
   return "".join(result)


if __name__ == "__main__":
   main(184298)
