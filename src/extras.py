from ..models import *
from django import template
register=template.Library()

@register.inclusion_tag("base_updates.html")
def updates(count):
	return{
		"updates":Update.all()
			.order("-added")
			.run(limit=count),
	}
	
@register.inclusion_tag("base_signup.html")
def signup(event):
	return{
		"event":event,
		"form":signup_conf(event)["form"](),
	}

from datetime import datetime,tzinfo,timedelta
from time import localtime
ZERO=timedelta(0)
class FixedOffset(tzinfo):
	def __init__(self, offset, name):
		self.__offset = timedelta(minutes = offset)
		self.__name = name
	def utcoffset(self, dt):
		return self.__offset
	def tzname(self, dt):
		return self.__name
	def dst(self, dt):
		return ZERO
eastern=FixedOffset(-5*60,"US/Eastern")
def clean(ent):
	now=datetime.time(datetime.now(eastern))
	ent.when="after"if now<ent.start else "now"if now<ent.end else"before"
	return ent
@register.inclusion_tag("base_matches.html")
def matches():
	return{
		"matches":map(clean,VolleyballMatch.all()
			.order("start"))
	}
