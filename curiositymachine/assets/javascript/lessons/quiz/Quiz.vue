<template>
  <div class="quiz" v-bind:class="{ correct: quiz.correct }">

    <div v-if="!quiz.answered">
      <slot name="start-header"></slot>
    </div>
    <div v-else-if="quiz.correct">
      <slot name="correct-header"></slot>
    </div>
    <div v-else>
      <slot name="incorrect-header"></slot>
    </div>

    <template v-for="(question, q_index) in quiz.questions">
      <strong>{{ question.text }}</strong>
      <template v-for="(option, o_index) in question.options">
        <div class="form-check">
          <span class="grading-mark grading-mark-correct" v-if="isCorrect(question, option)">✓</span>
          <span class="grading-mark grading-mark-incorrect" v-if="isIncorrect(question, option)">✗</span>
          <input
            :disabled="isDisabled(question, option)"
            class="form-check-input"
            type="radio"
            :name="inputAttrs(q_index, o_index).name"
            :id="inputAttrs(q_index, o_index).id"
            :value="inputAttrs(q_index, o_index).value"
            v-model="quiz.answers[q_index]"
          >
          <label class="form-check-label" :for="inputAttrs(q_index, o_index).id">
            {{ option.text }}
          </label>
        </div>
      </template>
      <hr />
      <div v-if="question.correct">
        <p>
          Explanation:
        </p>
        <p v-html="question.explanation"></p>
      </div>
    </template>

    <button
      class="btn btn-primary d-block mx-auto"
      @click="submit"
      v-if="showSubmit"
      v-bind:disabled="!submittable"
      v-text="submitText"
    ></button>
  </div>
</template>

<script>
  import Api from './api';
  import promiseFinally from 'promise.prototype.finally';
  promiseFinally.shim();

  export default {

    props: {
      quizId: Number, 
      takerId: Number,
    },

    data: function () {
      return {
        quiz: {},
        pending: 0,
      }
    },

    computed: {
      showSubmit: function () {
        return !this.quiz.answered || !this.quiz.correct;
      },

      submitText: function () {
        return this.quiz.answered && !this.quiz.correct ? "Try again" : "Submit";
      },

      submittable: function () {
        return this.quiz
          && this.quiz.questions
          && this.quiz.answers
          && this.quiz.questions.length === this.quiz.answers.length
          && !this.pending;
      },

      takingDisabled: function () {
        return !this.takerId;
      }
    },

    created: function () {
      var opts = {
        quiz: this.quizId,
        taker: this.takerId
      }
      this.api = new Api(opts);
      this.getQuiz();
    },

    methods: {

      submit: function () {
        var that = this;
        that.pending += 1;
        that.api
        .submit({ answers: that.quiz.answers })
        .then(function (data) {
          return that.getQuiz();
        })
        .catch(function (error) {
          console.log(error); // TODO
        })
        .finally(function () {
          that.pending -= 1;
        });
      },

      getQuiz: function() {
        var that = this;
        that.pending += 1;
        that.api
        .get_quiz()
        .then(function (data) {
          that.quiz = data;
        })
        .catch(function (error) {
          console.log(error); // TODO
        })
        .finally(function () {
          that.pending -= 1;
        });
      },

      isCorrect: function(question, option) {
        return option.selected && question.correct;
      },

      isIncorrect: function(question, option) {
        return option.selected && !question.correct;
      },
      
      isDisabled: function(question, option) {
        return this.takingDisabled || (question.answered && question.correct);
      },

      inputAttrs: function(question_idx, option_idx) {
        return {
          name: 'answer_' + (question_idx + 1),
          id: 'answer_' + (question_idx + 1) + '_' + (option_idx + 1),
          value: option_idx + 1
        }
      },

    }
  }
</script>

<style>
</style>
