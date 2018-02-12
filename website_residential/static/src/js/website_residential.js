$(function() {
	"use strict";

    var processing = false;

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

    $(".type-listing").click(function() {
        if (!$(this).hasClass("selected")) {
            if ($(this).attr("id") == "type-list")
                $("#type_listing").val("0");
            else
                $("#type_listing").val("1");

            $("#rem-search-button").click();
        }
    });

    $(".rem-form-search .nav-tabs li").click(function() {
        if (!$(this).hasClass("active")) {
            $(".rem-form-search .nav-tabs li").removeClass("active");
            $(this).addClass("active");
            $("#offer_type").val($(this).attr("id").replace("ct-", ""));
        }
    });

    $("#multi_search").keyup(function()  {
        get_multi_search_results();
    }).focus(function() {
        get_multi_search_results();
    }).blur(function() {
        hide_rem_autocomplete();
    });

    $("#my-favorites-photo-cards .rem-unit-photo-card-favorite").click(function() {
        $.ajax(
        {
            url: "/rem/favorite/unset/" + $(this).attr("id").replace("fv-", ""),
            type: "GET",
            dataType: "json",
            success: function(json)
            {
                var result = json.result;

                if (result.length == 0)
                {
                    box_dialog("Error", '<div>Sorry, something went wrong, please try again later.</div>');
                }
                else
                {
                    window.location.replace("/my/favorites");
                }
            },
            error: function(xhr, status, errorThrown)
            {
                box_dialog("Error", '<div>Sorry, something went wrong, please try again later.</div>');
            }
        });
        return false;
    });

    $("#units-list-photo-cards .rem-unit-photo-card-favorite").click(function() {
        var url = "";
        var id = $(this).attr("id");

        if ($(this).hasClass("saved")) {
            url = "/rem/favorite/unset/";
        } else {
            url = "/rem/favorite/set/";
        }

        if (!processing) {
            $.ajax(
            {
                url: url + $(this).attr("id").replace("fv-", ""),
                type: "GET",
                dataType: "json",
                success: function(json)
                {
                    var result = json.result;

                    if (result.length == 0)
                    {
                        box_dialog("Error", '<div>Sorry, something went wrong, please try again later.</div>');
                    }
                    else if (result[0].result == 0)
                    {
                        box_dialog("Sign up", '<div id="rem-container">' +
                                     '<div class="form-group">' +
                                        '<div><a href="/web/signup" target="_blank">Sign up</a> or <a href="/web/login" target="_blank">log in</a> to save properties and access them on any device.</div>' +
                                     '</div>' +
                                     '<div id="email-container" class="form-group margin-top-30">' +
                                        '<input type="email" id="email" name="email" maxlength="128" class="form-control" title="Email" placeholder="Email"/>' +
                                     '</div>' +
                                     '<div class="form-group margin-top-30">' +
                                        '<div id="rem-signup" class="btn btn-primary btn-block ladda-button waves-effect waves-light" data-style="zoom-out"><i class="zmdi zmdi-account-add"></i> Sign up</div>' +
                                     '</div>' +
                                 '</div>');
                    }
                    else
                    {
                        if ($("#" + id).hasClass("saved")) {
                            $("#" + id).removeClass("saved");
                            $("#" + id).html('<i class="zmdi zmdi-star-outline"></i>');
                        } else {
                            $("#" + id).addClass("saved");
                            $("#" + id).html('<i class="zmdi zmdi-star"></i>');
                        }
                    }
                },
                error: function(xhr, status, errorThrown)
                {
                    box_dialog("Error", '<div>Sorry, something went wrong, please try again later.</div>');
                }
            });
        }
        return false;
    });

    $(".rem-unit-card-actions-favorite").click(function() {
        var url = "";
        var id = $(this).attr("id");

        if ($(this).hasClass("saved")) {
            url = "/rem/favorite/unset/";
        } else {
            url = "/rem/favorite/set/";
        }

        if (!processing) {
            $.ajax(
            {
                url: url + $(this).attr("id").replace("fv-", ""),
                type: "GET",
                dataType: "json",
                success: function(json)
                {
                    var result = json.result;

                    if (result.length == 0)
                    {
                        box_dialog("Error", '<div>Sorry, something went wrong, please try again later.</div>');
                    }
                    else if (result[0].result == 0)
                    {
                        box_dialog("Sign up", '<div id="rem-container">' +
                                     '<div class="form-group">' +
                                        '<div><a href="/web/signup" target="_blank">Sign up</a> or <a href="/web/login" target="_blank">log in</a> to save properties and access them on any device.</div>' +
                                     '</div>' +
                                     '<div id="email-container" class="form-group margin-top-30">' +
                                        '<input type="email" id="email" name="email" maxlength="128" class="form-control" title="Email" placeholder="Email"/>' +
                                     '</div>' +
                                     '<div class="form-group margin-top-30">' +
                                        '<div id="rem-signup" class="btn btn-primary btn-block ladda-button waves-effect waves-light" data-style="zoom-out"><i class="zmdi zmdi-account-add"></i> Sign up</div>' +
                                     '</div>' +
                                 '</div>');
                    }
                    else
                    {
                        if ($("#" + id).hasClass("saved")) {
                            $("#" + id).removeClass("saved");
                            $("#" + id).html('<i class="zmdi zmdi-star-outline"></i> Save');
                        } else {
                            $("#" + id).addClass("saved");
                            $("#" + id).html('<i class="zmdi zmdi-star"></i> Saved');
                        }
                    }
                },
                error: function(xhr, status, errorThrown)
                {
                    box_dialog("Error", '<div>Sorry, something went wrong, please try again later.</div>');
                }
            });
        }
    });

    $("body").on("keyup", "#email", function()
    {
        if (event.keyCode == 13 || event.witch == 13)
            $("#rem-signup").click();
    });

    $("body").on("click", "#rem-signup", function()
    {
        if ($("#email").val() == "" || !validate_email($("#email").val()))
        {
            if (!$("#email-container").hasClass("has-error"))
                $("#email-container").addClass("has-error");
            $("#email").focus();
        }
        else
        {
            var l = Ladda.create(document.querySelector("#rem-signup"));
            l.start();

            $.ajax(
            {
                url: "/rem/user/signup/" + $("#email").val(),
                type: "GET",
                dataType: "json",
                success: function(json)
                {
                    var result = json.result;

                    if (result.length == 0)
                    {
                        box_dialog("Error", '<div>Sorry, something went wrong, please try again later.</div>');
                    }
                    else if (result[0].result == 0)
                    {
                        box_dialog("Successfully signed up", '<div id="rem-container">'+
                                                                '<p>You have already signed up with this email.</p>' +
                                                                '<p>Please check your email for your password and <a href="/web/login" target="_blank">log in</a>.</p>' +
                                                                '<p>If you want to reset your password, click in the following button:</p>' +
                                                                '<div class="margin-top-30">' +
                                                                    '<a href="/web/reset_password" target="_blank" class="btn btn-primary btn-block waves-effect waves-light"><i class="zmdi zmdi-key"></i> &nbsp;Reset password</a>' +
                                                                '</div>' +
                                                            '</div>');
                    }
                    else
                    {
                        box_dialog("Successfully signed up", '<div id="rem-container">'+
                                                                '<p>You have successfully signed up, please check your email for your password.</p>' +
                                                                '<p>If you want to reset your password, click in the following button:</p>' +
                                                                '<div class="margin-top-30">' +
                                                                    '<a href="/web/reset_password" target="_blank" class="btn btn-primary btn-block waves-effect waves-light"><i class="zmdi zmdi-key"></i> &nbsp;Reset password</a>' +
                                                                '</div>' +
                                                            '</div>');
                    }
                },
                error: function(xhr, status, errorThrown)
                {
                    box_dialog("Error", '<div>Sorry, something went wrong, please try again later.</div>');
                },
                complete: function(xhr, status)
                {
                    l.stop();
                }
            });
        }
    });
});

