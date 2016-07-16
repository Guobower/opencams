$(function() {
	"use strict";

	$(".btn").each(function(){
		$(this).addClass("waves-effect waves-light");
    });

	Waves.attach('.waves-effect');
	Waves.init();

    $('#carousel-homepage').carousel({
        pause: "false"
    });
});