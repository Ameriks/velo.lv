var tsConfig = require('./tsconfig.json').compilerOptions;
tsConfig.references = ['node_modules/**/*.d.ts', 'typings/**/*.d.ts'];

module.exports = function (grunt) {

  var appConfig = grunt.file.readJSON('package.json');

  // Load grunt tasks automatically
  // see: https://github.com/sindresorhus/load-grunt-tasks
  require('load-grunt-tasks')(grunt);

  // Time how long tasks take. Can help when optimizing build times
  // see: https://npmjs.org/package/time-grunt
  require('time-grunt')(grunt);

  var pathsConfig = function (appName) {
    this.app = appName || appConfig.name;

    return {
      app: this.app,
      templates: this.app + '/templates',
      css: this.app + '/static/css',
      sass: this.app + '/static/sass',
      fonts: this.app + '/static/fonts',
      images: this.app + '/static/images',
      ts: this.app + '/static/ts',
      js: this.app + '/static/js',

      js_template: this.app + '/static/template/velo-2016/html/js',
      sass_template: this.app + '/static/template/velo-2016/html/css',

      manageScript: 'manage.py'
    }
  };

  grunt.initConfig({

    paths: pathsConfig(),
    pkg: appConfig,

    // see: https://github.com/gruntjs/grunt-contrib-watch
    watch: {
      gruntfile: {
        files: ['Gruntfile.js']
      },
      sass: {
        files: ['<%= paths.sass %>/**/*.{scss,sass}', '<%= paths.sass_template %>/**/*.{scss,sass}'],
        tasks: ['sass:dev'],
        options: {
          atBegin: true
        }
      },
      concat: {
        files: ['<%= paths.js_template %>/**/*.js', '<%= paths.js %>/components/*.js', '<%= paths.js %>/../coffee/*.js'],
        tasks: ['concat:dist'],
        options: {
          atBegin: true
        }
      },
      livereload: {
        files: [
          '<%= paths.js %>/**/*.js',
          '<%= paths.sass %>/**/*.{scss,sass}',
          '<%= paths.app %>/**/*.html'
          ],
        options: {
          spawn: false,
          livereload: true
        }
      }
    },
    concat: {
      dist: {
        src: [
              '<%= paths.js_template %>/libs/*.js',
              '<%= paths.js_template %>/utilities/*.js',
              '<%= paths.js_template %>/components/*.js',
              '<%= paths.js %>/components/*.js',
              '<%= paths.js %>/../coffee/*.js'
        ],
        dest: '<%= paths.js %>/project.js'
      }
    },
    uglify: {
      options: {
        mangle: false,
        screwIE8: true,
        sourceMap: true
      },
      project: {
        files: {
          '<%= paths.js %>/project.min.js': ['<%= paths.js %>/project.js']
        }
      }
    },

    sass: {
      dev: {
          options: {
              outputStyle: 'nested',
              sourceMap: false,
              precision: 10
          },
          files: {
              '<%= paths.css %>/main/project.css': '<%= paths.sass %>/project.scss'
          },
      },
      dist: {
          options: {
              outputStyle: 'compressed',
              sourceMap: false,
              precision: 10
          },
          files: {
              '<%= paths.css %>/main/project.min.css': '<%= paths.sass %>/project.scss'
          },
      }
    },

    //see https://github.com/nDmitry/grunt-postcss
    postcss: {
      options: {
        map: true, // inline sourcemaps

        processors: [
          require('pixrem')(), // add fallbacks for rem units
          require('autoprefixer-core')({browsers: [
            'Android 2.3',
            'Android >= 4',
            'Chrome >= 20',
            'Firefox >= 24',
            'Explorer >= 8',
            'iOS >= 6',
            'Opera >= 12',
            'Safari >= 6'
          ]}), // add vendor prefixes
          require('cssnano')() // minify the result
        ]
      },
      dist: {
        src: '<%= paths.css %>/*.css'
      }
    },

    docker_io: {
      dist: {
        options: {
          dockerFileLocation: '.',
          buildName: 'project_velo',
          tag: 'latest',
          username: 'ameriks',
          push: false,
          force: true
        }
      }
    },

    // see: https://npmjs.org/package/grunt-bg-shell
    bgShell: {
      _defaults: {
        bg: false
      },
      runDjango: {
        cmd: 'python <%= paths.manageScript %> runserver'
      },
      devDocker: {
        cmd: 'docker-compose -f dev.yml build django'
      }
    }
  });

  grunt.registerTask('serve', [
    'bgShell:runDjango',
    'watch'
  ]);

  grunt.registerTask('build', [
    'sass:dist',
    'postcss',
    'concat:dist',
    'uglify:project'

  ]);

  grunt.registerTask('default', [
    'build'
  ]);
};
