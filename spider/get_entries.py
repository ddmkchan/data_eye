#!/usr/bin/env python
#encoding=utf-8

import sys
sys.path.append('/home/cyp/Utils/common')
from define import *
from model import *
import requests
import json
import re
from bs4 import BeautifulSoup

db_conn = new_session()
s = requests.session()

tv_names = "虎妈猫爸,嘿老头,酷爸俏妈,待嫁老爸"
names = "爸爸去哪儿,爸爸回来了"

url = "http://so.iqiyi.com/so/q_%s"

def func():
	URLS = [(i, url %i) for i in names.split(',')[:1]]
	for i in URLS:
		r = s.get(i[1])
		soup = BeautifulSoup(r.text)
		for link in soup.find_all("a", class_="album_link"):
			if 'javascript' not in link.get('href'):
				#href = link.get('href')
				#m = re.search('data-player-tvid=\"(\d+)\"', s.get(href).text)
				#tvid = m.group(1) if m is not None else ''
				#m2 = re.search('data-qitancomment-qitanid=\"(\d+)\"', s.get(href).text)
				#qitanid = m2.group(1) if m2 is not None else ''
				#if tvid and qitanid:
				#	print i[0], link.get('title').encode('utf-8'), link.get('href').encode('utf-8'), tvid, qitanid
				if re.search(u'第\d+集', link.get('title')) is not None: 
					print i[0], link.get('title').encode('utf-8'), link.get('href').encode('utf-8')


def func2():
	URLS = [(i, url %i) for i in tv_names.split(',')[2:3]]
	for i in URLS:
		r = s.get(i[1])
		soup = BeautifulSoup(r.text)
		for link in soup.find_all("a", class_="album_link"):
			if 'javascript' not in link.get('href'):
				#href = link.get('href')
				#m = re.search('data-player-tvid=\"(\d+)\"', s.get(href).text)
				#tvid = m.group(1) if m is not None else ''
				#m2 = re.search('data-qitancomment-qitanid=\"(\d+)\"', s.get(href).text)
				#qitanid = m2.group(1) if m2 is not None else ''
				#if tvid and qitanid:
				print i[0], link.get('title').encode('utf-8'), link.get('href').encode('utf-8')
					#print i[0], link.get('title').encode('utf-8'), link.get('href').encode('utf-8'), tvid.encode('utf-8'), qitanid.encode('utf-8')
			
def process():
	with open('id_list') as f:
		for line in f.readlines():
			tv_name, episode, url, tvid, qitanid = line.rstrip().split()
			ins = db_conn.query(IQIYI_TV).filter(IQIYI_TV.tv_name==tv_name).filter(IQIYI_TV.episode==episode).first()
			if not ins:
				item = IQIYI_TV(**{'tv_name':tv_name, 'episode':episode, 'url':url, 'tvid':int(tvid), 'qitanid' : int(qitanid)})
				db_conn.add(item)
	db_conn.commit()


def get_link_from_file():
	f = open('kbqm')
	soup = BeautifulSoup(f.read().decode('utf-8'))
	for i in soup.find_all("a", class_="album_link"):
		if 'javascript' not in i.get('href'):
			print i.get('title'), i.get('href')

def get_baba_comeback_entry():
	with open('babaqunar') as f:
		for line in f.readlines():
			r = s.get(line.rstrip())
			m = re.search('data-player-tvid=\"(\d+)\"', r.text)
			tvid = m.group(1) if m is not None else ''
			m2 = re.search('data-qitancomment-qitanid=\"(\d+)\"', r.text)
			qitanid = m2.group(1) if m2 is not None else ''
			#if tvid and qitanid:
			print tvid, qitanid
			tv_name = '爸爸去哪儿'
			item = IQIYI_TV(**{'tv_name':tv_name, 'episode':tvid, 'url':line.rstrip(), 'tvid':int(tvid), 'qitanid' : int(qitanid)})
			db_conn.add(item)
	db_conn.commit()
			
