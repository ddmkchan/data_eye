#!/usr/bin/python
#-*- coding:utf-8 -*-
import pandas as pd
import pandas.io.sql as sql
import datetime
import time
import sys
from define import *
from get_logger import *
import traceback

mylogger = get_logger('h5_report')

def get_id_map():
    id_map = {}
    with open('de_app') as f:
        for line in f.readlines():
            company_id, appid, server_id = line.rstrip().split('\t')
            if server_id in ['206', '208']:
                conn = conn1 if server_id == '206' else conn2
                id_map[appid] = (company_id, conn)
    return id_map

def get_game_type_summary():
    d = {'appid':[], 'typename':[]}
    for line in open('h5_apps').readlines():
        appid, typename = line.rstrip().split('\t')
        d['appid'].append(appid)
        d['typename'].append(typename)
    df = pd.DataFrame(d)
    gb = df.groupby('typename').size()
    for k, v in gb.iteritems():
        print k, v

def get_h5_summary_by_appid(company_id, appid, typename, start_date, end_date, conn):

    """
    Appid_dc_everyday_h5：TotalPv1/TotalPv(首页跳出率） 
    childNodeCount/parentNodeCount （活跃k系数）
    """
    df = pd.DataFrame()
    _sql = "select StatiTime, sum(TotalPv) as TotalPv,sum(TotalUv) as TotalUv, sum(UniqIP) as UniqIP, \
    sum(TotalSession) as TotalSession, IF(sum(TotalPv)>0, round(sum(TotalPv1)/sum(TotalPv),4), 0) as run_off_rate, \
    IF(sum(ParentNodeCount)>0, round(sum(ChildNodeCount)/sum(ParentNodeCount), 4), 0) as active_k_rate \
    from dc_%s.%s_dc_everyday_h5 where PlayerType=2 and StatiTime>=%s and StatiTime<=%s \
    group by StatiTime" % (company_id, appid, start_date, end_date)
    df = sql.read_sql(_sql, conn)
    df['AppId'] = appid
    df['TypeName'] = typename
    dt = [datetime.date.fromtimestamp(int(i)) for i in df['StatiTime']]
    df['dt'] = dt
    del df['StatiTime']
    return df

def get_duration_by_appid(company_id, appid, typename, start_date, end_date, conn):

    """
    对应活跃用户页面
    每次游戏时长分布, 每日累计游戏时长分布
    """

    df = pd.DataFrame()
    _sql = "select a.StatiTime, b.new_user_num, a.activet_user_num, a.activet_user_num-b.new_user_num as old_user_num, a.TotalSession, a.cost_per_uv, a.cost_per_sess \
    from (select StatiTime, sum(TotalUv) as activet_user_num, sum(TotalSession) as TotalSession,sum(TotalOnlineTime)/sum(TotalUv)/60 as cost_per_uv, \
    sum(TotalOnlineTime)/sum(TotalSession)/60 as cost_per_sess from dc_%s.%s_dc_everyday_h5 where PlayerType=2 and StatiTime>=%s and StatiTime<=%s group by StatiTime) a \
    join (select StatiTime, sum(TotalUv) as new_user_num from dc_%s.%s_dc_everyday_h5 where PlayerType=1 and StatiTime>=%s and StatiTime<=%s group by StatiTime) b on a.StatiTime=b.StatiTime" % (company_id, appid, start_date, end_date, company_id, appid, start_date, end_date)
    df = sql.read_sql(_sql, conn)
    df['AppId'] = appid
    df['TypeName'] = typename
    dt = [datetime.date.fromtimestamp(int(i)) for i in df['StatiTime']]
    df['dt'] = dt
    del df['StatiTime']
    return df


def get_payamount_by_appid(company_id, appid, typename, start_date, end_date, conn):
    
    """
    每日付费率, 
    Appid_dc_payment_by_day_h5中的PayNum;
    活跃是Appid_dc_everyday_h5中的TotalUv
    ARPPU
    """

    df = pd.DataFrame()
    _sql = "select a.*, b.TotalUv, a.PayNum/b.TotalUv as payment_rate, a.PayAmount/a.PayNum as arppu \
    from (select StatiTime, PayAmount, PayTimes, PayNum from dc_%s.%s_dc_payment_by_day_h5 \
    where StatiTime>=%s and StatiTime<=%s) a join (select StatiTime, sum(TotalUv) as TotalUv \
    from dc_%s.%s_dc_everyday_h5 where PlayerType=2 and StatiTime>=%s and StatiTime<=%s group by StatiTime) b on a.StatiTime=b.StatiTime" % (company_id, appid, start_date, end_date, company_id, appid, start_date, end_date)
    df = sql.read_sql(_sql, conn)
    df['AppId'] = appid
    df['TypeName'] = typename
    dt = [datetime.date.fromtimestamp(int(i)) for i in df['StatiTime']]
    df['dt'] = dt
    del df['StatiTime']
    return df


