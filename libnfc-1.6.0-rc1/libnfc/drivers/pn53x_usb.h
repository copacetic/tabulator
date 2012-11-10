/**
 * Public platform independent Near Field Communication (NFC) library
 * 
 * Copyright (C) 2009, Roel Verdult
 * Copyright (C) 2011, Romain Tartière
 * 
 * This program is free software: you can redistribute it and/or modify it
 * under the terms of the GNU Lesser General Public License as published by the
 * Free Software Foundation, either version 3 of the License, or (at your
 * option) any later version.
 * 
 * This program is distributed in the hope that it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
 * FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
 * more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>
 * 
 * 
 * @file pn53x_usb.h
 * @brief Drive for PN53x USB devices
 */

#ifndef __NFC_DRIVER_PN53X_USB_H__
#define __NFC_DRIVER_PN53X_USB_H__

#include <sys/time.h>

#include <nfc/nfc-types.h>

#include "nfc-internal.h"

bool    pn53x_usb_probe (nfc_connstring connstrings[], size_t connstrings_len, size_t *pszDeviceFound);
nfc_device *pn53x_usb_open (const nfc_connstring connstring);
int    pn53x_usb_send (nfc_device *pnd, const uint8_t *pbtData, const size_t szData, int timeout);
int    pn53x_usb_receive (nfc_device *pnd, uint8_t *pbtData, const size_t szData, int timeout);
void    pn53x_usb_close (nfc_device *pnd);

extern const struct nfc_driver pn53x_usb_driver;

#endif // ! __NFC_DRIVER_PN53X_USB_H__
