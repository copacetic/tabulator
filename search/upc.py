#!/usr/bin/env python
#

import sys
from xmlrpc.client import ServerProxy, Error
from search import google_guesser
import data.simple_text_db as db

SPRITE_UPC = "049000001327"
RPC_KEY = 'dd32f3999b03b5b3db78b3a75c7e3f91f256d9bb'

def lookup(upc):
    #For demo purposes only we have a special check here to see if it is
    #sprite. If it is, we use google scraping to guess.
    values = db.get_record(0,upc)
    itemsOfInterest = []
    if values != None:
        itemsOfInterest.append(('description', values[0]))
        itemsOfInterest.append(('status', 'success'))
        itemsOfInterest.append(('found', True))
        itemsOfInterest.append(('size', values[1]))
        itemsOfInterest.append(('price', values[2]))
        return dict(itemsOfInterest)

    if upc != SPRITE_UPC:
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
            db.add_product(upc, itemsOfInterest['description'],
                    itemsOfInterest['size'], itemsOfInterest['price'])
            return itemsOfInterest
        elif upc_data['status'] != "success":
            return upc_data
    res = google_guesser.guess(upc)
    if res == None:
        return None
    itemsOfInterest.append(('description', res))
    itemsOfInterest.append(('status', 'success'))
    itemsOfInterest.append(('found', True))
    itemsOfInterest.append(('price', 0))
    itemsOfInterest.append(('size','Not found'))
    answer = dict(itemsOfInterest)
    db.add_product(upc, answer['description'], answer['size'],
            answer['price'])
    return dict(itemsOfInterest)
