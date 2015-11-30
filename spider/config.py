#!/usr/bin/env python
#encoding=utf-8

import sys
sys.path.append('/home/cyp/Utils/common')

import socket

localIP = socket.gethostbyname(socket.gethostname())#这个得到本地ip
print localIP
