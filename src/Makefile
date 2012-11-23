.PHONY: copy
copy:
	grep -v '[^[:alnum:]]*vim:' base_home.html > ../site/msmcyc/templates/base_home.html
	sed '/>.*[{,]/s/>/ /g' main.css | grep -v '[^[:alnum:]]*vim:' > ../site/static/css/main.css
	grep -v '[^[:alnum:]]*vim:' index.html > ../site/msmcyc/templates/index.html
	grep -v '[^[:alnum:]]*vim:' main.js > ../site/static/js/main.js
