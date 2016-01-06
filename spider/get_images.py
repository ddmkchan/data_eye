#!/usr/bin/env python
#encoding=utf-8

import os
import urllib
import requests
import traceback

from config import *
mylogger = get_logger('get_images')
map_logger = get_logger('image_map')

db_conn = new_session()

import socket
socket.setdefaulttimeout(30)

import multiprocessing
from multiprocessing.dummy import Pool as ThreadPool

import uuid
import imghdr

if localIP == u'192.168.1.215':
	imgs_path = "/root/yanpengchen/data_eye/spider/imgs"
	imgs_path_v2 = "/root/yanpengchen/data_eye/spider/imgs_v2"
else:
	imgs_path = "/home/cyp/data_eye/spider/imgs"
	imgs_path_v2 = "/home/cyp/data_eye/spider/imgs_v2"

def download_pic(args):
	try:
		url, name = args
		if not os.path.isfile("%s/%s" % (imgs_path, name)):
			mylogger.info("downloading pic ... %s" % name)
			urllib.urlretrieve(url, "%s/%s" % (imgs_path, name))
	except Exception,e:
		mylogger.error(traceback.format_exc())

def get_imgs():
	try:
		pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
		pics = get_imgs_from_db()
		pool.map_async(download_pic, pics)
		pool.close()
		pool.join()
	except Exception,e:
		mylogger.error(traceback.format_exc())

def download_pic_v2(img_url, pic_name):
	try:
		img_file = "%s/%s" % (imgs_path_v2, pic_name)
		if not os.path.isfile(img_file):
			mylogger.info("downloading pic ... %s" % pic_name)
			urllib.urlretrieve(img_url, img_file)
			if os.path.exists(img_file):
				img_type = imghdr.what(img_file)
				if img_type is not None:
					new_img_file = "%s.%s" %(img_file, img_type)
					os.rename(img_file, new_img_file)
					return "%s.%s" % (pic_name, img_type)
				else:
					return pic_name
	except Exception,e:
		mylogger.error(traceback.format_exc())
	return None

def get_imgs_from_db():
	return [(re.img_path, re.id) for re in db_conn.query(ADVRecord).filter(ADVRecord.    img_path!=u'')]

def download_imgs():
	count = 0
	for ret in db_conn.query(ADVGameDetail).filter(ADVGameDetail.img_url!=u'').filter(ADVGameDetail.img_path==u''):
		uid = str(uuid.uuid1())
		map_logger.info("%s\t%s" % (ret.id, uid))
		pic_name = download_pic_v2(ret.img_url, uid)
		if pic_name is not None:
			count += 1
			if isinstance(pic_name, str):
				pic_name = pic_name.decode('utf-8')
			ret.img_path = pic_name
		if count % 100:
			mylogger.info("update img_path %s commit" % count)
			db_conn.commit()
	db_conn.commit()
		
if __name__ == '__main__':
	mylogger.info("download imgs ...")
	download_imgs()
