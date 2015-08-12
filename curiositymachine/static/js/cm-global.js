"use strict";

var CM = {};

CM.Navigation = {
  $navTop: $('.nav-wrapper').length ? $('.nav-wrapper').offset().top : false,
  $navWrapper: $('.nav-wrapper'),
  $mentorNavWrapper: $('.mentor-panel-wrapper')
};

CM.showMessage = function(message, classes) {
  $('#message-bar').removeClass().addClass(classes);
  $('#message-bar').addClass('active').find('.text').append(message);
  var timer = setTimeout(function() {
    $('#message-bar').removeClass('active');
  }, 6 * 1000);
};

CM.FilePicker = {
  config : {},
  init : function(parent) {
    var $modal = $(parent);
    var self = this;

    if ($('form', $modal).length) {
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
          CM.showMessage(error.toString(), "error");
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
};

$(document).ready(function() {

  $('.ajax-and-refresh-form').on('submit', function(e) {
    e.preventDefault();
    var $self = $(this);
    var data = {
      url: $self.attr('action'), 
      type:$self.attr('method'), data: $self.serialize()
    }
    console.log(data);
    $.ajax(data).done(function(data) {
      location.reload();
    }).fail(function(data) {
      console.log(data);
      alert( "There was an error; please try again later" );
    })

  });
  
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
    var $content = $('.container-fluid');
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
  $('.text_form textarea').on('keyup', function(e) {
    if ($(this).val() == '') {
      $(this.form).find('input[type=submit]').attr('disabled', 'disabled');
    } else {
      $(this.form).find('input[type=submit]').removeAttr('disabled');
    }
  });
  $('a[data-remote-replace=true]').click(function (e) {
    e.preventDefault();
    var me = $(this);
    var targetSelector= me.data('target');
    var url = me.attr('href');
    $.ajax(url).success(function (data) {
      $(targetSelector).replaceWith(data);
    });
  });


  $('.text_form input[type=text]').on('keyup', function(e) {
    if ($(this).val() == '') {
      $(this.form).find('input[type=submit]').attr('disabled', 'disabled');
    } else {
      $(this.form).find('input[type=submit]').removeAttr('disabled');
    }
  });

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


  //===== carousel setup

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

  //====== end carousel setup

  $('.image-gallery .image-container').on('click', function() {
    var image = $(this).clone();
    var modalContent = $('#galleryModal .modal-content');
    var header = '<div class="modal-header"><button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button><h2>&nbsp;</h2></div>';
    console.log(header);
    modalContent.empty();
    
    modalContent.append(header);
    modalContent.append(image);
    image.wrap('<div class="modal-body"></div>');
    
  });

  //this shows or hides the button on challenge details page depending on if the video is playing

  $('.challenge-details-hero .cm-mejs-player').on('pause', function() {
      $('.challenge-details .btn-primary').css('position', 'relative').css('z-index', 2);
      $('.challenge-details-hero .details').show();
  });

  $('.challenge-details-hero .cm-mejs-player').on('play', function() {
      $('.challenge-details .btn-primary').css('position', 'static').css('z-index', 0);
      $('.challenge-details-hero .details').hide();
  });

  // auto enable using JSON attribute
  $('.cm-mejs-player').mediaelementplayer({
    features: ['playpause','progress','current','duration','tracks','volume','fullscreen','googleanalytics']
  });

  $('#introduction-modal').on('hidden.bs.modal', function (){
    $("#intro-video")[0].pause();
  });  

}); //end dom ready

$.fn.extend({
  initPanelCarousel: function(opts) {
    var opts = $.extend({
      items : 4,
      itemsCustom : false,
      itemsDesktop : [1199,3],
      itemsDesktopSmall : [980,3],
      itemsTablet: [768,2],
      itemsTabletSmall: false,
      itemsMobile : [479,1],
      singleItem : false,
      itemsScaleUp : false
    }, opts);
    return this.owlCarousel(opts);
  },

  disableEmptySubmit: function() {
    return $(this).find("textarea, input[type=text]").on('keyup', function(e) {
      var widget = this;
      if ($(widget).val() == '') {
        $(widget.form).find('input[type=submit]').attr('disabled', 'disabled');
      } else {
        $(widget.form).find('input[type=submit]').removeAttr('disabled');
      }
    });
  }
});