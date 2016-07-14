var gulp = require('gulp');
var concatCSS = require('gulp-concat-css');
var cleanCSS = require('gulp-clean-css');

gulp.task('dark',function() {
    return gulp.src(['assets/css/darkly.css', 'assets/css/mainstuff.css'])
        .pipe(concatCSS('css/dark1.css'))
        .pipe(cleanCSS())
        .pipe(gulp.dest('assets'));
});

gulp.task('light',function() {
    return gulp.src(['assets/css/flatly.css', 'assets/css/mainstuff.css'])
        .pipe(concatCSS('css/light1.css'))
        .pipe(cleanCSS())
        .pipe(gulp.dest('assets'));
});

gulp.task('default', ['dark', 'light']);