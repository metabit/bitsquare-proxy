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
import time, datetime
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
    assert direction == 'BUY' or direction == 'SELL', 'Unknown direction %s' % direction
    epoch_now=int(time.time())
    #print '###############', epoch_now, epoch
    # history check
    if epoch_now - epoch > 3600:
        #print 'history price check for', currency, 'at', epoch
        # as token take a date with full hour string - no minutes and seconds
        token_date_str=datetime.datetime.utcfromtimestamp(epoch-epoch%3600).strftime('%Y-%m-%d %H:')
        try:
            f=open('online_prices/20160604-'+currency+'-per_hour_monthly_sliding_window.csv','r')
            for line in f:
                if line.startswith(token_date_str):
                    f.close()
                    # average price both for buy and for sell
                    return line.split(',')[3]
            f.close()
        except IOError:
            # no currency file
            pass
        return 'No price available'
    # live check
    else:
        print 'live price check'
        # FIXME: don't break SSL certs
        bu=butils()
        response=bu.get_data('https://api.bitcoinaverage.com/ticker/'+currency+'/')
        if direction=='BUY': # bid
            return response['bid']
        else: #'SELL' than ask
            return response['ask']

def get_log(txid, escrow_epoch=0): # txid is a filename under offers dir
    d=get_details(txid)
    try:
        currency=str(d['currencyCode'].strip('\''))
        direction=str(d['direction'])
        margin=float(d['marketPriceMargin'])
        if escrow_epoch == 0:
            epoch=int(d['date'])
            #print 'using original epoch'
        else:
            epoch=escrow_epoch
            #print 'using escrow epoch'
        price=0

        if d['useMarketBasedPrice']=='true':
            assert direction == 'BUY' or direction == 'SELL', 'Unknown direction %s' % direction
            try:
                raw_price=float(get_price(currency,direction,epoch))
            except ValueError:
                #print "no price available for", epoch
                raw_price=0.0
            if direction == 'BUY':
                price=raw_price*(1.0-margin)
            else:
                price=raw_price*(1.0+margin)
        else:
            price=float(d['fiatPrice'])/10000

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
               'txid':txid}

        log_line=json.dumps(log_d, sort_keys=True)
        message = BitcoinMessage(log_line)
        key = CBitcoinSecret(signer_privkey)
        signature = SignMessage(key, message)
        sign_d={'address':signer_addr,'signature':signature}
        sign_line=json.dumps(sign_d, sort_keys=True)
        return log_line,sign_line,log_d
    except KeyError:
        # entry is probably not on the filesystem
        return "","",{}
