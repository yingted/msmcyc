.PHONY: all
all: *.min.js
%.min.js: %.js
	js -f ../../../../fulljsmin.js -e 'print(jsmin((b=(a=snarf(readline())).match(/^\/\*(?:x|[^x])*?\*\//)),a.substring(b.length).trim()).trim())' <<< $< > $@
