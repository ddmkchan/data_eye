#!/usr/bin/python
#-*- coding:utf-8 -*-
import MySQLdb

#dc_business_user
conn1 = MySQLdb.connect(host="192.168.1.175",port=3306,user="dbuser",passwd="user#2013!",charset="utf8")
#companyid < 382 and companyid !=49
conn2 = MySQLdb.connect(host="192.168.1.171",port=3307,user="dbuser",passwd="user#2013!",charset="utf8")
conn3 = MySQLdb.connect(host="192.168.1.175",port=3307,user="dbuser",passwd="user#2013!",charset="utf8")

db_175_3306 = conn1.cursor()
db_171_3306 = conn2.cursor()
db_175_3307 = conn3.cursor()

