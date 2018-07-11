import axios from 'axios';

const client = axios.create({
  xsrfCookieName: 'csrftoken',
  xsrfHeaderName: 'X-CSRFToken',
  baseURL: '/lessons/'
})

export default function Api(opts) {
  this.enabled = opts.enabled !== undefined ? opts.enabled : true;

  this.get_quiz = function() {
    var url = 'quiz/' + opts.quiz + '/';
    if (opts.taker) {
      url += '?taker=' + opts.taker;
    }
    return client
    .get(url)
    .then(function (response) {
      return response.data;
    });
  };

  this.submit = function(data) {
    data.quiz = opts.quiz;
    data.taker = opts.taker;

    return client
    .post('quiz_result/', data)
    .then(function (response) {
      return response.data;
    });
  };
}
