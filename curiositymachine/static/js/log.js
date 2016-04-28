window.log = function(){
  var config;

  var log = function(message, level) {
    if (!config) {
      console.log('Call CM.log.init() before using CM.log()');
      return;
    }
    
    console.log(config);
    var xhr = new XMLHttpRequest();
    xhr.open('PUT', config.endpoint);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader("X-CSRFToken", config.csrf_token);
    xhr.send(JSON.stringify({
      message: message,
      level: level
    }));
  };

  log.init = function(opts) {
    config = opts;
  };

  return log;
}();
