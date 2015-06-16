#!/usr/bin/env python
#encoding=utf-8

import requests
import json
import re
from bs4 import BeautifulSoup

s = requests.session()

tv_names = "虎妈猫爸,嘿老头,酷爸俏妈,待嫁老爸"
names = "爸爸回来了,爸爸去哪儿"

url = "http://so.iqiyi.com/so/q_%s"

def func():
	URLS = [(i, url %i) for i in names.split(',')]
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
				print i[0], link.get('title').encode('utf-8'), link.get('href').encode('utf-8')


def func2():
	URLS = [(i, url %i) for i in tv_names.split(',')]
	for i in URLS:
		r = s.get(i[1])
		soup = BeautifulSoup(r.text)
		for link in soup.find_all("a", class_="album_link"):
			if 'javascript' not in link.get('href'):
				href = link.get('href')
				m = re.search('data-player-tvid=\"(\d+)\"', s.get(href).text)
				tvid = m.group(1) if m is not None else ''
				m2 = re.search('data-qitancomment-qitanid=\"(\d+)\"', s.get(href).text)
				qitanid = m2.group(1) if m2 is not None else ''
				if tvid and qitanid:
					print i[0], link.get('title').encode('utf-8'), link.get('href').encode('utf-8'), tvid, qitanid
			
if __name__ == '__main__':
	func()
