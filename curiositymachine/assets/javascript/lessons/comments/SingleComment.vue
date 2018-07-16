<template>
  <div>

    <comment
      v-if="comment"
      :key="comment.id"
      v-bind:initial="comment"
      v-bind:api="api"
      v-on:remove="remove"
    ></comment>

    <div v-else class="my-3">
      <textarea
        class="form-control"
        disabled
        v-bind:disabled="disabled"
        placeholder="Post a comment"
        v-model="newComment"></textarea>

      <button type="submit"
        class="btn btn-primary mt-3"
        disabled
        v-bind:disabled="disabled"
        @click="addTextComment">Post</button>
    </div>

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

  export default {

    components: {
      Comment
    },

    props: ['author', 'progress', 'role'],

    data: function () {
      return {
        newComment: '',
        comment: undefined,
        api: undefined,
        error: undefined,
      };
    },

    computed: {
      disabled: function () {
        return !this.api || this.api.disabled;
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
        });
      },

      getComment: function (comment_id) {
        var that = this;
        that.api
        .retrieve()
        .then(function (data) {
          that.comment = data;
        })
        .catch(function (error) {
          that.error = true;
          //Rollbar.error("error getting comment", error);
        });
      },

      addTextComment: function () {
        var value = this.newComment && this.newComment.trim();
        if (!value) return;
        var that = this;
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
          //Rollbar.error("error adding text comment", error);
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