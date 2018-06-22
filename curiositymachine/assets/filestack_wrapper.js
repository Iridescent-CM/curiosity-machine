import * as filestack from 'filestack-js';

const fsclient = filestack.init('AGMpw9ALPRTObV0qAHZKJz');

export default function() {
  return new Promise(function(resolve, reject) {
    fsclient.picker({
      uploadInBackground: false,
      fromSources: ['local_file_system', 'webcam', 'video'],
      onFileUploadFinished: resolve,
      onFileUploadFailed: function(upload, error) {
        reject(error);
      }
    }).open();
  });
}
