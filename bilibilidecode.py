import urllib.request as urllib
import json
import html
import time

api_1 = "http://api.bilibili.com"
api_2 = "http://interface.bilibili.com"
api_3 = "http://comment.bilibili.com"

bilibilijj = "http://www.bilibilijj.com"
api_key = "8e9fc618fbd41e28"


def get_json(url):
   return json.loads(
       urllib.urlopen(url).read().decode("unicode-escape").replace('\r\n', ''),
       strict=False)


def printf(str, *val):
   print(str.format(*val))


def get_info(aid):
   video_info = [
       get_json("{0}/view?type=json&appkey={1}&id={2}".format(
           api_1, api_key, aid))
   ]
   pages_num = video_info[0]['pages']
   if pages_num > 1:
      video_info = []
      for i in range(1, pages_num + 1):
         time.sleep(0.2)
         video_info.append(
             get_json("{0}/view?type=json&appkey={1}&id={2}&page={3}".format(
                 api_1, api_key, aid, i)))
   return video_info


def print_info(v_info):
   cid = v_info['cid']
   link_info = get_json(
       '{0}/playurl?type=mp4&otype=json&quality=4&appkey={1}&cid={2}'.format(
           api_2, api_key, cid))
   try:
      printf(">> cid: {0}", cid)
      printf(">> Title: {1} Author: {0[author]} Upload Time: {0[created_at]}",
             v_info, html.unescape(v_info['title']))
      printf(
          ">> Play: {0[play]} Coins: {0[coins]} Fav: {0[favorites]} Pages: {0[pages]}",
          v_info)
      printf(">> Type: {0[typename]} Tag: {1}", v_info,
             v_info['tag'].split(','))
      printf(">> Description: {0}", html.unescape(v_info['description']))
      printf(">> Danmu file link at: {0}/{1}.xml", api_3, cid)
      printf(">> Video link at bilibilijj: {0}/freedown/spare/{1}.mp4",
             bilibilijj, cid)
      try:
         printf(">> Video link at: {0}", link_info['durl'][0]['url'])
      except KeyError:
         printf("E> Failed to get Video Link: {0}", link_info)
         return
   except KeyError:
      printf("E> Video not found")
      printf("D> {0}", v_info)
      return


def main():
   aid = input("aid of video \n> av")
   try:
      int(aid)
   except ValueError:
      print("Value Error")
      return

   i = 0
   try:
      for video_info in get_info(aid):
         i += 1
         printf("\n>> ====== Page {0} ======", i)
         print_info(video_info)
   except KeyError:
      printf("E> Video not found")
      return


if __name__ == "__main__":
   while True:
      main()
