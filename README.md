# bitsquare-proxy

What is bitsquare-proxy?
------------------------

bitsquare-proxy is a python framework that communicates with a local java based bitsquare client using py4j and with a remote bitcore server over https in order to enable an extended set of features.

Added features should still follow the bitsquare protocol, or supply additional communication channels.


Status
------

The code is in a *very early* stage, and it is actually only a snapshot of what I have been playing with, so consider it only for fun and hacking purposes at this moment.

The early features are planned to be API for ticker, price/volume history, order book, and statistics of the bitsquare network. Since bitsquare is decentralised, API infrastructure would be offered by volunteers and the trust could be achieved using reputation, so automatic signature on the API is included. It is also clear that different nodes may see a different picture of the network.

Further features would be trading bots and protocol hardening tests :)


Quickstart
----------

Compile bitsquare from https://github.com/metabit/bitsquare/ or simply add the following patches to the official bitsquare repository:

- https://github.com/metabit/bitsquare/commit/ee56bce52211a1e83d73806d837873f1a436842a
- https://github.com/metabit/bitsquare/commit/3771f656ba68317a764e73df2e553acb340cce0a

Run bitsquare client - it will listen on local port 25333.


To find the trades history.

    $ python check_all.py > history_trades.txt
    $ cat history_trades.txt | sort > snapshots/sorted_history_trades.txt

    # The script goes over all transactions entering the currently only 
    # arbitrator and checking which resulted in an escrow. For those, if a 
    # corresponding contract file exists, the details of the trade are 
    # printed out
    # Prices are checked only for Fiat using a price snapshot of monthly
    # sliding price per currency:
    # https://api.bitcoinaverage.com/history/EUR/per_hour_monthly_sliding_window.csv
    # a cronjob should monthly update those files. Currently supported
    # the following currencies: AUD EUR NOK USD CNY GBP SEK
    # Other currencies will have price 0.0 if contract marked as based on
    # market.
    # Trade logs with no details mean that the contract file is not available
    # locally.
    # If regenerate_ticker is True snapshots/unsorted_ticker is generated
    # In order to generate the sorted ticker:

    $ cat snapshots/unsorted_ticker | sort > snapshots/ticker
    

To generate the price ticker.

    $ python bitsquare_proxy.py
    144 => 142
    set(['aacb6489f026db37b1ad83bbb59e4dcbca4c8a18ea21ba427349b493fd7708ed'])
    142 => 141
    141 => 142
    set(['50dced84bf4166e9b00c19e61245e11b3edee0b4c0f5cfdcad759bb137e24354'])
    142 => 141
    141 => 142
    142 => 143

    # Each available offer is saved under directory offers with fee txid as a 
    # filename.
    # Each change in the number of available offers is noted in a printout.
    # When the number of available offers is dropped, the list of the vanishing
    # offers is printed out and each one of the tx is followd on the blockchain
    # to determine if it got resulted in an escrow.
    # An entry log containing real time calculated price is printed with
    # a signature.
    # The ticker file is updated with latest trade: snapshots/ticker


License
-------

bitsquare-proxy is [free software](https://www.gnu.org/philosophy/free-sw.html), licensed under version 3 of the [GNU Affero General Public License](https://gnu.org/licenses/agpl.html).

In short, this means you are free to fork this repository and do anything with it that you please. However, if you _distribute_ your changes, i.e. create your own build of the software and make it available for others to use, you must:

 1. Publish your changes under the same license, so as to ensure the software remains free.
 2. Use a name different "bitsquare-proxy". This allows for competition without confusion.

See [LICENSE](LICENSE) for complete details.


About
-----

https://github.com/metabit

Donations (and signatures): 1MetabitMKKGcYZy8YieDHenjjoMxHNAgW
