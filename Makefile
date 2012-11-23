.PHONY: deploy
deploy:
	find site -name \*.pyc -delete
	google_appengine/appcfg.py update site
