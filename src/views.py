#!/usr/bin/python
from django.views.generic.simple import direct_to_template
from django.shortcuts import render
import logging
logging.getLogger().setLevel(logging.NOTSET)

from models import *

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
from django.core.validators import email_re
from ajax_forms import ajax_fields
class MyEmailField(forms.EmailField):
	def __init__(self,*args,**kwargs):
		kwargs["max_length"]=254
		forms.EmailField.__init__(self,*args,**kwargs)
		self.regex=email_re
ajax_fields.register(MyEmailField,ajax_fields.AjaxRegexField)
class ContactForm(forms.Form):
	name=forms.CharField(max_length=1000)
	sender=MyEmailField(label="Your email")
	about=forms.ChoiceField(choices=(
		("Sponsors","Becoming a sponsor"),
		("Volleyball","MS Volleyball Tournament"),
		("AboutUs","General information"),
		("HelpMe","I need help with..."),
		("Website","Website issues"),
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
from django.template import Template,RequestContext
def events(request):
	events=Event.all()\
		.filter("when >",datetime.now())\
		.order("when")\
		.fetch(None)
	for event in events:
		event.signup=Template(event.signup).render(RequestContext(request))
	return render(request,"events.html",{
		"events":events,
	})

from legacy.google.appengine.ext.db.djangoforms import ModelForm
from google.appengine.api import users
edit_entity="^/add_%s/([1-9][0-9]*)$"#TODO implement
def add_entity(request,what):
	if users.is_current_user_admin():
		ent=None
		match=re.match(edit_entity%what,request.path)
		if match:
			klass=form_class(what)
			ent=klass.Meta.model.get_by_id(long(match.group(1)))
		if request.method=="POST":
			form=form_class(what)(request.POST,instance=ent)
			if form.is_valid():
				return render(request,"base_admin_success.html",{
					"success":"Saved %s"%what,
					"form":form,
					"what":what,
					"ent":form.save(),
				})
		else:
			form=form_class(what)(instance=ent)
		return render(request,"base_add.html",{
			"what":what,
			"form":form,
			"logout":users.create_logout_url("/"),
		})
	else:
		return redirect(users.create_login_url(request.path))
from django.core.exceptions import PermissionDenied
def signup(request,event):
	conf=signup_conf(event)
	if request.method=="POST":
		form=conf["form"](request.POST)
		if form.is_valid():
			ent=form.save()
			uri=request.build_absolute_uri("/view/%s/%s"%(event,ent.key().id()))
			if event=="volleyball":
				player=next(form for form in form if form.is_valid()).cleaned_data
				EmailMessage(
					sender="MS Youth Committee <info@msyouthmississauga.org>",
					subject="MS Volleyball Tournament Confirmation",
					body="""Hello!

This email is to confirm that you are officially registered for the 1st
Annual MS Volleyball Tournament at *Mentor College* on* Saturday, January
5th, 2013* from 8AM to 5PM. If you are part of a team, registration is
complete once ALL members of your team signs up on our website:
www.msyouthmississauga.org and hands in the appropriate documents before
tournament day.

Remember that the registration fee is minimum $10/person (you are welcome
	to donate more!). As well, you can get a pledge form from your student
ambassador at your respective schools. It is encouraged that you approach
your family, friends, parents\u2019 colleagues or workplaces to sponsor you. The
pledge form is also as attached. *If you raise more than $50, you will be
exempt from paying the $10 registration fee.* Remember that all proceeds go
towards research for multiple sclerosis!


*Please give your registration fee, pledge forms, and liability forms (attached) to
your student ambassador before Thursday, December 20th, as they will drop
off these three items to us. Ensure that you sign off on the amount of
money that you paid/raised.
*


**

If you are unable to give these three items to your student ambassador
before Thursday, December 20th, you are asked to bring them yourselves or
on Saturday December 22nd (more details to come). All payment and liability
forms must be received* BEFORE *the day of the tournament. Listed below is
our current network of student ambassadors; please refer to your respective
school's ambassadors to arrange the collection of payment/liability forms.

*
*

*Network of Student Ambassadors: *

Cawthra Secondary School: Jesse Yan

Glenforest Secondary School: Edward Chen, Mike Wang, Ruhi Kokal

Gordon Graydon Memorial Secondary School: Moksha Patel, Ayesha Madan

John Fraser Secondary School: Christine Xin, Braeden Page, Daaniya Tariq

Lorne Park Secondary School: Kim Ren, Jenny Qian

Philopateer Christian College: George Keliny

Rick Hansen Secondary School: Supriya Gopalan, Shiwei Zhuang

St. Francis Xavier Secondary School: Natasha Mathew

St. Marcellinus Secondary School: Eva Xu

Stephen Lewis Secondary School: Sathu Sivalogarajah, Anish Arora

The Woodlands Secondary School: Jonathan Martins, Ashley Tam, April Liu



If there is no student ambassador at your school, please drop off your
*registration
fee, pledge forms, and liability forms* (attached) in person to Mississauga Central
Library on Thursday, December 20th to one of the Executives present. Thank
you for your interest and to view your team info, visit this URL:

%s

We look forward to seeing you on the court!


Cheers,
*Cathy L.
*
MS Mississauga Youth Committee Executive
www.msyouthmississauga.org
"""%uri,
					html="""<p class="MsoNormal" style="margin-bottom:12.0pt;line-height:normal"><span style="font-size:12.0pt;font-family:&quot;Times New Roman&quot;,&quot;serif&quot;">Hello! </span></p>

<p class="MsoNormal" style="margin-bottom:12.0pt;line-height:normal"><span style="font-size:12.0pt;font-family:&quot;Times New Roman&quot;,&quot;serif&quot;">This email is to confirm that you
are officially registered for the 1st Annual MS Volleyball Tournament at <b>Mentor
College</b> on<b> Saturday, January 5th, 2013</b> from 8AM to 5PM. If you are part
of a team, registration is complete once ALL members of your team signs up on
our website: <a href="http://www.msyouthmississauga.org">www.msyouthmississauga.org</a>
and hands in the appropriate documents before tournament day. <span style> </span></span></p>

<p class="MsoNormal" style="margin-bottom:0in;margin-bottom:.0001pt;line-height:normal"><span style="font-size:12.0pt;font-family:&quot;Times New Roman&quot;,&quot;serif&quot;" lang="EN-CA">Remember
that the registration fee is minimum $10/person (you are welcome to donate
more!). As well, you can get a pledge form from your student ambassador at your
respective schools. It is encouraged that you approach your family, friends,
parents&#8217; colleagues or workplaces to sponsor you. The pledge form is also as
attached. <b>If you raise more than $50, you will be exempt from paying the $10
registration fee.</b> Remember that all proceeds go towards research for
multiple sclerosis! </span></p>

<p class="MsoNormal" style="margin-bottom:0in;margin-bottom:.0001pt;line-height:normal"><span style="font-size:12.0pt;font-family:&quot;Times New Roman&quot;,&quot;serif&quot;" lang="EN-CA"></span></p><p class="MsoNormal" style="margin-bottom:0in;margin-bottom:.0001pt;line-height:normal">

<br><span style="font-size:12.0pt;font-family:&quot;Times New Roman&quot;,&quot;serif&quot;" lang="EN-CA"></span><span style="font-size:12.0pt;font-family:&quot;Times New Roman&quot;,&quot;serif&quot;"></span></p>

<p class="MsoNormal" style="margin-bottom:0in;margin-bottom:.0001pt;line-height:normal"><b><span style="font-size:12.0pt;font-family:&quot;Times New Roman&quot;,&quot;serif&quot;;color:red" lang="EN-CA">Please give your <i style><u>registration
fee</u></i>, <i style><u>pledge forms</u></i>, and
<i style><u>liability forms</u></i> (attached) to your
student ambassador before Thursday, December 20th, as they will drop off these
three items to us. Ensure that you sign off on the amount of money that you
paid/raised. <br></span></b></p><p class="MsoNormal" style="margin-bottom:0in;margin-bottom:.0001pt;line-height:normal"><br><b><span style="font-size:12.0pt;font-family:&quot;Times New Roman&quot;,&quot;serif&quot;;color:red" lang="EN-CA"></span></b><span style="font-size:12.0pt;font-family:&quot;Times New Roman&quot;,&quot;serif&quot;"></span></p>



<p class="MsoNormal" style="margin-bottom:0in;margin-bottom:.0001pt;line-height:normal"><span style="font-size:12.0pt;font-family:&quot;Times New Roman&quot;,&quot;serif&quot;" lang="EN-CA">If
you are unable to give these three items to your student ambassador before
Thursday, December 20th, you are asked to bring them yourselves or on Saturday
December 22nd (more details to come). All payment and liability forms must be
received<b> BEFORE </b>the day of the tournament. Listed below is our current
network of student ambassadors; please refer to your respective school&#39;s
ambassadors to arrange the collection of payment/liability forms. </span><span style="font-size:12.0pt;font-family:&quot;Times New Roman&quot;,&quot;serif&quot;"></span></p>

<p class="MsoNormal" style="margin-bottom:0in;margin-bottom:.0001pt;line-height:normal"><b><span style="font-size:12.0pt;font-family:&quot;Times New Roman&quot;,&quot;serif&quot;" lang="EN-CA"><br></span></b></p><p class="MsoNormal" style="margin-bottom:0in;margin-bottom:.0001pt;line-height:normal">

<b><span style="font-size:12.0pt;font-family:&quot;Times New Roman&quot;,&quot;serif&quot;" lang="EN-CA">Network
of Student Ambassadors: </span></b><span style="font-size:12.0pt;font-family:&quot;Times New Roman&quot;,&quot;serif&quot;"></span></p>

<p class="MsoNormal" style="margin-bottom:0in;margin-bottom:.0001pt;line-height:normal"><span style="font-size:12.0pt;font-family:&quot;Times New Roman&quot;,&quot;serif&quot;" lang="EN-CA">Cawthra Secondary School: Jesse Yan</span></p>

<p class="MsoNormal" style="margin-bottom:0in;margin-bottom:.0001pt;line-height:normal"><span style="font-size:12.0pt;font-family:&quot;Times New Roman&quot;,&quot;serif&quot;" lang="EN-CA">Glenforest Secondary School: Edward
Chen, Mike Wang, Ruhi Kokal </span><span style="font-size:12.0pt;font-family:&quot;Times New Roman&quot;,&quot;serif&quot;"></span></p>

<p class="MsoNormal" style="margin-bottom:0in;margin-bottom:.0001pt;line-height:normal"><span style="font-size:12.0pt;font-family:&quot;Times New Roman&quot;,&quot;serif&quot;" lang="EN-CA">Gordon Graydon Memorial Secondary
School: Moksha Patel, Ayesha Madan</span><span style="font-size:12.0pt;font-family:&quot;Times New Roman&quot;,&quot;serif&quot;"></span></p>

<p class="MsoNormal" style="margin-bottom:0in;margin-bottom:.0001pt;line-height:normal"><span style="font-size:12.0pt;font-family:&quot;Times New Roman&quot;,&quot;serif&quot;" lang="EN-CA">John Fraser Secondary School:
Christine Xin, Braeden Page, Daaniya Tariq</span><span style="font-size:12.0pt;font-family:&quot;Times New Roman&quot;,&quot;serif&quot;"></span></p>

<p class="MsoNormal" style="margin-bottom:0in;margin-bottom:.0001pt;line-height:normal"><span style="font-size:12.0pt;font-family:&quot;Times New Roman&quot;,&quot;serif&quot;" lang="EN-CA">Lorne Park Secondary School: Kim
Ren, Jenny Qian</span><span style="font-size:12.0pt;font-family:&quot;Times New Roman&quot;,&quot;serif&quot;"></span></p>

<p class="MsoNormal" style="margin-bottom:0in;margin-bottom:.0001pt;line-height:normal"><span style="font-size:12.0pt;font-family:&quot;Times New Roman&quot;,&quot;serif&quot;" lang="EN-CA">Philopateer Christian College:
George Keliny</span><span style="font-size:12.0pt;font-family:&quot;Times New Roman&quot;,&quot;serif&quot;"></span></p>

<p class="MsoNormal" style="margin-bottom:0in;margin-bottom:.0001pt;line-height:normal"><span style="font-size:12.0pt;font-family:&quot;Times New Roman&quot;,&quot;serif&quot;" lang="EN-CA">Rick Hansen Secondary School:
Supriya Gopalan, Shiwei Zhuang</span><span style="font-size:12.0pt;font-family:&quot;Times New Roman&quot;,&quot;serif&quot;"></span></p>

<p class="MsoNormal" style="margin-bottom:0in;margin-bottom:.0001pt;line-height:normal"><span style="font-size:12.0pt;font-family:&quot;Times New Roman&quot;,&quot;serif&quot;" lang="EN-CA">St. Francis Xavier Secondary School:
Natasha Mathew </span><span style="font-size:12.0pt;font-family:&quot;Times New Roman&quot;,&quot;serif&quot;"></span></p>

<p class="MsoNormal" style="margin-bottom:0in;margin-bottom:.0001pt;line-height:normal"><span style="font-size:12.0pt;font-family:&quot;Times New Roman&quot;,&quot;serif&quot;" lang="EN-CA">St. Marcellinus Secondary School:
Eva Xu</span><span style="font-size:12.0pt;font-family:&quot;Times New Roman&quot;,&quot;serif&quot;"></span></p>

<p class="MsoNormal" style="margin-bottom:0in;margin-bottom:.0001pt;line-height:normal"><span style="font-size:12.0pt;font-family:&quot;Times New Roman&quot;,&quot;serif&quot;" lang="EN-CA">Stephen Lewis Secondary School:
Sathu Sivalogarajah, Anish Arora</span><span style="font-size:12.0pt;font-family:&quot;Times New Roman&quot;,&quot;serif&quot;"></span></p>

<p class="MsoNormal" style="margin-bottom:0in;margin-bottom:.0001pt;line-height:normal"><span style="font-size:12.0pt;font-family:&quot;Times New Roman&quot;,&quot;serif&quot;" lang="EN-CA">The Woodlands Secondary School:
Jonathan Martins, Ashley Tam, April Liu </span></p>

<p class="MsoNormal" style="margin-bottom:0in;margin-bottom:.0001pt;line-height:normal"><span style="font-size:12.0pt;font-family:&quot;Times New Roman&quot;,&quot;serif&quot;" lang="EN-CA"> </span></p>

<p class="MsoNormal" style="margin-bottom:0in;margin-bottom:.0001pt;line-height:normal"><span style="font-size:12.0pt;font-family:&quot;Times New Roman&quot;,&quot;serif&quot;" lang="EN-CA">If there is no student ambassador at
your school, please drop off your</span><span style lang="EN-CA"> </span><b><span style="font-size:12.0pt;font-family:&quot;Times New Roman&quot;,&quot;serif&quot;;color:red" lang="EN-CA"><i style><u>registration fee, pledge forms</u></i><u>, and </u><i style><u>liability
forms</u></i> (attached)</span></b><span style="font-size:12.0pt;font-family:&quot;Times New Roman&quot;,&quot;serif&quot;" lang="EN-CA"> in person to Mississauga Central Library on Thursday, December 20<sup>th</sup>
to one of the Executives present. Thank you for your interest and to view your team info, click <a href="%s">here</a>. We look forward
to seeing you on the court! <br></span></p><p class="MsoNormal" style="margin-bottom:0in;margin-bottom:.0001pt;line-height:normal"><br><span style="font-size:12.0pt;font-family:&quot;Times New Roman&quot;,&quot;serif&quot;" lang="EN-CA"></span><span style></span></p>



<div><div><font color="#666666">Cheers, </font><div><font color="#666666"> </font></div><div><b><font color="#666666">Cathy L.<br></font></b></div><div><font color="#666666">MS Mississauga Youth Committee Executive<br><a href="http://www.msyouthmississauga.org/" target="_blank">www.msyouthmississauga.org</a><br>

</font></div></div></div><br>
"""%uri,
					attachments=(
						("Release_of_Liability.pdf",file("att/Release_of_Liability.pdf").read()),
						("Volleyball Pledge Form.doc",file("att/Volleyball Pledge Form.doc").read()),
					),
					to="%s %s <%s>"%(player["first_name"],player["last_name"],player["email"]),
				).send()
			return render(request,"signup_success.html",{
				"event":event,
				"name":conf["name"],
				"uri":uri,
			})
	else:
		form=conf["form"]()
	return render(request,"signup.html",{
		"event":event,
		"name":conf["name"],
		"form":form,
	})

from creepy import first_signups,first_signups_fields
from django.http import HttpResponse
import itertools
first_signups_keyed=tuple(tuple(val.lower()if type(val)==str else val for val in record)+record for record in first_signups)
def one(ite):
	"""Returns the one value or None"""
	lst=list(itertools.islice(ite,2))
	if len(lst)==1:
		return lst[0]
def prev_players(request,key,prefix):
	if prefix:
		prefix=prefix.lower()
		try:
			idx=first_signups_fields.index(key)
			val=one(record[len(first_signups_fields):] for record in first_signups_keyed if record[idx].startswith(prefix))
			if val:
				return HttpResponse("\t".join(map(str,val)),content_type="text/plain")
		except ValueError:
			pass
	return HttpResponse(content_type="text/plain")
def team_prefix(request,prefix):
	prefix=normalize_name(prefix)
	lst=VolleyballTeam.all().filter("index_key >=",prefix).filter("index_key <=",prefix+u"\uffff").order("index_key").fetch(2)
	if len(lst)>1 and lst[0].index_key!=prefix:
		lst=False
	return HttpResponse(str(int(lst[0].team_type=="Competitive"))+lst[0].name if lst else"",content_type="text/plain")

from itertools import imap
def view(request,event,uid):
	conf=signup_conf(event)
	ent=conf["model"].get_by_id(long(uid))
	children=None
	if"children"in conf:
		children=conf["children"].all().ancestor(ent)
		if"order"in conf and conf["order"]:
			children=children.order(conf["order"])
		children=imap(to_pretty_dict,children.run())
	return render(request,"view.html",{
		"event":event,
		"name":conf["name"],
		"ent":to_pretty_dict(ent),
		"children":children,
	})

import csv
from datetime import datetime
def export(request,event,kind):
	conf=signup_conf(event)
	model,fields=conf["export"][int(kind)-1]
	response=HttpResponse(mimetype="text/csv")
	response['Content-Disposition']='attachment; filename="export-%s_%s-%s.csv"'%(event,kind,datetime.now().strftime("%y-%m-%d-%H-%M-%S"))
	writer=csv.writer(response)
	for ent in model.all().order(conf["order"]).run():
		writer.writerow(map(lambda field:field(ent)if hasattr(field,"__call__")else getattr(ent,field),fields))
	return response
