document.addEventListener("DOMContentLoaded", function(event) { 

  function init(els) {
    Array.prototype.forEach.call(els, function (el) {
      el.onclick = function () {
        var el = this;
        var container = el.parentNode;
        var urlField = container.querySelector('#' + el.id + '_url');
        var mimeField = container.querySelector('#' + el.id + '_mimetype');
        var filenameDisplay = container.querySelector('#' + el.id + '_filename');

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
          },
          function error (err) {
            if (!err.code || err.code !== 101) {
              Rollbar.error("Filepicker returned an error", err);
            }
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
    Rollbar.critical("filepicker not available on page");

    var xhr = new XMLHttpRequest();
    xhr.open('PUT', '/log/');
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(JSON.stringify({
      message: "log: filepicker not available on page",
      level: "critical"
    }));

    Array.prototype.forEach.call(els, function (el) {
      el.disabled = "disabled";
    });
  }
});
