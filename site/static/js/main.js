$(function(){
	$("a:not(.click)").filter(function(i,e){
		return/^https?:$/.test(e.protocol)&&e.host!=location.host;
	}).addClass("external");
});
/* vim: set ts=4 sw=4: */
