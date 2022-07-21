process.traceDeprecation = true;
const package_json = require("./package.json");
const path = require("path");

module.exports = {
    entry: './resources/view.js',
    output: {
        path: path.resolve(__dirname, 'eea/facetednavigation/static'),
        filename: 'faceted-view.min.js',
    },
};
