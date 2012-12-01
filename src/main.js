(function($){
	$.fn.button=function(f){
		return this.wrapInner("<a href=\"#\" class=\"click\">").children().click(function(e){
			if(e.preventDefault)
				e.preventDefault();
			else e.returnValue=false;
			return f.apply(this.parentNode,arguments);
		}).attr("role","button").parent();
	}
	$.fn.togglerFor=function(e){
		this.button(function(){
			$(e).toggle("fast");
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
