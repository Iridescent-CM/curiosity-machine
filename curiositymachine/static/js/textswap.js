// find every element with a "data-text-swap" attribute on the page
// when it's clicked:
// find the element inside it with a "show" class and remove the "hidden-xl-down" class, and
// find the element inside with a "hide" class and add the "hidden-xl-down" class
// if it's clicked again, do the opposite

$('[data-text-swap]').click( function(idx,el) {
  console.log($($(el).attr('href')));
  $( ".show" ).removeClass( "hidden-xl-down" );
  $( ".hide" ).addClass( "hidden-xl-down" );
});


// $('.collapse').on('hidden.bs.collapse', function () {
//   var $trigger = $('[href="#' + this.id + '"], [data-target="#' + this.id + '"]')
//   $trigger.find( ".show" ).removeClass( "hidden-xl-down" );
//   $trigger.find( ".hide" ).addClass( "hidden-xl-down" );
// })
//
// $('.collapse').on('show.bs.collapse', function () {
//   var $trigger = $('[href="#' + this.id + '"], [data-target="#' + this.id + '"]')
//   $trigger.find( ".show" ).addClass( "hidden-xl-down" );
//   $trigger.find( ".hide" ).removeClass( "hidden-xl-down" );
// })

// $('#outline-button').on("mouseover", function() {
//     $('#outline').css({fill: "red"});
//     $(this).css({color: "red"});
// });

// $('[data-text-swap]').each(function(idx, el) {
//     console.log($($(el).attr('href'))
//   );
// });
