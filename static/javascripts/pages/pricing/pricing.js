$(document).ready(function () {

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
  })

})
