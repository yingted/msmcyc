from ..models import *
from django import template
register=template.Library()

@register.inclusion_tag("base_updates.html")
def updates(count):
	return{
		"updates":Update.all()
			.order("-added")
			.run(limit=3),
	}

