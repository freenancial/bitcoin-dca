#!/bin/bash

git submodule update --init

python3 -m venv ./venv
source venv/bin/activate

pip install -r requirements.txt