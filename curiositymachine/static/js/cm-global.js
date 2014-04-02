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

  //this is so we can reload content into the same modal.
  //re-initilaizes the modal when hidden
  $('body').on('hidden.bs.modal', '.modal', function () {
    $(this).removeData('bs.modal');
  });


});


