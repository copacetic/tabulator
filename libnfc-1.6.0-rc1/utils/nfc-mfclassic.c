/*-
 * Public platform independent Near Field Communication (NFC) library examples
 * 
 * Copyright (C) 2009, Roel Verdult
 * Copyright (C) 2010, Romuald Conty, Romain Tartière
 * Copyright (C) 2011, Adam Laurie
 * 
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *  1) Redistributions of source code must retain the above copyright notice,
 *  this list of conditions and the following disclaimer. 
 *  2 )Redistributions in binary form must reproduce the above copyright
 *  notice, this list of conditions and the following disclaimer in the
 *  documentation and/or other materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 * 
 * Note that this license only applies on the examples, NFC library itself is under LGPL
 *
 */

/**
 * @file nfc-mfclassic.c
 * @brief MIFARE Classic manipulation example
 */

#ifdef HAVE_CONFIG_H
#  include "config.h"
#endif // HAVE_CONFIG_H

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#include <string.h>
#include <ctype.h>

#include <nfc/nfc.h>

#include "mifare.h"
#include "nfc-utils.h"

static nfc_device *pnd;
static nfc_target nt;
static mifare_param mp;
static mifare_classic_tag mtKeys;
static mifare_classic_tag mtDump;
static bool bUseKeyA;
static bool bUseKeyFile;
static uint8_t uiBlocks;
static uint8_t keys[] = {
  0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
  0xd3, 0xf7, 0xd3, 0xf7, 0xd3, 0xf7,
  0xa0, 0xa1, 0xa2, 0xa3, 0xa4, 0xa5,
  0xb0, 0xb1, 0xb2, 0xb3, 0xb4, 0xb5,
  0x4d, 0x3a, 0x99, 0xc3, 0x51, 0xdd,
  0x1a, 0x98, 0x2c, 0x7e, 0x45, 0x9a,
  0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0xab, 0xcd, 0xef, 0x12, 0x34, 0x56
};

static const nfc_modulation nmMifare = {
  .nmt = NMT_ISO14443A,
  .nbr = NBR_106,
};

static size_t num_keys = sizeof (keys) / 6;

#define MAX_FRAME_LEN 264

static uint8_t abtRx[MAX_FRAME_LEN];
static int szRxBits;
static size_t szRx = sizeof(abtRx);

uint8_t  abtHalt[4] = { 0x50, 0x00, 0x00, 0x00 };

// special unlock command
uint8_t  abtUnlock1[1] = { 0x40 };
uint8_t  abtUnlock2[1] = { 0x43 };

static  bool
transmit_bits (const uint8_t *pbtTx, const size_t szTxBits)
{
  // Show transmitted command
  printf ("Sent bits:     ");
  print_hex_bits (pbtTx, szTxBits);
  // Transmit the bit frame command, we don't use the arbitrary parity feature
  if ((szRxBits = nfc_initiator_transceive_bits (pnd, pbtTx, szTxBits, NULL, abtRx, NULL)) < 0)
    return false;

  // Show received answer
  printf ("Received bits: ");
  print_hex_bits (abtRx, szRxBits);
  // Succesful transfer
  return true;
}


static  bool
transmit_bytes (const uint8_t *pbtTx, const size_t szTx)
{
  // Show transmitted command
  printf ("Sent bits:     ");
  print_hex (pbtTx, szTx);
  // Transmit the command bytes
  if (nfc_initiator_transceive_bytes (pnd, pbtTx, szTx, abtRx, &szRx, 0) < 0)
    return false;

  // Show received answer
  printf ("Received bits: ");
  print_hex (abtRx, szRx);
  // Succesful transfer
  return true;
}

static void
print_success_or_failure (bool bFailure, uint32_t *uiBlockCounter)
{
  printf ("%c", (bFailure) ? 'x' : '.');
  if (uiBlockCounter && !bFailure)
    *uiBlockCounter += (*uiBlockCounter < 128) ? 4 : 16;
}

static  bool
is_first_block (uint32_t uiBlock)
{
  // Test if we are in the small or big sectors
  if (uiBlock < 128)
    return ((uiBlock) % 4 == 0);
  else
    return ((uiBlock) % 16 == 0);
}

