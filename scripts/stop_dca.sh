#!/bin/bash

kill $(ps aux|grep "[b]itcoin_dca.py" |  awk '{print $2}')
