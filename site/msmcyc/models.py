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
