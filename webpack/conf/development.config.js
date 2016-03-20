// Webpack config for development
var fs = require('fs');
var path = require('path');
var webpack = require('webpack');
var projectRootPath = path.resolve(__dirname, '../../');
var assetsPath = path.resolve(projectRootPath, './static/javascripts/');
var host = (process.env.HOST || 'localhost');
var port = (+process.env.PORT + 1) || 3001;
var WebpackConfig = require('webpack-config');
var BundleTracker = require('webpack-bundle-tracker');


module.exports = new WebpackConfig().extend({
    'webpack/conf/base.config.js': function (config) {
        return config;
    }
}).merge({
    debug: true,
    devtool: 'cheap-module-inline-source-map',
    output: {
        path: path.resolve(assetsPath, '../bundles'),
        chunkFilename: '[name]-[chunkhash].js',
        filename: '[name]-[hash].js'
    },
    module: {
        loaders: [
            {
                test: /\.jsx?$/, exclude: /node_modules/, loader: 'babel',
                query: {
                    presets: ['react', 'es2015', 'stage-0']
                }
            }
        ]
    },
    entry: {
        'main': [
            'docs/index.js'
        ]
    },
    plugins: [
        new BundleTracker({filename: './webpack-stats.json'}),
        new webpack.IgnorePlugin(/webpack-stats\.json$/)
    ]
});
