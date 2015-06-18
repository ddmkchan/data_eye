#!usr/bin/env python
#-*- coding:utf-8 -*-

import sys
sys.path.append('/home/cyp/Utils/common')
from define import *
from model import *
import re
import traceback
import json

db_conn = new_session()

import mmseg

mmseg.Dictionary.load_dictionaries()
mmseg.Dictionary.load_words('word.dict')

def get_word_dict():
	with open('custom.dict') as f:
		return [line.rstrip() for line in f.readlines()]


if __name__ == '__main__':
	#for i in mmseg.Algorithm('森碟奥莉kimi暂存以备天天提交的变更'):
	#	print i
	#mydict = {}
	#for ret in db_conn.query(IQIYI_TV_COMMENTS).filter(IQIYI_TV_COMMENTS.tv_name=='爸爸回来了').all():
	#	print "-------", ret.comment
	#	for k in mmseg.Algorithm(ret.comment.encode('utf-8')):
	#		print k
	#	for w in mmseg.Algorithm(ret.comment.encode('utf-8')):
	#		print w, '****'
	#		w = w.decode('utf-8')
	#		if len(w) >= 2:
	#			mydict[w] = mydict[w]+1 if w in mydict else 1
	#print mydict

	for w in get_word_dict():
		print "%s\t%s" %(w, len(w.decode('utf-8')))
