/*
 * Main Javascript file for ppp_application.
 *
 * This file bundles all of your javascript together using webpack.
 */

// JavaScript modules
require("@fortawesome/fontawesome-free");
require("jquery");
require("@popperjs/core");
require("bootstrap");

require.context(
  "../img", // context folder
  true, // include subdirectories
  /.*/, // RegExp
);

// Your own code
require("./plugins.js");
require("./script.js");