static  bool
is_trailer_block (uint32_t uiBlock)
{
  // Test if we are in the small or big sectors
  if (uiBlock < 128)
    return ((uiBlock + 1) % 4 == 0);
  else
    return ((uiBlock + 1) % 16 == 0);
}

static  uint32_t
get_trailer_block (uint32_t uiFirstBlock)
{
  // Test if we are in the small or big sectors
  uint32_t trailer_block = 0;
  if (uiFirstBlock < 128) {
    trailer_block = uiFirstBlock + (3 - (uiFirstBlock % 4));
  } else {
    trailer_block = uiFirstBlock + (15 - (uiFirstBlock % 16));
  }
  return trailer_block;
}

static  bool
authenticate (uint32_t uiBlock)
{
  mifare_cmd mc;
  uint32_t uiTrailerBlock;
  size_t  key_index;

  // Set the authentication information (uid)
  memcpy (mp.mpa.abtUid, nt.nti.nai.abtUid + nt.nti.nai.szUidLen - 4, 4);

  // Should we use key A or B?
  mc = (bUseKeyA) ? MC_AUTH_A : MC_AUTH_B;

  // Key file authentication.
  if (bUseKeyFile) {

    // Locate the trailer (with the keys) used for this sector
    uiTrailerBlock = get_trailer_block (uiBlock);

    // Extract the right key from dump file
    if (bUseKeyA)
      memcpy (mp.mpa.abtKey, mtKeys.amb[uiTrailerBlock].mbt.abtKeyA, 6);
    else
      memcpy (mp.mpa.abtKey, mtKeys.amb[uiTrailerBlock].mbt.abtKeyB, 6);

    // Try to authenticate for the current sector
    if (nfc_initiator_mifare_cmd (pnd, mc, uiBlock, &mp))
      return true;
  } else {
    // Try to guess the right key
    for (key_index = 0; key_index < num_keys; key_index++) {
      memcpy (mp.mpa.abtKey, keys + (key_index * 6), 6);
      if (nfc_initiator_mifare_cmd (pnd, mc, uiBlock, &mp)) {
        if (bUseKeyA)
          memcpy (mtKeys.amb[uiBlock].mbt.abtKeyA, &mp.mpa.abtKey, 6);
        else
          memcpy (mtKeys.amb[uiBlock].mbt.abtKeyB, &mp.mpa.abtKey, 6);
        return true;
      }
      nfc_initiator_select_passive_target (pnd, nmMifare, nt.nti.nai.abtUid, nt.nti.nai.szUidLen, NULL);
    }
  }

  return false;
}

static bool
unlock_card (void)
{
  printf ("Unlocking card\n");

  // Configure the CRC
  if (nfc_device_set_property_bool (pnd, NP_HANDLE_CRC, false) < 0) {
    nfc_perror (pnd, "nfc_configure");
    exit (EXIT_FAILURE);
  }
  // Use raw send/receive methods
  if (nfc_device_set_property_bool (pnd, NP_EASY_FRAMING, false) < 0) {
    nfc_perror (pnd, "nfc_configure");
    exit (EXIT_FAILURE);
  }

  iso14443a_crc_append(abtHalt, 2);
  transmit_bytes (abtHalt, 4);
  // now send unlock
  if (!transmit_bits (abtUnlock1, 7)) {
    printf("unlock failure!\n");
    return false;
  }
  if (!transmit_bytes (abtUnlock2, 1)) {
    printf("unlock failure!\n");
    return false;
  }

  // reset reader
  // Configure the CRC
  if (nfc_device_set_property_bool (pnd, NP_HANDLE_CRC, true) < 0) {
    nfc_perror (pnd, "nfc_device_set_property_bool");
    exit (EXIT_FAILURE);
  }
  // Switch off raw send/receive methods
  if (nfc_device_set_property_bool (pnd, NP_EASY_FRAMING, true) < 0) {
    nfc_perror (pnd, "nfc_device_set_property_bool");
    exit (EXIT_FAILURE);
  }
  return true;
}

