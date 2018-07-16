import Vue from 'vue'
import Comments from './Comments.vue'
import SingleComment from './SingleComment.vue'
import SingleUpload from './SingleUpload.vue'

new Vue({
  el: '.lesson-comments-app',
  components: { 
    Comments,
    SingleComment,
    SingleUpload
  }
})