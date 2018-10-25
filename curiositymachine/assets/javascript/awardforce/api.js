import axios from 'axios';

const client = axios.create({
  xsrfCookieName: 'csrftoken',
  xsrfHeaderName: 'X-CSRFToken',
  baseURL: '/family/'
})

export default function Api(opts) {
  this.get = function () {
    var url = 'checklist/';
    return client.get(url)
      .then(function (response) {
        return response.data;
      });
  };
}