static  bool
read_card (int read_unlocked)
{
  int32_t iBlock;
  bool    bFailure = false;
  uint32_t uiReadBlocks = 0;

  if(read_unlocked)
    if (!unlock_card())
      return false;


  printf ("Reading out %d blocks |", uiBlocks + 1);

  // Read the card from end to begin
  for (iBlock = uiBlocks; iBlock >= 0; iBlock--) {
    // Authenticate everytime we reach a trailer block
    if (is_trailer_block (iBlock)) {
      // Skip this the first time, bFailure it means nothing (yet)
      if (iBlock != uiBlocks)
        print_success_or_failure (bFailure, &uiReadBlocks);

      // Show if the readout went well
      if (bFailure) {
        // When a failure occured we need to redo the anti-collision
        if (nfc_initiator_select_passive_target (pnd, nmMifare, NULL, 0, &nt) < 0) {
          printf ("!\nError: tag was removed\n");
          return false;
        }
        bFailure = false;
      }

      fflush (stdout);

      // Try to authenticate for the current sector
      if (!read_unlocked && !authenticate (iBlock)) {
        printf ("!\nError: authentication failed for block 0x%02x\n", iBlock);
        return false;
      }
      // Try to read out the trailer
      if (nfc_initiator_mifare_cmd (pnd, MC_READ, iBlock, &mp)) {
        if(read_unlocked) {
          memcpy (mtDump.amb[iBlock].mbd.abtData, mp.mpd.abtData, 16);
        } else {
          // Copy the keys over from our key dump and store the retrieved access bits
          memcpy (mtDump.amb[iBlock].mbt.abtKeyA, mtKeys.amb[iBlock].mbt.abtKeyA, 6);
          memcpy (mtDump.amb[iBlock].mbt.abtAccessBits, mp.mpd.abtData + 6, 4);
          memcpy (mtDump.amb[iBlock].mbt.abtKeyB, mtKeys.amb[iBlock].mbt.abtKeyB, 6);
        }
      } else {
        printf ("!\nError: unable to read trailer block 0x%02x\n", iBlock);
      }
    } else {
      // Make sure a earlier readout did not fail
      if (!bFailure) {
        // Try to read out the data block
        if (nfc_initiator_mifare_cmd (pnd, MC_READ, iBlock, &mp)) {
          memcpy (mtDump.amb[iBlock].mbd.abtData, mp.mpd.abtData, 16);
        } else {
          bFailure = true;
          printf ("!\nError: unable to read block 0x%02x\n", iBlock);
          return false;
        }
      }
    }
  }
  print_success_or_failure (bFailure, &uiReadBlocks);
  printf ("|\n");
  printf ("Done, %d of %d blocks read.\n", uiReadBlocks, uiBlocks + 1);
  fflush (stdout);

  return true;
}

static  bool
write_card (int write_block_zero)
{
  uint32_t uiBlock;
  bool    bFailure = false;
  uint32_t uiWriteBlocks = 0;


  if(write_block_zero)
    if (!unlock_card())
      return false;

  printf ("Writing %d blocks |", uiBlocks + 1);
  // Write the card from begin to end;
  for (uiBlock = 0; uiBlock <= uiBlocks; uiBlock++) {
    // Authenticate everytime we reach the first sector of a new block
    if (is_first_block (uiBlock)) {
      // Skip this the first time, bFailure it means nothing (yet)
      if (uiBlock != 0)
        print_success_or_failure (bFailure, &uiWriteBlocks);

      // Show if the readout went well
      if (bFailure) {
        // When a failure occured we need to redo the anti-collision
        if (nfc_initiator_select_passive_target (pnd, nmMifare, NULL, 0, &nt) < 0) {
          printf ("!\nError: tag was removed\n");
          return false;
        }
        bFailure = false;
      }

      fflush (stdout);

      // Try to authenticate for the current sector
      if (!write_block_zero && !authenticate (uiBlock)) {
        printf ("!\nError: authentication failed for block %02x\n", uiBlock);
        return false;
      }
    }

    if (is_trailer_block (uiBlock)) {
      // Copy the keys over from our key dump and store the retrieved access bits
      memcpy (mp.mpd.abtData, mtDump.amb[uiBlock].mbt.abtKeyA, 6);
      memcpy (mp.mpd.abtData + 6, mtDump.amb[uiBlock].mbt.abtAccessBits, 4);
      memcpy (mp.mpd.abtData + 10, mtDump.amb[uiBlock].mbt.abtKeyB, 6);

      // Try to write the trailer
      if (nfc_initiator_mifare_cmd (pnd, MC_WRITE, uiBlock, &mp) == false) {
        printf ("failed to write trailer block %d \n", uiBlock);
        bFailure = true;
      }
    } else {
      // The first block 0x00 is read only, skip this
      if (uiBlock == 0 && ! write_block_zero)
        continue;


      // Make sure a earlier write did not fail
      if (!bFailure) {
        // Try to write the data block
        memcpy (mp.mpd.abtData, mtDump.amb[uiBlock].mbd.abtData, 16);
        // do not write a block 0 with incorrect BCC - card will be made invalid!
        if (uiBlock == 0) {
          if((mp.mpd.abtData[0] ^ mp.mpd.abtData[1] ^ mp.mpd.abtData[2] ^ mp.mpd.abtData[3] ^ mp.mpd.abtData[4]) != 0x00) {
            printf ("!\nError: incorrect BCC in MFD file!\n");
            return false;
          }
        }
        if (!nfc_initiator_mifare_cmd (pnd, MC_WRITE, uiBlock, &mp))
          bFailure = true;
      }
    }
  }
  print_success_or_failure (bFailure, &uiWriteBlocks);
  printf ("|\n");
  printf ("Done, %d of %d blocks written.\n", uiWriteBlocks, uiBlocks + 1);
  fflush (stdout);

  return true;
}

