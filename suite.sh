#!/bin/bash

domain=$1
threads=$2

timeout 7s python subdomain.py $domain $threads

python dirbuster.py http://$domain $threads .php

python vuln_scanner.py $domain