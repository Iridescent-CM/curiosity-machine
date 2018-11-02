$(function(){
  function checkControls($control, total) {
    var $control = $control || $("[data-formset-add]");
    var prefix = $control.attr('data-formset-add');
    var total = total || $('input[name="' + prefix + '-TOTAL_FORMS"]').val();
    var max = $('input[name="' + prefix + '-MAX_NUM_FORMS"]').val();

    $control.prop("disabled", total >= max);
  }

  $(document).on("click", "*[data-formset-add]", function(evt){
    evt.preventDefault();

    var prefix = $(evt.target).attr('data-formset-add');
    var $template = $('script[data-formset="' + prefix + '"]')
    var $total = $('input[name="' + prefix + '-TOTAL_FORMS"]');
    var idx = parseInt($total.val())
    var added = $($template.text().replace(/__prefix__/g, idx)).insertAfter($template);
    $total.val(idx + 1);
    checkControls($(evt.target), $total.val());
  });

  checkControls();
});
