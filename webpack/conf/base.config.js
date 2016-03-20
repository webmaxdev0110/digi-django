// https://github.com/halt-hammerzeit/webpack-isomorphic-tools
var fs = require('fs');
var path = require('path');
var webpack = require('webpack');
var projectRootPath = path.resolve(__dirname, '../../');


module.exports = {
  devtool: 'source-map',
  context: projectRootPath,
  debug: true,
  progress: true,
  resolve: {
    root: path.resolve('./static/javascripts'),
    modulesDirectories: [
      'node_modules'
    ],
    extensions: ['', '.json', '.js', '.jsx']
  }
};