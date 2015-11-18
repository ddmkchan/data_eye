#!/usr/bin/env python
#encoding=utf-8

import sys
import requests
import json
import urllib
import traceback
import re
import sys
sys.path.append('/home/cyp/Utils/common')
from define import *
from model import *
from bs4 import BeautifulSoup
import time

from get_logger import *
mylogger = get_logger('hot_game')

s = requests.session()
db_conn = new_session()


source_map = {
			"baidu"	: 0,
			"xiaomi": 1,
			"360"	: 2,
			"9game"	: 3,
			"9game_hot_wanted"	: 4,
				}

def get_baidu_hot_games():
	url = "http://shouji.baidu.com/game"
	r = s.get(url)
	if r.status_code == 200:
		soup = BeautifulSoup(r.text)
		hot = soup.find("div", class_="sec-hot tophot")
		if hot is not None:
			for k in hot.find_all("li")[:]:
				popular 	= u""
				game_type 	= u""
				status 		= u""
				url 		= u""
				source 		= source_map.get('baidu')
				url_a = k.find("a",class_="app-box")
				if url_a is not None:
					url = "http://shouji.baidu.com%s" % url_a.get('href')
				detail = k.find("div",class_="app-detail")
				if detail is not None:
					game_name = detail.find("p").text
					img = detail.find("div", class_="icon").find("img").get("src")
					down_size = detail.find("p", class_="down-size")	
					downloads = down_size.find("span", class_="down").text
					size = down_size.find("span", class_="size").text
					yield game_name, img, downloads, size, source, popular, game_type, status, url

def download_pic(url, name):
	try:
		if not os.path.isfile("/home/cyp/data_eye/spider/ttt/%s" % (name)):
			print '**'
			urllib.urlretrieve(url, "/home/cyp/data_eye/spider/ttt/%s" % name)
	except Exception,e:
		print traceback.format_exc()

def download_pic2(args):
	try:
		url, name = args
		if not os.path.isfile("/home/cyp/data_eye/spider/pics/%s" % (name)):
			mylogger.info("downloading pic ... %s" % name)
			urllib.urlretrieve(url, "/home/cyp/data_eye/spider/pics/%s" % name)
	except Exception,e:
		mylogger.error(traceback.format_exc())

def get_appannie_icons():
	import multiprocessing
	from multiprocessing.dummy import Pool as ThreadPool
	try:
		pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
		urls = [(ret.src, ret.name+"_"+str(ret.source)) for ret in db_conn.query(HotGames).filter(HotGames.create_date=="2015-09-02").filter(HotGames.source!=4)]	
		pool.map_async(download_pic2, urls)
		pool.close()
		pool.join()
	except Exception,e:
		print traceback.format_exc()
	

def get_icons(f):
	import multiprocessing
	from multiprocessing.dummy import Pool as ThreadPool
	try:
		pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
		urls = []
		for ret in f():
			app_name, src, download_count, size, source = ret
			url = src 
			name = app_name.encode("utf-8")+"_"+str(source)
			urls.append((url, name))
			#pool.apply_async(download_pic, (url, name))
		pool.map_async(download_pic2, urls)
		pool.close()
		pool.join()
	except Exception,e:
		mylogger.error(traceback.format_exc())

def get_active_game_rank(page):
	url = "http://game.xiaomi.com/index.php?c=app&a=ajaxPage&type=rank"
	payload = {
				"page"			:page,
				"category_id"	:"",
				"total_page"	:60,
				"rank_id"		:12,
				"type"			:"rank"
				}
	r = s.post(url, data=payload)
	if r.status_code == 200:
		return r.json()
	return None

def get_xiaomi_games():
	for page in xrange(5):
		detail = get_active_game_rank(page)
		if detail is not None:
			for d in detail:
				popular 	= u""
				game_type 	= u""
				status 		= u""
				url 		= u"http://game.xiaomi.com/app-appdetail--app_id__%s.html" % d.get("ext_id")
				game_name = d.get("game_name")
				img = d.get("icon")
				downloads = d.get("download_count")
				size = d.get("apk_size")
				source = source_map.get('xiaomi')
				yield game_name, img, downloads, size, source, popular, game_type, status, url

def get_360_online_games():
	for page in xrange(1,4):
		r = s.get('http://zhushou.360.cn/list/index/cid/100451/order/download/?page=%s' % page)
		if r.status_code == 200:
			soup = BeautifulSoup(r.text)
			for i in soup.find("ul", class_="iconList").find_all("li"):
				popular 	= u""
				game_type 	= u""
				status 		= u""
				item = i.find('h3').find('a')
				url 		= u"http://zhushou.360.cn/detail/index/soft_id/%s" % item.get('sid')
				game_name = item.text
				img = i.find("a", sid="%s" % item.get("sid")).find("img").get("_src")
				downloads = i.find("span").text
				size 		= u""
				source 		= source_map.get("360")
				yield game_name, img, downloads, size, source, popular, game_type, status, url


def get_9game_new_wanted_list():
	r = s.get("http://www.9game.cn/xyqdb/")
	if r.status_code == 200:
		soup = BeautifulSoup(r.text)
		t = soup.find("div", class_="box-text").find("table").find_all("tr")
		for i in t[1:]:
			td_list = i.find_all("td")
			#print td_list
			rank = td_list[0].find("span").text
			title = td_list[1].find("a").get("title")
			url = u"http://www.9game.cn%s" % td_list[1].find("a").get("href")
			game_type = td_list[2].text.rstrip()
			status = td_list[3].text.strip()
			popular = td_list[4].text.strip()
			yield rank, title, url, game_type, status, popular


