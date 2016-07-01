var app = angular.module('material-website', [
	'jcs-autoValidate',
]);

app.controller('material', function($scope) {

	$scope.formModel = {};

	$scope.onSubmit = function(valid) {
		if (valid) {
			var l = Ladda.create(document.querySelector("#material-submit-button"));

			l.start();

			$('#material_form input, #material_form textarea').each(function() {
				$("#submit-form-inputs").append("<input name=\"" + $(this).attr("name") + "\" value=\"" + $(this).val() + "\"/>");
			});

			$("#material-hidden-form-submit").click();
		}
	};
});

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

    $('select.form-control').change(function() {
        if ($(this).val() == "")
            $(this).removeClass("selected");
        else
            $(this).addClass("selected");
    });
});