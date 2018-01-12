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

  function init(context, opts) {
    var opts = opts || {};
    $('select[name$="family_role"]', context).each(function(i, el){
      var $el = $(el);
      var $group = $el.closest('fieldset').find('.form-group:has(select[name$="birthday_year"])');
      sync($el, $group, opts);
      $el.change(sync.bind(null, $el, $group));
    });
  }

  $(document).on("click", "*[data-formset-add]", function(evt){
    evt.preventDefault();

    var prefix = $(evt.target).attr('data-formset-add');
    var $template = $('script[data-formset="' + prefix + '"]')
    var $total = $('input[name="' + prefix + '-TOTAL_FORMS"]');
    var idx = parseInt($total.val())
    var added = $($template.text().replace(/__prefix__/g, idx)).insertAfter($template);
    init(added);
    $total.val(idx + 1);
  });

  init();
});
