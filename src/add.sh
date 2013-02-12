#!/bin/sh
while [ "$#" -gt 0 ]
do
	cp -nv "$1" ./ && echo "	grep -v '[^[:alnum:]]vim:' ${1##*/} > $1" >> Makefile && git rm --cached "$1" && (cd ..; echo "${1#../}" >> .gitignore;) && git add "${1##*/}"
	shift
done
