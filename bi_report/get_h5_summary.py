#!/usr/bin/python
#-*- coding:utf-8 -*-
import pandas as pd
import pandas.io.sql as sql
import datetime
import time
import sys
from define import *

def get_company_id_by_appid(appid):
	db_175_3306.execute("select CompanyID from dc_business_user.dc_games where AppId=\'%s\'" % appid)
	ret = db_175_3306.fetchone()
	return -1 if len(ret) == 0 else ret[0]


def get_game_type_summary():
	game_type_sql = "select b.TypeName, a.SeqNo from  (select SeqNo, Type from dc_business_user.dc_games where Flag='h5' and Name not like '%测试%') a join (select SeqNo, TypeName from dc_business_user.dc_game_type) b on a.Type=b.SeqNo"
	df = sql.read_sql(game_type_sql, conn1)
	gb = df.groupby('TypeName').size()
	for k, v in gb.iteritems():
		print k, v

def get_retain_summary_by_appid(appid, dt, dt2):

	"""
	Front_Appid_dc_retain_by_day_h5（新增留存）/Appid_dc_everyday_h5（新增）
	"""

	df = pd.DataFrame()
	dt = int(time.mktime(time.strptime('%s 00:00:00' % dt, '%Y-%m-%d %H:%M:%S')))
	dt2 = int(time.mktime(time.strptime('%s 00:00:00' % dt2, '%Y-%m-%d %H:%M:%S')))
	company_id = get_company_id_by_appid(appid)
	if company_id != -1:
		_sql = "select a.StatiTime, a.TotalUv, b.RetainedNum_1, if(a.TotalUv>0, round(b.RetainedNum_1/a.TotalUv,2), 0) as retain_rate from (select StatiTime, sum(TotalUv) as TotalUv from dc_%s.%s_dc_everyday_h5 where StatiTime>=%s and StatiTime<=%s and PlayerType=1 group by StatiTime) a join (select StatiTime, sum(RetainedNum_7) as RetainedNum_1 from dc_%s.Front_%s_dc_retain_by_day_h5 where StatiTime>=%s and StatiTime<=%s and PlayerType=1 group by StatiTime) b on a.StatiTime=b.StatiTime" % (company_id, appid, dt, dt2, company_id, appid, dt, dt2)
		print _sql
		if company_id < 382 and company_id!=49:
			df = sql.read_sql(_sql, conn2)
		else:
			df = sql.read_sql(_sql, conn3)
	df['AppId'] = appid
	_datetime = [datetime.date.fromtimestamp(int(i)) for i in df['StatiTime']]
	df['dt'] = _datetime
	return df	
	
def get_retain_summary():
	
	"""
	不同游戏类型留存统计
	"""

	out = pd.DataFrame()
	game_type_sql = "select b.TypeName, a.SeqNo, a.AppId from  (select SeqNo, Type, AppId from dc_business_user.dc_games where Flag='h5' and Name not like '%测试%' limit 3) a join (select SeqNo, TypeName from dc_business_user.dc_game_type) b on a.Type=b.SeqNo"
	df = sql.read_sql(game_type_sql, conn1)
	for appid in df['AppId']:
		retain_df = get_retain_summary_by_appid(appid, '2015-07-01', '2015-07-10')
		out = pd.concat([out, retain_df])
	out = pd.merge(out, df, on="AppId")
	return out

def get_h5_summary_by_appid(appid, dt, dt2):

	"""
	Appid_dc_everyday_h5：TotalPv1/TotalPv(首页跳出率） 
	childNodeCount/parentNodeCount （活跃k系数）
	"""

	out = pd.DataFrame()
	dt = int(time.mktime(time.strptime('%s 00:00:00' % dt, '%Y-%m-%d %H:%M:%S')))
	dt2 = int(time.mktime(time.strptime('%s 00:00:00' % dt2, '%Y-%m-%d %H:%M:%S')))
	company_id = get_company_id_by_appid(appid)
	if company_id != -1:
		_sql = "select StatiTime, sum(TotalPv) as TotalPv,sum(TotalUv) as TotalUv, sum(UniqIP) as UniqIP,sum(TotalSession) as TotalSession, IF(sum(TotalPv)>0, round(sum(TotalPv1)/sum(TotalPv),2), 0) as run_off_rate, IF(sum(ParentNodeCount)>0, round(sum(ChildNodeCount)/sum(ParentNodeCount),2), 0) as active_k_rate from dc_%s.%s_dc_everyday_h5 where PlayerType=2 and StatiTime>=%s and StatiTime<=%s group by StatiTime" % (company_id, appid, dt, dt2)
		print _sql
		if company_id < 382 and company_id!=49:
			out = sql.read_sql(_sql, conn2)
		else:
			out = sql.read_sql(_sql, conn3)
	_datetime = [datetime.date.fromtimestamp(int(i)) for i in out['StatiTime']]
	out['dt'] = _datetime
	out['AppId'] = appid
	return out

