.PHONY: all copy watch
all: copy
test: copy
	[ "$(TERM)" = "screen" ] && echo -en '\ekgae\e\\' || :
	python ../google_appengine/dev_appserver.py ../site --address 0.0.0.0
watch: copy
	[ "$(TERM)" = "screen" ] && echo -en '\ekwatch\e\\' || :
	while :; do inotifywait -e close_write -e delete_self -e create -e move_self -qqrt5 *; make; done
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
copy: *.min.js *-scaled.jpg
	grep -v '[^[:alnum:]]*vim:' base_home.html > ../site/msmcyc/templates/base_home.html
	sed '/>.*[{,]/s/>/ /g' main.css | grep -v '[^[:alnum:]]*vim:' > ../site/static/css/main.css
	grep -v '[^[:alnum:]]*vim:' index.html > ../site/msmcyc/templates/index.html
	curl -sd compilation_level=SIMPLE_OPTIMIZATIONS -d output_format=text -d output_info=compiled_code --data-urlencode 'js_code@main.js' http://closure-compiler.appspot.com/compile > ../site/static/js/main.js || grep -v '[^[:alnum:]]*vim:' main.js > ../site/static/js/main.js
	grep -v '[^[:alnum:]]*vim:' views.py > ../site/msmcyc/views.py
	grep -v '[^[:alnum:]]*vim:' models.py > ../site/msmcyc/models.py
	grep -v '[^[:alnum:]]*vim:' events.html > ../site/msmcyc/templates/events.html
	grep -v '[^[:alnum:]]*vim:' extras.py > ../site/msmcyc/templatetags/extras.py
	grep -v '[^[:alnum:]]*vim:' base_signup.html > ../site/msmcyc/templates/base_signup.html
	grep -v '[^[:alnum:]]*vim:' sponsors.html > ../site/msmcyc/templates/sponsors.html
	grep -v '[^[:alnum:]]*vim:' signup_success.html > ../site/msmcyc/templates/signup_success.html
	grep -v '[^[:alnum:]]*vim:' signup.html > ../site/msmcyc/templates/signup.html
	grep -v '[^[:alnum:]]*vim:' scoreboard.html > ../site/msmcyc/templates/scoreboard.html
	grep -v '[^[:alnum:]]*vim:' base_matches.html > ../site/msmcyc/templates/base_matches.html
	grep -v '[^[:alnum:]]*vim:' ambassadors.html > ../site/msmcyc/templates/ambassadors.html
	grep -v '[^[:alnum:]]*vim:' execs.html > ../site/msmcyc/templates/execs.html
