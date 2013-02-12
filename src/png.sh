#!/bin/bash
for png in "$@"
do
	echo processing "$png"
	optipng -o7 "$png" && advpng -z4 "$png" && advdef -z4 "$png"
done
