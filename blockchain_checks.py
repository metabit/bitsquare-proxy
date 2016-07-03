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

from bit_utils import butils
import datetime

required_escrow_ops=set(('OP_HASH160','OP_RETURN'))

class blockchain_checks:
    """A class for advanced blockchain checks"""

    # get the basic bitcoin utils class
    bu=butils()

    def is_escrow(self, txid):
        tx=self.bu.get_tx(txid)
        ops=set()
        for vout in tx['vout']:
            try:
                ops.add(vout['scriptPubKey']['asm'].split(' ')[0])
            except KeyError:
                pass
        return ops.issuperset(required_escrow_ops)

    def was_offer_accepted(self, txid):
        potential_deal_tx=self.bu.get_tx(txid)
        # observe the outputs of the tx
        for vout in potential_deal_tx['vout']:
            try:
                # the output must be spent
                potential_escrow_txid=vout['spentTxId']
                potential_escrow_tx=self.bu.get_tx(potential_escrow_txid)
                # observe the outputs of each of the above
                if self.is_escrow(potential_escrow_txid):
                    escrow_epoch = potential_escrow_tx['blocktime']
                    details_log=str(potential_escrow_tx['blockheight'])+' '+ datetime.datetime.fromtimestamp(potential_escrow_tx['blocktime']).strftime('%c')+' '+str(txid)+' '+str(potential_escrow_txid)
                    return (True, potential_escrow_txid, escrow_epoch, details_log)
            except KeyError:
                pass
        return (False,'','','')
