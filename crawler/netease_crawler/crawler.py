# coding:utf-8

from urllib import response, request
from html.parser import HTMLParser
import re
from netease.download import NetEase

website = "http://music.163.com"
path = "/home/bright/music/Crawler/data"


def crawl_by_artist():
    artist_pool = ["http://music.163.com/discover/artist/cat?id=1001&initial=-1",
                   "http://music.163.com/discover/artist/cat?id=1002&initial=-1",
                   "http://music.163.com/discover/artist/cat?id=1003&initial=-1",
                   "http://music.163.com/discover/artist/cat?id=2001&initial=-1",
                   "http://music.163.com/discover/artist/cat?id=2002&initial=-1",
                   "http://music.163.com/discover/artist/cat?id=2003&initial=-1"
                   ]
    obj = NetEase(60, None, path, True, True, False)
    artist_ptn = re.compile(r'/artist\?id=\d+')
    list_cnt=0
    for a_list in artist_pool:
        list_cnt+=1
        if list_cnt<=2:
            quit_thre=110
        elif list_cnt==5 or list_cnt==4:
            quit_thre=50
        else:
            quit_thre=35
        htmltext = request.urlopen(a_list).read().decode('utf-8')
        artist_mch = artist_ptn.findall(htmltext)
        id_mch = re.compile(r'\d+')
        cnt = 0
        for artist_link in artist_mch:
            artist_id = id_mch.findall(artist_link)[0]
            obj.download_artist_by_id(artist_id)
            cnt += 1
            if cnt >= quit_thre:
                break

def crawl_by_list(id_list):
    obj = NetEase(60,None,path,True,True,False)
    for id in id_list:
        obj.download_playlist_by_id(id, 'playlist' + str(id))