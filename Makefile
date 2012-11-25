.PHONY: deploy commit
deploy:
	find site -name \*.pyc -delete
	google_appengine/appcfg.py update site
commit:
	git add site src
	git commit -a
