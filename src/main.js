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
		this.removeClass("input-hinted").prev().filter(".input-hint").remove();
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
	var cache={},queue={};
	$.ajaxC=function(url,f){
		if(cache.hasOwnProperty(url)){
			if(queue.hasOwnProperty(url))
				queue[url].push(f);
			else
				f.apply(cache[url].ths,cache[url].args);
			return cache[url].ret;
		}
		queue[url]=[f];
		var ret=$.ajax(url).success(function(){
			for(var i=0;i<queue[url].length;queue[url][i++].apply(this,arguments));
			cache[url].ths=this;
			cache[url].args=arguments;
			delete queue[url];
		});
		cache[url]={ret:ret};
		return ret;
	}
})(jQuery);
$(function(){
	$("a:not(.click)").filter(function(i,e){
		return/^https?:$/.test(e.protocol)&&e.href&&e.host!=location.host;
	}).addClass("external");
});
/* vim: set ts=4 sw=4: */