def get_9game_new_hot_list():
	r = s.get("http://www.9game.cn/xyrb/")
	if r.status_code == 200:
		soup = BeautifulSoup(r.text)
		t = soup.find("div", class_="box-text").find("table").find_all("tr")
		for i in t[1:]:
			td_list = i.find_all("td")
			#print td_list
			rank = td_list[0].find("span").text
			title = td_list[1].find("a").get("title")
			url = u"http://www.9game.cn%s" % td_list[1].find("a").get("href")
			game_type = td_list[2].text
			status = td_list[3].text
			popular = td_list[4].text
			yield rank, title, url, game_type, status, popular

def get_9game_detail():
	for i in get_9game_new_hot_list():
		rank, title, url, game_type, status, popular = i
		r = s.get(url)
		if r.status_code == 200:
			soup = BeautifulSoup(r.text)
			try:
				title_div = soup.find("div", class_="title")
				img_div = soup.find("div", class_="info").find("span", class_="img")
				if img_div is not None:
					img = img_div.find("img").get("src")
				elif soup.find("div", class_="info").find("img") is not None:
					img = soup.find("div", class_="info").find("img").get("src")
				else:
					img 		= u""
				if title_div is not None:
					game_name = title_div.text.strip()
				elif soup.find("div", class_="contain-title").find("div", class_="h-title") is not None:
					game_name = soup.find("div", class_="contain-title").find("div", class_="h-title").find('h1').text
				else:
					game_name = u""
				source = source_map.get('9game')
				downloads 	= u""
				size 		= u""
				yield game_name, img, downloads, size, source, popular, game_type, status, url
			except Exception,e:
				mylogger.error("%s\t%s" % (title, traceback.format_exc()))

def get_9game_detail2():
	for i in get_9game_new_wanted_list():
		rank, title, url, game_type, status, popular = i
		r = s.get(url)
		if r.status_code == 200:
			soup = BeautifulSoup(r.text)
			try:
				title_div = soup.find("div", class_="title")
				img_div = soup.find("div", class_="info").find("span", class_="img")
				if img_div is not None:
					img = img_div.find("img").get("src")
				elif soup.find("div", class_="info").find("img") is not None:
					img = soup.find("div", class_="info").find("img").get("src")
				else:
					img 		= u""
				if title_div is not None:
					game_name = title_div.text.strip()
				elif soup.find("div", class_="contain-title").find("div", class_="h-title") is not None:
					game_name = soup.find("div", class_="contain-title").find("div", class_="h-title").find('h1').text
				else:
					game_name = u""
				source = source_map.get('9game_hot_wanted')
				downloads 	= u""
				size 		= u""
				yield game_name, img, downloads, size, source, popular, game_type, status, url
			except Exception,e:
				mylogger.error("%s\t%s" % (title, traceback.format_exc()))

def get_9game_page_detail():
	r = s.get(url)
	if r.status_code == 200:
		soup = BeautifulSoup(r.text)
		try:
			pass
		except Exception,e:
			mylogger.error("%s" % (traceback.format_exc()))
	


headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.125 Safari/537.36'}

def get_appannie_hot_list():
	r = s.get("https://www.appannie.com/apps/ios/top/china/games/?device=iphone", headers=headers, timeout=10)
	if r.status_code == 200:
		soup = BeautifulSoup(r.text)
		t = soup.find("div", class_="region-main-inner").find("table").find_all("tr")
		for i in t[1:]:
			hot = i.find_all("td")[2]
			d = hot.find("div", class_="main-info").find("a")
			yield d.text, d.get("href")

def get_appannie_detail():
	for i in get_appannie_hot_list():
		app_name, url = i
		r = s.get("https://www.appannie.com/cn%s" % url, headers=headers)
		if r.status_code == 200:
			soup = BeautifulSoup(r.text)
			img_div = soup.find("div", class_="col-lg-3 col-md-3 col-sm-4 text-center-mobile app-logo")
			yield app_name, img_div.find("img").get("src"), u"", u"", 4


def get_data(f):
	for i in enumerate(f()):
		rank, ret = i
		game_name, img, downloads, size, source, popular, game_type, status, url = ret
		ins = db_conn.query(HotGames).filter(HotGames.name==game_name).filter(HotGames.source==source).filter(HotGames.create_date==date.today()).first()
		if ins is None:
			item = HotGames(**{
							"name"			: game_name,
							"src"			: img,
							"download_count"		: downloads,
							"size"			: size,
							"source"		: source,
							"rank"			: rank+1,
							"popular"		: popular,
							"game_type"		: game_type,
							"status"		: status,
							"url"			: url
							})
			db_conn.merge(item)
	db_conn.commit()
	mylogger.info("%s done!" % f.__name__)

def main():
	mylogger.info("holy shit!")
	#get_icons(get_baidu_hot_games)
	get_data(get_baidu_hot_games)
	get_data(get_xiaomi_games)
	get_data(get_360_online_games)
	get_data(get_9game_detail)
	get_data(get_9game_detail2)
	#get_data(get_appannie_detail)

if __name__ == '__main__':
	main()
	#get_data(get_9game_detail)
	#get_data(get_appannie_detail)
