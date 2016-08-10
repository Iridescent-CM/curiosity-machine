## Updating and maintaining Curiosity Machine fonts
Curiosity Machine's newer stylesheets use Icomoon for maintaining custom icons. Here are the steps to updating them. Note that icons added this way will not show up in the old base template, which uses bootstrap's glyphicons.

## Icomoon
- Go to [Icomoon App](https://icomoon.io/app/#/select)
- Upload `curiositymachine/static/fonts/curiosity-machine-selection.json`
- Add / manage icons, then "Generate Font"
     - (At this point, sometimes I use their preview url and check and see if the icons look okay in context)
- Download the .zip file
- Rename "selection.json" to "curiosity-machine-selection.json" and replace `curiositymachine/static/fonts/curiosity-machine-selection.json`
- Copy the 4 files in `/fonts` (.eot, .svg, .ttf and .woff) and overwrite the files in `curiositymachine/static/fonts/`
- Open up the downloaded `style.css` and `curiositymachine/sass/base/_fonts.scss`
- Copy your new icon classes over from `style.css`
     - It's important to not just overwrite the entirety of `_fonts.scss` with `style.css` because the file paths (listed at the top of the file) will be incorrect. If you do this, just add a `../` before `fonts` in all the source urls
- Make sure you're compiling with `grunt`
- You can discard the rest of the generated Icomoon files
