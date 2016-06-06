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

def load2(file):
	try:
		path = os.path.abspath(file)
		with open(path, "rb") as f:
 			binary = f.read()
			return binary
			offset, = _unpack_N(binary[:4])
			index = binary[4:offset]
	except Exception as ex:
		print "cannot open file %s" % file
		print ex.message
		exit(0)

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

def func():
	IPX.load(os.path.abspath("mydata4vipday2_160217.datx"))
	count = 0
	with open('ip_160217') as f:
		for line in f.readlines()[:]:
			segs = line.rstrip().split('\t')
			try:
				new_addr = IP.find(segs[0]).split()
				if len(new_addr) == 4:
			#print segs[0], "****", IP.find(segs[0])
					segs.append(new_addr[2].encode('utf-8'))
					m = "1" if  new_addr[2].encode('utf-8')==segs[1] else "0"
					if m == "0":
						#print len(segs), line
						count+=1
						print segs[0], segs[1], IPX.find(segs[0]).split()[2]
					segs.append(m)
					#print "\t".join(segs)
			except Exception,e:
				pass
	print count


if __name__=="__main__":
	#IPX.load(os.path.abspath("mydata4vipday2.datx"))
	#main()
	#print IPX.find("36.100.222.222")
	func()
