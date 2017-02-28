$(document).ready(function () {
  // handle buy now button click
  $('button.btn-purchase').click(function() {
    var plan = $(this).data('plan');
    var period = 'annually'
    if($('.js-price-toggle.active').hasClass('js-price-monthly')){
      period = 'monthly';
    }
    window.location.href = window.SPA_ROOT_URL + "/sign-up/business-plan?plan=" + plan + '-' + period;
  });
  // toggle display of monthly and annual prices
  $('.js-price-toggle').click(function() {
    $('.js-price-toggle').each(function() {
      $(this).removeClass('active');
    });
    $(this).addClass('active');
    if($(this).hasClass('js-price-monthly')) {
      $('.js-pricing-plan').each(function() {
        var newPrice = $(this).data('price-monthly');
        if(newPrice) {
          $(this).find('.js-price').text(newPrice);
        }
      });
    }
    if($(this).hasClass('js-price-annual')) {
      $('.js-pricing-plan').each(function() {
        var newPrice = $(this).data('price-annual');
        if(newPrice) {
          $(this).find('.js-price').text(newPrice);
        }
      });
    }
  });

  // hide all faq's on page load
  $('.js-faq').each(function() {
    $(this).addClass('collapsed');
    $(this).find('.js-faq-a').hide();
  });
  // faq toggle
  $('.js-faq-q').click(function() {
    var faq = $(this).parent('.js-faq');
    if(faq.hasClass('collapsed')) {
      faq.find('.js-faq-a').slideDown();
    }
    else {
      faq.find('.js-faq-a').slideUp();
    }
    faq.toggleClass('collapsed');
    return false;
  });

  // faq tabs

  $('.js-faq-tab').click(function(e) {
    e.preventDefault();
    // deactivate tabs
    $('.js-faq-tab').each(function() {
      $(this).removeClass('js-active');
    });
    // hide panes
    $('.js-faq-tabpane').each(function() {
      $(this).hide();
    });
    // activate tab
    $(this).addClass('js-active');
    // show pane
    var tid = $(this).attr('href');
    $('' + tid).show();
  });

  // custom intercom launcher
  $('#intercom-custom-launcher').click(function() {
    if(Intercom) {
      Intercom('show');
    }
  });

})
