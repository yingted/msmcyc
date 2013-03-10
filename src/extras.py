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
	"MSMYC":mark_safe("<abbr title=\"Multiple Sclerosis Mississauga Youth Committee\">MSMYC</abbr>"),
	"MS":mark_safe("<abbr title=\"multiple sclerosis\">MS</abbr>"),
}
from msmcyc.settings import TEMPLATE_DEBUG as DEBUG
import logging
if DEBUG:
        @register.simple_tag
        def the(what):
                if what in CONSTS:
                        return CONSTS[what]
                logging.warning("{%% the '%s' %%} unresolved"%str(what).encode("string_escape"))
                return""
else:
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

from google.appengine.api import users
from django.template import Node
class IfAdminNode(Node):
	def __init__(self,nodelist):
		self.nodelist=nodelist
	def render(self,context):
		return self.nodelist.render(context)if users.is_current_user_admin()else""
@register.tag
def ifadmin(parser,token):
	nodelist=parser.parse(("endifadmin",))
	parser.delete_first_token()
	return IfAdminNode(nodelist)
class LogoutNode(Node):
	def render(self,context):
		return users.create_logout_url("/")if users.is_current_user_admin()else""
@register.tag
def logout(parser,token):
	return LogoutNode()
