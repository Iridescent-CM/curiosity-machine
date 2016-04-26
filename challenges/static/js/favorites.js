$(function(){
  $("input[data-toggle='favorite']").change(function(){
    var url = $(this).attr(this.checked ? 'data-set-url' : 'data-clear-url');
    $.post(url).done(function(result){
      if (!result.success) ; // TODO: error handling
    });
  });
});