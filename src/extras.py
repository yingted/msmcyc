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

from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
@register.filter(is_safe=True)
@stringfilter
def email(addr):
	addr="".join("&#%d;"%ord(c)for c in addr)
	return"<a href=\"mailto:%s\">%s</a>"%(addr,addr)

CONSTS={
	"email":email("info@msyouthmississauga.org"),
	"name":mark_safe("<abbr title=\"Multiple Sclerosis Mississauga Youth Committee\">MSMYC</abbr>"),
	"MS":mark_safe("<abbr title=\"multiple sclerosis\">MS</abbr>"),
}
@register.simple_tag
def the(what):
	return CONSTS[what]if what in CONSTS else""

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
