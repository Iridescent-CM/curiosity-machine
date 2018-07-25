import $ from "jquery";
import csrf from "./csrf";
import log from "./log";

csrf($);
window.$ = window.jQuery = $;
window.log = log;

import "./ga-track";
import "./modals";
import "./smoothscroll";
import "./textswap";
