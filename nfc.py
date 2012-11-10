import sys
from ctypes import *

def getRFID(timeout):
  libnfc = cdll.LoadLibrary("./libnfc-1.6.0-rc1/libnfc/.libs/libnfc.so")

  NMT_ISO14443A     = c_int(1)
  NMT_JEWEL         = c_int(2)
  NMT_ISO14443B     = c_int(3)
  NMT_ISO14443BI    = c_int(4)
  NMT_ISO14443B2SR  = c_int(5)
  NMT_ISO14443B2CT  = c_int(6)
  NMT_FELICA        = c_int(7)
  NMT_DEP           = c_int(8)

  NBR_UNDEFINED     = c_int(0)
  NBR_106           = c_int(1)
  NBR_212           = c_int(2)
  NBR_424           = c_int(3)
  NBR_847           = c_int(4)

  NDM_UNDEFINED = c_int(0)
  NDM_PASSIVE = c_int(1)
  NDM_ACTIVE = c_int(2)

  class nfc_modulation(Structure):
    _fields_ = [("nmt", c_int),
                ("nbr", c_int)]

  class nfc_dep_info(Structure):
    _fields_ = [("abtNFCID3", c_uint8 * 10),
                ("btDID", c_uint8),
                ("btBS", c_uint8),
                ("btBR", c_uint8),
                ("btTO", c_uint8),
                ("btPP", c_uint8),
                ("abtGB", c_uint8 * 48),
                ("szGB", c_size_t),
                ("ndm", c_int)]

  class nfc_iso14443a_info(LittleEndianStructure):
    _pack_ = 1
    _fields_ = [("abtAtqa", c_uint8 * 2),
                ("btSak", c_uint8),
                ("szUidLen", c_size_t),
                ("abtUid", c_uint8 * 10),
                ("szAtsLen", c_size_t),
                ("abtAts", c_uint8 * 254)]

  class nfc_felica_info(Structure):
    _fields_ = [("szLen", c_size_t),
                ("btResCode", c_uint8),
                ("abtId", c_uint8 * 8),
                ("abtPad", c_uint8 * 8),
                ("abtSysCode", c_uint8 * 2)]

  class nfc_iso14443b_info(Structure):
    _fields_ = [("abtPupi", c_uint8 * 4),
                ("abtApplicationData", c_uint8 * 4),
                ("abtProtocolInfo", c_uint8 * 3),
                ("ui8CardIdentifier", c_uint8)]

  class nfc_iso14443bi_info(Structure):
    _fields_ = [("abtDIV", c_uint8 * 4),
                ("btVerLog", c_uint8),
                ("btConfig", c_uint8),
                ("szAtrLen", c_size_t),
                ("abtAtr", c_uint8 * 33)]

  class nfc_iso14443b2sr_info(Structure):
    _fields_ = [("abtUID", c_uint8 * 8)]

  class nfc_iso14443b2ct_info(Structure):
    _fields_ = [("abtUID", c_uint8 * 4),
                ("btProdCode", c_uint8),
                ("btFabCode", c_uint8)]

  class nfc_jewel_info(Structure):
    _fields_ = [("btSensRes", c_uint8 * 2),
                ("btId", c_uint8 * 4)]

  class nfc_target_info(Union):
    _fields_ = [("nai", nfc_iso14443a_info),
                ("nfi", nfc_felica_info),
                ("nbi", nfc_iso14443b_info),
                ("nii", nfc_iso14443bi_info),
                ("nsi", nfc_iso14443b2sr_info),
                ("nci", nfc_iso14443b2ct_info),
                ("nji", nfc_jewel_info),
                ("ndi", nfc_dep_info)]

  class nfc_target(Structure):
    _fields_ = [("nti", nfc_target_info),
                ("nm", nfc_modulation)]

  uiPollNr = c_uint8(timeout)
  uiPeriod = c_uint8(2)
  szModulations = c_size_t(1)
  nmModulations = (nfc_modulation * 5)()

  nmModulations[0].nmt = NMT_ISO14443A
  nmModulations[0].nbr = NBR_106
  '''
  nmModulations[1].nmt = NMT_ISO14443B
  nmModulations[1].nbr = NBR_106

  nmModulations[2].nmt = NMT_FELICA
  nmModulations[2].nbr = NBR_212

  nmModulations[3].nmt = NMT_FELICA
  nmModulations[3].nbr = NBR_424

  nmModulations[4].nmt = NMT_JEWEL
  nmModulations[4].nbr = NBR_106
  '''
  nt = nfc_target()

  libnfc.nfc_init(0)

  pnd = libnfc.nfc_open(0, 0)

  if pnd == 0:
    return None

  if libnfc.nfc_initiator_init(pnd) < 0:
    return None

  res = libnfc.nfc_initiator_poll_target (pnd, nmModulations, szModulations,
                                          uiPollNr, uiPeriod, byref(nt))  

  if (res > 0):
    a = nt.nti.nai

    retval = 0
    for i in range(a.szUidLen):
      retval <<= 8
      retval |= a.abtUid[i]
    return retval
