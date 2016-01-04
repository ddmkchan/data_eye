#! /usr/bin/env python
#coding=utf-8
from sqlalchemy import MetaData, Column, Integer, String, Float, CHAR
from sqlalchemy import DateTime, func, Unicode, UnicodeText, Boolean, Date, Text, BLOB, Date
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import UniqueConstraint
#from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declared_attr
from datetime import *

Base = declarative_base()


class KC_LIST(Base):

	__tablename__ = 'kc_list'

	id = Column(Integer, primary_key=True, autoincrement=True)
	time = Column(Unicode(50), nullable=False, default=u'')
	title = Column(Unicode(50), nullable=False, default=u'')
	title2 = Column(Unicode(50), nullable=False, default=u'')
	img = Column(UnicodeText, nullable=False, default=u'')
	url = Column(Unicode(100), nullable=False, default=u'')
	device = Column(Unicode(50), nullable=False, default=u'')
	publish_status = Column(Unicode(50), nullable=False, default=u'')
	game_type = Column(Unicode(50), nullable=False, default=u'')
	game_id = Column(Unicode(50), nullable=False, default=u'')
	pkg_name = Column(Unicode(200), nullable=False, default=u'')
	popular = Column(Unicode(50), nullable=False, default=u'')
	publish_date = Column(Unicode(50), nullable=False, default=u'')
	source = Column(Integer, nullable=False, default=0)
	status = Column(Integer, nullable=False, default=0)
	create_date = Column(DateTime,nullable=False,default=datetime.now())#创建时间
	last_update = Column(DateTime,nullable=False,default=datetime.now())#最后更新时间

class HotGames(Base):
	
	__tablename__ = 'hot_games'
	
	id = Column(Integer, primary_key=True, autoincrement=True)
	name = Column(Unicode(100), nullable=False, default=u'', index=True)
	img = Column(UnicodeText, nullable=False, default=u'')
	download_count = Column(Unicode(50), nullable=False, default=u'')
	size = Column(Unicode(100), nullable=False, default=u'')
	rank = Column(Integer, nullable=False, default=0)
	url = Column(Unicode(100), nullable=False, default=u'')
	identifying = Column(Unicode(500), nullable=False, default=u'')
	status = Column(Integer, nullable=False, default=0)
	game_type = Column(Unicode(50), nullable=False, default=u'')
	popular = Column(Unicode(50), nullable=False, default=u'')
	source = Column(Integer, nullable=False, default=-1, index=True)
	dt = Column(Unicode(100), nullable=False, default=u'')
	create_date = Column(DateTime,nullable=False,default=datetime.now())#创建时间
	last_update = Column(DateTime,nullable=False,default=datetime.now())#最后更新时间


class PageSource(Base):
	
	__tablename__ = 'page_source'
	
	id = Column(Integer, primary_key=True, autoincrement=True)
	url = Column(Unicode(200), nullable=False, default=u'', index=True)
	code = Column(UnicodeText, nullable=False, default=u'')
	source = Column(Integer, nullable=False, default=-1, index=True)
	create_date = Column(DateTime,nullable=False,default=date.today())#创建时间
	last_update = Column(DateTime,nullable=False,default=date.today())#最后更新时间

class GameDetailByDay(Base):
	
	__tablename__ = 'game_detail_by_day'
	
	id = Column(Integer, primary_key=True, autoincrement=True)
	kc_id = Column(Integer, nullable=False, default=0, index=True)
	name = Column(Unicode(100), nullable=False, default=u'', index=True)
	imgs = Column(UnicodeText, nullable=False, default=u'')
	game_type = Column(Unicode(100), nullable=False, default=u'')
	summary = Column(UnicodeText, nullable=False, default=u'')
	download_num = Column(Unicode(50), nullable=False, default=u'')
	comment_num = Column(Unicode(50), nullable=False, default=u'')
	rating = Column(Unicode(50), nullable=False, default=u'')
	rank = Column(Unicode(50), nullable=False, default=u'')
	topic_num_day = Column(Unicode(50), nullable=False, default=u'')
	topic_num_total = Column(Unicode(50), nullable=False, default=u'')
	pkg_size = Column(Unicode(50), nullable=False, default=u'')
	company = Column(Unicode(100), nullable=False, default=u'')
	version = Column(Unicode(100), nullable=False, default=u'')
	author = Column(Unicode(100), nullable=False, default=u'')
	dt = Column(Unicode(100), nullable=False, default=u'')
	update_time = Column(Unicode(100), nullable=False, default=u'')
	create_date = Column(DateTime, nullable=False, default=datetime.now())#创建时间
	last_update = Column(DateTime, nullable=False, default=datetime.now())#最后更新时间

