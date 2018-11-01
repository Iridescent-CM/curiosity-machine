<template>
  <div v-if="loaded">

    <div class="m-2 ml-4">
      <i class="checkbox" :class="{ 'checkbox-checked': checklist.items.email_has_not_been_used }"></i>
      Your email has not been used to start a submission.
      <div class="v-email-change-controls" v-if="!checklist.items.email_has_not_been_used">
        <div class="card">
          <div class="card-body">
            <p>
              Another account has used this email address to begin a submission. Please choose a new email address to begin a submission from this account.
            </p>

            <form class="form-inline">
              <label class="sr-only" for="email_change_controls_email_field">Email address</label>
              <input
                type="email"
                class="form-control mr-3"
                v-bind:class="email_change_classes"
                id="email_change_controls_email_field"
                v-model="email"
                placeholder="Email address"
              />
              <div v-for="error in email_save_response_errors" class="invalid-feedback">{{ error[0] }}</div>
              <button class="btn btn-primary" :disabled="email_change_controls_save_disabled" @click="submit_email">Save</button>
              <small v-if="submit_email_pending" class="text-muted ml-2">Please wait...</small>
            </form>

          </div>
        </div>
      </div>
    </div>
    <div class="m-2 ml-4">
      <i class="checkbox" :class="{ 'checkbox-checked': checklist.items.email_verified }"></i>
      You have verified your email address.
      <div class="v-verified-email-controls" v-if="!checklist.items.email_verified">
        <div class="card">
          <div class="card-body">
            <p>
              Check your email (<strong>{{ checklist.email_address }}</strong>) and follow the instructions to verify your email.
            </p>
            <button class="btn btn-primary" @click="resend_verification_email">Re-send verification</button>
          </div>
        </div>
      </div>
    </div>
    <div class="m-2 ml-4">
      <i class="checkbox" :class="{ 'checkbox-checked': checklist.items.enough_challenges_completed }"></i>
      You have completed at least {{ checklist.challenge_count_required }} design challenges.
      <div class="v-challenge-count-controls" v-if="!checklist.items.enough_challenges_completed">
        <div class="card">
          <div class="card-body">
            <p>
              Please upload a picture, video or text to {{ checklist.challenge_count_required }} or more AI Family Challenge design challenges.
            </p>
          </div>
        </div>
      </div>
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

    <div class="my-5 d-flex justify-content-center">
      <a v-if="checklist.complete" class="btn btn-primary v-create" :href="create_url">I'm ready to submit!</a>
      <a v-else class="btn btn-primary disabled v-create" href="#">I'm ready to submit!</a>
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
        checklist: {},
        email: undefined,
        email_save_response: undefined,
        submit_email_pending: false
      }
    },

    computed: {
      challenge_count_remaining: function () {
        return this.checklist.challenge_count_required - this.checklist.challenges_completed;
      },
      email_change_controls_save_disabled: function() {
        return !this.email || this.submit_email_pending;
      },
      email_change_classes: function () {
        return {
          'is-invalid': this.email_save_response && this.email_save_response.status === 'error',
        }
      },
      email_save_response_errors: function () {
        if (this.email_save_response && this.email_save_response.errors) {
          return this.email_save_response.errors.email;
        }
        return undefined;
      }
    },

    created: function () {
      var that = this;
      that.load()
      .then(function (data) {
        that.email = that.checklist.email_address;
      })
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

      resend_verification_email: function () {
        var that = this;
        that.api.resend_verification_email()
        .then(function () {
          // ?
        })
        .catch(function (error) {
          console.log(error); // TODO
        });
      },

      submit_email: function (e) {
        e.preventDefault();

        var that = this;
        that.submit_email_pending = true;
        that.api.change_email(that.email)
        .then(function (data) {
          that.email_save_response = data;
          that.load();
        })
        .catch(function (error) {
          console.log(error);
        })
        .finally(function () {
          that.submit_email_pending = false;
        });

      }
    }
  }
</script>

<style>
</style>
