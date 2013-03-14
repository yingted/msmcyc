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
def validator(f):
	def is_valid(val):
		if not f(val):
			raise ValidationError("Invalid value")
	return is_valid
class Student(db.Model):
	added=db.DateTimeProperty(auto_now_add=True)
	first_name=db.StringProperty(required=True)
	last_name=db.StringProperty(required=True)
	school=db.StringProperty(verbose_name="School")
	grade=db.IntegerProperty(required=True,validator=validator(lambda x:9<=x<=12),choices=xrange(9,13))
	gender=db.StringProperty(choices=("Male","Female"),required=True)
	email=db.EmailProperty(required=True)
	phone=db.PhoneNumberProperty()
class VolleyballPlayer(db.Model):
	added=db.DateTimeProperty(auto_now_add=True)
	first_name=db.StringProperty()
	last_name=db.StringProperty()
	school=db.StringProperty(verbose_name="School")
	grade=db.IntegerProperty(validator=validator(lambda x:9<=x<=12))
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
def to_pretty_dict(ent):
	klass=ent.__class__
	return dict([(klass._properties[k].verbose_name or string.capwords(k.replace("_"," ")),v.__get__(ent,klass))for k,v in klass.properties().iteritems()]+[(string.capwords(k.replace("_"," ")),getattr(ent,k))for k in klass.__dict__ if not k.startswith("_")])
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
class MsWalkVolunteer(Student):
	pass
class MsAwarenessVolunteer(HasRandom):
	added=db.DateTimeProperty(auto_now_add=True)
	first_name=db.StringProperty(required=True)
	last_name=db.StringProperty(required=True)
	@property
	def name(self):
		return self.first_name+" "+self.last_name
	school=db.StringProperty(verbose_name="School")
	grade=db.IntegerProperty(required=True,validator=validator(lambda x:9<=x<=12),choices=xrange(9,13))
	gender=db.StringProperty(choices=("Male","Female"),required=True)
	may_9=db.BooleanProperty()
	may_10=db.BooleanProperty()
	may_11=db.BooleanProperty()
	available="may_9","may_10","may_11"
	face_painting=db.BooleanProperty(verbose_name="Face-painting")
	making_balloon_animals=db.BooleanProperty()
	route_marshall=db.BooleanProperty()
	registration_helper=db.BooleanProperty()
	food_helper=db.BooleanProperty()
	interest="face_painting","making_balloon_animals","route_marshall","registration_helper","food_helper"
	address=db.StringProperty(required=True)
	postal=db.StringProperty(verbose_name="Postal Code")
	city=db.StringProperty(required=True)
	province=db.StringProperty(required=True)
	cell=db.StringProperty(verbose_name="Cell Phone")
	phone=db.PhoneNumberProperty(required=True)
	business=db.StringProperty(verbose_name="Business Phone")
	email=db.EmailProperty(required=True)
	perm=db.BooleanProperty(verbose_name="I give permission to be emailed")
	contact=db.StringProperty(verbose_name="Emergency contact name")
	contactphone=db.StringProperty(verbose_name="Emergency contact home phone")
	contactbusiness=db.StringProperty(verbose_name="Emergency contact business phone")
	rationale=db.StringProperty(verbose_name="Why are you interested? What do you hope to accomplish?")
	fund=db.BooleanProperty(verbose_name="Fundraising")
	out=db.BooleanProperty(verbose_name="Outreach")
	adm=db.BooleanProperty(verbose_name="Administrative")
	com=db.BooleanProperty(verbose_name="Committee")
	board=db.BooleanProperty(verbose_name="Board Member")
	msam=db.BooleanProperty(verbose_name="MS Ambassador")
	other=db.BooleanProperty()
	length=db.StringProperty(verbose_name="I plan to commit for this long")
	adv=db.BooleanProperty(verbose_name="Advertisement brought me here")
	friend=db.BooleanProperty(verbose_name="A friend brought me here")
	mssoc=db.BooleanProperty(verbose_name="MS Society brought me here")
	vc=db.BooleanProperty(verbose_name="A volunteer centre brought me here")
	other2=db.BooleanProperty(verbose_name="I heard about this from somewhere else")
	hear=db.StringProperty(verbose_name="Where else did you hear about this?")
	inst1=db.StringProperty(verbose_name="Institution 1")
	course1=db.StringProperty(verbose_name="Course/Degree/Diploma 1")
	date1=db.StringProperty(verbose_name="Date of Study 1")
	inst2=db.StringProperty(verbose_name="Institution 2")
	course2=db.StringProperty(verbose_name="Course/Degree/Diploma 2")
	date2=db.StringProperty(verbose_name="Date of Study 2")
	inst3=db.StringProperty(verbose_name="Institution 3")
	course3=db.StringProperty(verbose_name="Course/Degree/Diploma 3")
	date3=db.StringProperty(verbose_name="Date of Study 3")
	job=db.StringProperty(multiline=True,validator=validator(lambda s:not s or len(s)<201),verbose_name="Prior jobs (max 200 chars)")
	skills=db.StringProperty(multiline=True,validator=validator(lambda s:not s or len(s)<201),verbose_name="Relevant skills (max 200 chars)")
	experience=db.StringProperty(multiline=True,validator=validator(lambda s:not s or len(s)<201),verbose_name="Other experience (max 200 chars)")
	ref1name=db.StringProperty(verbose_name="Reference 1")
	ref1phone=db.StringProperty(verbose_name="Reference 1 home phone")
	ref1bus=db.StringProperty(verbose_name="Reference 1 bus phone")
	ref1rel=db.StringProperty(verbose_name="Reference 1 relationship to you")
	ref2name=db.StringProperty(verbose_name="Reference 2")
	ref2phone=db.StringProperty(verbose_name="Reference 2 home phone")
	ref2bus=db.StringProperty(verbose_name="Reference 2 bus phone")
	ref2rel=db.StringProperty(verbose_name="Reference 2 relationship to you")
	comments=db.StringProperty(multiline=True)
	iagree=db.BooleanProperty(required=True,verbose_name="By checking this box, I authorize MS Society of Canada to obtain references from the individuals listed above, and I certify that the information I have provided is true and complete to the best of my knowledge.")
import carnations
def signup_conf(event):
	return{
		"volleyball":{
			"name":"volleyball tournament",
			"form":VolleyballFormSet,
			"model":VolleyballTeam,
			"children":VolleyballPlayer,
			"order":"added",
			"export":(
				(VolleyballPlayer,("email","first_name","last_name","gender","grade","phone","school")+(lambda ent:"%s (%d)"%(ent.parent().name,ent.parent().key().id())if ent.parent()else"",)),
			),
		},
		"mswalk":{
			"name":"MS Walk",
			"form":form_class("mswalk"),
			"model":MsWalkVolunteer,
			"export":(
				(MsWalkVolunteer,("email","first_name","last_name","gender","grade","phone","school")),
			),
		},
		"carnations":{
			"name":"Carnations Campaign",
			"form":form_class("carnations"),
			"model":MsAwarenessVolunteer,
			"order":"added",
			"export":(
				(MsAwarenessVolunteer,("name","phone","email")+MsAwarenessVolunteer.interest+MsAwarenessVolunteer.available+("comments","address","city","province","postal")),
			),
			"view_postheader":"base_carnations_pdf.html",
			"print":{
				"pdf":carnations.respond,
			},
		},
	}[event]
