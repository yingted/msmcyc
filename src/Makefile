.PHONY: all test copy watch deploy commit slow fast copyfast png jpg symlinks rebuild
all: png jpg copy
rebuild: symlinks all
test: copy
	[ "$(TERM)" = "screen" ] && echo -en '\ekgae\e\\' || :
	python ../google_appengine/dev_appserver.py ../site --host 0.0.0.0
watch: copy
	[ "$(TERM)" = "screen" ] && echo -en '\ekwatch\e\\' || :
	while :; do inotifywait -e close_write -e delete_self -e create -e move_self -qqrt5 *; make copyfast fast; done
deploy:
	make deploy -C ..
commit:
	make commit -C ..
symlinks:
	find -type l -exec sh -c 'touch -a "$$(readlink -f $$0)"' {} \;
%.min.js: %.js
	mkdir -p "$$(dirname -- "$$(readlink -m -- $@)")"
	js -f ../fulljsmin.js -e 'print(jsmin((b=(a=snarf(readline())).match(/^\/\*(?:x|[^x])*?\*\//)),a.substring(b&&b[0].length).trim()).trim())' <<< $< > $$(readlink -m -- $@)
images/%-scaled.jpg: images/%-orig.jpg
	mkdir -p $$(dirname -- $$(readlink -m -- $@))
	convert $< -resize 336x280\< -resize 336x280\> $$(readlink -m -- $@)
png:
	find images ../site/static -iname \*.png -printf 'processing %p\n' -execdir optipng -o7 {} \; -execdir advpng -z4 {} \; -execdir advpng -z4 {} \;
jpg:
	find images ../site/static \( -iname \*.jpg -o -iname \*.jpeg \) -printf 'processing %p\n' -execdir jpegtran -copy none -optimize -progressive -outfile {} {} \;
slow: main.js
	curl -sd compilation_level=SIMPLE_OPTIMIZATIONS -d output_format=text -d output_info=compiled_code --data-urlencode 'js_code@main.js' http://closure-compiler.appspot.com/compile > ../site/static/js/main.js || grep -v '[^[:alnum:]]vim:' main.js > ../site/static/js/main.js
fast: main.js
	grep -v '[^[:alnum:]]vim:' main.js > ../site/static/js/main.js
copy: copyfast slow
#phony target dependencies elided
copyfast: *.min.js images/*-scaled.jpg main.sass
	css="$$(tr '>' ' ' < main.sass | sed 's/^\(\t*\) /\1/' | sass --compass -Ct compressed)" && echo "$$css" > ../site/static/css/main.css
	grep -v '[^[:alnum:]]vim:' base_home.html > ../site/msmcyc/templates/base_home.html
	grep -v '[^[:alnum:]]vim:' models.py > ../site/msmcyc/models.py
	grep -v '[^[:alnum:]]vim:' extras.py > ../site/msmcyc/templatetags/extras.py
	grep -v '[^[:alnum:]]vim:' views.py > ../site/msmcyc/views.py