function hide_rem_autocomplete()
{
    $("#multi_search_autocomplete").hide();
    $("#multi_search_autocomplete").text("");
}

function get_multi_search_results()
{
    if ($("#multi_search").val().length > 2)
    {
        $.ajax(
        {
            url: "/rem/search/" + $("#multi_search").val() + "/" + $("#offer_type").val(),
            type: "GET",
            dataType: "json",
            success: function(json)
            {
                var units = json.result;

                if (units.length == 0)
                {
                    hide_rem_autocomplete();
                }
                else
                {
                    $(".rem-autocomplete").text("");

                    for (var i = 0; i < units.length; i++)
                    {
                        $(".rem-autocomplete").append('<li onmousedown="autofill_multi_search(\'' + units[i].result + '\');">' + units[i].result + "</li>");
                    }

                    $(".rem-autocomplete").show();
                }
            },
            error: function(xhr, status, errorThrown)
            {
                hide_rem_autocomplete();
            }
        });
    }
    else
    {
        hide_rem_autocomplete();
    }
}

function autofill_multi_search(unit)
{
    $("#multi_search").val(unit);
    hide_rem_autocomplete();
}

function validate_email(email)
{
    var re = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(email);
}

function box_dialog(title_, message_)
{
    bootbox.hideAll();

    bootbox.dialog(
    {
        message: message_,
        title: title_
    });
}
