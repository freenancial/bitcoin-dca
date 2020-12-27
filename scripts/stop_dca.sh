#!/bin/bash
dca_pid=$(pgrep -f '[b]itcoin_dca.py')
[ -n "$dca_pid" ] && kill $dca_pid || true
