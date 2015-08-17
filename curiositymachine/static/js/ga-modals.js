$(document).ready(function(){

  $('.modal[data-pageview-url]').on('show.bs.modal', function(){
    ga('send', 'pageview', $(this).attr('data-pageview-url'));
  });

});