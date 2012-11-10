#!/usr/bin/python
from django.views.generic.simple import direct_to_template
import logging

from django.template import TemplateDoesNotExist
from django.shortcuts import redirect
import re
useful=re.compile(r'^/(?!base_)([^\.]*?)(?:\.html)?$')
def index(request):
	match=useful.match(request.path)
	if match:
		try:
			return direct_to_template(request,(match.group(1)or"index")+".html")
		except TemplateDoesNotExist as e:
			logging.error(e)
	return redirect("/static"+request.path)

from django import forms
from django.shortcuts import render
class ContactForm(forms.Form):
	name=forms.CharField(max_length=1000)
	sender=forms.EmailField(label="Your email")
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

from models import Event
from datetime import datetime
def events(request):
	return render(request,"event.html",{
		Event.all()
			.filter("when >",datetime.now())
			.order("when")
	})

def add_event(request):
	if request.method=="POST":
		form=AddEventForm(request.POST)
		if form.is_valid():
			pass
			return direct_to_template(request,"base_admin_success.html")
	else:
		form=AddEventForm()
	return render(request,"add_event.html",{
		"form":form,
	})
