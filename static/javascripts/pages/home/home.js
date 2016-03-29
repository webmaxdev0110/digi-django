// todo: Move to another file
// using jQuery
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
    beforeSend: function (xhr, settings) {
        if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
            // Send the token to same-origin, relative URLs only.
            // Send the token only if the method warrants CSRF protection
            // Using the CSRFToken value acquired earlier
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

var submitEmailAddress = function(email, form) {
    $.post('/', {
        email: email,
        tagIndex: form.find('input[name="tag_index"]').val()
    }, function () {
        $('[data-remodal-id=submitFinished]').remodal({hashTracking: false}).open();
    });
};
var isOnTablet = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile/i.test(navigator.userAgent);
var isSmallDevice = function() {
    return $(window).width() <= 480; // This is synced with includemedia.scss
};

if(!isOnTablet) {
    $('input[name="email"]').keyup(function(e){
        var $this = $(this);
        var emailAddr = $this.val();
        if (/^([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$/.test(emailAddr)) {
            // So the placeholer will not outside the box
            var leftDistance = Math.min(emailAddr.length * 10 + 20, $this.innerWidth() - 80);
            $this.siblings('.input-enter-prompt').css({'left': leftDistance }).show();
            if (e.which === 13) {
                // Enter key
                submitEmailAddress(emailAddr, $this.parents('form'));
            }
        } else {
            $this.siblings('.input-enter-prompt').hide();
        }
    });
}


// click action
$('.js-submit').click(function (e) {
    e.stopPropagation();
    e.preventDefault();
    var target = $(e.target);
    if (isSmallDevice() && target.parents('.fixed-header-wrapper').length > 0) {
        $('html,body').animate({ scrollTop: $('.row.cta').position().top }, 'slow');
        return false;
    }


    var form = target.parents('form');
    var email = target.parents('form').find('input[name="email"]:visible').val();
    if (!/^([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$/.test(email)) {
        alert('Email format is invalid');
        return false;
    }

    submitEmailAddress(email, form);
});


// how it works carousel
$('.js-how-it-works .slide-controls > li').click(function () {
    var $this = $(this);
    var itemIndex = $this.index();
    $this.addClass('active').siblings().removeClass('active');
    $('.js-how-it-works .feature-text').each(function () {
        $(this).children().eq(itemIndex)
            .siblings()
            .removeClass('active animated fadeinUp');
        $(this).children().eq(itemIndex).addClass('active');
        $(this).children().eq(itemIndex).addClass('animated fadeInUp');
    });
});

var initCountingNumber = function () {
    // Counting numbers
    $('.js-number-count').each(function () {
        var $this = $(this);
        var finishText = $this.attr('counter-finish-text');
        var counterEnd = parseInt($this.data('counter-end'), 10);

        var tmpl = fmt('<span class="number-count">0</span>' +
            '<span class="number-appendix">x</span>' +
            '<div class="cover-text">#{finishText}</div>');
        var rendered = tmpl({finishText: finishText});
        $this.append($(rendered));
        var $numberCount = $this.children('.number-count');
        var $coverText = $this.find('.cover-text');
        $this.prop('counter', 0).animate({
            'counter': counterEnd
        }, {
            duration: 600,
            easing: 'swing',
            step: function (now) {
                $numberCount.text(Math.ceil(now));
            },
            complete: function () {
                $coverText.show().addClass('animated fadeInUp');
            }
        });
    });
};

new Waypoint({
    element: $('.row.efficiency')[0],
    handler: function () {
        initCountingNumber();
        this.destroy();
    }
});


new Waypoint({
  element: $('.row.old-new-compare')[0],
  handler: function(direction) {

    if (direction === 'down') {
        $('.fixed-header-wrapper').slideDown(200);
    } else {
        $('.fixed-header-wrapper').slideUp(200);
    }
  }
});

new Waypoint({
  element: $('.row.electronic-signature')[0],
  handler: function(direction) {

    if (direction === 'down') {
        $('.fixed-header-wrapper').slideUp(200);
    } else {
        $('.fixed-header-wrapper').slideDown(200);
    }
  }
});


