document.addEventListener("DOMContentLoaded", function(event) { 

  function init(els) {
    Array.prototype.forEach.call(els, function (el) {
      el.onclick = function () {
        var el = this;
        var urlField = document.getElementById(el.id + '_url');
        var mimeField = document.getElementById(el.id + '_mimetype');
        var filenameDisplay = document.getElementById(el.id + '_filename');

        filepicker.setKey(el.getAttribute('data-fp-apikey'));
        var opts = {
          mimetypes: el.getAttribute('data-fp-mimetypes').split(','),
        };
        if (el.hasAttribute('data-fp-opento')) {
          opts.openTo = el.getAttribute('data-fp-opento');
        }
        if (el.hasAttribute('data-fp-services')) {
          opts.services = el.getAttribute('data-fp-services').split(',')
        }

        filepicker.pick(
          opts,
          function success (blob) {
            urlField.value = blob.url;
            mimeField.value = blob.mimetype;
            filenameDisplay.textContent = blob.filename;
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
