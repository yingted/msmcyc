#!/usr/bin/python
from django.views.generic.simple import direct_to_template
from django.shortcuts import redirect
import logging
import re
useful=re.compile(r'^/(?!base_)([^\.]*?)(?:\.html)?$')

def index(request):
	match=useful.match(request.path)
	if match:
		try:
			return direct_to_template(request,(match.group(1)or"index")+".html")
		except TemplateDoesNotExist as e:
			logging.error(e)
	return redirect("/static"+request.path)
