$(function(){
  if (typeof filepicker === 'undefined') {
    var els = document.querySelectorAll('[data-toggle="filepicker"]');
    Array.prototype.forEach.call(els, function (el) {
      el.disabled = "disabled";
    });

    Rollbar.critical("filepicker not available on page");
    log("log: filepicker not available on page", "critical");
  }
});

$(document).on('click', '[data-toggle="filepicker"]', function(evt) {
  var el = this;
  var container = el.parentNode;
  var urlField = container.querySelector('#' + el.id + '_url');
  var mimeField = container.querySelector('#' + el.id + '_mimetype');
  var filenameDisplay = container.querySelector('#' + el.id + '_filename');

  filepicker.setKey(el.getAttribute('data-fp-apikey'));
  var injectPreview = el.hasAttribute('data-show-preview');

  var opts = {
    mimetypes: el.getAttribute('data-fp-mimetypes').split(','),
    webcam: {}
  };
  opts.openTo = el.hasAttribute('data-fp-opento') ? el.getAttribute('data-fp-opento') : undefined;
  opts.services = el.hasAttribute('data-fp-services') ? el.getAttribute('data-fp-services').split(',') : undefined;
  opts.conversions = el.hasAttribute('data-fp-conversions') ? el.getAttribute('data-fp-conversions').split(',') : undefined;
  opts.cropRatio = el.hasAttribute('data-fp-cropratio') ? el.getAttribute('data-fp-cropratio') : undefined;
  opts.cropForce = el.hasAttribute('data-fp-cropforce');
  opts.webcam.videoLen = el.hasAttribute('data-fp-video-length') ? el.getAttribute('data-fp-video-length') : undefined;

  filepicker.pick(
    opts,
    function success (blob) {
      urlField.value = blob.url;
      mimeField.value = blob.mimetype;
      filenameDisplay.value = blob.filename;

      if (injectPreview) {
        Array.prototype.forEach.call(container.querySelectorAll('.pickwidget-preview'), function(el) {
          container.removeChild(el);
        });
        if (blob.mimetype.substr(0, 5) === 'image') {
          var el = document.createElement('img');
          el.src = blob.url;
          el.classList.add('pickwidget-preview');
          container.insertBefore(el, container.firstChild);
        }
        else if (blob.mimetype.substr(0, 5) === 'video') {
          var el = document.createElement('video');
          el.src = blob.url;
          el.controls = 'controls';
          el.classList.add('pickwidget-preview');
          container.insertBefore(el, container.firstChild);
        }
      }
      //submit the form upon saving
      evt.target.form.submit();
      evt.target.form.hidden = true;

      var title = document.getElementById("comment_title")
      title.textContent = "Please wait...";

      $('.hide_upon_submit').hide();
    },
    function error (err) {
      if (!err.code || err.code !== 101) {
        Rollbar.error("Filepicker returned an error", err);
        alert("We’re experiencing a problem with our media service. Our engineers are on the case, and will have things back to normal shortly.");
      }
    }
  );
});
