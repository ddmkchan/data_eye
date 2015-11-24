#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

PTPQ_DB_HOST = '127.0.0.1'
PTPQ_DB_PORT = '3306'
PTPQ_DB_USER = 'root'
PTPQ_DB_PASS = 'admin'
PTPQ_DB_NAME = 'dataeye'

PTPQ_ENGINE = create_engine(
    'mysql+mysqldb://%s:%s@%s:%s/%s?charset=utf8' % (
    #'mysql+mysqldb://%s:%s@%s:%s/%s?charset=utf8' % (
        PTPQ_DB_USER,
        PTPQ_DB_PASS,
        PTPQ_DB_HOST,
        PTPQ_DB_PORT,
        PTPQ_DB_NAME
    ),
    echo=False,
    pool_recycle=14400,
)

def new_session():
    return scoped_session(sessionmaker(bind=PTPQ_ENGINE, autoflush=True))

session = new_session()

def createtable(model, engine):
    try:
        pass
        model.__table__.drop(engine)
    except:
        pass
    model.__table__.create(engine)


