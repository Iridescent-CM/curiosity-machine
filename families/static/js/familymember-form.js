$(function(){
  function sync($el, $group, opts) {
    var opts = opts || {};
    var duration = opts.duration || "fast";
    if ($el.val() === "1") {
      $group.show(duration);
    }
    else {
      $group.hide(duration);
    }
  }

  function initGroups(context, opts) {
    var opts = opts || {};
    $('select[name$="family_role"]', context).each(function(i, el){
      var $el = $(el);
      var $group = $el.closest('fieldset').find('.form-group:has(input[name$="age"])');
      sync($el, $group, opts);
      $el.change(sync.bind(null, $el, $group));
    });
  }

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
    initGroups(added);
    $total.val(idx + 1);
    checkControls($(evt.target), $total.val());
  });

  initGroups();
  checkControls();
});
