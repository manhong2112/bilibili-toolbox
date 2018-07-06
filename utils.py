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


class Int16(object):
   SIZE = 2

   @staticmethod
   def toUInt8arr(num):
      s = Int16.SIZE
      n = Int16.toUInt16(num)
      assert 0 <= n < (1 << (8 * s))
      limit = 255
      parts = [0] * s
      for i in range(0, s)[::-1]:
         parts[i] = n & limit
         n >>= 8
      return parts

   @staticmethod
   def fromUInt8arr(arr):
      return Int16.fromUint16(sum(v << (8 * (1 - i)) for i, v in enumerate(arr[:Int16.SIZE], 0)))

   @staticmethod
   def toUInt16(num):
      import struct
      return struct.unpack_from("H", struct.pack("h", num))[0]

   @staticmethod
   def fromUint16(num):
      import struct
      return struct.unpack_from("h", struct.pack("H", num))[0]


class Int32(object):
   SIZE = 4

   @staticmethod
   def toUInt8arr(num):
      s = Int32.SIZE
      n = Int32.toUInt32(num)
      assert 0 <= n < (1 << (8 * s))
      limit = 255
      parts = [0] * s
      for i in range(0, s)[::-1]:
         parts[i] = n & limit
         n >>= 8
      return parts

   @staticmethod
   def fromUInt8arr(arr):
      s = Int32.SIZE
      return Int32.fromUint32(sum(v << (8 * (3 - i)) for i, v in enumerate(arr[:s], 0)))

   @staticmethod
   def toUInt32(num):
      import struct
      return struct.unpack_from("I", struct.pack("i", num))[0]

   @staticmethod
   def fromUint32(num):
      import struct
      return struct.unpack_from("i", struct.pack("I", num))[0]

import urllib.request as request
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import json

def POST(url, headers=dict(), data=dict()):
    request = Request(url, urlencode(data).encode())
    for k in headers:
        request.add_header(k, headers[k])
    return urlopen(request)

def GET(url, headers=dict()):
    request = Request(url)
    for k in headers:
        request.add_header(k, headers[k])
    return urlopen(request)

def GET_json(url, headers=dict()):
    return json.loads(GET(url, headers).read().decode("unicode-escape").replace('\r\n', ''), strict=False)

def POST_json(url, headers=dict(), data=dict()):
    return json.loads(POST(url, headers, data).read().decode("unicode-escape").replace('\r\n', ''), strict=False)
