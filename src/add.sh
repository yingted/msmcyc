#!/bin/sh
while [ "$#" -gt 0 ]
do
	cp -nv "$1" ./ && echo "	grep -v '[^[:alnum:]]*vim:' ${1##*/} > $1" >> Makefile && git rm --cached "$1" && (cd ..; readlink -f "src/$1" >> .gitignore;)
	shift
done
