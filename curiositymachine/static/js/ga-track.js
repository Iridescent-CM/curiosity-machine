var tracklinks = document.querySelectorAll('[data-ga-track="pageview"]');
Array.prototype.forEach.call(tracklinks, function(link) {
  link.addEventListener("click", function(evt){
    var page = link.getAttribute("data-ga-page");
    ga('send', 'pageview', page);
  });
});
