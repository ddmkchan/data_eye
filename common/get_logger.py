#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import logging
from logging.handlers import RotatingFileHandler

LOG_FILE = "/home/cyp/logs"


#定义一个RotatingFileHandler，最多备份5个日志文件，每个日志文件最大10M
def get_logger(logname):
    Rthandler = RotatingFileHandler('%s/%s.log' % (LOG_FILE, logname), maxBytes=10*1024*1024, backupCount=5)
    formatter = logging.Formatter('%(levelname)s\t%(asctime)-15s\t%(message)s')
    Rthandler.setFormatter(formatter)
    logger = logging.getLogger(logname)
    logger.setLevel(logging.INFO)
    logger.addHandler(Rthandler)
    return logger