def get_h5_summary():
	
	"""
	不同游戏类型留存首页跳出率, 活跃K系数
	"""

	out = pd.DataFrame()
	game_type_sql = "select b.TypeName, a.SeqNo, a.AppId from  (select SeqNo, Type, AppId from dc_business_user.dc_games where Flag='h5' and Name not like '%测试%' limit 3) a join (select SeqNo, TypeName from dc_business_user.dc_game_type) b on a.Type=b.SeqNo"
	df = sql.read_sql(game_type_sql, conn1)
	for appid in df['AppId']:
		h5_df = get_h5_summary_by_appid(appid, '2015-07-01', '2015-07-10')
		out = pd.concat([out, h5_df])
	out = pd.merge(out, df, on="AppId")
	return out

def get_duration_by_appid(appid, dt, dt2):

	"""
	每次游戏时长分布, 每日累计游戏时长分布
	"""

	out = pd.DataFrame()
	dt = int(time.mktime(time.strptime('%s 00:00:00' % dt, '%Y-%m-%d %H:%M:%S')))
	dt2 = int(time.mktime(time.strptime('%s 00:00:00' % dt2, '%Y-%m-%d %H:%M:%S')))
	company_id = get_company_id_by_appid(appid)
	if company_id != -1:
		_sql = "select a.StatiTime, b.new_user_num, a.activet_user_num, a.activet_user_num-b.new_user_num as old_user_num, a.TotalSession, a.cost_per_uv, a.cost_per_sess \
from (select StatiTime, sum(TotalUv) as activet_user_num, sum(TotalSession) as TotalSession,sum(TotalOnlineTime)/sum(TotalUv)/60 as cost_per_uv, \
sum(TotalOnlineTime)/sum(TotalSession)/60 as cost_per_sess from dc_%s.%s_dc_everyday_h5 where PlayerType=2 and StatiTime>=%s and StatiTime<=%s group by StatiTime) a \
join (select StatiTime, sum(TotalUv) as new_user_num from dc_%s.%s_dc_everyday_h5 where PlayerType=1 and StatiTime>=%s and StatiTime<=%s group by StatiTime) b on a.StatiTime=b.StatiTime" % (company_id, appid, dt, dt2, company_id, appid, dt, dt2)
		print _sql
		if company_id < 382 and company_id!=49:
			out = sql.read_sql(_sql, conn2)
		else:
			out = sql.read_sql(_sql, conn3)
	_datetime = [datetime.date.fromtimestamp(int(i)) for i in out['StatiTime']]
	out['dt'] = _datetime
	out['AppId'] = appid
	return out


def get_new_user_summary(appid):
	out = None
	company_id = get_company_id_by_appid(appid)
	if company_id != -1:
		_sql = "select StatiTime, sum(TotalUv), sum(TotalPv),sum(TotalSession),sum(TotalOnlineTime) from dc_%s.%s_dc_everyday_h5 where PlayerType=2 and StatiTime>=1436889600 group by StatiTime" % (company_id, appid)
		#_sql = "select sum(TotalPv),sum(TotalUv),sum(UniqIP),sum(TotalSession),sum(TotalOnlineTime),sum(TotalPv1) from dc_%s.%s_dc_everyday_h5 where PlayerType=1" % (company_id, appid)
		print _sql
		if company_id < 382 and company_id!=49:
			db_171_3307.execute(_sql)
			out = db_171_3307.fetchall()
		else:
			db_175_3307.execute(_sql)
			out = db_175_3307.fetchall()
	return out

def get_promteChannel_summary(appid):
	out = None
	company_id = get_company_id_by_appid(appid)
	print company_id
	if company_id != -1:
		_sql = "select * from dc_%s.%s_dc_distributed_everyday_h5 where StatiTime>=1436889600 limit 1" % (company_id, appid)
		print _sql
		if company_id < 382 and company_id!=49:
			db_171_3307.execute(_sql)
			out = db_171_3307.fetchall()
		else:
			db_175_3307.execute(_sql)
			out = db_175_3307.fetchall()
	return out


def get_device_summary(appid):
	out = None
	company_id = get_company_id_by_appid(appid)
	print "***", company_id
	if company_id != -1:
		_sql = "select a.type, b.vkey, sum(a.value) from (select * from dc_%s.%s_dc_distributed_everyday_h5 where PlayerType=2 and StatiTime=1437321600) a join \
(select * from dc_%s.dc_custom_id_h5) b on a.vkey=b.seqno group by a.type,b.vkey" % (company_id, appid, company_id)
		print _sql
		if company_id < 382 and company_id!=49:
			db_171_3307.execute(_sql)
			out = db_171_3307.fetchall()
		else:
			db_175_3307.execute(_sql)
			out = db_175_3307.fetchall()
	return out


if __name__=="__main__":
	print get_duration_by_appid("5CB577BE32F5C89EF50C84269C30AA07", "2015-07-01", "2015-07-10")
	#print get_h5_summary_by_appid("5CB577BE32F5C89EF50C84269C30AA07", "2015-07-01", "2015-07-10")
	#print get_h5_summary()
	#get_game_type_summary()
	#for i in get_promteChannel_summary("54F1633BA050F951B3A62EFCD234EF2F"):
	#	print i
	#print get_retain_summary()
	#print get_company_id_by_appid('C107EF78DFC4FDD285C1F08F43C551FE')
