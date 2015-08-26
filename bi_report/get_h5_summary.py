#!/usr/bin/python
#-*- coding:utf-8 -*-
import pandas as pd
import pandas.io.sql as sql
import time
import sys
from define import *

def get_company_id_by_appid(appid):
	cursor2.execute("select CompanyID from dc_business_user.dc_games where AppId=\'%s\'" % appid)
	ret = cursor2.fetchall()
	return -1 if len(ret) == 0 else ret[0]

def get_h5_summary(appid):
	company_id = get_company_id_by_appid(appid)
	if company_id != -1:
		_sql = "select StatiTime,sum(TotalPv),sum(TotalUv),sum(UniqIP),sum(TotalSession),sum(TotalOnlineTime),sum(TotalPv1),sum(ParentNodeCount),sum(ChildNodeCount) from %s_dc_EVERYDAY_H5" % appid	


def getData(Appid,D1,D2,PlatForm,kind):

    date1 = int(time.mktime(time.strptime(D1+' 00:00:00', '%Y-%m-%d %H:%M:%S')))
    date2 = int(time.mktime(time.strptime(D2+' 00:00:00', '%Y-%m-%d %H:%M:%S')))
    print date1
    print date2
    ARPUARPPUPayrateDataFrame = pd.DataFrame()
    ARPUARPPUPayrateDataFrame1 = pd.DataFrame()

    conn1 = MySQLdb.connect(host="192.168.1.171",port=3307,user="dbuser",passwd="user#2013!",charset="utf8")
    conn2 = MySQLdb.connect(host="192.168.1.175",port=3306,user="dbuser",passwd="user#2013!",charset="utf8")
    conn3 = MySQLdb.connect(host="192.168.1.175",port=3307,user="dbuser",passwd="user#2013!",charset="utf8")

    cursor1 = conn1.cursor()
    cursor2 = conn2.cursor()
    cursor3 = conn3.cursor()

    getCompanyidSql = 'select CompanyId from dc_business_user.dc_games where Appid='+`Appid`

    cursor2.execute(getCompanyidSql)
    getcomp = cursor2.fetchall()
    if len(getcomp) != 0:
        for item in getcomp:
            companyid = item[0]
        print companyid
        getSeqnoSql = 'select seqno from dc_'+str(companyid)+'.dc_custom_id where Vkey='+"'_ALL_GS'"+'and PlatFormType='+str(PlatForm)+' and Appid='+`Appid`
        if companyid < 382 and companyid !=49:
            cursor1.execute(getSeqnoSql)
            getSeqno = cursor1.fetchall()
        else:
            cursor3.execute(getSeqnoSql)
            getSeqno = cursor3.fetchall()
        if len(getSeqno) != 0:
            for item in getSeqno:
                seqno = item[0]
            print seqno
            for item in xrange(date1,date2+86400,86400):
                print item
                getARPUARPPUPayrateSql = 'select distinct StatiTime,vkey,sum(value) from  dc_'+str(companyid)+'.'+Appid+'_dc_distributed_everyday where GameRegionID='+str(seqno)+' and PlatFormType='+str(PlatForm)+' and type='+kind+' and PlayerType=2 and StatiTime='+str(item)+' group by statitime,vkey'
                print getARPUARPPUPayrateSql
                if companyid < 382 and companyid !=49:
                    getARPUARPPUPayrateDataFrame = sql.read_sql(getARPUARPPUPayrateSql,conn1)
                else:
                    getARPUARPPUPayrateDataFrame = sql.read_sql(getARPUARPPUPayrateSql,conn3)
                print len(getARPUARPPUPayrateDataFrame);
                if len(getARPUARPPUPayrateDataFrame) != 0:

                    getARPUARPPUPayrateDataFrame['Appid'] = Appid
                    print getARPUARPPUPayrateDataFrame
                    ARPUARPPUPayrateDataFrame = pd.concat([ARPUARPPUPayrateDataFrame,getARPUARPPUPayrateDataFrame])
                    print ARPUARPPUPayrateDataFrame   
            ARPUARPPUPayrateDataFrame1 = pd.concat([ARPUARPPUPayrateDataFrame1,ARPUARPPUPayrateDataFrame]) 
            print ARPUARPPUPayrateDataFrame1
        return ARPUARPPUPayrateDataFrame1

fileName = raw_input('Input the name of csv:')
appidFrame = pd.read_csv(fileName+'.csv')
platform = input('iOS:1 Android:2')
startDate = raw_input('Input startdate:')
endDate = raw_input('Input enddate:')
tmpDataFrame = pd.DataFrame()
kind=raw_input('Input the kind of Dis:')
for item in appidFrame['Appid']:
    print item
    if isinstance(getData(item,startDate,endDate,platform,kind),pd.core.frame.DataFrame):
        tmpDataFrame = pd.concat([tmpDataFrame,getData(item,startDate,endDate,platform,kind)])
print tmpDataFrame
ARPUARPPUPayrateData = tmpDataFrame
print ARPUARPPUPayrateData
ARPUARPPUPayrateData.to_csv(fileName+'PayrateDisCT.csv')
