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
  });

  //focus on the first input element in modals
  //and other stuff when the modal opens like firelpicker
  $('body').on('shown.bs.modal', '.modal:visible', function () {
    $(this).find('input:visible,textarea:visible').first().focus();
  });

  //actiavate tabs
  $('body').on('click', '.nav-tabs a', function(e) {
      e.preventDefault();
      $(this).tab('show');
  });
  //======= end bootstrappy stuff
}); //end dom ready

$.fn.extend({
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

$(function(){
  $('[data-debounce="true"]').each(function() {
    var $el = $(this);
    $el.parent('form').on('submit', function() {
      $el.prop('disabled', true).css({
        'pointer-events': 'all',
        'cursor': 'progress'
      });
      return true;
    });
  });
});
