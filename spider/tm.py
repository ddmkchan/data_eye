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

def main():
	tv = '爸爸去哪儿,爸爸回来了,虎妈猫爸,嘿老头,待嫁老爸,酷爸俏妈'
	for name in tv.split(','):
		print name
		mydict = {}
		for ret in db_conn.query(LETV_TV_COMMENTS).filter(LETV_TV_COMMENTS.tv_name==name).all():
			for w in mmseg.Algorithm(ret.comment.encode('utf-8').lower()):
				w = w.text.decode('utf-8')
				if len(w) >= 2:
					mydict[w] = mydict[w]+1 if w in mydict else 1
		_s = sorted(mydict.iteritems(), key=lambda d:d[1], reverse=True)
		for i in _s[:100]:
			if i[0].encode('utf-8') in get_word_dict():
				print "%s\t%s" % (i[0], i[1])

if __name__ == '__main__':
	#for i in mmseg.Algorithm('森碟嗯哼奥莉kimi暂存以备天天提交的变更'):
	#		print i

	#for w in get_word_dict():
	#	print "%s %s" %(len(w.decode('utf-8')), w)
	main()
