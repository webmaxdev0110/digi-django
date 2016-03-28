/* Ruby-like simple string interpolation for Node.js
 * Copyright (c) 2013 Mark Vasilkov (https://github.com/mvasilkov)
 * License: MIT */
(function () {
    var cache = {};

    function rewrite(foo, bar) {
        return '"+(typeof obj["' + bar + '"]!="undefined"?obj["' + bar + '"]:"' + foo + '")+"'
    }

    function fmt(input, options) {
        if (!(options && options.noCache) && input in cache) return cache[input];

        var out = JSON.stringify(input).replace(/#\{(.*?)\}/g, rewrite);
        /* jshint boss: true, evil: true */
        return (cache[input] = Function('obj', 'return ' + out))
    }
    window.fmt = fmt;
}());
