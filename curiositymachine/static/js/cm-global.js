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


});


