<template>
  <div v-if="loaded">

    <div class="mb-3">
      <i class="checkbox" :class="{ 'checkbox-checked': checklist.items.email_has_not_been_used }"></i>
      <span class="checkbox-label">Enter an email that has not been used to start a submission.</span>
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
    <div class="mb-3">
      <i class="checkbox" :class="{ 'checkbox-checked': checklist.items.email_verified }"></i>
      <span class="checkbox-label">Verify your email address.</span>
      <div class="v-verified-email-controls" v-if="!checklist.items.email_verified">
        <div class="card">
          <div class="card-body">
            <p>
              Check your email (<strong>{{ checklist.email_address }}</strong>) and follow the instructions to verify your email.
            </p>
            <button class="btn btn-primary" :disabled="verified_email_controls_disabled" @click="resend_verification_email">Re-send verification</button>
            <small v-if="verified_email_pending" class="text-muted ml-2">Please wait...</small>
            <small v-if="verified_email_sent" class="text-success ml-2">Sent, please check your inbox</small>
          </div>
        </div>
      </div>
    </div>
    <div class="mb-3" v-if="!checklist.items.exempt_from_post_survey">
      <i class="checkbox" :class="{ 'checkbox-checked': checklist.items.post_survey_taken }"></i>
      <span class="checkbox-label">Complete the post-survey.</span>
      <div class="v-survey-controls" v-if="!checklist.items.post_survey_taken">
        <div class="card">
          <div class="card-body">
            <a class="btn btn-primary" :href="checklist.post_survey_url">Take survey</a>
          </div>
        </div>
      </div>
    </div>
    <div class="mb-3">
      <i class="checkbox v-family-checkbox" :class="{ 'checkbox-checked': checklist.items.family_confirmed_all_listed }"></i>
      <span class="checkbox-label">List all of your family members.</span>
      <div class="v-family-controls" v-if="!checklist.items.family_confirmed_all_listed">
        <div class="card">
          <div class="card-body">
            <slot name="family_members"></slot>
            <p>Are all your family members listed?</p>
            <div class="mb-3">
              <button class="btn btn-primary v-confirm-family mr-2" @click="confirm_family">Yes</button>
              <a :href="change_family_members_url" class="btn btn-danger v-edit-family">No</a>
            </div>
            <small class="text-muted">You will not be able to add family members once they are confirmed.</small>
          </div>
        </div>
      </div>
    </div>

    <div class="my-5 d-flex">
      <a v-if="checklist.complete" class="btn btn-orange v-create" :href="create_url" target="_blank">I'm ready to submit!</a>
      <a v-else class="btn btn-orange disabled v-create" href="#">I'm ready to submit!</a>
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
        submit_email_pending: false,
        verified_email_pending: false,
        verified_email_sent: false
      }
    },

    computed: {
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
      },
      verified_email_controls_disabled: function () {
        return this.verified_email_pending;
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
        that.verified_email_pending = true;
        that.api.resend_verification_email()
        .catch(function (error) {
          console.log(error); // TODO
        })
        .finally(function () {
          that.verified_email_pending = false;
          that.verified_email_sent = true;
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
