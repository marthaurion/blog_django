var gulp = require('gulp');
var concatCSS = require('gulp-concat-css');
var cleanCSS = require('gulp-clean-css');
var concat = require('gulp-concat');  
var rename = require('gulp-rename');  
var uglify = require('gulp-uglify');  

gulp.task('dark',function() {
    return gulp.src(['assets/css/darkly.css', 'assets/css/mainstuff.css'])
        .pipe(concatCSS('css/darkv2.css'))
        .pipe(cleanCSS())
        .pipe(gulp.dest('assets'));
});

gulp.task('light',function() {
    return gulp.src(['assets/css/flatly.css', 'assets/css/mainstuff.css'])
        .pipe(concatCSS('css/lightv2.css'))
        .pipe(cleanCSS())
        .pipe(gulp.dest('assets'));
});

gulp.task('scripts', function() {  
    return gulp.src(['assets/js/bootstrap.min.js', 'assets/js/mystuff.js'])
        .pipe(concat('all.js'))
        .pipe(gulp.dest('assets/js'))
        .pipe(rename('allv2.min.js'))
        .pipe(uglify())
        .pipe(gulp.dest('assets/js'));
});

gulp.task('default', ['dark', 'light', 'scripts']);