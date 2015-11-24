#!usr/bGin/env python
#-*- coding:utf-8 -*-

import urllib
import os
import socket
import sys
sys.path.append('/home/cyp/Utils/common')
from define import *
from model import *
from bs4 import BeautifulSoup
import traceback
from get_logger import *
mylogger = get_logger('hot_game')

db_conn = new_session()
import xlsxwriter


def to_excel():
	workbook = xlsxwriter.Workbook('demo.xlsx')
	#worksheet = workbook.add_worksheet(u"百度游戏")
	#bold = workbook.add_format({'bold': True})
	#worksheet.write(0, 0, u'排名', bold)
	#worksheet.write(0, 1, u'游戏名', bold)
	#worksheet.set_column(0, 1, 20)
	#worksheet.write(0, 2, u'ICON', bold)
	#_row = 1
	mydict = {}
	id2source = {
				"0": u"百度游戏",
				"1": u"小米游戏",
				"2": u"360游戏",
				"3": u"9游游戏",
				"4": u"appannie游戏",
				}
	for ret in db_conn.query(HotGames).filter(HotGames.create_date=="2015-09-02").filter(HotGames.source==3):
	#for ret in db_conn.query(HotGames).filter(HotGames.create_date=="2015-09-02"):
		source = id2source.get(str(ret.source))
		if source in mydict:
			mydict[source].append((ret.rank, ret.name, ret.source))
		else:
			mydict[source] = [(ret.rank, ret.name, ret.source)]
	for source_name, d in mydict.iteritems():
		print source_name, len(d)
		worksheet = workbook.add_worksheet(source_name)
		bold = workbook.add_format({'bold': True})
		worksheet.write(0, 0, u'排名', bold)
		worksheet.write(0, 1, u'游戏名', bold)
		worksheet.set_column(0, 1, 20)
		worksheet.write(0, 2, u'ICON', bold)
		_row = 1
	#for ret in db_conn.query(HotGames).filter(HotGames.create_date=="2015-09-02").filter(HotGames.source==0):
		#worksheet.set_row(_row, 50)
		for ret in d:
			try:
				rank, name, source = ret
				worksheet.write(_row, 0, rank)
				worksheet.write(_row, 1, name)
				pic_name = u"/home/cyp/data_eye/spider/pics/%s_%s" % (name, source)
				#pic_name = u"/home/cyp/data_eye/spider/pics/%s_%s" % (name.encode('utf-8'), str(source))
				if source_name == u"360游戏":
					worksheet.insert_image('C%s' % str(_row+1),  pic_name, {'x_scale': 1, 'y_scale': 1})
				else:
					worksheet.insert_image(_row, 2,  pic_name, {'x_offset': 40, 'y_offset': 40})
					#worksheet.insert_image('C%s' % str(_row+1),  pic_name, {'x_scale': 0.4, 'y_scale': 0.3})
				worksheet.set_row(_row, 80)
				_row += 6
			except Exception,e:
				print name, "\n",traceback.format_exc()
	workbook.close()

def check_and_convert():
	from PIL import Image
	for f in os.listdir("/home/cyp/data_eye/spider/pics"):
		im = Image.open("/home/cyp/data_eye/spider/pics/%s" % f)
		if im.format == "GIF":
			print f
			os.rename("/home/cyp/data_eye/spider/pics/%s" % f, "/home/cyp/data_eye/spider/pics/%s_old" % f) 
			im.save("/home/cyp/data_eye/spider/pics/%s.png" % f)
			os.rename("/home/cyp/data_eye/spider/pics/%s.png" % f, "/home/cyp/data_eye/spider/pics/%s" % f) 

if __name__ == '__main__':
	#download_pic()
	to_excel()
	#check_and_convert()
