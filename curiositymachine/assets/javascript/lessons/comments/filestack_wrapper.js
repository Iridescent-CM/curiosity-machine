import * as filestack from 'filestack-js';

export default function(key) {

  const fsclient = filestack.init(key);

  return {
    pick: function() {
      return new Promise(function(resolve, reject) {
        fsclient.picker({
          uploadInBackground: false,
          fromSources: ['local_file_system', 'webcam', 'video'],
          accept: ['video/*', 'image/*', '.pdf'],
          onFileUploadFinished: resolve,
          onFileUploadFailed: function(upload, error) {
            reject(error);
          },
          onCancel: function() {
            reject();
          }
        }).open();
      });
    }
  }
}
