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
      <div class="card my-3">

        <template v-if="comment.upload">
          <template v-if="comment.upload.type == 'image'">
            <img class="card-img-top" v-bind:src="comment.upload.url" alt="user uploaded image" />
            <div class="card-body">
              <button class="btn btn-sm btn-outline-purple" @click="removeComment(comment)">Remove</button>
              <button class="btn btn-sm btn-outline-purple" @click="editMediaComment(comment)">Edit</button>
            </div>
          </template>

          <template v-if="comment.upload.type == 'video'">
            <div v-if="comment.upload.encodings.length">
              <video
                class="w-100"
                preload="none"
                v-bind:poster="comment.upload.thumbnail"
                controls
              >
                <template v-for="encoding in comment.upload.encodings">
                  <source v-bind:src="encoding.url" v-bind:type="encoding.mimetype" />
                </template>
              </video>
            </div>
            <div v-else>
              <video
                class="w-100"
                preload="none"
                v-bind:src="comment.upload.url"
                v-bind:poster="comment.upload.thumbnail"
                controls
              >
              </video>
            </div>
            <div class="card-body">
              <button class="btn btn-sm btn-outline-purple" @click="removeComment(comment)">Remove</button>
              <button class="btn btn-sm btn-outline-purple" @click="editMediaComment(comment)">Edit</button>
            </div>
          </template>
        </template>

        <template v-if="comment.text">
          <div class="card-body" :class="{ editing: comment == editing }">
            <div class="view">
              <p class="card-text" style="white-space: pre;">{{ comment.text }}</p>
              <button class="btn btn-sm btn-outline-purple" @click="removeComment(comment)">Remove</button>
              <button class="btn btn-sm btn-outline-purple" @click="makeEditable(comment)">Edit</button>
            </div>
            <div class="edit">
              <textarea
                class="form-control"
                v-model="comment.text"
              ></textarea>
              <button class="btn btn-sm btn-outline-purple" @click="editTextComment(comment)">Save</button>
              <button class="btn btn-sm btn-outline-purple" @click="cancelEdit">Cancel</button>
            </div>
          </div>
        </template>

      </div>
    </template>
  </div>
</template>

<script>
  import init from './filestack_wrapper';
  import Api from './api';

  export default {

    props: ['author', 'progress', 'fskey'],

    data: function () {
      return {
        newComment: '',
        editing: undefined,
        comments: [],
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
      this.picker = init(this.fskey);
      if (this.enabled) {
        this.getComments();
      }
    },

    methods: {

      getComments: function () {
        var that = this;
        that.api
        .list()
        .then(function (data) {
          that.comments = data;
        })
        .catch(function (error) {
          that.error = true;
          Rollbar.error("error getting comments", error);
        });
      },

      addTextComment: function () {
        var value = this.newComment && this.newComment.trim();
        if (!value) return;
        var that = this;
        that.api
        .create({text: value})
        .then(function (response) {
          that.newComment = '';
          that.getComments();
        })
        .catch(function (error) {
          that.error = true;
          Rollbar.error("error adding text comment", error);
        });
      },

      makeEditable: function (comment) {
        this.editing = comment;
        this.editingCache = comment.text;
      },

      cancelEdit: function () {
        this.editing.text = this.editingCache;
        this.editing = undefined;
        this.editingCache = undefined;
      },

      editTextComment: function (comment) {
        var that = this;
        that.api
        .update(comment.id, {text: this.editing.text.trim()})
        .then(function (response) {
          that.editing = undefined;
        })
        .catch(function (error) {
          that.error = true;
          Rollbar.error("error editing text comment", error);
        });
      },

      addMediaComment: function () {
        var that = this;
        this.picker.pick()
        .then(function (upload) {
          return that.api.create({
            upload: upload
          });
        })
        .then(function (response) {
          that.getComments();
        })
        .catch(function (error) {
          that.error = true;
          Rollbar.error("error adding media comment", error);
        });
      },

      editMediaComment: function (comment) {
        var that = this;
        this.picker.pick()
        .then(function (upload) {
          return that.api.update(comment.id, {
            upload: upload
          });
        })
        .then(function (response) {
          that.getComments();
        })
        .catch(function (error) {
          that.error = true;
          Rollbar.error("error editing media comment", error);
        });
      },

      removeComment: function (comment) {
        if (window.confirm("Are you sure you want to remove your comment?")) {
          var that = this;
          that.api
          .destroy(comment.id)
          .then(function (response) {
            that.getComments();
          })
          .catch(function (error) {
            that.error = true;
            Rollbar.error("error removing comment", error);
          });
        }
      }

    }
  }
</script>

<style>
</style>