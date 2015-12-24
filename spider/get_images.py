#!/usr/bin/env python
#encoding=utf-8

import os
import urllib
import requests
import traceback

from config import *
mylogger = get_logger('get_images')

db_conn = new_session()

import socket
socket.setdefaulttimeout(30)

import multiprocessing
from multiprocessing.dummy import Pool as ThreadPool


def download_pic(args):
	try:
		url, name = args
		if not os.path.isfile("%s/imgs/%s" % (os.getcwd(), name)):
			mylogger.info("downloading pic ... %s" % name)
			urllib.urlretrieve(url, "%s/imgs/%s" % (os.getcwd(), name))
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

def get_imgs_from_db():
	return [(re.img_path, re.id) for re in db_conn.query(ADVRecord).filter(ADVRecord.img_path!='')]

if __name__ == '__main__':
	get_imgs()
