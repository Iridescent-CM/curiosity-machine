/*
* Google Analytics Plugin
* Requires
*
*/

(function($) {

$.extend(mejs.MepDefaults, {
  googleAnalyticsTitle: '',
  googleAnalyticsCategory: 'Videos',
  googleAnalyticsEventPlay: 'Play',
  googleAnalyticsEventPause: 'Pause',
  googleAnalyticsEventEnded: 'Ended',
  googleAnalyticsEventTime: 'Time'
});


$.extend(MediaElementPlayer.prototype, {
  buildgoogleanalytics: function(player, controls, layers, media) {
    player._lastTime = 0;
    $(window).bind('beforeunload', function(e) {
        if (player._lastTime > 0) {
          //NB: still not sure if this works.
          //looks like the browser closes a second after this function is executing
          ga('send', {
              'hitType': 'timing',
              'timingCategory': player.options.googleAnalyticsCategory,
              'timingVar': player.options.googleAnalyticsEventTime,
              'timingValue': player._lastTime,
              'timingLabel': (player.options.googleAnalyticsTitle === '') ? player.node.baseURI : player.options.googleAnalyticsTitle
          });
          sleep(1000);
        }
    });

    media.addEventListener('playing', function (e) {
        player.intervalCounter = setInterval(function () {
            var currentTime = media.currentTime;

            if (!isNaN(currentTime) && currentTime > 0) {
                player._lastTime += 50;
            }
        }, 50);

    }, false);

    media.addEventListener('play', function() {
      if (typeof ga != 'undefined') {
        ga('send', 'event', 
          player.options.googleAnalyticsCategory, 
          player.options.googleAnalyticsEventPlay, 
          // (player.options.googleAnalyticsTitle === '') ? player.currentSrc : player.options.googleAnalyticsTitle
          (player.options.googleAnalyticsTitle === '') ? player.node.baseURI : player.options.googleAnalyticsTitle
        );
        
      }
    }, false);
    
    media.addEventListener('pause', function() {
      if (typeof ga != 'undefined') {
        ga('send', 'event', 
          player.options.googleAnalyticsCategory, 
          player.options.googleAnalyticsEventPause, 
          // (player.options.googleAnalyticsTitle === '') ? player.currentSrc : player.options.googleAnalyticsTitle
          (player.options.googleAnalyticsTitle === '') ? player.node.baseURI : player.options.googleAnalyticsTitle
        );
        clearInterval(player.intervalCounter);
      }
    }, false);  
    
    media.addEventListener('ended', function() {
      if (typeof ga != 'undefined') {
        ga('send', 'event', 
          player.options.googleAnalyticsCategory, 
          player.options.googleAnalyticsEventEnded, 
          // (player.options.googleAnalyticsTitle === '') ? player.currentSrc : player.options.googleAnalyticsTitle
          (player.options.googleAnalyticsTitle === '') ? player.node.baseURI : player.options.googleAnalyticsTitle
        );
      }
      clearInterval(player.intervalCounter);
      if (player._lastTime > 0) {
          ga('send', {
              'hitType': 'timing',
              'timingCategory': player.options.googleAnalyticsCategory,
              'timingVar': player.options.googleAnalyticsEventTime,
              'timingValue': player._lastTime,
              'timingLabel': (player.options.googleAnalyticsTitle === '') ? player.node.baseURI : player.options.googleAnalyticsTitle
          });
          player._lastTime = 0;
        }
    }, false);
    
    /*
    media.addEventListener('timeupdate', function() {
      if (typeof _gaq != 'undefined') {
        _gaq.push(['_trackEvent', 
          player.options.googleAnalyticsCategory, 
          player.options.googleAnalyticsEventEnded, 
          player.options.googleAnalyticsTime,
          (player.options.googleAnalyticsTitle === '') ? player.currentSrc : player.options.googleAnalyticsTitle,
          player.currentTime
        ]);
      }
    }, true);
    */
  }
});
  
})(mejs.$);