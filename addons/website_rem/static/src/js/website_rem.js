$(function() {
	"use strict";

    window.ondragstart = function() {return false;}

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
            $(".type-listing").removeClass("selected");
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

    $("#multi_search").keyup(function()  {
        get_multi_search_results();
    }).focus(function() {
        get_multi_search_results();
    }).blur(function() {
        hide_rem_autocomplete();
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
            url: "/rem/search/" + $("#multi_search").val(),
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
                        $(".rem-autocomplete").append('<li onmousedown="autofill_multi_search(\'' + units[i].name + '\');">' + units[i].name + "</li>");
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