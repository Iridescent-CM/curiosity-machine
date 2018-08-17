import $ from "jquery";

$(function() {
  $('.modal').on('shown.bs.modal', function () {
    $(this).find('input:visible, textarea:visible').first().select();
  });
});
