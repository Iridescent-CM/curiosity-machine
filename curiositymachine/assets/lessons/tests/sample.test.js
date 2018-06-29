import Api from '../api';

test('whatevs', () => {
  var api = new Api({});
  expect(api.disabled).toBeTruthy();
});