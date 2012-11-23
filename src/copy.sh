#!/bin/sh
tail -n+7 "$0" | while read x
do
	cp -uv "${x%*/}" "$x"
done
exit 0
../site/static/css/main.css
../site/msmcyc/templates/base_home.html
