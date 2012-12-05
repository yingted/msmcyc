(function($){
	$.fn.button=function(f){
		return this.wrapInner("<a href=\"#\" class=\"click\">").children().click(function(e){
			if(e.preventDefault)
				e.preventDefault();
			else e.returnValue=false;
			return f.apply(this.parentNode,arguments);
		}).attr("role","button").parent();
	}
	$.fn.hint=function(hint){//assume parent is display:block
		if(hint)
			return this.before(this.clone().removeAttr("id").addClass("input-hint").val(hint).attr("tabindex",-1)).addClass("input-hinted");
		this.removeClass("input-hinted").prev(".input-hint").remove();
		return this;
	}
	$.unhint=function(){
		$(".input-hinted").hint();
	}
	$.fn.guess=function(guess,force){
		var val=this.val();
		return this.hint(val+guess.substring(force?0:val.length));
	}
	var prefixes=["+ ","\u2212 "];
	$.fn.togglerFor=function(e){
		var i=0,prefix=$("<span>").text(prefixes[i]);
		this.prepend(prefix).button(function(){
			$(e).toggle("fast");
			prefix.text(prefixes[i^=1]);
		});
		return $(e).hide();
	}
})(jQuery);
$(function(){
	$("a:not(.click)").filter(function(i,e){
		return/^https?:$/.test(e.protocol)&&e.href&&e.host!=location.host;
	}).addClass("external");
});
/* vim: set ts=4 sw=4: */
