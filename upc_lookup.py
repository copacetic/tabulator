#!/usr/bin/env python
#
#

import sys
from xmlrpc.client import ServerProxy, Error

rpc_key = 'dd32f3999b03b5b3db78b3a75c7e3f91f256d9bb'

def upc_lookup(upc):
    s = ServerProxy('http://www.upcdatabase.com/xmlrpc')
    params = { 'rpc_key': rpc_key, 'upc': upc }
    return s.lookup(params)

def print_upc_data(upc_data):
    if 'description' in upc_data:
        if upc_data['description'] != '':
            print("Item description: ", upc_data['description'])
    if 'size' in upc_data:
        if upc_data['size'] != '':
            print("Item quantity: ", upc_data['size'])

if __name__=='__main__':
    while True:
        print('Enter a UPC to lookup:')
        scanned_upc = input()
        if scanned_upc == "quit":
            break
        upc_data = upc_lookup(scanned_upc)
        if upc_data['status'] == "success" and upc_data['found']:
            print_upc_data(upc_data)
        else:
            print("Failed to retrieve UPC data from upc database:")
            if 'message' in upc_data:
                print("The reason for failure is: ", upc_data['message'])
        print()
