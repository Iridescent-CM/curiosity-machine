"use strict";

$(document).ready(function() {
  
  $('.navbar-toggle').on('click', function(e) {
    e.preventDefault();
    var $content = $('.main-content');
    if ($content.hasClass('nav-open')) {
      $content.removeClass('nav-open');
    } else {
      $content.addClass('nav-open');
    }
  });


//=======================
//bootstrapy stuff
//====================
  //this is so we can reload content into the same modal.
  //re-initilaizes the modal when hidden
  $('body').on('hidden.bs.modal', '.modal', function () {
    $(this).removeData('bs.modal');
  });

  //actiavate tabs
  $('body').on('click', '.nav-tabs a', function(e) {
      e.preventDefault();
      $(this).tab('show');
  });
//======= end bootstrappy stuff


  $(".panel-carousel").owlCarousel({
    items : 4,
    itemsCustom : false,
    itemsDesktop : [1199,3],
    itemsDesktopSmall : [980,3],
    itemsTablet: [768,2],
    itemsTabletSmall: false,
    itemsMobile : [479,1],
    singleItem : false,
    itemsScaleUp : false
  });

  $('.theme-carousel').owlCarousel({
    items : 6,
    itemsCustom : false,
    itemsDesktop : [1199,6],
    itemsDesktopSmall : [980,4],
    itemsTablet: [768,3],
    itemsTabletSmall: false,
    itemsMobile : [479,1],
    singleItem : false,
    itemsScaleUp : false
  });

  $('.challenge-nav.primary li').not(':first-child').on('click', function() {
    var $self = $(this);
    var position = $self.position();
    var width = $self.width();
    var color = $('button', this).css('color');
    function ColorLuminance(hex, lum) {
      // validate hex string
      hex = String(hex).replace(/[^0-9a-f]/gi, '');
      if (hex.length < 6) {
        hex = hex[0]+hex[0]+hex[1]+hex[1]+hex[2]+hex[2];
      }
      lum = lum || 0;

      // convert to decimal and change luminosity
      var rgb = "#", c, i;
      for (i = 0; i < 3; i++) {
        c = parseInt(hex.substr(i*2,2), 16);
        c = Math.round(Math.min(Math.max(0, c + (c * lum)), 255)).toString(16);
        rgb += ("00"+c).substr(c.length);
      }

      return rgb;
    }
    $('.challenge-nav.clipper').css('clip', 'rect(0px,' +(position.left + width) + 'px,100px,' + position.left +'px)');
    $('.challenge-nav.clipper .cursor').css({
      'left' : (position.left - 2) + 'px',
      'width' : (width + 4) + 'px',
      'background-color' : color
    });
    $('.challenge-nav.primary .cursor').css({
      'left' : (position.left - 2) + 'px',
      'width' : (width + 4) + 'px'
    });
    $('.challenge-nav.primary .cursor .top').css({'border-color' : 'transparent ' + color + ' transparent transparent'});
    $('.challenge-nav.primary .cursor .bottom').css({'border-color' : 'transparent transparent ' + color + ' transparent'});
    //$('.challenge-nav.primary .cursor .front').css({'border-color' : ('transparent transparent transparent ' + color) });
  });

  $('.challenge-nav.primary li').eq(1).trigger('click');

});


