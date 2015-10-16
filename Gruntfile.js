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
          "./curiositymachine/static/css/filepicker.css": "./curiositymachine/static/less/pages/filepicker.less",
        }
      }
    },
    watch: {
      less: {
        files: ["./curiositymachine/static/less/**/*"],
        tasks: ["less"]
      },
      sass: {
        files: ["./curiositymachine/sass/**/*"],
        tasks: ["sass"]
      }
    },
    sass: {
      options: {
        sourceMap: true
      },
      dist: {
        files: {
          './curiositymachine/static/css/main.css': './curiositymachine/sass/main.scss',
          './curiositymachine/static/css/temp-fonts.css': './curiositymachine/sass/temp-fonts.scss',
        }
      }
    }
  });

  // Load the plugin that provides the "uglify" task.
  //grunt.loadNpmTasks('grunt-contrib-uglify');
  grunt.loadNpmTasks('grunt-contrib-less');
  grunt.loadNpmTasks('grunt-contrib-watch');
  //added in for sass:
  grunt.loadNpmTasks('grunt-sass');
  // Default task(s).
  grunt.registerTask('default', ['less', 'sass']);

};