class Course(Base):

    __tablename__ = 'course'

    cid = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Unicode(50), nullable=False, default=u'', info={'comment':'Segregation Code'})
    t = Column(Integer, nullable=False, default=0)



class ProxyList(Base):

	__tablename__ = 'proxy_list'

	id = Column(Integer, primary_key=True, autoincrement=True)
	ip = Column(Unicode(100), nullable=False, default=u'', index=True)
	port = Column(Unicode(20), nullable=False, default=u'', index=True)
	location = Column(Unicode(100), nullable=False, default=u'')
	is_anonymity = Column(Unicode(20), nullable=False, default=u'')
	type = Column(Unicode(20), nullable=False, default=u'')
	status = Column(Integer, nullable=False, default=0)
	check_time = Column(Unicode(100), nullable=False, default=u'')
	create_time = Column(DateTime, nullable=False, default=datetime.now())#创建时间
	last_update = Column(DateTime, nullable=False, default=datetime.now())#最后更新时间


class PublishGame(Base):

	__tablename__ = 'publish_game'

	id = Column(Integer, primary_key=True, autoincrement=True)
	name = Column(Unicode(100), nullable=False, default=u'', index=True)
	logo = Column(Unicode(200), nullable=False, default=u'')
	imgs = Column(UnicodeText, nullable=False, default=u'')
	game_type = Column(Unicode(100), nullable=False, default=u'')
	summary = Column(UnicodeText, nullable=False, default=u'')
	download_num = Column(Unicode(50), nullable=False, default=u'')
	comment_num = Column(Unicode(50), nullable=False, default=u'')
	rating = Column(Unicode(50), nullable=False, default=u'')
	rank = Column(Unicode(50), nullable=False, default=u'')
	topic_num = Column(Unicode(50), nullable=False, default=u'')
	pkg_size = Column(Unicode(50), nullable=False, default=u'')
	version = Column(Unicode(100), nullable=False, default=u'')
	author = Column(Unicode(100), nullable=False, default=u'')
	device = Column(Unicode(100), nullable=False, default=u'')
	publish_status = Column(Unicode(100), nullable=False, default=u'')
	kc_list_ids = Column(UnicodeText, nullable=False, default=u'')
	channels = Column(UnicodeText, nullable=False, default=u'')
	publish_dates = Column(UnicodeText, nullable=False, default=u'')
	dt = Column(Unicode(100), nullable=False, default=u'')
	create_date = Column(DateTime, nullable=False, default=datetime.now())#创建时间
	last_update = Column(DateTime, nullable=False, default=datetime.now())#最后更新时间


class HotGameDetailByDay(Base):
	
	__tablename__ = 'hot_game_detail_by_day'
	
	id = Column(Integer, primary_key=True, autoincrement=True)
	identifying = Column(Unicode(500), nullable=False, default=u'', index=True)
	imgs = Column(UnicodeText, nullable=False, default=u'')
	game_type = Column(Unicode(100), nullable=False, default=u'')
	summary = Column(UnicodeText, nullable=False, default=u'')
	download_num = Column(Unicode(50), nullable=False, default=u'')
	comment_num = Column(Unicode(50), nullable=False, default=u'')
	rating = Column(Unicode(50), nullable=False, default=u'')
	rank = Column(Unicode(50), nullable=False, default=u'')
	download_num_day = Column(Unicode(50), nullable=False, default=u'')
	topic_num_total = Column(Unicode(50), nullable=False, default=u'')
	pkg_size = Column(Unicode(50), nullable=False, default=u'')
	company = Column(Unicode(100), nullable=False, default=u'')
	version = Column(Unicode(100), nullable=False, default=u'')
	author = Column(Unicode(100), nullable=False, default=u'')
	dt = Column(Unicode(100), nullable=False, default=u'', index=True)
	channel = Column(Integer, nullable=False, default=0, index=True)
	status = Column(Integer, nullable=False, default=0)
	update_time = Column(Unicode(100), nullable=False, default=u'')
	create_date = Column(DateTime, nullable=False, default=datetime.now())#创建时间
	last_update = Column(DateTime, nullable=False, default=datetime.now())#最后更新时间

