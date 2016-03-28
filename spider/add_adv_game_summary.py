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

from get_adv_game_match import *

def get_dc_game_theme_map():
	d = {}
	for ret in db_conn.execute(u"select * from dc_game_theme"):
		gid, name = ret
		d[name] = gid
	return d
				
def get_gameplay_map():
	d = {}
	for ret in db_conn.execute(u"select id, typeName from dc_game_type where detailType=0;"):
		id, name = ret
		d[name] = id
	return d

network_type_map = {
					u"单机"	:	1,
					u"网游"	:	2}

screen_type_map = {
					"2D"	: 1,
					"3D"	: 2}

gameplay_map = get_gameplay_map()

theme_map = get_dc_game_theme_map()

def add_adv_record_summary():
	count = 0
	for ret in db_conn.execute("select a.id, c.company, c.network_type, c.screen_type, c.gameplay, c.theme from (select * from adv_game_detail where net_type_id=-1) a join adv_game_map b on a.id=b.adv_game_detail_id join adv_game_summary c on b.adv_game_summary_id=c.id"):
		adv_game_id, company, network_type, screen_type, gameplay, theme = ret
		gameplay = re.split(u'-[\u4e00-\u9fa5]+', gameplay)[0]
		
		network_type_id = network_type_map.get(network_type, -1)
		screen_type_id = screen_type_map.get(screen_type, -1)
		gameplay_id = gameplay_map.get(gameplay, -1)
		theme_id = theme_map.get(theme, -1)
		ins = db_conn.query(ADVGameDetail).filter(ADVGameDetail.id==adv_game_id).first()
		if ins is not None:
			ins.dc_game_type_id = gameplay_id
			ins.net_type_id = network_type_id
			ins.game_theme_id = theme_id
			ins.frame_theme_id = screen_type_id
			ins.game_developer = company
			ins.last_update = datetime.now()
			count += 1
			if count % 1000 == 0:
				mylogger.info("%s commit!" % count)
				db_conn.commit()
	mylogger.info("%s commit!" % count)
	db_conn.commit()

def add_new_adv_game_summary():
	_dict = {}
	for ret in db_conn.execute("select * from games_advgamesummary"):
		gid, name, prefix, company, network_type, screen_type, gameplay, theme = ret
		if gid >= 1333:
			ins = db_conn.execute(u"select * from adv_game_summary where name=\'%s\'" % name).first()
			if ins is None:
				#print gid, name, prefix, company, network_type, screen_type, gameplay, theme
				item = ADVGameSummary(**{
										"name" 			: name,
										"company"		: company,
										"network_type"	: network_type,
										"screen_type"	: screen_type,
										"gameplay"		: gameplay,
										"theme"			: theme,
										})
				#print gid, name
				db_conn.add(item)
				db_conn.commit()
				_dict[str(gid)] = item.id
				print gid, item.id
			else:
				_dict[str(gid)] = ins.id
				print gid, name, '****', ins.id
	rc.set("id_map", json.dumps(_dict))

def get_adv_to_game():
	id_map = json.loads(rc.get('id_map'))
	for ret in db_conn.execute("select adv_game_id, game_summary_id from games_advtogame"):
		adv_id, game_summary_id = ret
		if game_summary_id > 1333:
			adv_game_summary_id = id_map.get(str(game_summary_id))
			print adv_id, game_summary_id, '----->',  adv_game_summary_id
			add_adv_game_map(adv_id, adv_game_summary_id)
		elif game_summary_id < 1333:
			print adv_id, game_summary_id
			add_adv_game_map(adv_id, game_summary_id)

if __name__=="__main__":
	update_adv_record_without_name()
	add_adv_record_map_by_game_name()
	add_adv_record_map_by_alias()
	add_adv_record_map_by_img_url()
	#add_adv_record_map_by_es()
	add_adv_record_summary()
	#add_new_adv_game_summary()
	#get_adv_to_game()
