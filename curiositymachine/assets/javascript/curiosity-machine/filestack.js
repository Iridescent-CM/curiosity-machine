import * as filestack from 'filestack-js';
import $ from "jquery";

$(document).on('click', '[data-toggle="filepicker"]', function(evt) {
  const btn = this;
  const container = btn.parentNode;
  const urlField = container.querySelector('#' + btn.id + '_url');
  const mimeField = container.querySelector('#' + btn.id + '_mimetype');
  const filenameDisplay = container.querySelector('#' + btn.id + '_filename');

  const fsclient = filestack.init(btn.getAttribute('data-fp-apikey'));

  const accepted_mimetypes = $(btn).data('mimetypes').split(',');
  const types = accepted_mimetypes.reduce(function (acc, curr) {
    var type = curr.split('/')[0];
    if (acc.indexOf(type) < 0) {
      acc.push(type);
    }
    return acc;
  }, []);
  var sources = ['local_file_system'];
  if (types.indexOf("video") != -1) {
    sources.unshift('video');
  }
  if (types.indexOf("image") != -1) {
    sources.unshift('webcam');
  }
  
  var crop = $(btn).data('fp-cropratio') ? { aspectRatio: $(btn).data('fp-cropratio'), force: true } : true;

  fsclient.picker({
    uploadInBackground: false,
    accept: accepted_mimetypes,
    fromSources: sources,
    transformations: {
      circle: true,
      crop: crop,
      rotate: true,
    },
    onFileUploadFinished: function (blob) {
      urlField.value = blob.url;
      mimeField.value = blob.mimetype;
      filenameDisplay.value = blob.filename;

      var target_form = evt.target.closest("form");
      if ($(target_form).find('[data-auto-submit]').length) {
        target_form.submit();
        target_form.hidden = true;
        $('.hide_upon_submit').hide();
        $('[data-submit-replacement-text]').each(function () {
          $(this).text($(this).attr('data-submit-replacement-text'));
        });
      }
    },
    onFileUploadFailed: function() {
      if (!err.code || err.code !== 101) {
        //Rollbar.error("Filepicker returned an error", err);
        alert("We’re experiencing a problem with our media service. Our engineers are on the case, and will have things back to normal shortly.");
      }
    }
  }).open();
});
