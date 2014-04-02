module.exports = function(grunt) {

  // Project configuration.
  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),
    less: {
        development: {
            options: {
                paths: ["./less/", "./css/"],
                compress: true
            },
            files: {
                "./css/base.css": "./less/cm_bootstrap.less",
            }
        }
    },
    watch: {
        files: ["./less/*","./less/pages/*"],
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