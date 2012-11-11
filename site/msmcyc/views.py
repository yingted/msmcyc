#!/usr/bin/python
from django.views.generic.simple import direct_to_template
from django.shortcuts import render
import logging
from models import *

from django.template import TemplateDoesNotExist
from django.shortcuts import redirect
import re
useful=re.compile(r'^/(?!base_)([^\.]*?)(?:\.html)?$')
def index(request):
	match=useful.match(request.path)
	if match:
		try:
			return render(request,(match.group(1)or"index")+".html",{
				"updates":Update.all()
					.order("-added")
					.run(limit=3),
			})
		except TemplateDoesNotExist as e:
			logging.error(e)
	return redirect("/static"+request.path)

from django import forms
from ajax_forms import ajax_fields
class MyEmailField(forms.EmailField):
	def __init__(self,*args,**kwargs):
		kwargs["max_length"]=254
		forms.EmailField.__init__(self,*args,**kwargs)
		self.regex=re.compile("""(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])""")
ajax_fields.register(MyEmailField,ajax_fields.AjaxRegexField)
class ContactForm(forms.Form):
	name=forms.CharField(max_length=1000)
	sender=MyEmailField(label="Your email")
	about=forms.ChoiceField(choices=(
		("AboutUs","Stuff about this organization"),
		("HelpMe","I need help with..."),
		("Website","The website sucks/rocks!"),
		("Internet","My internet is down!"),
		("Other","Other"),
	))
	message=forms.CharField(widget=forms.widgets.Textarea)
	cc_sender=forms.BooleanField(required=False,label="CC myself")
import settings
from google.appengine.api.mail import EmailMessage
def contact(request):
	if request.method=="POST":
		form=ContactForm(request.POST)
		if form.is_valid():
			message=EmailMessage(
				sender="MSMYC mailer <youth.mssociety@gmail.com>",
				subject="[ContactUs_%s] %s <%s>"%tuple(map(form.cleaned_data.get,("about","name","sender"))),
				body=form.cleaned_data["message"],
				to="youth.mssociety@gmail.com",
			)
			if form.cleaned_data["cc_sender"]:
				message.cc="%s <%s>"%tuple(map(form.cleaned_data.get,("name","sender")))
			message.send()
			return direct_to_template(request,"contact_success.html")
	else:
		form=ContactForm()
	return render(request,"contact.html",{
		"form":form,
	})

from datetime import datetime
def events(request):
	return render(request,"events.html",{
		"events":Event.all()
			.filter("when >",datetime.now())
			.order("when")
	})

from google.appengine.ext.db.djangoforms import ModelForm
from google.appengine.api import users
def add_entity(request,what):
	class AddEntityForm(ModelForm):
		class Meta:
			model={"event":Event,"update":Update}[what]
	if users.is_current_user_admin():
		if request.method=="POST":
			form=AddEntityForm(request.POST)
			if form.is_valid():
				form.save()
				return render(request,"base_admin_success.html",{
					"success":"Added %s."%what,
					"form":form,
				})
		else:
			form=AddEntityForm()
		return render(request,"base_add.html",{
			"what":what,
			"form":form,
			"logout":users.create_logout_url("/"),
		})
	else:
		return redirect(users.create_login_url(request.path))
