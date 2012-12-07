#!/bin/sh
while [ "$#" -gt 0 ]
do
	path="$(lua - <<< 'for line in io.lines("../.gitignore")do if "/"..arg[1]==line:sub(-1-#arg[1])then print(line)end end' "$1")"
	sed -i "$(grep -nFx "$path" ../.gitignore | cut -d: -f1)d" ../.gitignore && sed -i "/ $1 > /d" Makefile && git add "../$path" && git rm "$1" && rm "$1"
	shift
done
