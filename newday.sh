#!/bin/sh

python solutions/new_day.py $1

python -m black solutions/__main__.py 2> /dev/null