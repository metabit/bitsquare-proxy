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
import simplejson

arbitrator_addrs='1FdFzBazmHQxbUbdCUJwuCtR37DrZrEobu,19xdeiQM2Hn2M2wbpT5imcYWzqhiSDHPy4'
get_a_fresh_tx_list=False
regenerate_ticker=True

# get instances of tools classes
bu=butils()
bchk=blockchain_checks()

txid_list=[]
if get_a_fresh_tx_list:
    for arbitrator_addr in arbitrator_addrs.split(','):
        txid_list+=bu.get_addr_tx_list(arbitrator_addr)
    sorted_txid_list=bu.sort_tx_list(txid_list)

    f=open('sorted_txid_list.txt', 'w')
    simplejson.dump(txid_list,f)
    f.close()

f=open('sorted_txid_list.txt', 'r')
sorted_txid_list=simplejson.load(f)
f.close()

for txid in sorted_txid_list[-500:]: # just the last 500 tx
    (accepted, escrow_txid, escrow_epoch, details_log)=bchk.was_offer_accepted(txid)
    if accepted:
        trade_log,sign_log,trade_d=get_log(txid, escrow_epoch)
        print details_log+' '+trade_log+' '+sign_log
        if trade_d != {} and regenerate_ticker:
            entry=str(trade_d['epoch'])+' '+str(trade_d['price'])+' '+trade_d['currencyCode']+' '+trade_d['direction']+' '+str(trade_d['txid'])+'\n'
            f=open('snapshots/unsorted_ticker','a')
            f.write(entry)
            f.close()
