.PHONY: all copy watch
all: copy
test: copy
	python ../google_appengine/dev_appserver.py ../site --address 0.0.0.0
watch: copy
	while :; do inotifywait -e close_write -e delete_self -e create -e move_self -qqrt5 *; make; done
deploy:
	make deploy -C ..
commit:
	make commit -C ..
%.min.js: %.js
	js -f ../fulljsmin.js -e 'print(jsmin((b=(a=snarf(readline())).match(/^\/\*(?:x|[^x])*?\*\//)),a.substring(b.length).trim()).trim())' <<< $< > $@
copy: *.min.js
	grep -v '[^[:alnum:]]*vim:' base_home.html > ../site/msmcyc/templates/base_home.html
	sed '/>.*[{,]/s/>/ /g' main.css | grep -v '[^[:alnum:]]*vim:' > ../site/static/css/main.css
	grep -v '[^[:alnum:]]*vim:' index.html > ../site/msmcyc/templates/index.html
	grep -v '[^[:alnum:]]*vim:' main.js > ../site/static/js/main.js
	grep -v '[^[:alnum:]]*vim:' views.py > ../site/msmcyc/views.py
	grep -v '[^[:alnum:]]*vim:' models.py > ../site/msmcyc/models.py
	grep -v '[^[:alnum:]]*vim:' events.html > ../site/msmcyc/templates/events.html
	grep -v '[^[:alnum:]]*vim:' extras.py > ../site/msmcyc/templatetags/extras.py
	grep -v '[^[:alnum:]]*vim:' base_signup.html > ../site/msmcyc/templates/base_signup.html
	grep -v '[^[:alnum:]]*vim:' sponsors.html > ../site/msmcyc/templates/sponsors.html
.PHONY: all
