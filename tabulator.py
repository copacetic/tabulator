import nfc
import barcode
import upc

import os
import time
import threading

import curses

IDLE, PRIMED, USED, PRICE_CHECK = range(4)
stateStr = [ "IDLE", "PRIMED", "USED", "PRICE_CHECK" ]
RFID, BARCODE = range(2)

undo_card = 1253887727


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
        elif rfid == undo_card:
          s.reset()
        else:
          s.startTransaction(rfid, RFID)
      elif s.state == USED:
        if rfid == s.ID and s.Type == RFID:
          s.checkout()
        elif rfid == undo_card:
          s.undo()
        else:
          s.startTransaction(rfid, RFID)
      TransactionState.lock.release()
      time.sleep(1)

def BarcodeThread(s, mainwin):
  while True:
    code = barcode.scan(mainwin)
    TransactionState.lock.acquire()
    if s.state == IDLE:
      #record = db.get_record(1, code)
      record = None
      if int(code) == 23102492:
        record = (BARCODE, 'Zachary Bush')
      if record != None:
        s.startTransaction(code, BARCODE)
      else: 
        s.priceCheck(upc.lookup(code))
        TransactionState.lock.release()
        time.sleep(3)
        TransactionState.lock.acquire()
        s.reset()
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

  def undo(self):
    self.stack.pop()
    if len(self.stack) == 0:
      self.state = PRIMED

  def priceCheck(self, data):
    self.state = PRICE_CHECK
    self.pc_data = data

  def __str__(self):
    retval = stateStr[self.state]
    if self.ID != None:
      retval += " : "
      retval += str(self.ID)
      retval += " : %d transactions" % len(self.stack)
    return retval

csua_rows = [
' .d8888b.   .d8888b.  888     888       d8888',
'd88P  Y88b d88P  Y88b 888     888      d88888',
'888    888 Y88b.      888     888     d88P888',
'888         "Y888b.   888     888    d88P 888',
'888            "Y88b. 888     888   d88P  888',
'888    888       "888 888     888  d88P   888',
'Y88b  d88P Y88b  d88P Y88b. .d88P d8888888888',
' "Y8888P"   "Y8888P"   "Y88888P" d88P     888'
]

price_check_rows = [
' ######   ######     ###    ##    ##',
'##    ## ##    ##   ## ##   ###   ##',
'##       ##        ##   ##  ####  ##',   
' ######  ##       ##     ## ## ## ##',
'      ## ##       ######### ##  ####',
'##    ## ##    ## ##     ## ##   ###',
' ######   ######  ##     ## ##    ##',
'',
'#### ######## ######## ##       ##',
' ##     ##    ##       ###     ###',
' ##     ##    ##       ####   ####',
' ##     ##    ######   ## ## ## ##',
' ##     ##    ##       ##  ###  ##',
' ##     ##    ##       ##       ##',
'####    ##    ######## ##       ##'
]

login_rows = [
' ######   ######     ###    ##    ##',
'##    ## ##    ##   ## ##   ###   ##',
'##       ##        ##   ##  ####  ##',   
' ######  ##       ##     ## ## ## ##',
'      ## ##       ######### ##  ####',
'##    ## ##    ## ##     ## ##   ###',
' ######   ######  ##     ## ##    ##',
'',
'#### #####   ',
' ##  ##  ### ',
' ##  ##    ##',
' ##  ##    ##',
' ##  ##    ##',
' ##  ##  ### ',
'#### #####   '
]

def graphics(stdscr, state):
  r = threading.Thread(target=RFIDThread, args=[state])
  b = threading.Thread(target=BarcodeThread, args=[state, stdscr])

  r.daemon = True
  b.daemon = True

  r.start()
  b.start()

  height, width = stdscr.getmaxyx()

  topWin = curses.newwin(10, 0)
  leftWin = curses.newwin(height - 11, int(width/2), 10, 0)
  rightWin = curses.newwin(height - 11, int(width/2), 10, int(width/2))
  mainWin = curses.newwin(height - 11, 0, 10, 0)
  statusBar = curses.newwin(1, 0, height - 1, 0)

  topWin.border()
  startrow = 1
  for row in csua_rows:
    startix = int(width / 2 - (len(row) / 2))
    topWin.addstr(startrow, startix, row)
    startrow += 1
  topWin.refresh()

  while r.isAlive() and b.isAlive():
    TransactionState.lock.acquire()
    statusBar.erase()
    statusBar.addstr(0, 0, str(state))
    statusBar.refresh()
    if state.state == IDLE:
      leftWin.erase()
      leftWin.border()

      startrow = 1
      for row in price_check_rows:
        startix = int(width / 4 - (len(row) / 2))
        leftWin.addstr(startrow, startix, row)
        startrow += 1
      t = "For a price check"
      leftWin.addstr(startrow + 1, int(width / 4 - (len(t) / 2)), t)
      leftWin.refresh()

      rightWin.erase()
      rightWin.border()

      startrow = 1
      for row in login_rows:
        startix = int(width / 4 - (len(row) / 2))
        rightWin.addstr(startrow, startix, row)
        startrow += 1
      t = "To begin a transaction"
      rightWin.addstr(startrow + 1, int(width / 4 - (len(t) / 2)), t)
      rightWin.refresh()
      rightWin.refresh()
    elif state.state == PRICE_CHECK:
      mainWin.border()

      mainWin.addstr(1, 1, str(state.pc_data))

      mainWin.refresh()
    else:
      mainWin.border()
      mainWin.refresh()
    TransactionState.lock.release()
    time.sleep(.5)

if __name__ == "__main__":
  state = TransactionState()
  curses.wrapper(graphics, state)
