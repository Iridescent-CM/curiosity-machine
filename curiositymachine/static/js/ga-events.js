$(document).ready(function(){

  $('.modal').on('show.bs.modal', function(){
    ga('send', 'event', 'modal', 'show', $(this).attr('id'));
  });
  $('.modal').on('hide.bs.modal', function(){
    ga('send', 'event', 'modal', 'hide', $(this).attr('id'));
  });

});
