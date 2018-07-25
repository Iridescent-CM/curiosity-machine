import $ from "jquery";

$(function() {
  var tracklinks = document.querySelectorAll('[data-ga-track="pageview"]');
  Array.prototype.forEach.call(tracklinks, function(link) {
    link.addEventListener("click", function(evt){
      var page = link.getAttribute("data-ga-page");
      ga('send', 'pageview', page);
    });
  });

  var trackVideos = document.querySelectorAll('[data-ga-track="video"]');
  Array.prototype.forEach.call(trackVideos, function(video) {
    var label = video.getAttribute("data-ga-label");

    video.addEventListener("loadstart", function(evt){
      ga('send', {
        hitType: 'event',
        eventCategory: 'Videos',
        eventAction: 'Loading',
        eventLabel: label,
        nonInteraction: true
      });
    });
    video.addEventListener("playing", function(evt){
      ga('send', {
        hitType: 'event',
        eventCategory: 'Videos',
        eventAction: 'Play',
        eventLabel: label
      });
    });
    video.addEventListener("pause", function(evt){
      ga('send', {
        hitType: 'event',
        eventCategory: 'Videos',
        eventAction: 'Pause',
        eventLabel: label
      });
    });
    video.addEventListener("seeked", function(evt){
      ga('send', {
        hitType: 'event',
        eventCategory: 'Videos',
        eventAction: 'Seek',
        eventLabel: label
      });
    });
    video.addEventListener("ended", function(evt){
      ga('send', {
        hitType: 'event',
        eventCategory: 'Videos',
        eventAction: 'Ended',
        eventLabel: label,
        nonInteraction: true
      });
    });

  });
});
