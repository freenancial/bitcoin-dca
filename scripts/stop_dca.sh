#!/bin/bash

kill $(ps aux|grep "[b]uy_bitcoin.py" |  awk '{print $2}')
