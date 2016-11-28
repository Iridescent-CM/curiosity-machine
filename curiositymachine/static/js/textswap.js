// $('[data-text-swap]').on('hidden.bs.collapse', function () {
//   var $trigger = $('[href="#' + this.id + '"], [data-target="#' + this.id + '"]')
//   $trigger.find( ".show" ).removeClass( "hidden-xl-down" );
//   $trigger.find( ".hide" ).addClass( "hidden-xl-down" );
// })
//
// $('[data-text-swap]').on('show.bs.collapse', function () {
//   var $trigger = $('[href="#' + this.id + '"], [data-target="#' + this.id + '"]')
//   $trigger.find( ".show" ).addClass( "hidden-xl-down" );
//   $trigger.find( ".hide" ).removeClass( "hidden-xl-down" );
// })

$('[data-text-swap-trigger]').on("click", function () {
  $(this).find( ".show" ).addClass( "hidden-xl-down" );
  $(this).find( ".hide" ).removeClass( "hidden-xl-down" );
})

$('[data-text-swap-trigger]').on("click", function () {
  $(this).find( ".show" ).removeClass( "hidden-xl-down" );
  $(this).find( ".hide" ).addClass( "hidden-xl-down" );
})

// $('[data-text-swap-trigger]').on('show.bs.collapse', function () {
//   find( ".show" ).addClass( "hidden-xl-down" );
//   find( ".hide" ).removeClass( "hidden-xl-down" );
// })


// console.log('got em');
