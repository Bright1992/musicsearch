from urllib import request
import re

from .netease_crawler import crawler

if __name__=='__main__':
    crawler.crawl_by_list([108406896])
    crawler.crawl_by_artist()

# response = request.urlopen('http://music.163.com/playlist?id=26558065')
# data = response.read()
# website="music.163.com/"
# discover_ptn = re.compile(r'href="/discover/playlist.*?"')
# play_list_ptn = re.compile(r'href="/playlist\?id=\d+?"')
# song_ptn=re.compile(r'href="/song\?id=\d*?"')
# print(str(data.decode("utf-8")))
# discover_mch=discover_ptn.findall(str(data))
# playlist_mch=play_list_ptn.findall(str(data))
# song_mch=song_ptn.findall(str(data.decode("utf-8")))
# discover_mch.count()
