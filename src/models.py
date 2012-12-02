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
class VolleyballPlayer(db.Model):
	first_name=db.StringProperty()
	last_name=db.StringProperty()
	gender=db.StringProperty(choices=("Male","Female"))
	email=db.EmailProperty()
import random
from words import words
class HasRandom(db.Model):
	random=db.StringProperty(name="random")#too much work to fix
	def __init__(self,*args,**kwargs):
		if"random"not in kwargs or not kwargs["random"]:
			kwargs["random"]="_".join(random.choice(words)for _ in xrange(4))
		super(HasRandom,self).__init__(*args,**kwargs)
class VolleyballTeam(HasRandom):
	team_type=db.StringProperty(choices=("Competitive","Recreational"))
	name=db.StringProperty(verbose_name="Team name")
	email=db.EmailProperty(verbose_name="Account email",required=True)
	phone=db.PhoneNumberProperty(verbose_name="Contact number")
	school=db.StringProperty(verbose_name="School(s) to mention")
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
class VolleyballManagementForm(ManagementForm,ModelForm):
	class Meta:
		model=VolleyballTeam
		exclude=("random",)
	def save(self,*args,**kwargs):
		return ModelForm.save(self,*args,**kwargs)
	__metaclass__=classmaker()
from django.forms.util import ValidationError
def to_dict(ent):
	klass=ent.__class__
	return dict((k,v.__get__(ent,klass))for k,v in klass.properties().iteritems())
class BaseVolleyballFormSet(BaseFormSet):
	def __init__(self,*args,**kwargs):
		rebuild="instance"in kwargs
		if rebuild:
			self.instance=kwargs["instance"]
			self.players=VolleyballPlayer.all().ancestor(self.instance).fetch(limit=8)
			kwargs["initial"]=map(to_dict,self.players)
			del kwargs["instance"]
		else:
			self.instance=None
		super(BaseVolleyballFormSet,self).__init__(*args,**kwargs)
		if self.instance:
			team=to_dict(self.instance)
			team.update({
				TOTAL_FORM_COUNT:8,
				INITIAL_FORM_COUNT:8,
				MAX_NUM_FORM_COUNT:8,
			})
			if self.data=={}:
				self.data=dict(("form-"+k,v)for k,v in team.iteritems())
				self.is_bound=True
	def clean(self):
		if any(self.errors):
			return
		deleted=self.deleted_forms()
		forms=[form for form in self if form.is_valid()and form not in deleted]
		if len(forms)==0:
			raise ValidationError("You need at least one team member")
		if len(forms)>1 and sum(int(form.cleaned_data["gender"]=="Female")for form in forms)<2:
			raise ValidationError("You need at least 2 female players on the court")
	@BaseFormSet.management_form.getter
	def management_form(self):
		"""Returns the ManagementForm instance for this FormSet."""
		if self.is_bound:
			form = VolleyballManagementForm(self.data, auto_id=self.auto_id, prefix=self.prefix, instance=self.instance)
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
		event=self.management_form.save()
		i=0
		deleted=self.deleted_forms
		for form in self:
			if form in deleted and i<len(self.players):
				VolleyballPlayer(key=self.players[i].key()).delete()
			elif form.is_valid()and form.has_changed():
				props=to_dict(form.save(commit=False))
				if self.instance and i<len(self.players):
					props["key"]=self.players[i].key()
				else:
					props["parent"]=event
				VolleyballPlayer(**props).put()
			i+=1
		return event
VolleyballFormSet=formset_factory(form_class(VolleyballPlayer),formset=BaseVolleyballFormSet,max_num=8,extra=8,can_delete=True)
def signup_conf(event):
	return{
		"volleyball":{
			"name":"volleyball tournament",
			"form":VolleyballFormSet,
			"model":VolleyballTeam,
		},
	}[event]
