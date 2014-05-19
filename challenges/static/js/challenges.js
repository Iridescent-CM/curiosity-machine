
CM.Challenge = {};

CM.Challenge.Reflect = {
  config: {
    firstQuestion: null,
    currentQuestion : null
  },
  init : function() {
    this.config.firstQuestion = $('.challenge-reflect-questions li').first();
    this.config.currentQuestion = this.config.firstQuestion;
    this.updateQuestion(true); //argument specifys if it is the first update
    this.bind();
  },
  bind : function() {
    var self = this;
    //questions
    $('.reflect-question .refresh').on('click', function() {
      self.updateQuestion();
    });
    //images
    $('#reflect-images-selector li').on('click', function() {
      self.selectImage($(this));
    });

    $('#reflect-images-modal .btn-primary').on('click', function() {
      self.saveImage($('#reflect-images-selector .selected'));
    })

  },
  updateQuestion : function(isFirst) {
    var self = this;
    var currentIndex = self.config.currentQuestion.index()
    if (isFirst || currentIndex + 2 > $('.challenge-reflect-questions li').length) {
      self.updateFields(self.config.firstQuestion);
    } else {
      self.updateFields($('.challenge-reflect-questions li').eq(currentIndex + 1));
    }
  },
  updateFields : function(question) {
    $('.reflect-question .question').text(question.text());
    $('#id_question_text').val(question.text());
    this.config.currentQuestion = question;
  },
  selectImage : function(li) {
    li.siblings().removeClass('selected');
    li.addClass('selected');
  },
  saveImage : function(li) {
    if (li.length) {
      var src = li.find('img').attr('src');
      $('#id_picture_filepicker_url').val(src);
      $('#reflect-images img').remove();
      $('#reflect-images .img-wrapper').append('<img src="' + src + '" />')
    } else {
      //close modal
    }
  }
};

$(document).ready(function() {

  //change the comment form action url from build to test
  $('.stage-switch input').on('change', function(e) {
    var url = $('.stage-switch input:checked').parent().find('.url').val();
    $('.comment-form').attr('action', url);
  });


  $('.challenge-progress-form').on('submit', function(e) {
    e.preventDefault();
    var $self = $(this);
    var data = {
      url: $self.attr('action'), 
      type:$self.attr('method'), data: $self.serialize()
    }
    console.log(data);
    $.ajax(data).done(function(data) {
      location.reload();
    }).fail(function(data) {
      console.log(data);
      alert( "There was an error switching progress. try again later" );
    })

  });

  $('.comment-form').find('input[type=filepicker-dragdrop]').on('change', function(e) {
    disable_submit_until_filled(this);
  });

  $('.comment-form textarea').on('keyup', function(e) {
    disable_submit_until_filled(this);
  });

    //reflect pickers
  CM.Challenge.Reflect.init();

});

function disable_submit_until_filled(element) {
  var empty = false;
  var form = element.form;
  $(form).find(':input').each(function() {
      if ((this.type == 'text'|| this.type == 'textarea') && $(this).val() == '') {
          empty = true;
      }
  });
  if (empty) {
      $(form).find('input[type=submit]').attr('disabled', 'disabled');
  } else {
      $(form).find('input[type=submit]').removeAttr('disabled');
  }
}

