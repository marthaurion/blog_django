var gulp = require('gulp');
var concatCSS = require('gulp-concat-css');
var cleanCSS = require('gulp-clean-css');

gulp.task('default',function() {
    return gulp.src(['assets/css/bootstrap.min.css', 'assets/css/mainstuff.css'])
        .pipe(concatCSS('css/allv2.css'))
        .pipe(cleanCSS())
        .pipe(gulp.dest('assets'));
});