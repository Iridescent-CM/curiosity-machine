import axios from 'axios';

const client = axios.create({
  xsrfCookieName: 'csrftoken',
  xsrfHeaderName: 'X-CSRFToken',
  baseURL: '/lessons/'
})

export default function Api(opts) {
  this.disabled = !opts.progress;

  this.list = function() {
    return client
    .get('comment/?lesson_progress=' + opts.progress)
    .then(function (response) {
      return response.data;
    });
  };

  this.create = function(data) {
    data.upload = data.upload || {};
    data.text = data.text || "";

    return client
    .post(
      'comment/',
      {
        author: opts.author,
        lesson_progress: opts.progress,
        text: data.text,
        upload: data.upload
      }
    );
  };

  this.update = function(comment, data) {
    return client
    .patch(
      'comment/' + comment + '/',
      data
    );
  };

  this.destroy = function(comment) {
    return client.delete(
      'comment/' + comment + '/'
    );
  };
}
