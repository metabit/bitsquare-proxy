#!/usr/bin/python

#################################################
#                                               #
# Bitsquare Proxy                               #
#                                               #
# metabit <metabit@riseup.net>                  #
# https://github.com/metabit                    #
# Donations: 1MetabitMKKGcYZy8YieDHenjjoMxHNAgW #
# License: AGPLv3                               #
#                                               #
#################################################

from blockchain_checks import *
from retrieve_details import get_log
from bit_utils import butils

arbitrator_addr='1FdFzBazmHQxbUbdCUJwuCtR37DrZrEobu'

# get instances of tools classes
bu=butils()
bchk=blockchain_checks()

print 'running on all tx of', arbitrator_addr
txid_list=bu.get_addr_tx_list(arbitrator_addr)

sorted_txid_list=bu.sort_tx_list(txid_list)

print 'list collected'

for txid in sorted_txid_list[-120:]: # just the last 120
#    print txid
    (accepted, escrow_txid, details_log)=bchk.was_offer_accepted(txid)
    if accepted:
        print details_log +' '+ get_log(txid)
