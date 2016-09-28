//Install gulp: npm install --save-dev gulp
//Install Plumber: npm install --save-dev gulp-plumber
//Install Order: npm install --save-dev gulp-order
//Install JS Uglify: npm install --save-dev gulp-uglify
//Install Concat: npm install --save-dev gulp-concat
//Install SASS: npm install --save-dev gulp-sass
//Install AutoPrefixer: npm install --save-dev gulp-autoprefixer
//Install SVG sprite generator: npm install --save-dev gulp-svg-sprite

var gulp = require('gulp');
var plumber = require('gulp-plumber');
var order = require('gulp-order');
var uglify = require('gulp-uglify');
var concat = require('gulp-concat');
var sass = require('gulp-sass');
var svgSprite = require('gulp-svg-sprite');
var autoprefixer = require('gulp-autoprefixer');

var jsPath = 'html/js';
var jsSrc = [
                jsPath+'/libs/*.js',
                jsPath+'/utilities/*.js',
                jsPath+'/components/*.js'
            ];
var cssPath = 'html/css/main';
var cssSrc = cssPath+'/main.scss';

gulp.task('concat', function(){
    return gulp.src(jsSrc)
        .pipe(plumber())
        .pipe(order([
            // jsPath+'/libs/jquery-2.2.2.min.js',
            jsPath+'/libs/jquery.validate.min.js',
            jsPath+'/libs/component-history.js',
            jsPath+'/libs/jquery.unveil.js',
            jsPath+'/libs/modernizr-custom.js',
            jsPath+'/libs/owl.carousel.min.js',
            jsPath+'/libs/svg4everybody.min.js',
            jsPath+'/utilities/*.js',
            jsPath+'/components/*.js'
        ], { base: './' }))
        .pipe(concat('main.js'))
        .pipe(gulp.dest('html/js/main'));
});

gulp.task('compress', ['concat'], function(){
    return gulp.src(jsPath+'/main/main.js')
        .pipe(plumber())
        .pipe(uglify())
        .pipe(gulp.dest(jsPath+'/main'));
});

gulp.task('sass', function(){
    gulp.src(cssSrc)
        .pipe(plumber())
        .pipe(sass({
            outputStyle: 'compressed',
            errLogToConsole: true
        }).on('error', sass.logError))
        .pipe(autoprefixer())
        .pipe(gulp.dest(cssPath))
});

gulp.task('watch', function(){
    gulp.watch(jsSrc, ['concat', 'compress']);
    gulp.watch(cssSrc, ['sass']);
});

gulp.task('default', ['watch']);


var svgSpriteConfig = {
  mode: {
    symbol: {
      dest: '',
      sprite: 'icons.svg'
    }
  }
};

gulp.task('icons', function () {
  return gulp.src('./html/img/icons-minified/*.svg')
    .pipe(svgSprite(svgSpriteConfig))
    .pipe(gulp.dest('html/img'));
});
