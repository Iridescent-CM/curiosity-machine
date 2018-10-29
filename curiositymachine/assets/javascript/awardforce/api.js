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

  this.confirm_family = function () {
    var url = 'checklist/confirm_family/';
    return client.post(url);
  };

  this.resend_verification_email = function () {
    var url = 'checklist/resend_verification/';
    return client.post(url);
  };

  this.change_email = function (email_address) {
    var url = 'checklist/change_email/';
    return client.post(url, {
      email_address: email_address
    })
    .then(function (response) {
      return response.data;
    });
  };
}
