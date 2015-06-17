#!usr/bin/env python
#-*- coding:utf-8 -*-

import sys
sys.path.append('/home/cyp/Utils/common')
from define import *
from model import *
import re
import traceback
import json

db_conn = new_session()

import mmseg

mmseg.Dictionary.load_dictionaries()


if __name__ == '__main__':
	for i in mmseg.Algorithm('未暂存以备提交的变更'):
		print i
