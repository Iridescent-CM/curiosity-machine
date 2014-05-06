"use strict";

var CM = {};

CM.Navigation = {
  $navTop: $('.nav-wrapper').length ? $('.nav-wrapper').offset().top : false,
  $navWrapper: $('.nav-wrapper'),
  $mentorNavWrapper: $('.mentor-panel-wrapper')
}

$(document).ready(function() {


if (CM.Navigation.$navTop) {
  $(window).on('scroll', function() {
    var scrollTop = $(window).scrollTop();
    if (scrollTop > CM.Navigation.$navTop) {
      CM.Navigation.$navWrapper.addClass('sticky');
      CM.Navigation.$mentorNavWrapper.css('top', 100);
    } else {
      CM.Navigation.$navWrapper.removeClass('sticky');
      CM.Navigation.$mentorNavWrapper.css('top', CM.Navigation.$navTop - scrollTop + 100);
    }
  });
  $(window).trigger('scroll'); //if you refresh a scrolled page
}
  
  
  $('.navbar-toggle').on('click', function(e) {
    e.preventDefault();
    var $content = $('.main-content');
    var $nav = $('.nav-menu');
    if ($content.hasClass('nav-open')) {
      $content.removeClass('nav-open');
      $nav.removeClass('nav-open');
    } else {
      $content.addClass('nav-open');
      $nav.addClass('nav-open');
    }
  });

  //this adds margin to the images in comments so they always line up with the paper lines.
  $('.paper img').on('load',function() {
    var $self = $(this);
    var lineHeight = parseFloat($self.closest('.paper').css('line-height'));
    var height = $self.height();
    $self.css('margin-bottom', (lineHeight - (height % lineHeight)) + 'px' );
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

//========cahllenge nav -=======
  // $('.challenge-nav.primary li').not(':first-child').on('click', function() {
  //   var $self = $(this);
  //   var position = $self.position();
  //   var width = $self.width();
  //   var color = $('button', this).css('color');

  //   $('.challenge-nav.clipper').css('clip', 'rect(0px,' +(position.left + width) + 'px,100px,' + position.left +'px)');
  //   $('.challenge-nav.clipper .cursor').css({
  //     'left' : (position.left - 2) + 'px',
  //     'width' : (width + 4) + 'px',
  //     'background-color' : color
  //   });
  //   $('.challenge-nav.primary .cursor').css({
  //     'left' : (position.left - 2) + 'px',
  //     'width' : (width + 4) + 'px'
  //   });
  //   $('.challenge-nav.primary .cursor .top').css({'border-color' : 'transparent ' + color + ' transparent transparent'});
  //   $('.challenge-nav.primary .cursor .bottom').css({'border-color' : 'transparent transparent ' + color + ' transparent'});
  //   //$('.challenge-nav.primary .cursor .front').css({'border-color' : ('transparent transparent transparent ' + color) });
  
  //   $('.challenge-nav.clipper .btn').textillate({
  //       autoStart: false,
  //       'in': {
  //         effect : 'wobble'
  //       }
  //     }).textillate('start');
  // });

  // $('.challenge-nav.clipper .cursor').on('transitionend webkitTransitionEnd', function(e){
      
  // });
  // //start starting position...
  // $('.challenge-nav.primary li').eq(1).trigger('click');
//==== end challenge nav


});