typedef enum {
  ACTION_READ,
  ACTION_WRITE,
  ACTION_USAGE
} action_t;

static void
print_usage (const char *pcProgramName)
{
  printf ("Usage: ");
  printf ("%s r|R|w|W a|b <dump.mfd> [<keys.mfd>]\n", pcProgramName);
  printf ("  r|R|w|W       - Perform read from (r) or unlocked read from (R) or write to (w) or unlocked write to (W) card\n");
  printf ("                  *** note that unlocked write will attempt to overwrite block 0 including UID\n");
  printf ("                  *** unlocked read does not require authentication and will reveal A and B keys\n");
  printf ("                  *** unlocking only works with special Mifare 1K cards (Chinese clones)\n");
  printf ("  a|b           - Use A or B keys for action\n");
  printf ("  <dump.mfd>    - MiFare Dump (MFD) used to write (card to MFD) or (MFD to card)\n");
  printf ("  <keys.mfd>    - MiFare Dump (MFD) that contain the keys (optional)\n");
}

int
main (int argc, const char *argv[])
{
  action_t atAction = ACTION_USAGE;
  uint8_t *pbtUID;
  FILE   *pfKeys = NULL;
  FILE   *pfDump = NULL;
  int    unlock= 0;

  if (argc < 2) {
    print_usage (argv[0]);
    exit (EXIT_FAILURE);
  }
  const char *command = argv[1];

  if (strcmp (command, "r") == 0 || strcmp (command, "R") == 0) {
    if (argc < 4) {
      print_usage (argv[0]);
      exit (EXIT_FAILURE);
    }
    atAction = ACTION_READ;
    if (strcmp (command, "R") == 0)
      unlock= 1;
    bUseKeyA = tolower ((int) ((unsigned char) *(argv[2]))) == 'a';
    bUseKeyFile = (argc > 4);
  } else if (strcmp (command, "w") == 0 || strcmp (command, "W") == 0) {
    if (argc < 4) {
      print_usage (argv[0]);
      exit (EXIT_FAILURE);
    }
    atAction = ACTION_WRITE;
    if (strcmp (command, "W") == 0)
      unlock= 1;
    bUseKeyA = tolower ((int) ((unsigned char) *(argv[2]))) == 'a';
    bUseKeyFile = (argc > 4);
  }

  switch (atAction) {
  case ACTION_USAGE:
    print_usage (argv[0]);
    exit (EXIT_FAILURE);
    break;
  case ACTION_READ:
  case ACTION_WRITE:
    if (bUseKeyFile) {
      pfKeys = fopen (argv[4], "rb");
      if (pfKeys == NULL) {
        printf ("Could not open keys file: %s\n", argv[4]);
        exit (EXIT_FAILURE);
      }
      if (fread (&mtKeys, 1, sizeof (mtKeys), pfKeys) != sizeof (mtKeys)) {
        printf ("Could not read keys file: %s\n", argv[4]);
        fclose (pfKeys);
        exit (EXIT_FAILURE);
      }
      fclose (pfKeys);
    }

    if (atAction == ACTION_READ) {
      memset (&mtDump, 0x00, sizeof (mtDump));
    } else {
      pfDump = fopen (argv[3], "rb");

      if (pfDump == NULL) {
        printf ("Could not open dump file: %s\n", argv[3]);
        exit (EXIT_FAILURE);
      }

      if (fread (&mtDump, 1, sizeof (mtDump), pfDump) != sizeof (mtDump)) {
        printf ("Could not read dump file: %s\n", argv[3]);
        fclose (pfDump);
        exit (EXIT_FAILURE);
      }
      fclose (pfDump);
    }
    // printf("Successfully opened required files\n");

    nfc_init (NULL);
    
    // Try to open the NFC reader
    pnd = nfc_open (NULL, NULL);
    if (pnd == NULL) {
      printf ("Error opening NFC reader\n");
      exit (EXIT_FAILURE);
    }

    if (nfc_initiator_init (pnd) < 0) {
      nfc_perror (pnd, "nfc_initiator_init");
      exit (EXIT_FAILURE);    
    };

    // Let the reader only try once to find a tag
    if (nfc_device_set_property_bool (pnd, NP_INFINITE_SELECT, false) < 0) {
      nfc_perror (pnd, "nfc_device_set_property_bool");
      exit (EXIT_FAILURE);
    }
    // Disable ISO14443-4 switching in order to read devices that emulate Mifare Classic with ISO14443-4 compliance.
    nfc_device_set_property_bool (pnd, NP_AUTO_ISO14443_4, false);

    printf ("NFC reader: %s opened\n", nfc_device_get_name (pnd));

    // Try to find a MIFARE Classic tag
    if (nfc_initiator_select_passive_target (pnd, nmMifare, NULL, 0, &nt) < 0) {
      printf ("Error: no tag was found\n");
      nfc_close (pnd);
      nfc_exit (NULL);
      exit (EXIT_FAILURE);
    }
    // Test if we are dealing with a MIFARE compatible tag
    if ((nt.nti.nai.btSak & 0x08) == 0) {
      printf ("Warning: tag is probably not a MFC!\n");
    }

    // Get the info from the current tag
    pbtUID = nt.nti.nai.abtUid;

    if (bUseKeyFile) {
      uint8_t fileUid[4];
      memcpy (fileUid, mtKeys.amb[0].mbm.abtUID, 4);
      // Compare if key dump UID is the same as the current tag UID, at least for the first 4 bytes
      if (memcmp (pbtUID, fileUid, 4) != 0) {
        printf ("Expected MIFARE Classic card with UID starting as: %02x%02x%02x%02x\n",
                fileUid[0], fileUid[1], fileUid[2], fileUid[3]);
      }
    }
    printf ("Found MIFARE Classic card:\n");
    print_nfc_iso14443a_info (nt.nti.nai, false);

    // Guessing size
    if ((nt.nti.nai.abtAtqa[1] & 0x02) == 0x02)
      // 4K
      uiBlocks = 0xff;
    else if ((nt.nti.nai.btSak & 0x01) == 0x01)
      // 320b
      uiBlocks = 0x13;
    else
      // 1K
      // TODO: for MFP it is 0x7f (2K) but how to be sure it's a MFP? Try to get RATS?
      uiBlocks = 0x3f;
    printf ("Guessing size: seems to be a %i-byte card\n", (uiBlocks + 1) * 16);

    if (atAction == ACTION_READ) {
      if (read_card (unlock)) {
        printf ("Writing data to file: %s ...", argv[3]);
        fflush (stdout);
        pfDump = fopen (argv[3], "wb");
	if (pfDump == NULL) {
	    printf ("Could not open dump file: %s\n", argv[3]);
	    exit (EXIT_FAILURE);
	}
        if (fwrite (&mtDump, 1, sizeof (mtDump), pfDump) != sizeof (mtDump)) {
          printf ("\nCould not write to file: %s\n", argv[3]);
          exit (EXIT_FAILURE);
        }
        printf ("Done.\n");
        fclose (pfDump);
      }
    } else if (atAction == ACTION_WRITE) {
      write_card (unlock);
    }

    nfc_close (pnd);
    break;
  };
  
  nfc_exit (NULL);
  exit (EXIT_SUCCESS);
}
