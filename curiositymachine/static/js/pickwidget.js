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
  var btn = this;
  var container = btn.parentNode;
  var urlField = container.querySelector('#' + btn.id + '_url');
  var mimeField = container.querySelector('#' + btn.id + '_mimetype');
  var filenameDisplay = container.querySelector('#' + btn.id + '_filename');

  filepicker.setKey(btn.getAttribute('data-fp-apikey'));
  var injectPreview = btn.hasAttribute('data-show-preview');

  var opts = {
    mimetypes: btn.getAttribute('data-fp-mimetypes').split(','),
    webcam: {}
  };
  opts.openTo = btn.hasAttribute('data-fp-opento') ? btn.getAttribute('data-fp-opento') : undefined;
  opts.services = btn.hasAttribute('data-fp-services') ? btn.getAttribute('data-fp-services').split(',') : undefined;
  opts.conversions = btn.hasAttribute('data-fp-conversions') ? btn.getAttribute('data-fp-conversions').split(',') : undefined;
  opts.cropRatio = btn.hasAttribute('data-fp-cropratio') ? btn.getAttribute('data-fp-cropratio') : undefined;
  opts.cropForce = btn.hasAttribute('data-fp-cropforce');
  opts.webcam.videoLen = btn.hasAttribute('data-fp-video-length') ? btn.getAttribute('data-fp-video-length') : undefined;

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

      if ($(btn).data('auto-submit')) {
        evt.target.form.submit();
        evt.target.form.hidden = true;
        $('.hide_upon_submit').hide()
        if ($(btn).data('replacement-text')) {
          $('.replace_text_upon_submit').text($(btn).data('replacement-text'));
        }
      }
    },
    function error (err) {
      if (!err.code || err.code !== 101) {
        Rollbar.error("Filepicker returned an error", err);
        alert("We’re experiencing a problem with our media service. Our engineers are on the case, and will have things back to normal shortly.");
      }
    }
  );
});
