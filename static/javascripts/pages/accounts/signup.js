var theForm = document.getElementById('theForm');

new stepsForm(theForm, {
    onSubmit: function (form) {
        // hide form
        $(theForm.querySelector('.simform-inner')).addClass('hide');
        $.post('/accounts/api/users/', $(form).serialize(), function() {
            // let's just simulate something...
            var messageEl = theForm.querySelector('.final-message');
            messageEl.innerHTML = 'Your account activation link has sent to your email';
            classie.addClass(messageEl, 'show');
        });
    }
});

$('.show-password').click(function() {
    var passwordInput = $(this).siblings('input');
    if (passwordInput.attr('type') === 'password') {
        passwordInput.attr('type', 'text')
    } else {
        passwordInput.attr('type', 'password')
    }
});