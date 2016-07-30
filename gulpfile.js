var gulp = require('gulp');
var concatCSS = require('gulp-concat-css');
var cleanCSS = require('gulp-clean-css');
var concat = require('gulp-concat');  
var rename = require('gulp-rename');  
var uglify = require('gulp-uglify');  

gulp.task('dark',function() {
    return gulp.src(['assets/css/src/darkly.css', 'assets/css/src/mainstuff.css'])
        .pipe(concatCSS('css/live_darkv1.css'))
        .pipe(cleanCSS())
        .pipe(gulp.dest('assets'));
});

gulp.task('light',function() {
    return gulp.src(['assets/css/src/flatly.css', 'assets/css/src/mainstuff.css'])
        .pipe(concatCSS('css/live_lightv1.css'))
        .pipe(cleanCSS())
        .pipe(gulp.dest('assets'));
});

gulp.task('scripts', function() {  
    return gulp.src(['assets/js/src/bootstrap.min.js', 'assets/js/src/mystuff.js'])
        .pipe(concat('intermediate.js'))
        .pipe(gulp.dest('assets/js'))
        .pipe(rename('allv2.min.js'))
        .pipe(uglify())
        .pipe(gulp.dest('assets/js'));
});

gulp.task('default', ['dark', 'light', 'scripts']);