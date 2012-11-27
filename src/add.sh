#!/bin/sh
while [ "$#" -gt 0 ]
do
	cp -nv "$1" ./ && echo "	grep -v '[^[:alnum:]]*vim:' ${1##*/} > $1" >> Makefile && git add "${1##*/}" && (cd ..; echo "${1#../}" >> .gitignore;) && git rm --cached "$1"
	shift
done
