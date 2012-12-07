from google.appengine.ext import db
class Event(db.Model):
	when=db.DateTimeProperty(required=True)
	link=db.LinkProperty(verbose_name="Map link")
	name=db.StringProperty(verbose_name="Event name",required=True)
	html=db.TextProperty(verbose_name="[HTML] body")
	signup=db.TextProperty(verbose_name="[HTML] Embed code")
	stats=db.TextProperty(verbose_name="[HTML] stats")
class Update(db.Model):
	added=db.DateTimeProperty(auto_now_add=True)
	title=db.StringProperty()
	html=db.TextProperty(verbose_name="[HTML] body")
from django.forms.util import ValidationError
def validator(f):
	def is_valid(val):
		if not f(val):
			raise ValidationError("Invalid value")
	return is_valid
class VolleyballPlayer(db.Model):
	added=db.DateTimeProperty(auto_now_add=True)
	first_name=db.StringProperty()
	last_name=db.StringProperty()
	school=db.StringProperty(verbose_name="School")
	grade=db.IntegerProperty(validator=validator(lambda x:9<=x<=12))
	gender=db.StringProperty(choices=("Male","Female"),required=True)
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
	return normalize_kill.sub("",name).lower()#kill unpronounceables
class VolleyballTeam(db.Model):
	name=db.StringProperty(verbose_name="Team name")
	index_key=db.StringProperty()
	team_type=db.StringProperty(choices=("Competitive","Recreational"),required=True)
	date=db.DateTimeProperty(auto_now_add=True)
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
			}[what]if is_str else what
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
def to_dict(ent):
	klass=ent.__class__
	return dict((k,v.__get__(ent,klass))for k,v in klass.properties().iteritems())
def to_pretty_dict(ent):
	klass=ent.__class__
	props=klass.__dict__
	return dict((props[k].verbose_name or string.capwords(k.replace("_"," ")),v)for k,v in to_dict(ent).iteritems()if k not in _exclude)
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
		newevent=self.management_form.save(commit=False)
		newevent.index_key=normalize_name(newevent.name)
		event=team_by_name(newevent.index_key)
		if not event:
			event=newevent
			event.put()
		i=0
		for form in self:
			if form.is_valid()and form.has_changed():
				props=to_dict(form.save(commit=False))
				props["parent"]=event
				VolleyballPlayer(**props).put()
			i+=1
		return event
VolleyballFormSet=formset_factory(form_class(VolleyballPlayer),formset=BaseVolleyballFormSet,max_num=1)
def signup_conf(event):
	return{
		"volleyball":{
			"name":"volleyball tournament",
			"form":VolleyballFormSet,
			"model":VolleyballTeam,
			"children":VolleyballPlayer,
			"order":"added",
		},
	}[event]
