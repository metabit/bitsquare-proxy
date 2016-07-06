#!/bin/sh

TODAY=`date +%Y%m%d`

for CURRENCY in AUD CHF CNY EUR GBP NOK SEK USD; do
    filename="$TODAY-$CURRENCY-per_hour_monthly_sliding_window.csv"
    wget -O $filename "https://api.bitcoinaverage.com/history/"$CURRENCY"/per_hour_monthly_sliding_window.csv"
done
