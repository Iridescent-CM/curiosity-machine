document.addEventListener("DOMContentLoaded", function(event) { 

  function init(els) {
    Array.prototype.forEach.call(els, function (el) {
      el.onclick = function () {
        var el = this;
        var urlField = document.getElementById(el.id + '_url');
        var mimeField = document.getElementById(el.id + '_mimetype');
        var filenameDisplay = document.getElementById(el.id + '_filename');
        var container = document.getElementById(el.id + '_container');

        filepicker.setKey(el.getAttribute('data-fp-apikey'));
        var injectPreview = el.hasAttribute('data-show-preview');

        var opts = {
          mimetypes: el.getAttribute('data-fp-mimetypes').split(','),
        };
        opts.openTo = el.hasAttribute('data-fp-opento') ? el.getAttribute('data-fp-opento') : undefined;
        opts.services = el.hasAttribute('data-fp-services') ? el.getAttribute('data-fp-services').split(',') : undefined;
        opts.conversions = el.hasAttribute('data-fp-conversions') ? el.getAttribute('data-fp-conversions').split(',') : undefined;
        opts.cropRatio = el.hasAttribute('data-fp-cropratio') ? el.getAttribute('data-fp-cropratio') : undefined;
        opts.cropForce = el.hasAttribute('data-fp-cropforce');

        filepicker.pick(
          opts,
          function success (blob) {
            urlField.value = blob.url;
            mimeField.value = blob.mimetype;
            filenameDisplay.textContent = blob.filename;

            if (injectPreview) {
              Array.prototype.forEach.call(container.querySelectorAll('.pickwidget-preview'), function(el) {
                container.removeChild(el);
              });
              if (blob.mimetype.startsWith('image')) {
                var el = document.createElement('img');
                el.src = blob.url;
                el.classList.add('pickwidget-preview');
                container.insertBefore(el, container.firstChild);
              }
              else if (blob.mimetype.startsWith('video')) {
                var el = document.createElement('video');
                el.src = blob.url;
                el.controls = 'controls';
                el.classList.add('pickwidget-preview');
                container.insertBefore(el, container.firstChild);
              }
            }
          },
          function error (err) {
            // TODO: error handling
            console.log(err);
          }
        );
      };
    });
  }

  var els = document.querySelectorAll('[data-toggle="filepicker"]');
  if (typeof filepicker !== 'undefined') {
    init(els);
  }
  else {
    // TODO: alerting
    Array.prototype.forEach.call(els, function (el) {
      el.disabled = "disabled";
    });
  }
});
