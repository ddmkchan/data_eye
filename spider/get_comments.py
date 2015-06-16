#!/usr/bin/env python
#encoding : utf-8

import requests
import json
import re

s = requests.session()

IQIYI_SORT_TYPE = ['hot', 'add_time']

babaqunar_tv_id = ['373218100', '371481500', '369995300', '367089000', '365672200']

def get_iqiyi_comments(page, page_size, sort, tvid):
	url = "http://api.t.iqiyi.com/qx_api/comment/get_video_comments?aid=11163020&categoryid=6&cb=fnsucc&escape=true&need_reply=true&need_total=1&page=%s&page_size=%s&page_size_reply=3&qitan_comment_type=1&qitancallback=fnsucc&qitanid=11163020&sort=%s&tvid=%s" % (page, page_size, sort, tvid)
	r = s.get(url)
	p = re.compile(u'var\s*?fnsucc=([\s\S]*)')
	m = p.search(r.text.strip())
	root = json.loads(m.group(1))
	for i in root['data']['comments']:
		print  i['content']

def get_hunan_comments():
	url = "http://comment.hunantv.com/video_comment/list/?callback=callback&type=hunantv2014&subject_id=1005517&page=2"
	r = s.get(url)
	p = re.compile('callback\(([\s\S]*)\)')
	m = p.search(r.text.strip())
	root = json.loads(m.group(1))
	for i in root['comments']:
		print i['content']


if __name__ == '__main__':
	get_iqiyi_comments(20, 500, IQIYI_SORT_TYPE[1], babaqunar_tv_id[1])
	#get_hunan_comments()
