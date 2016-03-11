#!/usr/bin/env python
# -*- coding: utf-8 -*-

#import pyhs2
#
#with pyhs2.connect(host='192.168.1.192', port=10000, authMechanism="PLAIN", user='hive', password='new-password', database='tmp') as h_conn:
#    with h_conn.cursor() as h_cursor:
#        sql = "select count(1) from tmp.temp_cyp_uid_summary_d30"
#        h_cursor.execute(sql)
#        rows = h_cursor.fetchall()
#        for r in rows:
#            print "\t".join(r)
import re
import json
import traceback
from config import *
import Levenshtein
import redis

db_conn = new_session()

mylogger = get_logger('adv_game_name_match')

rc = redis.StrictRedis(host='127.0.0.1', port=6679)  

def get_position_type_map():
	d = {}
	for ret in db_conn.execute("select * from position_type"):
		position_type_id, position_type_name = ret
		d[position_type_name.encode('utf-8')] = position_type_id
	return d
				
def get_channel_map():
	d = {}
	for ret in db_conn.execute("select * from channel"):
		id, name = ret
		d[name.encode('utf-8')] = id
	d['AppStore'] = 35
	return d

def get_adv_game_detail_id(dt, channel_id, position_type_id, position_name):
	out = []
	for ret in db_conn.query(ADVRecord2).filter(ADVRecord2.update_date==dt).filter(ADVRecord2.channel_id==int(channel_id)).filter(ADVRecord2.position_type_id==int(position_type_id)).filter(ADVRecord2.position_name==position_name):
		out.append(ret.adv_game_detail_id)
	return out

def get_adv_game_name(adv_game_detail_id):
	ins = db_conn.query(ADVGameDetail).filter(ADVGameDetail.id==int(adv_game_detail_id)).first()
	if ins is not None:
		name = ins.game_name
		segs = re.split(u'-|（|\(', name)
		return segs[0].encode('utf-8')
	return None

def get_similarity_name(game_name, ids):
	_max = 0
	target_id = -1
	target = ""
	for adv_id in ids:
		source_game_name = get_adv_game_name(adv_id)
		sim = Levenshtein.ratio(source_game_name, game_name)
		if sim >= 1:
			return (adv_id, source_game_name)
		if sim > _max:
			target = source_game_name
			target_id = adv_id
			_max = sim
	return (target_id, target)
	
def get_adv_game_summary():
	with open('adv_games') as f:
		for line in f.readlines():
			dt,channel_name, position_type, position_name,game_name,author, network, screen, gameplay, theme = line.rstrip().split('\t')
			ins = db_conn.query(ADVGameSummary).filter(ADVGameSummary.name==game_name).first()
			if not ins:
				item = ADVGameSummary(**{
										"name": 	game_name,
										"company": 	author,
										"network_type": network,
										"screen_type": screen,
										"gameplay": gameplay,
										"theme": theme,
										})
				db_conn.merge(item)
				db_conn.commit()
	db_conn.commit()

def get_adv_summary_id(game_name):
	ins = db_conn.query(ADVGameSummary).filter(ADVGameSummary.name==game_name).first()
	if ins is not None:
		return ins.id
	return None

def add_adv_game_map(adv_id, adv_game_summary_id):
	ins = db_conn.query(ADVGameMap).filter(ADVGameMap.adv_game_summary_id==adv_game_summary_id).filter(ADVGameMap.adv_game_detail_id==adv_id).first()
	if ins is None:
		mylogger.info("add map \t %s====>%s" % (adv_id, adv_game_summary_id))
		item = ADVGameMap(**{"adv_game_summary_id": adv_game_summary_id,
							"adv_game_detail_id": adv_id})
		db_conn.merge(item)
		db_conn.commit()

def main():
	channel_map = get_channel_map()
	position_map = get_position_type_map()
	with open('adv_games') as f:
		for line in f.readlines()[:10]:
			try:
				dt,channel_name, position_type, position_name,game_name,author, network, screen, gameplay, theme = line.rstrip().split('\t')
				channel_id = channel_map.get(channel_name)
				position_type_id = position_map.get(position_type)
				print line
				print '=====', dt, channel_id, position_type_id, position_name
				adv_game_detail_ids = get_adv_game_detail_id(dt, channel_id, position_type_id, position_name)
				print adv_game_detail_ids
				adv_id, source_game_name = get_similarity_name(game_name, adv_game_detail_ids)
				adv_game_summary_id = get_adv_summary_id(game_name)
				#print '****', adv_id,  adv_game_summary_id
				#if adv_id != -1 and adv_game_summary_id is not None:
				#	add_adv_game_map(adv_id, adv_game_summary_id)
			except Exception,e:
				print traceback.format_exc()
	db_conn.commit()

def add_adv_game_summary():
	with open('adv_record_without_name.txt') as f:
		for line in f.readlines():
			if len(line.rstrip().split('\t')) == 8:
				gid, game_name, network,img_url, author, screen, gameplay, theme = line.rstrip().split('\t')
				ins = db_conn.query(ADVGameSummary).filter(ADVGameSummary.name==game_name).first()
				if ins is None:
					item = ADVGameSummary(**{
											"name": 	game_name,
											"company": 	author,
											"network_type": network,
											"screen_type": screen,
											"gameplay": gameplay,
											"theme": theme,
											})
					db_conn.merge(item)
					db_conn.commit()
	db_conn.commit()


