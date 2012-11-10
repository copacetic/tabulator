#!/usr/bin/env python
#
#
import sys
from xmlrpc.client import ServerProxy, Error
import google_guesser

SPRITE_UPC = "049000001327"
RPC_KEY = 'dd32f3999b03b5b3db78b3a75c7e3f91f256d9bb'

def lookup(upc):
    #For demo purposes only we have a special check here to see if it is
    #sprite. If it is, we use google scraping to guess.
    itemsOfInterest = []
    if upc == SPRITE_UPC:
        res = google_guesser.guess(upc)
        if res == None:
            return None
        itemsOfInterest.append(('description', res))
        itemsOfInterest.append(('status', 'success'))
        itemsOfInterest.append(('found', True))
        itemsOfInterest.append(('price', 0))
        itemsOfInterest.append(('size',''))
        return dict(itemsOfInterest)
    else:
        s = ServerProxy('http://www.upcdatabase.com/xmlrpc')
        params = { 'rpc_key': RPC_KEY, 'upc': upc }
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
