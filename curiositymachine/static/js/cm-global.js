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
      $('.student-column').removeClass('col-md-6').addClass('col-md-4');
    } else {
      $('.parent-info').hide();
      $('.student-column').removeClass('col-md-4').addClass('col-md-6');
    }
  },
}

CM.FilePicker = {
  config : {},
  init : function(parent) {
    var $modal = $(parent);
    var self = this;

    if ($('.comment-form', $modal).length) {
      $('input[type=filepicker-custom]', $modal).first().each(function() {
        var $self = $(this);
        $modal.find('input[type=submit]').attr('disabled', 'disabled');
        filepicker.setKey($self.data('fpApikey'));

        //create iframe
        $self.before('<iframe id="filepickerframe"></iframe>');

        filepicker.pick({
        mimetypes: $self.data('fpMimetypes').split(','),
        container: 'filepickerframe',
        services: $self.data('fpServices').split(','),
        openTo: $self.data('fpOpento').split(',')
        },
        function(data) {
          //success
          $self.val(data.url);
          $modal.find('input[type=submit]').removeAttr('disabled');
          $('#filepickerframe').remove();
          if ($self.attr('id') === "id_picture_filepicker_url") {
            $self.before('<div class="upload-success image-wrapper"><img src="' + data.url + '" ></div>' );
          } else {
            $self.before('<p class="upload-success">File [' + data.filename + '] has been successfully uploaded and is being processed.</p>')
          }
        },
        function(error) {
          //failure
          CM.userError(error.toString());
        }
        );

      });
    }
  },
  destroy : function(parent) {
    //reset the modal in case they want to try again.
    if ($('input[type=filepicker-custom]', parent).length) {
      $('#filepickerframe', parent).remove();
      $('.upload-success', parent).remove();
      $('input[type=filepicker-custom]', parent).val('');
    }
  }
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


  $('#text_form textarea').on('keyup', function(e) {
    if ($(this).val() == '') {
      $(this.form).find('input[type=submit]').attr('disabled', 'disabled');
    } else {
      $(this.form).find('input[type=submit]').removeAttr('disabled');
    }
  });

/////PROFILE!

  CM.Profile.init();


//=======================
//bootstrapy stuff
//====================
  //this is so we can reload content into the same modal.
  //re-initilaizes the modal when hidden
  $('body').on('hidden.bs.modal', '.modal', function () {
    $(this).removeData('bs.modal');
    CM.FilePicker.destroy(this);
  });

  //focus on the first input element in modals
  //and other stuff when the modal opens like firelpicker
  $('body').on('shown.bs.modal', '.modal:visible', function () {
    $(this).find('input:visible,textarea:visible').first().focus();
    //fielpicker
    CM.FilePicker.init(this);
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


