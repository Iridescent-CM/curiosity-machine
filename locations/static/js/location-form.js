$(function(){
  function sync($country, $stategroup) {
    if ($country.val() === "US") {
      $stategroup.show("fast");
    }
    else {
      $stategroup.hide("fast");
    }
  }

  $('select[name="country"]').each(function(i, el){
    var $el = $(el);
    var $stategroup = $el.closest('form').find('.form-group:has(select[name="state"])');
    console.log($stategroup);
    sync($el, $stategroup);
    $el.change(sync.bind(null, $el, $stategroup));
  });
});
