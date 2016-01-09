#!/usr/bin/env python
#encoding=utf-8

import requests
import json
import re
from bs4 import BeautifulSoup
from time import sleep
import traceback
from config import *
import random
import xmltodict
import datetime

db_conn = new_session()

from get_game_detail_by_day import mylogger, step3

import random

if __name__ == '__main__':
	step3()
