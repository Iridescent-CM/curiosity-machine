<template>
  <div v-if="loaded">

    <div class="m-2 ml-4">
      <i class="checkbox" :class="{ 'checkbox-checked': checklist.items.email_unique }"></i>
      Your email is not shared with other accounts.
    </div>
    <div class="m-2 ml-4">
      <i class="checkbox" :class="{ 'checkbox-checked': checklist.items.email_verified }"></i>
      You have verified your email address.
    </div>
    <div class="m-2 ml-4">
      <i class="checkbox" :class="{ 'checkbox-checked': checklist.items.enough_challenges_completed }"></i>
      You have completed at least 3 design challenges.
    </div>
    <div class="m-2 ml-4">
      <i class="checkbox" :class="{ 'checkbox-checked': checklist.items.post_survey_taken }"></i>
      You have completed the post-survey.
      <div class="v-survey-controls" v-if="!checklist.items.post_survey_taken">
        <div class="card">
          <div class="card-body">
            <a class="btn btn-primary" :href="checklist.post_survey_url">Take survey</a>
          </div>
        </div>
      </div>
    </div>
    <div class="m-2 ml-4">
      <i class="checkbox v-family-checkbox" :class="{ 'checkbox-checked': checklist.items.family_confirmed_all_listed }"></i>
      Your family members are all listed.
      <div class="v-family-controls" v-if="!checklist.items.family_confirmed_all_listed">
        <div class="card">
          <div class="card-body">
            <slot name="family_members"></slot>
          </div>
          <div class="card-body">
            <p>Are all your family members listed?</p>
            <button class="btn btn-primary v-confirm-family" @click="confirm_family">Yes</button>
            <a :href="change_family_members_url" class="btn btn-danger v-edit-family">No</a>
          </div>
        </div>
      </div>
    </div>

    <div class="my-5">
      <div class="card">
        <div class="card-body d-flex flex-column align-items-center">
          <strong class="mb-3">On Award Force you will have to submit...</strong>
          <ul>
            <li>4-5 minute video that explains your project</li>
            <li>A title and a description of your project</li>
            <li>Up to 4 photos of your project (optional)</li>
          </ul>

          <a v-if="checklist.complete" class="btn btn-primary v-create" :href="create_url">Create account</a>
          <a v-else class="btn btn-primary disabled v-create" href="#">Create account</a>
        </div>
      </div>
    </div>
  </div>

  <div v-else>

    <slot name="loader"></slot>

  </div>
</template>

<script>
  import Api from './api';
  import promiseFinally from 'promise.prototype.finally';
  promiseFinally.shim();

  export default {
    props: [
      'create_url',
      'change_family_members_url',
    ],

    data: function () {
      return {
        loaded: false,
        api: new Api(),
        checklist: {}
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
      },

      confirm_family: function () {
        var that = this;
        that.api.confirm_family()
        .then(function () {
          that.load();
        })
        .catch(function (error) {
          console.log(error); // TODO
        });
      },
    }
  }
</script>

<style>
</style>
