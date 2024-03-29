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
    $('.question-text').val(question.text());
    this.config.currentQuestion = question;
  },
};

$(document).ready(function() {

  $('.materials-form').css("display", "none");

  $('.edit-materials').on('click', function(e) {
    $(this).parent().hide()
    $('.materials-form').show()
  });

    //reflect pickers
  CM.Challenge.Reflect.init();

});

