import logging
logging.getLogger().setLevel(logging.NOTSET)
from google.appengine.ext import db
class Event(db.Model):
	id=db.StringProperty(default="",multiline=False)
	when=db.DateTimeProperty(required=True)
	link=db.LinkProperty(verbose_name="Title link")
	name=db.StringProperty(verbose_name="Event name",required=True)
	html=db.TextProperty(verbose_name="[HTML] body")
class Update(db.Model):
	added=db.DateTimeProperty(auto_now_add=True)
	title=db.StringProperty()
	html=db.TextProperty(verbose_name="[HTML] body")
from django.forms.util import ValidationError
def validator(f,required=True):
	def is_valid(val):
		if(val is not None or required)and not f(val):
			raise ValidationError("Invalid value: "+str(val))
	return is_valid
class Student(db.Model):
	added=db.DateTimeProperty(auto_now_add=True)
	first_name=db.StringProperty(required=True)
	last_name=db.StringProperty(required=True)
	school=db.StringProperty(verbose_name="School")
	grade=db.IntegerProperty(required=True,validator=validator(lambda x:9<=x<=12))
	gender=db.StringProperty(choices=("Male","Female"),required=True)
	email=db.EmailProperty(required=True)
	phone=db.PhoneNumberProperty()
class VolleyballPlayer(db.Model):
	added=db.DateTimeProperty(auto_now_add=True)
	first_name=db.StringProperty()
	last_name=db.StringProperty()
	school=db.StringProperty(verbose_name="School")
	grade=db.IntegerProperty(required=True,validator=validator(lambda x:9<=x<=12))
	gender=db.StringProperty(choices=("Male","Female"),required=True,verbose_name="Gender (min. 2 girls at any time)")
	email=db.EmailProperty()
	phone=db.PhoneNumberProperty()
import random
from words import words
class HasRandom(db.Model):
	random=db.StringProperty(name="random")#too much work to fix
	def __init__(self,*args,**kwargs):
		if"random"not in kwargs or not kwargs["random"]:
			kwargs["random"]="_".join(random.choice(words)for _ in xrange(4))
		super(HasRandom,self).__init__(*args,**kwargs)
import re
normalize_kill=re.compile(u"[-\t _]",re.UNICODE)
def normalize_name(name):
	return name and normalize_kill.sub("",name).lower()#kill unpronounceables
class VolleyballTeam(db.Model):
	name=db.StringProperty(verbose_name="Team name",required=False)
	index_key=db.StringProperty()
	team_type=db.StringProperty(choices=("Competitive","Recreational"),required=True)
	date=db.DateTimeProperty(auto_now_add=True)
single_recreational=VolleyballTeam.all().filter("index_key","_single_recreational").get()
single_competitive=VolleyballTeam.all().filter("index_key","_single_competitive").get()
import string
from legacy.google.appengine.ext.db.djangoforms import ModelForm
def form_class(what):
	is_str=type(what)in(unicode,str)
	class AddEntityForm(ModelForm):
		class Meta:
			model={
				"event":Event,
				"update":Update,
				"volleyball_player":VolleyballPlayer,
				"mswalk":MsWalkVolunteer,
				"carnations":MsAwarenessVolunteer,
				"api_key":ApiKey,
			}[what]if is_str else what
			exclude=_exclude
	AddEntityForm.__name__="Add%sForm"%(string.capwords(str(what),"_").replace("_"," ")if is_str else what.__name__)
	return AddEntityForm
from django.forms.formsets import BaseFormSet,ManagementForm,formset_factory,TOTAL_FORM_COUNT,INITIAL_FORM_COUNT,MAX_NUM_FORM_COUNT
from django import forms
from noconflict import classmaker
_exclude=("random","index_key","date","added",)
class VolleyballManagementForm(ManagementForm,ModelForm):
	class Meta:
		model=VolleyballTeam
		exclude=_exclude
	def save(self,*args,**kwargs):
		return ModelForm.save(self,*args,**kwargs)
	__metaclass__=classmaker()
def to_dict(ent):#dereferences keys
	klass=ent.__class__
	return dict([(k,v.__get__(ent,klass))for k,v in klass.properties().iteritems()]+[(k,getattr(ent,k))for k in klass.__dict__ if not k.startswith("_")])
