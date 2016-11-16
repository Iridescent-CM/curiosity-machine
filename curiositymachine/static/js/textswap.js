$('[data-text-swap]').on('hidden.bs.collapse', function () {
  var $trigger = $('[href="#' + this.id + '"], [data-target="#' + this.id + '"]')
  $trigger.find( ".show" ).removeClass( "hidden-xl-down" );
  $trigger.find( ".hide" ).addClass( "hidden-xl-down" );
})

$('[data-text-swap]').on('show.bs.collapse', function () {
  var $trigger = $('[href="#' + this.id + '"], [data-target="#' + this.id + '"]')
  $trigger.find( ".show" ).addClass( "hidden-xl-down" );
  $trigger.find( ".hide" ).removeClass( "hidden-xl-down" );
})
