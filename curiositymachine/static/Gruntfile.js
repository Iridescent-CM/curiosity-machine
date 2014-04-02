module.exports = function(grunt) {

  // Project configuration.
  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),
    less: {
        development: {
            options: {
                paths: ["./curiositymachine/static/less/", "./curiositymachine/static/css/"],
                compress: true
            },
            files: {
                "./curiositymachine/static/css/base.css": "./curiositymachine/static/less/cm_bootstrap.less",
            }
        }
    },
    watch: {
        files: ["./curiositymachine/static/less/*","./curiositymachine/static/less/pages/*"],
        tasks: ["less"]
    }
  });

  // Load the plugin that provides the "uglify" task.
  //grunt.loadNpmTasks('grunt-contrib-uglify');
  grunt.loadNpmTasks('grunt-contrib-less');
  grunt.loadNpmTasks('grunt-contrib-watch');
  // Default task(s).
  grunt.registerTask('default', ['less']);

};