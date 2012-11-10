#!/usr/bin/env python
#
#

import sys
from xmlrpc.client import ServerProxy, Error

rpc_key = 'dd32f3999b03b5b3db78b3a75c7e3f91f256d9bb'

if __name__=='__main__':
	if len(sys.argv) != 2:
		print('Usage: fetchupc.py <upc>')
		exit
	else:
		s = ServerProxy('http://www.upcdatabase.com/xmlrpc')
		params = { 'rpc_key': rpc_key, 'upc': sys.argv[1] }
		print(s.lookup(params))
