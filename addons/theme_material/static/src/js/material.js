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

    $("select.form-control").change(function() {
        if ($(this).val() == "")
            $(this).removeClass("selected");
        else
            $(this).addClass("selected");
    });

    $("select.form-control").each(function() {
        if ($(this).val() != "" && !$(this).hasClass("selected")) {
            $(this).addClass("selected");
        }
    });

    $(".rem-form-search .nav-tabs li").click(function() {
        if (!$(this).hasClass("active")) {
            $(".rem-form-search .nav-tabs li").removeClass("active");
            $(this).addClass("active");
            $("#ct").val($(this).attr("id").replace("ct-", ""));
        }
    });
});