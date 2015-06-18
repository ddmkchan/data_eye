#!/usr/bin/env python
#encoding=utf-8

import sys
sys.path.append('/home/cyp/Utils/common')
from define import *
from model import *
import requests
import traceback
import json
import re
from bs4 import BeautifulSoup
from time import sleep

s = requests.session()

IQIYI_SORT_TYPE = ['hot', 'add_time']


def get_iqiyi_comments(qitanid, page, page_size, tvid):
	try:
		url = "http://api.t.iqiyi.com/qx_api/comment/get_video_comments?aid=%s&categoryid=6&cb=fnsucc&escape=true&need_reply=true&need_total=1&page=%s&page_size=%s&page_size_reply=3&qitan_comment_type=1&qitancallback=fnsucc&sort=add_time&qitanid=%s&tvid=%s" % (qitanid, page, page_size, qitanid, tvid)
		r = s.get(url, timeout=10)
		p = re.compile(u'var\s*?fnsucc=([\s\S]*)')
		m = p.search(r.text.strip())
		if m is not None:
			root = json.loads(m.group(1))
			return root['data']['comments']
	except Exception,e:
		print traceback.format_exc()
	return None
	#for i in root['data']['comments']:
	#		print  i['content']

def get_hunan_comments():
	url = "http://comment.hunantv.com/video_comment/list/?callback=callback&type=hunantv2014&subject_id=1005517&page=2"
	r = s.get(url)
	p = re.compile('callback\(([\s\S]*)\)')
	m = p.search(r.text.strip())
	root = json.loads(m.group(1))
	for i in root['comments']:
		print i['content']

def get_letv_comments(pagesize, page, xid):
	url = "http://api.my.letv.com/vcm/api/list?jsonp=callback&type=video&rows=%s&page=%s&sort=&xid=%s&pid=0" % (pagesize, page, xid)
	r = s.get(url)
	p = re.compile('callback\(([\s\S]*)\)')
	m = p.search(r.text.strip())
	if m is not None:
		root = json.loads(m.group(1))
		return root['data']
	return None

def main():
	count = 0
	for ret in session.execute(u"select tv_name, episode, tvid, qitanid from iqiyi_tv where tv_name='爸爸去哪儿'"):
		tv_name, episode, tvid, qitanid = ret
		print tv_name, episode, tvid, qitanid
		for i in xrange(1, 11):
			try:
				comments = get_iqiyi_comments(qitanid, i, 500, tvid)
				sleep(1.11)
				if comments is not None:
				    for ret in comments:
					    if ret['content']:
						    count += 1
						    item = IQIYI_TV_COMMENTS(**{'comment_id': ret['contentId'], 'comment': ret['content'],
												'tv_name': tv_name, 'episode': episode})
						    session.merge(item)
						    if count % 2000 == 0:
								print "%s commit" % count
								session.commit()
			except Exception,e:
				print traceback.format_exc()
				session.rollback()
	session.commit()

def get_kbqm_comments():
	tv_name = "酷爸俏妈"
	f = open('kbqm')
	soup = BeautifulSoup(f.read().decode('utf-8'))
	_episode = set([])
	for i in soup.find_all("a", class_="album_link"):
		if 'javascript' not in i.get('href'):
			if i.get('title') not in _episode:
				xid = re.search(u'\d+', i.get('href')).group()
				print i.get('title'), xid
				_episode.add(i.get('title'))
				comments = get_letv_comments(500, 1, xid)
				if comments is not None:
					for ret in comments:
						if ret['content']:
							item = LETV_TV_COMMENTS(**{'comment_id': ret['_id'], 'comment': ret['content'],'tv_name': tv_name, 'episode': i.get('title')})
							session.merge(item)
	session.commit()


if __name__ == '__main__':
	#get_iqiyi_comments(20, 500, IQIYI_SORT_TYPE[1], babaqunar_tv_id[1])
	#print get_iqiyi_comments(1155064, 1, 100, 218444100)
	#get_letv_comments(20, 1, 22463310)
	#get_kbqm_comments()
	main()
