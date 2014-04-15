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
  
    $('.challenge-nav.clipper .btn').textillate({
        autoStart: false,
        'in': {
          effect : 'wobble'
        }
      }).textillate('start');
  });

  $('.challenge-nav.clipper .cursor').on('transitionend webkitTransitionEnd', function(e){
      
  });

  $('.challenge-nav.primary li').eq(1).trigger('click');

});


