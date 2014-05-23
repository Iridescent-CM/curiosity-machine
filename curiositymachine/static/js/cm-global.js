"use strict";

var CM = {};

CM.Navigation = {
  $navTop: $('.nav-wrapper').length ? $('.nav-wrapper').offset().top : false,
  $navWrapper: $('.nav-wrapper'),
  $mentorNavWrapper: $('.mentor-panel-wrapper')
}

CM.userError = function(message) {
  $('#message-bar').removeClass().addClass('error');
  $('#message-bar').addClass('active').find('.text').text(message);
  var timer = setTimeout(function() {
    $('#message-bar').removeClass('active');
  }, 3000)
}

CM.userSuccess = function(message) {
  $('#message-bar').removeClass().addClass('success');
  $('#message-bar').addClass('active').find('.text').text(message);
  var timer = setTimeout(function() {
    $('#message-bar').removeClass('active');
  }, 3000);
}

CM.Profile = {
  init : function() {
    this.show_or_hide_parent_fields();
    this.bind();
  },
  bind : function() {
    var self = this
    $('.birthday-field').find('select').on('change', function(e) {
      self.show_or_hide_parent_fields();
    });
  },
  show_or_hide_parent_fields : function() {
    var day = $('#id_birthday_day').val();
    var month = $('#id_birthday_month').val() - 1;
    var year = $('#id_birthday_year').val();
    var today = new Date();
    var age = today.getFullYear() - year;
    if (today.getMonth() < month || (today.getMonth() == month && today.getDate() < day)) {
      age--; //birthday hasn't happened this year
    }
    if (age < 13) {
      $('.parent-info').show();
      $('.profile-column').removeClass('col-md-6').addClass('col-md-4');
    } else {
      $('.parent-info').hide();
      $('.profile-column').removeClass('col-md-4').addClass('col-md-6');
    }
  },
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

  CM.Profile.init();


//=======================
//bootstrapy stuff
//====================
  //this is so we can reload content into the same modal.
  //re-initilaizes the modal when hidden
  $('body').on('hidden.bs.modal', '.modal', function () {
    $(this).removeData('bs.modal');
  });

  //focus on the first input element in modals
  $('body').on('shown.bs.modal', '.modal:visible', function () {
    $(this).find('input:visible:first').focus();
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


