#!/bin/sh
while [ "$#" -gt 0 ]
do
	cp "$1" ./
	echo "$1" >> copy.sh
	shift
done