def get_retain_summary_by_appid(company_id, appid, typename, start_date, end_date, conn):

    """
    Front_Appid_dc_retain_by_day_h5（新增留存）/Appid_dc_everyday_h5（新增）
    """

    df = pd.DataFrame()
    _sql = "select a.StatiTime, if(a.TotalUv>0, round(b.RetainedNum_1/a.TotalUv, 4), 0) as retain_rate_1, if(a.TotalUv>0, round(b.RetainedNum_7/a.TotalUv, 4), 0) as retain_rate_7, if(a.TotalUv>0, round(b.RetainedNum_3/a.TotalUv, 4), 0) as retain_rate_3 from  \
    (select StatiTime, sum(TotalUv) as TotalUv from dc_%s.%s_dc_everyday_h5 where StatiTime>=%s and StatiTime<=%s and PlayerType=1 group by StatiTime) a join \
    (select StatiTime, sum(RetainedNum_1) as RetainedNum_1, sum(RetainedNum_7) as RetainedNum_7, sum(RetainedNum_3) as RetainedNum_3 from dc_%s.Front_%s_dc_retain_by_day_h5 where StatiTime>=%s \
    and StatiTime<=%s and PlayerType=1 group by StatiTime) b on a.StatiTime=b.StatiTime" % (company_id, appid, start_date, end_date, company_id, appid, start_date, end_date)
    df = sql.read_sql(_sql, conn)
    df['TypeName'] = typename
    df['AppId'] = appid
    dt = [datetime.date.fromtimestamp(int(i)) for i in df['StatiTime']]
    df['dt'] = dt
    del df['StatiTime']
    return df

def get_new_user_num_by_appid(company_id, appid, start_date, end_date, conn):
    df = pd.DataFrame()
    _sql = "select StatiTime, PlatformType, sum(num) as total_new_user_num\
                from dc_%s.Front_%s_dc_everyday \
                where StatiTime >= %s  and StatiTime <= %s and PlayerType=1 \
                and GameRegionID in (select Seqno from dc_%s.dc_custom_id where AppID = \'%s\' and type = 2 and vkey = '_ALL_GS') \
                group by StatiTime, PlatformType;"% (company_id, appid, start_date, end_date, company_id, appid)
    df = sql.read_sql(_sql, conn)
    df['appid'] = appid
    return df


def main():
    df = pd.DataFrame()
    start_date = '2015-07-01'
    end_date = '2015-09-30'
    start_date = int(time.mktime(time.strptime('%s 00:00:00' % start_date, '%Y-%m-%d %H:%M:%S')))
    end_date = int(time.mktime(time.strptime('%s 00:00:00' % end_date, '%Y-%m-%d %H:%M:%S')))
    id_map = get_id_map()
    valid_apps = set([j.rstrip() for j in open('valid_apps').readlines()])
    with open('h5_apps') as f:
        for line in f.readlines()[:]:
            appid, typename = line.rstrip().split('\t')
            #appid = "5CB577BE32F5C89EF50C84269C30AA07"
            if appid in id_map and appid in valid_apps:
                company_id, conn = id_map.get(appid)
                mylogger.info("%s\t%s\t%s" % (appid, company_id, conn))
                for dt in range(start_date, end_date, 86400 * 30):
                    try:
                        dt2 = end_date if dt+86400*29 > end_date else dt+86400*29
                        #retain_df = get_retain_summary_by_appid(company_id, appid, typename, dt, dt2, conn)
                        #summary_df = get_h5_summary_by_appid(company_id, appid, typename, dt, dt2, conn)
                        #_df = get_duration_by_appid(company_id, appid, typename, dt, dt2, conn)
                        _df = get_payamount_by_appid(company_id, appid, typename, dt, dt2, conn)
                        df = pd.concat([df, _df])
                        time.sleep(1)
                    except Exception,e:
                        mylogger.error(traceback.format_exc())
    df.to_csv("h5_payamount_day")
    #company_id, conn = id_map.get(appid)
    #retain_df = get_retain_summary_by_appid(company_id, appid, start_date, end_date, conn)
    #print retain_df
    #print get_duration_by_appid(company_id, appid, start_date, end_date, conn)
    #print get_payamount_by_appid(company_id, appid, start_date, end_date, conn)
            
def func():
    payamount_df = pd.read_csv("h5_payamount_day")
    print len(payamount_df)


if __name__=="__main__":
    #main()
    func()

