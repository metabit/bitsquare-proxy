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

import json
from bit_utils import butils
from signer import signer_addr, signer_privkey

from bitcoin.wallet import CBitcoinSecret, P2PKHBitcoinAddress
from bitcoin.signmessage import BitcoinMessage, VerifyMessage, SignMessage

def get_details(txid):
    try:
        f=open('offers/'+txid)
        d=json.load(f)
        f.close()
    except IOError:
        # file doesn't exist
        #print "contract for %s is not on the filesystem" % txid
        d={}
    return d

def get_price(currency, direction, epoch):
    # FIXME: consider epoch
    # FIXME: don't break SSL certs
    bu=butils()
    response=bu.get_data('https://api.bitcoinaverage.com/ticker/'+currency+'/')
    assert direction == 'BUY' or direction == 'SELL', 'Unknown direction %s' % direction
    if direction=='BUY': # bid
        return response['bid']
    else: #'SELL' than ask
        return response['ask']

def get_log(txid): # txid is a filename under offers dir
    d=get_details(txid)
    try:
        currency=str(d['currencyCode'].strip('\''))
        direction=str(d['direction'])
        margin=float(d['marketPriceMargin'])
        price=0

        if d['useMarketBasedPrice']=='true':
            raw_price=get_price(currency,direction,0)
            assert direction == 'BUY' or direction == 'SELL', 'Unknown direction %s' % direction
            if direction == 'BUY':
                price=raw_price*(1.0-margin)
            else:
                price=raw_price*(1.0+margin)
        else:
            price=float(d['fiatPrice'])

        # epoch of accept tx
        epoch='unknown'

        log_d={'currencyCode':currency,\
               'direction':direction,\
               'minAmount':str(d['minAmount']),\
               'amount':str(d['amount']),\
               'useMarketBasedPrice':d['useMarketBasedPrice'],\
               'fiatPrice':d['fiatPrice'],\
               'marketPriceMargin':d['marketPriceMargin'],\
               'paymentMethodName':str(d['paymentMethodName'].strip('\'')),\
               'price':str(price),\
               'epoch':epoch,\
               'testing':'True',\
               'txid':txid}

        log_line=json.dumps(log_d, sort_keys=True)
        message = BitcoinMessage(log_line)
        key = CBitcoinSecret(signer_privkey)
        signature = SignMessage(key, message)
        sign_d={'address':signer_addr,'signature':signature}
        sign_line=json.dumps(sign_d, sort_keys=True)
        return log_line+','+sign_line
    except KeyError:
        # entry is probably not on the filesystem
        return '{},{}'
