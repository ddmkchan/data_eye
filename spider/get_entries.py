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
			

if __name__ == '__main__':
	#func2()
	#get_link_from_file()
    #func()
	get_baba_comeback_entry()
	#process()
