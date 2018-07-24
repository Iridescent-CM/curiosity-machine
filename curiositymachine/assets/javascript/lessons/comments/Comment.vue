<template>
  <div class="card my-3">

    <template v-if="comment.upload">
      <template v-if="comment.upload.type == 'image'">
        <img class="card-img-top" v-bind:src="comment.upload.url" alt="user uploaded image" />
        <div class="card-body">
          <button class="btn btn-sm btn-outline-purple" @click="remove" :disabled="disabled">Remove</button>
          <button class="btn btn-sm btn-outline-purple" @click="editMedia">Edit</button>
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
          <button class="btn btn-sm btn-outline-purple" @click="remove" :disabled="disabled">Remove</button>
          <button class="btn btn-sm btn-outline-purple" @click="editMedia">Edit</button>
        </div>
      </template>

      <template v-if="comment.upload.type == 'document'">
        <div class="card-body pb-0">
          <a :href="comment.upload.url">
            <img v-bind:src="comment.upload.thumbnail" alt="user uploaded document" />
            <p class="my-1">
              {{ comment.upload.filename }}
            </p>
          </a>
        </div>
        <div class="card-body">
          <button class="btn btn-sm btn-outline-purple" @click="remove" :disabled="disabled">Remove</button>
          <button class="btn btn-sm btn-outline-purple" @click="editMedia">Edit</button>
        </div>
      </template>
    </template>

    <template v-if="comment.text">
      <div class="card-body" :class="{ editing: editing }">
        <div class="view">
          <p class="card-text" style="white-space: pre-wrap;">{{ comment.text }}</p>
          <button class="btn btn-sm btn-outline-purple" @click="remove" :disabled="disabled">Remove</button>
          <button class="btn btn-sm btn-outline-purple" @click="makeEditable">Edit</button>
        </div>
        <div class="edit">
          <textarea
            class="form-control"
            v-model="comment.text"
          ></textarea>
          <button class="btn btn-sm btn-outline-purple" @click="editText" :disabled="disabled">Save</button>
          <button class="btn btn-sm btn-outline-purple" @click="cancelEdit">Cancel</button>
        </div>
      </div>
    </template>

    <div class="card-body" v-if="error">
      <div class="alert alert-danger">
        <small>
          Error encountered
        </small>
      </div>
    </div>

  </div>
</template>

<script>
  import promiseFinally from 'promise.prototype.finally';
  promiseFinally.shim();

  export default {
    props: ['initial', 'api', 'picker'],

    data: function() {
      return {
        comment: this.initial,
        editing: false,
        error: undefined,
        pending: 0,
        removed: false
      }
    },

    computed: {
      disabled: function () {
        return !!this.pending || this.removed;
      }
    },

    methods: {
      editMedia: function () {
        var that = this;
        that.pending += 1;
        that.picker.pick()
        .then(function (upload) {
          return that.api.update(that.comment.id, {
            upload: upload
          });
        })
        .then(function (response) {
          that.comment = response.data;
        })
        .catch(function (error) {
          that.error = true;
          //Rollbar.error("error editing media comment", error);
        })
        .finally(function () {
          that.pending -= 1;
        });
      },

      editText: function () {
        var that = this;
        that.pending += 1;
        that.api
        .update(that.comment.id, { text: this.comment.text.trim() })
        .then(function (response) {
          that.editing = false;
          that.comment = response.data;
        })
        .catch(function (error) {
          that.error = true;
          //Rollbar.error("error editing text comment", error);
        })
        .finally(function () {
          that.pending -= 1;
        });
      },

      makeEditable: function () {
        this.editing = true;
        this.editingCache = this.comment.text;
      },

      cancelEdit: function () {
        this.editing = false;
        this.comment.text = this.editingCache;
      },

      remove: function () {
        if (window.confirm("Are you sure you want to remove your comment?")) {
          var that = this;
          that.pending += 1;
          that.api
          .destroy(that.comment.id)
          .then(function (response) {
            that.removed = true;
            that.$emit('remove');
          })
          .catch(function (error) {
            that.error = true;
            //Rollbar.error("error removing comment", error);
          })
          .finally(function () {
            that.pending -= 1;
          });
        }
      }
    }
  }
</script>

<style>
</style>
