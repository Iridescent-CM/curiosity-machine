(function(window){

  // https://davidwalsh.name/query-string-javascript
  function getUrlParameter(name) {
    name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
    var regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
    var results = regex.exec(location.search);
    return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
  }

  if (!window.d3) return;

  var d3 = window.d3;
  var oldfn = d3.json;

  console.log("d3 ajax controls:");
  console.log("    Interferes with d3.json() call to introduce delays and errors.");
  console.log("");
  console.log("    Query parameters:");
  console.log("        force_d3_ajax_wait=<int> - will slow response up to <int> seconds maximum (default: 3)");
  console.log("        force_d3_ajax_error_result=[always|random|never] - choose method of forcing ajax error result (default: random)");
  console.log("");

  d3.json = function (url, callback) {
    var maxWait = parseInt(getUrlParameter('force_d3_ajax_wait')) || 3;
    var errorMode = getUrlParameter('force_d3_ajax_error_result') || 'random';
    var wait = Math.round(Math.random() * maxWait);
    console.log("d3.json(): waiting " + wait + " seconds, error mode " + errorMode);
    oldfn(url, function(err, data) {
      setTimeout(function() {
        if (errorMode == 'always') callback('error');
        else if (errorMode == 'random' && Math.random() < 0.3) callback('error');
        else callback(err, data);
      }, wait * 1000);
    });
  };

})(window);
