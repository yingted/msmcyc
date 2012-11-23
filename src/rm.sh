#!/bin/sh
while [ "$#" -gt 0 ]
do
	path="$(lua - <<< 'for line in io.lines("../.gitignore")do if arg[1]==line:sub(-#arg[1])then print(line)end end' "$1")"
	git add "../$path" && sed -i "$(grep -nFx "$path" ../.gitignore | cut -d: -f1)d" ../.gitignore && rm "$1"
	shift
done
