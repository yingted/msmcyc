.PHONY: all copy watch
all: copy
test: copy
	python ../google_appengine/dev_appserver.py ../site --address 0.0.0.0
watch: copy
	while :; do inotifywait -e close_write -e delete_self -e create -e move_self -qqrt5 *; make; done
copy:
	grep -v '[^[:alnum:]]*vim:' base_home.html > ../site/msmcyc/templates/base_home.html
	sed '/>.*[{,]/s/>/ /g' main.css | grep -v '[^[:alnum:]]*vim:' > ../site/static/css/main.css
	grep -v '[^[:alnum:]]*vim:' index.html > ../site/msmcyc/templates/index.html
	grep -v '[^[:alnum:]]*vim:' main.js > ../site/static/js/main.js
deploy:
	make deploy -C ..
commit:
	make commit -C ..
