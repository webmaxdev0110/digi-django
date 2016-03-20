'use strict';

var WebpackConfig = require('webpack-config');

WebpackConfig.environment.setAll({
    env: function() {
        return process.env.NODE_ENV;
    }
});

//module.exports = new WebpackConfig().extend('webpack/conf/[env].config.js');
module.exports = new WebpackConfig().extend('webpack/conf/development.config.js');