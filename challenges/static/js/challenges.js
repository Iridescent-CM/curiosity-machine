$(document).ready(function() {

  //change the comment form action url from build to test
  $('.stage-switch input').on('change', function(e) {
    var url = $('.stage-switch input:checked').parent().find('.url').val();
    $('.comment-form').attr('action', url);
  });


  $('.challenge-progress-form').on('submit', function(e) {
    e.preventDefault();
    var $self = $(this);
    var data = {
      url: $self.attr('action'), 
      type:$self.attr('method'), data: $self.serialize()
    }
    console.log(data);
    $.ajax(data).done(function(data) {
      location.reload();
    }).fail(function(data) {
      console.log(data);
      alert( "There was an error switching progress. try again later" );
    })

  });

});