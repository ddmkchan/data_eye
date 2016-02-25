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


def write_to_sheet_from_file(titles, sheet, _file):
	for i in xrange(len(titles.split(','))):
		sheet.write(0, i, titles.split(u',')[i])
	with open(_file) as f:
		lines = f.readlines()
		for j in xrange(len(lines)):
			segs = lines[j].rstrip().decode('utf-8').split(u'\t')
			for k in xrange(len(segs)):
				sheet.write(j+1, k, segs[k])

def to_excel():
	import xlsxwriter
	workbook = xlsxwriter.Workbook('game_value.xlsx')
	bold = workbook.add_format({'bold': True})
	worksheet = workbook.add_worksheet(u"新品游戏榜单概况")
	worksheet2 = workbook.add_worksheet(u"1月新游概况")
	worksheet3 = workbook.add_worksheet(u"1月新游价值")
	worksheet4 = workbook.add_worksheet(u"top300游戏价值")
	titles = u"开测时间,游戏名称,榜单名称,上榜时间,排名,榜单游戏名称,flag"
	titles2 = u"开测时间,游戏名称,渠道名称,日期,下载量,是否上榜（1为上过榜单， 0未上榜）"
	write_to_sheet_from_file(titles, worksheet, 'new_game_to_ranklist')	
	write_to_sheet_from_file(titles2, worksheet2, 'new_game_detail')	
	write_to_sheet_from_file(u"游戏名称,评分,上榜数", worksheet3, 'game_value_new')	
	write_to_sheet_from_file(u"falg,游戏名称,评分,上榜数", worksheet4, 'game_value_top300')	
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
