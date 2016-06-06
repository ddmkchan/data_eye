# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import os
import time
from ipip import IP
from ipip import IPX
import random

IP.load(os.path.abspath("mydata4vipday2.dat"))


def exeTime(func):
    def newFunc(*args, **args2):
        t0 = time.time()
        print "@%s, {%s} start" % (time.strftime("%X", time.localtime()), func.__name__)
        back = func(*args, **args2)
        print "@%s, {%s} end" % (time.strftime("%X", time.localtime()), func.__name__)
        print "@%.3fs taken for {%s}" % (time.time() - t0, func.__name__)
        return back
    return newFunc


@exeTime
def main():
	with open('ip_wifi.log') as f:
		lines = f.readlines()
		for _ in xrange(len(lines)):
		#for _ in xrange(1000):
			#segs = lines[random.randrange(len(lines))].rstrip().split()
			segs = lines[_].rstrip().split()
			r = IP.find(segs[1])
			segs2 = r.split('\t')
			hits = 1 if segs2[1].encode('utf-8') in segs[3] else 0
			print "%s\t%s\t%s\t%s" % (hits, segs[1], segs[3], r.encode('utf-8'))


import subprocess
import re
import json
import sys
 
import requests
 
 
def get_hops(ip):
    cmd = 'traceroute -nq 1 %s'
    p = subprocess.Popen(cmd % ip, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, universal_newlines=True)
    return p.stdout
 
 
def get_ip(hop):
    p = '.* (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
    m = re.match(p, hop)
    if m:
        return m.group(1)
 
 
def get_city(ip):
    api = 'http://ip.sankuai.com/api/ip/get/%s'
    r = requests.get(api % ip)
    if r.status_code == 200:
        country = json.loads(r.text)['country']
        city = json.loads(r.text)['city']
        return country + ', ' + city
 
 
if __name__ == '__main__':
    #try:
    #    srcip = sys.argv[1]
    #except IndexError:
    #    srcip = '106.38.130.52'
    #hops = get_hops(srcip)
    #for hop in hops:
        #print(ip, city)
	for hop in get_hops("110.185.128.0"):
		ip = get_ip(hop)
		print ip
        #city = get_city(ip)