from django.conf import settings
from django.utils import dateformat
from datetime import datetime
from django.utils.safestring import mark_safe,SafeData
def pretty(elt):
	if isinstance(elt,list):
		return"; ".join(map(pretty,elt))
	if isinstance(elt,datetime):
		return dateformat.format(elt,settings.DATETIME_FORMAT)
	if isinstance(elt,(basestring,SafeData)):
		return elt
	return str(elt)
formatters={
		"shifts":lambda data,sep="<br>",dash="&ndash;":mark_safe(sep.join("May "+str(int(float(shift.split(",")[0]))//100)+", "+dash.join("%d:%02d %sm"%((int(when)%100-1)%12+1,int(when%1*60),"a"if int(when)%100<12 else"p")for when in map(float,shift.split(",")))for shift in data)),
}
def to_pretty_dict(ent):
	klass=ent.__class__
	props=klass._properties
	title={}
	ret={}
	for k,v in klass.properties().iteritems():
		if k not in _exclude:
			title[k]=props[k].verbose_name or string.capwords(k.replace("_"," "))
			assert title[k]not in ret
			ret[title[k]]=v.__get__(ent,klass)
	for k in klass.__dict__:
		if not k.startswith("_")and k not in props and k not in _exclude:
			title[k]=string.capwords(k.replace("_"," "))
			assert title[k]not in ret
			ret[title[k]]=getattr(ent,k)
	for k,f in formatters.iteritems():
		if k in title:
			ret[title[k]]=f(ret[title[k]])
	return dict((k,pretty(v))for k,v in ret.iteritems())
def team_by_name(name):
	res=VolleyballTeam.all().filter("index_key",name).fetch(2)
	if len(res)==1:
		return res[0]
class BaseVolleyballFormSet(BaseFormSet):
	def clean(self):
		if any(self.errors):
			return
		if not any(form.is_valid() for form in self):
			raise ValidationError("You need at least one team member")
	@BaseFormSet.management_form.getter
	def management_form(self):
		"""Returns the ManagementForm instance for this FormSet."""
		if self.is_bound:
			form = VolleyballManagementForm(self.data, auto_id=self.auto_id, prefix=self.prefix)
			if not form.is_valid():
				raise ValidationError('ManagementForm data is missing or has been tampered with')
		else:
			form = VolleyballManagementForm(auto_id=self.auto_id, prefix=self.prefix, initial={
				TOTAL_FORM_COUNT: self.total_form_count(),
				INITIAL_FORM_COUNT: self.initial_form_count(),
				MAX_NUM_FORM_COUNT: self.max_num
			})  
		return form
	def save(self):
		event=self.management_form.save(commit=False)
		if event.name:
			event.index_key=normalize_name(event.name)
			oldevent=team_by_name(event.index_key)
			if oldevent:
				event=oldevent
			else:
				event.put()
		elif event.team_type=="Recreational":
			event=single_recreational
		elif event.team_type=="Competitive":
			event=single_competitive
		else:
			logger.warning("Invalid team type %s"%team_type)
		logging.info("Team: %s"%to_dict(event))
		i=0
		for form in self:
			if form.is_valid()and form.has_changed():
				props=to_dict(form.save(commit=False))
				logging.info("Player: %s"%props)
				props["parent"]=event
				VolleyballPlayer(**props).put()
			i+=1
		return event
VolleyballFormSet=formset_factory(form_class(VolleyballPlayer),formset=BaseVolleyballFormSet,max_num=1)
class VolleyballMatch(db.Model):
	start=db.TimeProperty()
	end=db.TimeProperty()
	a=db.ReferenceProperty(VolleyballTeam)
	b=db.StringProperty()
	a_points=db.IntegerProperty()
	b_points=db.IntegerProperty()
waiver=lambda:db.BooleanProperty(required=True,verbose_name="By checking this box, I hereby waive MS Society of Canada, MS Mississauga Youth Committee and their respective members from any liability of injury, loss or damage to personal property associated with activities participated in this event.")
class MsWalkVolunteer(Student):
	face_painting=db.BooleanProperty(verbose_name="Face-painting")
	making_balloon_animals=db.BooleanProperty()
	route_marshall=db.BooleanProperty()
	registration_helper=db.BooleanProperty()
	food_helper=db.BooleanProperty()
	iagree=waiver()
shift=re.compile(r"[0-9]*(?:\.[0-9]+)?,[0-9]*(?:\.[0-9]+)?")
class MsAwarenessVolunteer(HasRandom):
	added=db.DateTimeProperty(auto_now_add=True)
	first_name=db.StringProperty(required=True)
	last_name=db.StringProperty(required=True)
	@property
	def name(self):
		return self.first_name+" "+self.last_name
	name_of_parent=db.StringProperty()
	gender=db.StringProperty(choices=("Male","Female"),required=True)
	grade=db.IntegerProperty(required=True,validator=validator(lambda x:9<=x<=12))
	school=db.StringProperty(verbose_name="School")
	address=db.PostalAddressProperty()
	postal_code=db.StringProperty(validator=validator(re.compile(r"[a-z][0-9][a-z] ?[0-9][a-z][0-9]",re.I).match,required=False))
	email=db.EmailProperty(required=True)
	phone=db.PhoneNumberProperty(required=True)
	location=db.StringProperty(choices=("Erin Mills Town Centre","Dixie Value Mall","Clarkson GO","Cooksville GO","Meadowvale GO","Port Credit GO","Streetsville GO","No preference"),required=True)
	shifts=db.StringListProperty(verbose_name="Shifts I can make",required=True,validator=validator(lambda x:x and all(shift.match(x)for x in x)))
	max_shifts=db.IntegerProperty(required=True,validator=validator(lambda x:1<=x<=15),verbose_name="Maximum number of shifts I would like to attend")
	iagree=waiver()
class ApiKey(HasRandom):
	pass

import carnations
signup_conf={
	"volleyball":{
		"name":"volleyball tournament",
		"form":VolleyballFormSet,
		"model":VolleyballTeam,
		"children":VolleyballPlayer,
		"description":"<p>If you play regularly or are on a team, it is recommended that you sign up to play competitively.</p>",
		"order":"added",
		"export":(
			(VolleyballPlayer,("email","first_name","last_name","gender","grade","phone","school")+(lambda ent:"%s (%d)"%(ent.parent().name,ent.parent().key().id())if ent.parent()else"",)),
		),
	},
	"mswalk":{
		"name":"MS Walk",
		"form":form_class("mswalk"),
		"template":"base_mswalk.html",
		"model":MsWalkVolunteer,
		"description":"""<p>The Annual MS Walk is happening at Celebration Square on <strong>Sunday, May 26<sup>th</sup> from 7am to 4pm</strong>. We are looking for eager, willing and enthusiastic volunteers to help out with this year's MS Walk. Volunteer responsibilities are listed below; please make sure you are available before signing up.<br>Together, we can improve the life-enriching programs and services available to MS patients in Mississauga.</p>
		<p>Please make sure you are available on May 26<sup>th</sup> from 7am to 4pm before signing up.</p>""",
		"export":(
			(MsWalkVolunteer,("email","first_name","last_name","gender","grade","phone","school")),
		),
	},
	"carnations":{
		"name":"Carnations Campaign",
		"form":form_class("carnations"),
		"model":MsAwarenessVolunteer,
		"description":"""{% load extras %}<p>The carnation. It's more than just a yellow flower, it's Canada's oldest and most recognized symbol of hope in the quest to end multiple sclerosis.</p>
		<p>Many Canadians living with multiple sclerosis are mothers. Others, either children or adults, have mothers affected by this disease, because women are diagnosed with MS three times as often as men. That's why every year the MS Carnation Campaign takes place over Mother's Day weekend</p>
		<p>From <strong>May 9-11, 2013</strong>, the {% the "MSMYC" %} will be proud to join the thousands of volunteers in more than 280 communities across Canada and show our dedication to finding a cure to this disease. By selling carnations on street corners, malls and other public spaces, the youths of Mississauga will not only take leadership role by actively engaging with members of the communities, but also raise awareness and funds for Multiple Sclerosis. We are seeking passionate and friendly volunteers to help us out.</p>
		<p>Sound like something your interested in? Sign up today!</p>""",
		"order":"added",
		"export":(
			(MsAwarenessVolunteer,("name","phone","email","address","postal_code","location",lambda ent:formatters["shifts"](ent.shifts,"; ","-"))),#excel hates utf-8, so no \u2012
		),
		"view_postheader":"base_carnations_pdf.html",
		"print":{
			"pdf":carnations.respond,
		},
	},
}
from django.template import Template
for conf in signup_conf.itervalues():
	if"description"in conf:
		conf["description"]=Template(conf["description"])
