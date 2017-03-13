function login_post() {
    $.ajax({
        url: "/accounts/login/",
        type: "POST",
        data: {
            username: $('#post-email').val(),
            password: $('#post-pass').val()
        },
        success: function(r) {
            if (r == "success") {
                window.location.href=$('#post-next').val(); 
            } else if (r == "failed") {
                error_container = document.getElementById("error-container");
                error_container.innerHTML = "<p class='error'>Wrong email or password.</p>";
            } else {
                console.log(r);
                error_container = document.getElementById("error-container");
                var c = "<p class='error'>Account not active. <a href='/accounts/new_activation_link/";
                c += r;
                c += "'>Click here</a> to resend the activation link to this address.</p>";
                error_container.innerHTML = c;
            }
        },
        error: function(xhr, errmsg, err) {
            console.log("failure");
        } 
    });
}

$(document).ready(function() {
    $('#login-form').on('submit', function(event) {
        event.preventDefault();
        login_post();
    });
    
    $('#register-form').on('submit', function(event) {
        $('#register-submit').prop("disabled", true);
    });
});

/***********
CSRF CODE SO WE CAN USE AJAX
***********/

$(function() {
    // This function gets cookie with a given name
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');

    /*
    The functions below will create a header with csrftoken
    */

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    function sameOrigin(url) {
        // test that a given url is a same-origin URL
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    }

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                // Send the token to same-origin, relative URLs only.
                // Send the token only if the method warrants CSRF protection
                // Using the CSRFToken value acquired earlier
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

});