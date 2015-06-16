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
	URLS = [(i, url %i) for i in tv_names.split(',')]
	for i in URLS:
		r = s.get(i[1])
		soup = BeautifulSoup(r.text)
		for link in soup.find_all("a", class_="album_link"):
			if 'javascript' not in link.get('href'):
				print i[0], link.get('href').encode('utf-8')
			
			
if __name__ == '__main__':
	func()
