<template>
  <div>

    <comment
      v-if="comment"
      :key="comment.id"
      v-bind:initial="comment"
      v-bind:api="api"
      v-bind:picker="picker"
      v-on:remove="remove"
    ></comment>

    <div v-else class="card my-3">
      <div class="card-body">
        <button
          class="btn btn-primary d-block mx-auto"
          disabled
          v-bind:disabled="disabled"
          @click="addComment"><i class="icon-camera mr-1"></i> Choose</button>
      </div>
      <div v-if="error" class="card-body">
        <div class="alert alert-danger">
          <small>
            Error encountered
          </small>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
  import Comment from './Comment.vue'
  import init from './filestack_wrapper';
  import Api from './api';

  export default {

    components: {
      Comment
    },

    props: ['author', 'progress', 'fskey', 'role'],

    data: function () {
      return {
        newComment: '',
        comment: undefined,
        api: undefined,
        error: undefined,
        pending: 0,
      };
    },

    computed: {
      disabled: function () {
        return !this.api || this.api.disabled || !!this.pending;
      },
      enabled: function () {
        return this.api && !this.api.disabled;
      }
    },

    created: function () {
      this.api = new Api({
        author: this.author,
        progress: this.progress
      });
      this.picker = init(this.fskey);
      if (this.enabled) {
        this.getCommentByRole(this.role);
      }
    },

    methods: {

      getCommentByRole: function (role) {
        var that = this;
        that.pending += 1;
        that.api
        .list(role)
        .then(function (data) {
          if (data.length > 0) {
            that.comment = data[0];
          }
          if (data.length > 1) {
            // warn?
          }
        })
        .catch(function (error) {
          that.error = true;
          //Rollbar.error("error getting comment", error);
        })
        .finally(function () {
          that.pending -= 1;
        });
      },

      addComment: function () {
        var that = this;
        that.pending += 1;
        that.picker.pick()
        .then(function (upload) {
          return that.api.create({
            upload: upload,
            role: that.role
          });
        })
        .then(function (response) {
          that.comment = response.data;
        })
        .catch(function (error) {
          console.log('error', error);
          that.error = true;
          //Rollbar.error("error adding media comment", error);
        })
        .finally(function () {
          that.pending -= 1;
        });
      },

      remove: function () {
        this.comment = undefined;
      }
    }
  }
</script>

<style>
</style>