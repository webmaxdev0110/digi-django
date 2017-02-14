$(document).ready(function () {

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

  $('#intercom-custom-launcher').click(function() {
    if(Intercom) {
      Intercom('show');
    }
  });

})
