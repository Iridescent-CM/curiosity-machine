function transform(form, prefix) {
  var day = $('#id_' + prefix + '-birthday_day', form).val();
  var month = $('#id_' + prefix + '-birthday_month', form).val() - 1;
  var year = $('#id_' + prefix + '-birthday_year', form).val();
  var today = new Date();
  var age = today.getFullYear() - year;
  if (today.getMonth() < month || (today.getMonth() == month && today.getDate() < day)) {
    age--; //birthday hasn't happened this year
  }
  if (age < 13) {
    $('.parent-info', form).show();
    $('.student-column', form).removeClass('col-md-6').addClass('col-md-4');
    $(".student-column label[for='id_" + prefix + "-email']", form).text('Parent Email:');
  } else {
    $('.parent-info', form).hide();
    $('.student-column', form).removeClass('col-md-4').addClass('col-md-6');
    $(".student-column label[for='id_" + prefix + "-email']", form).text('Email:');
  }
}

$(function(){
  $('[data-apply="coppa-transforms"]').each(function(){
    var form = this;
    var prefix = $(form).attr('data-prefix');
    $('.birthday-field', form).find('select').on('change', function(e) {
      transform(form, prefix);
    });
    transform(form, prefix);
  });
});
