.PHONY: deploy commit test
deploy:
	find site -name \*.pyc -delete
	google_appengine/appcfg.py update site
test:
	make test -C src
commit:
	git add .
	git commit -a
