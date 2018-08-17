import axios from 'axios';

const client = axios.create({
  xsrfCookieName: 'csrftoken',
  xsrfHeaderName: 'X-CSRFToken',
  baseURL: '/lessons/'
})

export default function Api(opts) {
  this.disabled = !opts.progress;

  this.list = function(role) {
    var url = 'comment/?lesson_progress=' + opts.progress;
    if (role) {
      url += '&role=' + role;
    }
    return client
    .get(url)
    .then(function (response) {
      return response.data;
    });
  };

  this.retrieve = function(comment) {
    return client
    .get('comment/' + comment + '/')
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
        upload: data.upload,
        role: data.role
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
