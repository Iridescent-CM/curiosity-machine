<template>
  <div v-if="loaded">

    <div>
      <i class="checkbox" :class="{ 'checkbox-checked': checklist.email_unique }"></i>
      Your email is not shared with other accounts.
    </div>
    <div>
      <i class="checkbox" :class="{ 'checkbox-checked': checklist.email_verified }"></i>
      You have verified your email address.
    </div>
    <div>
      <i class="checkbox" :class="{ 'checkbox-checked': checklist.enough_challenges_completed }"></i>
      You have completed at least 3 design challenges.
    </div>
    <div>
      <i class="checkbox" :class="{ 'checkbox-checked': checklist.post_survey_taken }"></i>
      You have completed the post-survey.
    </div>
    <div>
      <i class="checkbox" :class="{ 'checkbox-checked': checklist.family_confirmed_all_listed }"></i>
      Your family members are all listed.
    </div>

    <div v-if="checklist.complete">
      <a class="btn btn-primary" :href="create_url">Create account</a>
    </div>
  </div>

  <div v-else>

    <slot></slot>

  </div>
</template>

<script>
  import Api from './api';
  import promiseFinally from 'promise.prototype.finally';
  promiseFinally.shim();

  export default {
    props: ['create_url'],

    data: function () {
      return {
        loaded: false,
        api: new Api()
      }
    },

    created: function () {
      var that = this;
      that.load()
      .finally(function () {
        that.loaded = true;
      });
    },

    methods: {
      load: function () {
        var that = this;
        return that.api.get()
        .then(function (data) {
          that.checklist = data;
        })
        .catch(function (error) {
          console.log(error); // TODO
        });
      }
    }
  }
</script>

<style>
</style>