def get_xiaomi():
	f = open('xm')
	soup = BeautifulSoup(f.read().decode('utf-8'))
	ll = [re.split('\_|\.', i.get('href'))[-2] for i in soup.find_all("a")]
	print len(ll)
	#for i in soup.find_all("a"):
#		href = i.get('href')
#		print re.split('\_|\.', href)


#_category_list_360 = [19, 20, 51, 52, 53, 54, 101587, 102238, 100451]
_category_list_360 = [11, 12, 14, 15,16, 17,18, 102228, 102230, 102231, 102232, 102233, 102239]

def get_360_list(cid, page):
	rs = []
	r = s.get('http://zhushou.360.cn/list/index/cid/%s?page=%s' % (cid, page))
	soup = BeautifulSoup(r.text)
	for i in soup.find("ul", class_="iconList").find_all("li"):
		item = i.find('h3').find('a')
		rs.append((item.text, item.get('sid')))
	return rs

def get_360_tags(sid):
	r = s.get('http://zhushou.360.cn/detail/index/soft_id/%s' % sid)
	soup = BeautifulSoup(r.text)
	tags = soup.find("div", class_="app-tags")
	if tags is not None:
		return u",".join([i.text for i in tags.find_all("a")])
	return u""

def get_360_main():
	count = 0
	for c in _category_list_360:
		#category = gameid2category.get(str(c))
		category = id2category.get(str(c))
		for i in xrange(1, 51):
			icon_list = get_360_list(c, i)
			#print category, ",".join([i[0] for i in icon_list])
			for icon in icon_list:
				print "%s\t%s\t%s" % (icon[1], icon[0].encode('utf-8'), category)
#				tags = get_360_tags(icon[1])
#				#print icon[0], icon[1], tags
#				count += 1
#				#ins = db_conn.query(APPLIST2).filter(APPLIST2.sid==int(icon[1])).first()
#				#if not ins:
#				item = APPLIST2(**{'sid': int(icon[1]), 'app_name': icon[0], 'tags': tags, 'category':category})
#				db_conn.merge(item)
#				if count % 1000 == 0:
#					print "%s commit" % count
#					db_conn.commit()
#	db_conn.commit()

id2category = {
"11"	 :"系统安全", 
"12" 	 :"通讯社交",
"14"	 :"影音视听",
"15"	 :"新闻阅读",
"16"	 :"生活休闲",
"18" 	 :"主题壁纸",
"17" 	 :"办公商务",
"102228" :"摄影摄像",
"102230" :"购物优惠",
"102231" :"地图旅游",
"102232" :"教育学习",
"102139" :"金融理财",
"102233" :"健康医疗"}


gameid2category = {
"20": 		"动作冒险", 
"19": 		"休闲益智",
"54": 		"棋牌天地",
"51": 		"体育竞速",
"53": 		"经营策略",
"52": 		"飞行射击",
"100451": 	"网络游戏",
"102238": 	"儿童游戏",
"101587": 	"角色扮演"
}

def match():
	with open('dataeye_games') as f:
		for line in f.readlines()[:]:
			app = line.rstrip()
			#print "****", app
			ins = db_conn.query(APPLIST2).filter(APPLIST2.app_name==app).filter(APPLIST2.tags!=u'').first()
			if ins:
				if len(ins.tags) != 0:
					print "%s\t%s" % (app, ins.tags.encode('utf-8'))


def get_ip_info():
	URL = "http://ip.chinaz.com/"
	payload = {'IP': '058.205.255.255,183.13.153.142,058.206.159.2551'}
	r = s.get(URL, params=payload)
	soup = BeautifulSoup(r.text)
	for i in soup.find("span", id="status").find_all('strong'):
		segs = i.text.split(": ")[1].split("==>>")
		

if __name__ == '__main__':
	#get_360_tags(1838349)
	get_360_main()
	#match()
	#get_ip_info()
