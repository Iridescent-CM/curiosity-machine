$(document).ready(function() {

  var csrftoken = getCookie('csrftoken');

  $.ajaxSetup({
    crossDomain: false, // obviates need for sameOrigin test
    beforeSend: function(xhr, settings) {
      if (!csrfSafeMethod(settings.type)) {
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
      }
    }
  });

  $(document).ajaxError(function(event, XMLHttpRequest, ajaxOptions) {
    console.group('Ajax Error');
    console.log('Request: ', ajaxOptions.url);
    console.log('Response', {response : XMLHttpRequest.responseText});
    console.dir(ajaxOptions);
    console.dir(XMLHttpRequest);
    console.groupEnd();
  });

  $(document).ajaxSuccess(function(event, XMLHttpRequest, ajaxOptions) {
    console.group('Ajax Success');
    console.log('Request: ', ajaxOptions.url);
    console.log('Response', {response : XMLHttpRequest.responseText});
    console.dir(ajaxOptions);
    console.dir(XMLHttpRequest);
    console.groupEnd();
  });
  
  $(document).ajaxSend(function(event, XMLHttpRequest, ajaxOptions) {
    console.group('Ajax Send');
    console.log('Request: ', ajaxOptions.url);
    console.dir(ajaxOptions);
    console.dir(XMLHttpRequest);
    console.groupEnd();
  });  


});

function csrfSafeMethod(method) {
  // these HTTP methods do not require CSRF protection
  return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

// using jQuery

function getCookie(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie != '') {
    var cookies = document.cookie.split(';');
    for (var i = 0; i < cookies.length; i++) {
      var cookie = jQuery.trim(cookies[i]);
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) == (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}