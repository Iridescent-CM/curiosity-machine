var config = require('./webpack.config.js');
const path = require('path');
const BundleTracker = require('webpack-bundle-tracker');
const VueLoaderPlugin = require('vue-loader/lib/plugin')

config.mode = "production";

config.output.path = path.resolve('./curiositymachine/static/js/dist/');

config.plugins = [
    new BundleTracker({filename: './curiositymachine/assets/webpack-stats-prod.json'}),
    new VueLoaderPlugin()
]

module.exports = config;
