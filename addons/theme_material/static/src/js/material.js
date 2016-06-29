var app = angular.module('website-contact-us', [
	'jcs-autoValidate',
]);

app.controller('contact-us', function($scope) {

	$scope.formModel = {};

	$scope.onSubmit = function(valid) {
		if (valid) {
			var lida = Ladda.create(document.querySelector("#contact-button"));

			lida.start();

			$('#ContactForm input, #ContactForm textarea').each(function() {
				$("#submit-form-inputs").append("<input name=\"" + $(this).attr("name") + "\" value=\"" + $(this).val() + "\"/>");
			});

			$("#validate-submit").click();
		}
	};
});

$(function() {
	"use strict";

	Waves.init();
	Waves.attach('.btn');
});
