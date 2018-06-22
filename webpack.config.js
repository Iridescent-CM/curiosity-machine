var path = require('path');
var BundleTracker = require('webpack-bundle-tracker');
const VueLoaderPlugin = require('vue-loader/lib/plugin')

module.exports = {
  mode: 'development',
  context: __dirname,
  entry: './curiositymachine/assets/lesson_commenting.js',

  output: {
      path: path.resolve('./curiositymachine/static/js/webpack_bundles/'),
      filename: "main.js"
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
      }
    ]
  },

  plugins: [
    new BundleTracker({filename: './curiositymachine/assets/webpack-stats.json'}),
    new VueLoaderPlugin()
  ]
}