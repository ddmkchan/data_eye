#!/usr/bin/env python
#encoding=utf-8

from selenium import webdriver
from selenium.webdriver.common.by import By
from get_kc_list import *
from time import sleep

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
	#driver.get("http://openbox.mobilem.360.cn/qcms/view/t/first_release?type=game&webpg=shoufanew")
	#driver.get("http://car.auto.ifeng.com/series/2382/spec/37691/")
	driver.get("https://www.appannie.com/apps/ios/top-chart/china/games/?date=2016-03-30")
	#driver.get("http://m.taoche.com/buycar/carconfig.aspx?sid=2046&carid=10946")
	return driver.page_source.encode('utf-8')
	#soup = BeautifulSoup(driver.page_source)
	driver.close()


def func3():
	from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
	from config import EXECUTABLE_PATH
	user_agent = (
	    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_4) " +
	    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.57 Safari/537.36"
	)
	
	dcap = dict(DesiredCapabilities.PHANTOMJS)
	dcap["phantomjs.page.settings.userAgent"] = user_agent

	driver = webdriver.PhantomJS(desired_capabilities=dcap, executable_path=EXECUTABLE_PATH)  #这要可能需要制定phatomjs可执行文件的位置
	#driver.get("http://ka.9game.cn/")
	#driver.get("http://m.taoche.com/buycar/carconfig.aspx?sid=2046&carid=10946")
	#driver.get('http://openbox.mobilem.360.cn/html/standalone/index.html?webpg=shilian1&showTitleBar=0&fm=gm004_shilian1&m=13389b498494c1230fab6b4c04572848&s_stream_app=1&m2=1680ae9efad81fb51224ec048d296b6a&v=3.5.15&re=1&nt=1&ch=100130&os=22&model=m2+note&sn=4.589389937671455&cu=mt6753&ca1=armeabi-v7a&ca2=armeabi&ppi=1080x1920&cpc=1&ui_version=v2')
	#driver.get('http://openbox.mobilem.360.cn/qcms/view/t/first_release?type=game&webpg=shoufanew')
	#driver.get('http://zhushou.360.cn/list/index/cid/2/order/newest/?page=1')
	driver.get('http://zhushou.360.cn/detail/index/soft_id/3220961')
	sleep(0.3)
	#driver.get('http://openbox.mobilem.360.cn/qcms/view/t/first_release?type=game&webpg=shoufanew')
	#print driver.current_url
	print driver.page_source.encode('utf-8')
	#print driver.find_element_by_id('result').text.split('\n')[0].split('来自：')[1]
	driver.quit

def fun4():
	import requests
	r = requests.get('http://zhushou.360.cn/detail/index/soft_id/3220961')
	print r.text.encode('utf-8')

if __name__ == '__main__':
	print func2()
	#func3()
	#sess = requests.session()
	#cookies = dict(PHPSESSID='h4pfli36lte3tet1rt2eg7ve00')
	##cookies = dict(cookies='PHPSESSID=h4pfli36lte3tet1rt2eg7ve00')
	##cookies = dict(cookies='aliyungf_tc=AQAAAObhmVcgdQMAfeR0cV+erKvYh1RQ; PHPSESSID=h4pfli36lte3tet1rt2eg7ve00; _ga=GA1.2.752348207.1459841670; baidu_qiao_v3_count_8356286=1; Hm_lvt_0d266795d9f60795734646d04334a96c=1459474268; Hm_lpvt_0d266795d9f60795734646d04334a96c=1460709102; activity-itc=1462377599000; activity-itc-0422')
	#headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.109 Safari/537.36'}
	#raw_data = {'code':'uNTVXA', 'referrer':'/'}
	#r = requests.post("http://aso100.com/error/ipLImit", data=raw_data, cookies=cookies)
	#print r.history
	#soup = BeautifulSoup(r.text)
	#print soup.title
