(function($){
	$.fn.button=function(f){
		return this.wrapInner("<a href=\"#\" class=\"click\">").children().click(function(e){
			if(e.preventDefault)
				e.preventDefault();
			else e.returnValue=false;
			return f.apply(this.parentNode,arguments);
		}).attr("role","button").parent();
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
