#!/bin/python

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

from time import sleep
from py4j.java_gateway import JavaGateway
from json import dumps
import blockchain_checks

# FIXME:
# make sure correct gateway is really running
# wrap in a class

gateway = JavaGateway()
bcheck = blockchain_checks.blockchain_checks()


chop_start=len('Offer{\n')
chop_end=len('}')
separator='\n\t'

currency_set=set()
prev_active_offers_fee_tx_set=set()
offers_per_currency={}
current_total_offers=0
prev_total_offers=0

while True:
    offers = gateway.entry_point.getOffers()
    # zero current active set
    current_active_offers_fee_tx_set=set()
    current_total_offers=len(offers)
    for i in range(len(offers)):
        offer=str(offers[i])[chop_start:-chop_end]
        offer_dict={}
        for l in offer.split(separator):
            value=l.split('=')
            try:
                offer_dict[value[0]]="".join(value[1:])
            except IndexError:
                pass

        try:
            fee_txid=offer_dict['offerFeePaymentTxID'].strip('\'')
            current_active_offers_fee_tx_set.add(fee_txid)
            # store offers on filesystem
            f=open('offers/'+fee_txid, 'w')
            f.write(dumps(offer_dict, sort_keys=True))
            f.close()
        except KeyError:
            print 'no offerFreePaymentTxID?'

        # sort per currency and direction
        currency=offer_dict['currencyCode']
        currency_set.add(currency)
        buy_sell=offer_dict['direction']
        if offers_per_currency.has_key(currency) and offers_per_currency[currency].has_key(buy_sell):
            offers_per_currency[currency][buy_sell].append(offer_dict)
        else:
            offers_per_currency[currency]={buy_sell:[offer_dict]}


    # check offers that vanished - either deal or cancel
    diff=prev_active_offers_fee_tx_set.difference(current_active_offers_fee_tx_set)

    if len(diff) > 0:
        print diff

    if prev_total_offers != current_total_offers:
        print prev_total_offers,'=>',current_total_offers

    for txid in diff:
        (accepted, escrow_txid, escrow_epoch, details_log)=bcheck.was_offer_accepted(txid)
        if accepted:
            trade_log,sign_log,trade_d=get_log(txid, escrow_epoch)
            print "Offer Accepted:", txid, details_log, trade_log ,sign_log
            entry=trade_d['epoch']+' '+trade_d['price']+' '+trade_d['currencyCode']+' '+trade_d['direction']+' '+trade_d['txid']
            f=open('snapshots/ticker','a')
            f.write(entry)
            f.close()

    prev_total_offers=current_total_offers
    prev_active_offers_fee_tx_set=current_active_offers_fee_tx_set
    sleep(1)


#sorted_by_amount={}
#for c in currency_set:
#    for direction in ['BUY', 'SELL']:
#        try:
#            amount=len(offers_per_currency[c][direction])
#            if sorted_by_amount.has_key(amount):
#                sorted_by_amount[amount].append(c+' '+direction)
#            else:
#               sorted_by_amount[amount]=[c+' '+direction]
#        except KeyError:
#            amount=0

#for k in sorted(sorted_by_amount.keys(), reverse=True):
#    print k, sorted_by_amount[k]

