
CM.Favorite = {};

CM.Favorite.Handlers =  {
  init: function () {
    this.initListeners()
  },

  initListeners: function () {
    $('.favorites-filter').click(function (e) {
      e.preventDefault();

      var target = $(e.currentTarget);
      var checkbox = target.find('.favorites-checkbox')
      if ( checkbox.is(":checked") ) {
        $.post(target.attr('data-clear-url')).done( function (result) {
          if (result.success) {
            checkbox.prop('checked', false);
          }
        });
      }
      else {
        $.post(target.attr('data-set-url')).done( function (result) {
          if (result.success) {
            checkbox.prop('checked', true);
          }
        });
      }
    })
  },
};



$(document).ready(function () {
  CM.Favorite.Handlers.init();
});