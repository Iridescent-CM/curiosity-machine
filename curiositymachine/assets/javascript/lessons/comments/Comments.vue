<template>
  <div>
    <div class="card my-3">
      <div class="card-header">
        Upload
      </div>
      <div class="card-body">
        <textarea
          class="form-control"
          disabled
          v-bind:disabled="disabled"
          placeholder="Post a comment or upload a file"
          v-model="newComment"></textarea>

        <button type="submit"
          class="btn btn-primary mt-3"
          disabled
          v-bind:disabled="disabled"
          @click="addTextComment">Post</button>

        <button
          class="btn btn-primary mt-3 ml-2"
          disabled
          v-bind:disabled="disabled"
          @click="addMediaComment"><i class="icon-camera mr-1"></i> Choose</button>
      </div>
      <div v-if="error" class="card-body">
        <div class="alert alert-danger">
          <small>
            Error encountered
          </small>
        </div>
      </div>
    </div>

    <template v-for="comment in comments">
      <comment
        :key="comment.id"
        v-bind:initial="comment"
        v-bind:api="api"
        v-bind:picker="picker"
        v-on:remove="getComments"
      ></comment>
    </template>
  </div>
</template>

<script>
  import Comment from './Comment.vue'
  import init from './filestack_wrapper';
  import Api from './api';
  import promiseFinally from 'promise.prototype.finally';
  promiseFinally.shim();

  export default {

    components: {
      Comment
    },

    props: ['author', 'progress', 'fskey', 'role'],

    data: function () {
      return {
        newComment: '',
        comments: [],
        api: undefined,
        error: undefined,
        pending: 0
      };
    },

    computed: {
      // FIXME: there's an asymmetry in enabled/disabled that isn't reflected in the naming
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
        this.getComments();
      }
    },

    methods: {

      getComments: function () {
        var that = this;
        that.pending += 1;
        that.api
        .list(that.role)
        .then(function (data) {
          that.comments = data;
        })
        .catch(function (error) {
          that.error = true;
          Rollbar.error("error getting comments", error);
        })
        .finally(function () {
          that.pending -= 1;
        });
      },

      addTextComment: function () {
        var value = this.newComment && this.newComment.trim();
        if (!value) return;
        var that = this;
        that.pending += 1;
        that.api
        .create({
          text: value,
          role: that.role
        })
        .then(function (response) {
          that.newComment = '';
          that.getComments();
        })
        .catch(function (error) {
          that.error = true;
          Rollbar.error("error adding text comment", error);
        })
        .finally(function () {
          that.pending -= 1;
        });
      },

      addMediaComment: function () {
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
          that.getComments();
        })
        .catch(function (error) {
          that.error = true;
          Rollbar.error("error adding media comment", error);
        })
        .finally(function () {
          that.pending -= 1;
        });
      }
    }
  }
</script>

<style>
</style>