class ChannelToRanking(Base):
	
	__tablename__ = 'channel_to_ranking'#渠道与榜单映射关系
	
	channel_id = Column(Integer, primary_key=True, autoincrement=False)
	ranking_id = Column(Integer, primary_key=True, autoincrement=False)


class Channel(Base):

	__tablename__ = 'channel'

	id = Column(Integer, primary_key=True, autoincrement=False)
	name = Column(Unicode(100), nullable=False, default=u'', index=True)


class RankingChannel(Base):

	__tablename__ = 'ranking_channel'

	id = Column(Integer, primary_key=True, autoincrement=False)
	name = Column(Unicode(100), nullable=False, default=u'', index=True)

class RanklistGame(Base):

	__tablename__ = 'ranklist_game'

	id = Column(Integer, primary_key=True, autoincrement=True)
	name = Column(Unicode(100), nullable=False, default=u'', index=True)
	channel_ids = Column(UnicodeText, nullable=False, default=u'')
	ranklists = Column(UnicodeText, nullable=False, default=u'')
	logo = Column(Unicode(500), nullable=False, default=u'')
	dt = Column(Unicode(100), nullable=False, default=u'', index=True)
	create_date = Column(DateTime, nullable=False, default=datetime.now())#创建时间
	last_update = Column(DateTime, nullable=False, default=datetime.now())#最后更新时间


class RanklistGameDetail(Base):

	__tablename__ = 'ranklist_game_detail'

	id = Column(Integer, primary_key=True, autoincrement=False)
	name = Column(Unicode(100), nullable=False, default=u'', index=True)
	logo = Column(Unicode(200), nullable=False, default=u'')
	imgs = Column(UnicodeText, nullable=False, default=u'')
	game_type = Column(Unicode(100), nullable=False, default=u'')
	summary = Column(UnicodeText, nullable=False, default=u'')
	download_num = Column(Unicode(50), nullable=False, default=u'')
	comment_num = Column(Unicode(50), nullable=False, default=u'')
	rating = Column(Unicode(50), nullable=False, default=u'')
	rank = Column(Unicode(50), nullable=False, default=u'')
	topic_num = Column(Unicode(50), nullable=False, default=u'')
	pkg_size = Column(Unicode(50), nullable=False, default=u'')
	version = Column(Unicode(100), nullable=False, default=u'')
	author = Column(Unicode(100), nullable=False, default=u'')
	device = Column(Unicode(100), nullable=False, default=u'')
	dt = Column(Unicode(100), nullable=False, default=u'')
	create_date = Column(DateTime, nullable=False, default=datetime.now())#创建时间
	last_update = Column(DateTime, nullable=False, default=datetime.now())#最后更新时间



class ADVRecord(Base):

	__tablename__ = 'adv_record'

	id = Column(Integer, primary_key=True, autoincrement=True)
	position_type_id = Column(Integer, nullable=False, default=0)
	channel_id = Column(Integer, nullable=False, default=-1, index=True)
	new_type_id = Column(Integer, nullable=False, default=-1)
	game_type_id = Column(Integer, nullable=False, default=-1)
	game_theme_id = Column(Integer, nullable=False, default=-1)
	frame_theme_id = Column(Integer, nullable=False, default=-1)
	game_name = Column(Unicode(100), nullable=False, default=u'')
	game_developer = Column(Unicode(100), nullable=False, default=u'')
	img_path = Column(Unicode(500), nullable=False, default=u'')
	update_date = Column(Date, nullable=False, default=date.today())
	platform = Column(Unicode(100), nullable=False, default=u'')
	position_name = Column(Unicode(100), nullable=False, default=u'')
	identifying = Column(Unicode(500), nullable=False, default=u'')
	platform = Column(Unicode(100), nullable=False, default=u'')
	create_date = Column(DateTime, nullable=False, default=datetime.now())#创建时间
	last_update = Column(DateTime, nullable=False, default=datetime.now())#最后更新时间

