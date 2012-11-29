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
	AddEntityForm.__name__="Add%sForm"%(string.capwords(what,"_").replace("_"," ")if isinstance(what,str)else what.__name__)
	return AddEntityForm
from django.forms.formsets import BaseFormSet,ManagementForm,formset_factory,TOTAL_FORM_COUNT,INITIAL_FORM_COUNT,MAX_NUM_FORM_COUNT
from django import forms
from noconflict import classmaker
class VolleyballManagementForm(ManagementForm,ModelForm):
	class Meta:
		model=VolleyballTeam
	__metaclass__=classmaker()
class BaseVolleyballFormSet(BaseFormSet):
	def clean(self):
		if any(self.errors):
			return
		pass
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
VolleyballFormSet=formset_factory(form_class(VolleyballPlayer),formset=BaseVolleyballFormSet,max_num=8)
