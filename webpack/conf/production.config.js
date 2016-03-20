var BundleTracker = require('webpack-bundle-tracker');
// Webpack config for creating the production bundle.
var path = require('path');
var webpack = require('webpack');
var WebpackConfig = require('webpack-config');
var CleanPlugin = require('clean-webpack-plugin');
var strip = require('strip-loader');

var projectRootPath = path.resolve(__dirname, '../../');
var assetsPath = path.resolve(projectRootPath, './static/javascripts/');
var distPath = path.resolve(assetsPath, '../bundles');



module.exports = new WebpackConfig().extend({
    'webpack/conf/base.config.js': function (config) {
        return config;
    }
}).merge({
    debug: false,
    output: {
        path: distPath,
        filename: '[name]-[chunkhash].js',
        chunkFilename: '[name]-[chunkhash].js'
    },
    entry: {
        'main': [
            'docs/index.js'
        ]
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
    plugins: [
        new CleanPlugin([distPath], {root: projectRootPath}),
        // css files from the extract-text-plugin loader

        // ignore dev config
        new webpack.IgnorePlugin(/\.\/dev/, /\/config$/),

        // optimizations
        new webpack.optimize.DedupePlugin(),
        new webpack.optimize.OccurenceOrderPlugin(),
        new webpack.optimize.UglifyJsPlugin({
            compress: {
                warnings: false
            }
        }),
        new BundleTracker({filename: './webpack-stats.json'})
    ]
});
