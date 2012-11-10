#!/usr/bin/env python
#
#
import sys
from xmlrpc.client import ServerProxy, Error

rpc_key = 'dd32f3999b03b5b3db78b3a75c7e3f91f256d9bb'

def lookup(upc):
    itemsOfInterest = []
    s = ServerProxy('http://www.upcdatabase.com/xmlrpc')
    params = { 'rpc_key': rpc_key, 'upc': upc }
    upc_data = s.lookup(params)
    if upc_data['status'] == "success" and upc_data['found']:
        if 'description' in upc_data:
            if upc_data['description'] != '':
                itemsOfInterest.append(('description', upc_data['description']));
        if 'size' in upc_data:
            if upc_data['size'] != '':
                itemsOfInterest.append(('size', upc_data['size']))
        itemsOfInterest.append(('status', upc_data['status']))
        itemsOfInterest.append(('found', upc_data['found']))
        itemsOfInterest = dict(itemsOfInterest)
        itemsOfInterest['price'] = 0 #get price from database here
        return itemsOfInterest
    else:
        return upc_data
