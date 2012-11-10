import nfc
import barcode
import upc

import os
import time
import threading

IDLE, PRIMED, USED = range(3)
RFID, BARCODE = range(2)


def RFIDThread(s):
  while True:
    rfid = nfc.getRFID(300)
    if rfid != None:
      TransactionState.lock.acquire()
      if s.state == IDLE:
        s.startTransaction(rfid, RFID)
      elif s.state == PRIMED:
        if rfid == s.ID and s.Type == RFID:
          s.reset()
        else:
          s.startTransaction(rfid, RFID)
      elif s.state == USED:
        if rfid == s.ID and s.Type == RFID:
          s.checkout()
        else:
          s.startTransaction(rfid, RFID)
      TransactionState.lock.release()
      time.sleep(1)

def BarcodeThread(s):
  while True:
    code = barcode.scan()
    TransactionState.lock.acquire()
    if s.state == IDLE:
      s.startTransaction(code, BARCODE)
    elif s.state == PRIMED:
      if code == s.ID and s.Type == BARCODE:
        s.reset()
      else:
        s.addTransaction(upc.lookup(code))
    elif s.state == USED:
      if code == s.ID and s.Type == BARCODE:
        s.checkout()
      else:
        s.addTransaction(upc.lookup(code))
    TransactionState.lock.release()

class TransactionState:
  lock = threading.RLock()

  def __init__(self, initialState = IDLE):
    self.state = initialState
    self.ID = None
    self.Type = None
    self.stack = []

  def startTransaction(self, ID, Type):
    self.state = PRIMED
    self.ID = ID
    self.Type = Type
    self.stack = []

  def reset(self):
    self.state = IDLE
    self.ID = None
    self.Type = None

  def addTransaction(self, transaction):
    self.stack.append(transaction)
    self.state = USED

  def checkout(self):
    self.reset()

  def __str__(self):
    retval = str(self.state) + "\n"
    for t in self.stack:
      retval += str(t) + "\n"
    return retval




if __name__ == "__main__":
  state = TransactionState()

  r = threading.Thread(target=RFIDThread, args=[state])
  b = threading.Thread(target=BarcodeThread, args=[state])

  r.daemon = True
  b.daemon = True

  r.start()
  b.start()

  while r.isAlive() and b.isAlive():
    os.system('clear')
    print(state)
    time.sleep(1)
