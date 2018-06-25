import axios from 'axios';

axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'

export default function Api(opts) {
  this.disabled = !opts.progress;

  this.list = function() {
    return axios
    .get('/lessons/comment/?lesson_progress=' + opts.progress)
    .then(function (response) {
      return response.data;
    });
  };

  this.create = function(data) {
    data.upload = data.upload || {};
    data.text = data.text || "";

    return axios
    .post(
      '/lessons/comment/',
      {
        author: opts.author,
        lesson_progress: opts.progress,
        text: data.text,
        upload: data.upload
      }
    );
  };

  this.update = function(comment, data) {
    return axios
    .patch(
      '/lessons/comment/' + comment + '/',
      data
    );
  };

  this.destroy = function(comment) {
    return axios.delete(
      '/lessons/comment/' + comment + '/'
    );
  };
}
