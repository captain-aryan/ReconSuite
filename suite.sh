#!/bin/bash

if [ -z "$1" ]; then
    echo "Usage: ./suite.sh <domain> <threads>"
    exit 1
fi

domain=$1
threads=$2

timeout 5s python subdomain.py $domain $threads
RET=$?

if [ $RET -eq 124 ]; then
    echo -e "\e[31m[-]\e[0m Subdomains not found"
fi

python dirbuster.py $domain $threads .php

python web_crawler.py $domain

python vuln_scanner.py --url-file recon/crawl_${domain//./_}.txt