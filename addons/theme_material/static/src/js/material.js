$(function() {
	"use strict";

    window.ondragstart = function() {return false;}

	$(".btn").each(function(){
		$(this).addClass("waves-effect waves-light");
    });

	Waves.attach('.waves-effect');
	Waves.init();

    $('#carousel-homepage').carousel({
        pause: "false"
    });

    $('select.form-control').change(function() {
        if ($(this).val() == "")
            $(this).removeClass("selected");
        else
            $(this).addClass("selected");
    });
});