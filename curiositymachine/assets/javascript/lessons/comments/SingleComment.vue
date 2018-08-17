<template>
  <div>
    <template v-if="comment">
      <slot name="comment-header"></slot>
      <comment
        :key="comment.id"
        v-bind:initial="comment"
        v-bind:api="api"
        v-on:remove="remove"
      ></comment>
    </template>

    <template v-else>
      <slot name="no-comment-header"></slot>
      <div class="my-3">
        <textarea
          class="form-control"
          disabled
          v-bind:disabled="disabled"
          v-bind:placeholder="placeholder"
          v-model="newComment"></textarea>

        <button type="submit"
          class="btn btn-primary mt-3"
          disabled
          v-bind:disabled="disabled"
          @click="addComment">Post</button>
      </div>
    </template>

    <div v-if="error">
      <div class="alert alert-danger">
        <small>
          Error encountered
        </small>
      </div>
    </div>

  </div>
</template>

<script>
  import Comment from './Comment.vue'
  import Api from './api';
  import promiseFinally from 'promise.prototype.finally';
  promiseFinally.shim();

  export default {

    components: {
      Comment
    },

    props: {
      'author': String,
      'progress': String,
      'role': String,
      'placeholder': {
        type: String,
        default: "Post a comment"
      }
    },

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
          Rollbar.error("error getting comment", error);
        })
        .finally(function () {
          that.pending -= 1;
        });
      },

      addComment: function () {
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
          that.comment = response.data;
        })
        .catch(function (error) {
          that.error = true;
          Rollbar.error("error adding text comment", error);
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