def update_adv_record_without_name():
	#根据人工录入的数据，补充市场推荐位对应的game_name
	with open('/data2/yanpengchen/data_eye/spider/adv_record_without_name.txt') as f:
		for line in f.readlines():
			if len(line.rstrip().split('\t')) == 8:
				gid, game_name, network, img_url, author, screen, gameplay, theme = line.rstrip().split('\t')
				sql = "update adv_game_detail set game_name=\'%s\' where img_url=\'%s\' and game_name=''" % (game_name, img_url)
				db_conn.execute(sql.decode('utf-8'))
	db_conn.commit()


def get_adv_game_img_map():
	d = {}
	for ret in db_conn.execute("select a.id, a.img_url, b.adv_game_summary_id from (select * from adv_game_detail where img_url!='') a join adv_game_map b on a.id=b.adv_game_detail_id"):
		aid, img_url, adv_game_summary_id = ret
		d[img_url] = adv_game_summary_id
	return d
		

def get_adv_game_name_map():
	#别名映射
	d = {}
	for ret in db_conn.execute("select a.game_name, b.adv_game_summary_id from (select * from adv_game_detail where img_url!='') a join adv_game_map b on a.id=b.adv_game_detail_id"):
		game_name, adv_game_summary_id = ret
		d[game_name] = adv_game_summary_id
	return d
		

def add_adv_record_map_by_img_url():
	img_map = get_adv_game_img_map()
	for ret in db_conn.execute("select a.id, a.img_url from adv_game_detail a left join adv_game_map b on a.id=b.adv_game_detail_id where b.adv_game_detail_id is null;"):
		adv_id, img_url = ret
		adv_game_summary_id = img_map.get(img_url)
		if adv_game_summary_id is not None:
			#print adv_id, img_url, img_map.get(img_url), '***'
			mylogger.info("ADD BY img_url : %s\t %s" % (adv_id, adv_game_summary_id))
			add_adv_game_map(adv_id, adv_game_summary_id)

sys.path.append('/data2/yanpengchen/winterfall/eleme_search')
from dataeye_search import _search


def add_adv_record_map_by_game_name():
	#join 关联名称相同的adv_record
	count = 0
	for ret in db_conn.execute("select a.id, b.id as adv_game_summary_id from adv_game_detail a join adv_game_summary b on a.game_name=b.name;"):
		adv_id, adv_game_summary_id = ret
		add_adv_game_map(adv_id, adv_game_summary_id)
		count += 1
	mylogger.info("ADD BY join : totle\t %s" % (count))

def add_adv_record_map_by_alias():
	alias_map = get_adv_game_name_map()
	for ret in db_conn.execute("select a.id, a.game_name from (select * from adv_game_detail where game_name!='') a left join adv_game_map b on a.id=b.adv_game_detail_id where b.adv_game_detail_id is null;"):
		adv_id, game_name = ret
		if alias_map.get(game_name) is not None:
			#print adv_id, game_name
			adv_game_summary_id = alias_map.get(game_name)
			mylogger.info("ADD BY alias : %s\t %s" % (adv_id, adv_game_summary_id))
			add_adv_game_map(adv_id, adv_game_summary_id)

def add_adv_record_map_by_es():
	#通过es，搜索相似
	for ret in db_conn.execute("select a.id, a.game_name from (select * from adv_game_detail where game_name!='') a left join adv_game_map b on a.id=b.adv_game_detail_id where b.adv_game_detail_id is null;"):
		adv_id, keyword = ret
		m = re.search(u"《([\u4e00-\u9fa5]+)》", keyword)
		if m is not None:
			q = m.group(1)
		elif len(re.split(u"\S*-\S*|（|\(", keyword)) >= 2:
			q = re.split(u"\s*-\s*", keyword)[0]
		else:
			q = keyword
		for rs in _search(keyword=q, length=5)['data']:
			if rs['ratio'] >= 1:
				adv_game_summary_id = rs['id']
				mylogger.info("ADD BY es : %s\t %s" % (adv_id, adv_game_summary_id))
				add_adv_game_map(adv_id, adv_game_summary_id)
				break

def get_uncheck_to_rc():
	target = []
	for ret in db_conn.execute("select a.id, a.game_name from (select * from adv_game_detail where game_name!='') a left join adv_game_map b on a.id=b.adv_game_detail_id where b.adv_game_detail_id is null;"):
		adv_id, name = ret
		target.append({"adv_id": adv_id, "game_name": name})
	rc.set("uncheck_adv_game", json.dumps(target))

def tt():
	with open('dc_game_theme') as f:
		lines = f.readlines()
		for i in xrange(0, len(lines), 2):
			title, code = lines[i:i+2]
			m = re.search('\d+', code)
			if m is not None:
				title = title.rstrip()
				tid = m.group()
				sql = "insert into dc_game_theme (id, theme) values (\'%s\', \'%s\')" % (tid, title)
				db_conn.execute(sql.decode('utf-8'))
			
	db_conn.commit()

if __name__=="__main__":
	#get_uncheck_to_rc()
	#add_adv_record_map_by_es()
	pass
