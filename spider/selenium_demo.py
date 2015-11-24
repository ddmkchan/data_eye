#!/usr/bin/env python
#encoding=utf-8

from selenium import webdriver
from selenium.webdriver.common.by import By
from get_kc_list import *

def func():
	driver = webdriver.Firefox()
	#driver.get("http://data.auto.qq.com/car_brand/index.shtml#_其他___")
	driver.get("http://data.auto.qq.com/car_brand/index.shtml?type=serial")
	#print driver.page_source.encode('utf-8')
	soup = BeautifulSoup(driver.page_source)
	for rs in soup.find_all('div', class_='listAll'):
		id = rs.get('id').encode('utf-8')
		for i in rs.find_all('div', class_='listData'):
			for j in i.find('ul').find_all('li'):
				dt = j.find('dt')
				print id,dt.find('a').get('href').encode('utf-8'), dt.text.encode('utf-8')
				for k in j.find_all('dd'):
					print k.text.encode('utf-8')
	driver.close()



def func2():
	driver = webdriver.Firefox()
	driver.get("http://car.auto.ifeng.com/series/2382/spec/37691/")
	return driver.page_source.encode('utf-8')
	#soup = BeautifulSoup(driver.page_source)
	driver.close()

if __name__ == '__main__':
	print func2()
