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
import traceback
from config import *
import Levenshtein

db_conn = new_session()

mylogger = get_logger('adv_game_name_match')


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

def main():
	channel_map = get_channel_map()
	position_map = get_position_type_map()
	with open('adv_games') as f:
		for line in f.readlines():
			try:
				dt,channel_name, position_type, position_name,game_name,author, network, screen, gameplay, theme = line.rstrip().split('\t')
				channel_id = channel_map.get(channel_name)
				position_type_id = position_map.get(position_type)
				adv_game_detail_ids = get_adv_game_detail_id(dt, channel_id, position_type_id, position_name)
				adv_id, source_game_name = get_similarity_name(game_name, adv_game_detail_ids)
				adv_game_summary_id = get_adv_summary_id(game_name)
				#print '****', adv_id,  adv_game_summary_id
				if adv_id != -1 and adv_game_summary_id is not None:
					ins = db_conn.query(ADVGameMap).filter(ADVGameMap.adv_game_summary_id==adv_game_summary_id).filter(ADVGameMap.adv_game_detail_id==adv_id).first()
					if ins is None:
						item = ADVGameMap(**{"adv_game_summary_id": adv_game_summary_id,
											"adv_game_detail_id": adv_id})
						db_conn.merge(item)
						db_conn.commit()
			except Exception,e:
				print traceback.format_exc()

if __name__=="__main__":
	#get_adv_game_summary()
	main()
