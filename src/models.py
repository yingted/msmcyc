from google.appengine.ext import db
class Event(db.Model):
	when=db.DateTimeProperty()
	link=db.LinkProperty(verbose_name="Map link")
	name=db.StringProperty(verbose_name="Event name")
	html=db.TextProperty(verbose_name="[HTML] body")
	signup=db.TextProperty(verbose_name="[HTML] Embed code")
	stats=db.TextProperty(verbose_name="[HTML] stats")
class Update(db.Model):
	added=db.DateTimeProperty(auto_now_add=True)
	title=db.StringProperty()
	html=db.TextProperty(verbose_name="[HTML] body")
class VolleyballPlayer(db.Model):
	male=db.BooleanProperty()
	first_name=db.StringProperty()
	last_name=db.StringProperty()
	email=db.EmailProperty()
	phone=db.PhoneNumberProperty()
class VolleyballTeam(db.Model):
	name=db.StringProperty(verbose_name="Team name")
	school=db.StringProperty()
from legacy.google.appengine.ext.db.djangoforms import ModelForm
import string
def form_class(what):
	class AddEntityForm(ModelForm):
		class Meta:
			model={
				"event":Event,
				"update":Update,
				"volleyball_player":VolleyballPlayer,
			}[what]if isinstance(what,str)else what
	AddEntityForm.__name__="Add%sForm"%string.capwords(what,"_").replace("_"," ")
	return AddEntityForm
from django.forms.formsets import BaseFormSet,formset_factory
from django import forms
class BaseVolleyballFormSet(BaseFormSet):
	def __init__(self,*args,**kwargs):
		if"initial"in kwargs:
			del kwargs["initial"]
		super(BaseVolleyballFormSet,self).__init__(self,initial=6,*args,**kwargs)
	def clean(self):
		if any(self.errors):
			return
		pass
	@BaseFormSet.management_form.getter
	def management_form(self):
		from views import logging
		logging.debug(BaseFormSet.management_form.fget)
		form=BaseFormSet.management_form.fget(self)
		logging.debug(form)
		return form
VolleyballFormSet=formset_factory(form_class(VolleyballPlayer),formset=BaseVolleyballFormSet,max_num=8)
