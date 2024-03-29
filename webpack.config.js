const path = require('path');
const BundleTracker = require('webpack-bundle-tracker');
const VueLoaderPlugin = require('vue-loader/lib/plugin')

module.exports = {
  mode: 'development',
  context: __dirname,
  entry: {
    awardforce_checklist: './curiositymachine/assets/javascript/awardforce/index.js',
    lesson_comments: './curiositymachine/assets/javascript/lessons/comments/index.js',
    lesson_quiz: './curiositymachine/assets/javascript/lessons/quiz/index.js',
    site: './curiositymachine/assets/javascript/curiosity-machine/index.js'
  },

  output: {
      path: path.resolve('./curiositymachine/static/js/webpack_bundles/'),
      filename: "[name].js"
  },

  resolve: {
    alias: {
      'vue$': 'vue/dist/vue.esm.js'
    },
    extensions: ['*', '.js', '.vue', '.json']
  },

  module: {
    rules: [
      {
        test: /\.vue$/,
        loader: 'vue-loader'
      },
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['babel-preset-env']
          }
        }
      }
    ]
  },

  plugins: [
    new BundleTracker({filename: './curiositymachine/assets/webpack-stats.json'}),
    new VueLoaderPlugin()
  ]
}