(function() {
  /*
   * django_ace doesn't make .setTabSize() available, but 
   * we can retrieve the editors and set it on each this way.
   */

  function init() {
    var editors = document.getElementsByClassName('ace_editor');

    for (var i = 0; i < editors.length; i++) {
      var editor = ace.edit(editors[i]);
      editor.getSession().setTabSize(2);
    }
  }

  if (window.addEventListener) { // W3C
      window.addEventListener('load', init);
  } else if (window.attachEvent) { // Microsoft
      window.attachEvent('onload', init);
  }
})();

