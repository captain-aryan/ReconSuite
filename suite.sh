#!/bin/bash

domain=$1
threads=$2

timeout 5s python subdomain.py $domain $threads
RET=$?

if [ $RET -eq 124 ]; then
    echo -e "\e[31m[-]\e[0m Subdomains not found"
fi

python dirbuster.py http://$domain $threads .php

python vuln_scanner.py $domain