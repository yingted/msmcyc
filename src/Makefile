.PHONY: all copy watch slow fast png
all: copy
test: copy
	[ "$(TERM)" = "screen" ] && echo -en '\ekgae\e\\' || :
	python ../google_appengine/dev_appserver.py ../site --address 0.0.0.0
watch: copy
	[ "$(TERM)" = "screen" ] && echo -en '\ekwatch\e\\' || :
	while :; do inotifywait -e close_write -e delete_self -e create -e move_self -qqrt5 *; make copyfast fast; done
deploy:
	make deploy -C ..
commit:
	make commit -C ..
%.min.js: %.js
	mkdir -p $$(dirname -- $$(readlink -m -- $@))
	js -f ../fulljsmin.js -e 'print(jsmin((b=(a=snarf(readline())).match(/^\/\*(?:x|[^x])*?\*\//)),a.substring(b&&b[0].length).trim()).trim())' <<< $< > $$(readlink -m -- $@)
%-scaled.jpg: %-orig.jpg
	mkdir -p $$(dirname -- $$(readlink -m -- $@))
	convert $< -resize 336x280\< -resize 336x280\> $$(readlink -m -- $@)
png:
	find ../site/static -name \*.png -exec ./png.sh {} +
slow: main.js
	curl -sd compilation_level=SIMPLE_OPTIMIZATIONS -d output_format=text -d output_info=compiled_code --data-urlencode 'js_code@main.js' http://closure-compiler.appspot.com/compile > ../site/static/js/main.js || grep -v '[^[:alnum:]]vim:' main.js > ../site/static/js/main.js
fast: main.js
	grep -v '[^[:alnum:]]vim:' main.js > ../site/static/js/main.js
copy: copyfast slow
#phony target dependencies elided
copyfast: *.min.js *-scaled.jpg main.sass
	css="$$(tr '>' ' ' < main.sass | sed 's/^\(\t*\) /\1/' | sass -Ct compressed)" && echo "$$css" > ../site/static/css/main.css
	grep -v '[^[:alnum:]]vim:' base_home.html > ../site/msmcyc/templates/base_home.html
	grep -v '[^[:alnum:]]vim:' index.html > ../site/msmcyc/templates/index.html
	grep -v '[^[:alnum:]]vim:' models.py > ../site/msmcyc/models.py
	grep -v '[^[:alnum:]]vim:' extras.py > ../site/msmcyc/templatetags/extras.py
	grep -v '[^[:alnum:]]vim:' sponsors.html > ../site/msmcyc/templates/sponsors.html
	grep -v '[^[:alnum:]]vim:' ambassadors.html > ../site/msmcyc/templates/ambassadors.html
	grep -v '[^[:alnum:]]vim:' execs.html > ../site/msmcyc/templates/execs.html
	grep -v '[^[:alnum:]]*vim:' apply.html > ../site/msmcyc/templates/apply.html
