# CM SASS stylesheets

## Overview

### LESS deprecated

CM has LESS stylesheets used by the deprecated base template
in `curiositymachine/static/less`. As soon as the deprecated
base template can be dropped, these styles will go too.

### SASS organization

  * `base/`: base styles for the whole app
	* `components/`: styles for reusable components used throughout the site
	    * be careful when modifying that you understand the variety of use-cases across the site
	* `layout/`: styles associated specifically with base templates and layouts
	* `pages/`: page-specific styles, these should be nested in a page-level class to limit their application
	    * consider promoting things up to components if you see duplication between different pages
	* `utils/`: SASS functions, includes, variables, etc.
	* `vendors/`: vendor files, bower dependencies are installed here
	    * **do not** add files or directories here, add dependencies to `bower.json`
	* `main.scss`

### Building

`grunt` or `grunt watch` will build CSS from both LESS and SASS