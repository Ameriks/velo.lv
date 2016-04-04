
/*!
 * This Gruntfile is used to build the project files.
 */

/*jshint
    node: true
 */


module.exports = function( grunt ) {

    // Read the package manifest.
    var packageJSON = grunt.file.readJSON( 'package.json' )


    // Add the “curly” template delimiters.
    grunt.template.addDelimiters( 'curly', '{%', '%}' )


    // Load the NPM tasks.
    grunt.loadNpmTasks( 'grunt-contrib-watch' )
    grunt.loadNpmTasks( 'grunt-contrib-jshint' )
    grunt.loadNpmTasks( 'grunt-contrib-qunit' )
    grunt.loadNpmTasks( 'grunt-contrib-copy' )
    grunt.loadNpmTasks( 'grunt-contrib-sass' )
    grunt.loadNpmTasks( 'grunt-contrib-cssmin' )
    grunt.loadNpmTasks( 'grunt-contrib-uglify' )
    grunt.loadNpmTasks( 'grunt-autoprefixer' )


    // Setup the initial configurations.
    grunt.initConfig({


        // Add the package data.
        pkg: packageJSON,


        // Set up the directories.
        dirs: {
            tests: 'tests',
            lib: {
                src: 'lib',
                min: 'lib/compressed'
            },
            themes: {
                src: 'lib/themes-source',
                dest: 'lib/themes',
                min: 'lib/compressed/themes'
            },
            translations: {
                src: 'lib/translations',
                min: 'lib/compressed/translations'
            },
            docs: {
                src: '_docs',
                dest: '.'
            },
            demo: {
                images: 'demo/images',
                scripts: 'demo/scripts',
                styles: {
                    src: 'demo/styles/sass',
                    dest: 'demo/styles/css'
                }
            },
        },


        // Generate static HTML templates.
        htmlify: {
            docs: {
                expand: true,
                cwd: '<%= dirs.docs.src %>',
                src: [ '/!(base|hero)*.htm' ],
                dest: '',
                base: '/base.htm'
            }
        },


        // Copy over files to destination directions.
        copy: {
            pkg: {
                options: {
                    processContent: function( content ) {
                        return grunt.template.process( content, { delimiters: 'curly' } )
                    }
                },
                files: [
                    { '<%= pkg.name %>.jquery.json': 'package.json' },
                    { 'bower.json': 'package.json' },
                    { 'README.md': '<%= dirs.docs.src %>/README.md' },
                    { 'LICENSE.md': '<%= dirs.docs.src %>/LICENSE.md' },
                    { 'CHANGELOG.md': '<%= dirs.docs.src %>/CHANGELOG.md' },
                    { 'CONTRIBUTING.md': '<%= dirs.docs.src %>/CONTRIBUTING.md' }
                ]
            }
        },


        // Compile sass into CSS.
        sass: {
            options: {
                style: 'expanded'
            },
            demo: {
                files: {
                    '<%= dirs.demo.styles.dest %>/main.css': '<%= dirs.demo.styles.src %>/base.scss'
                }
            },
            themes: {
                files: {
                    '<%= dirs.themes.dest %>/default.css': [ '<%= dirs.themes.src %>/base.scss', '<%= dirs.themes.src %>/default.scss' ],
                    '<%= dirs.themes.dest %>/classic.css': [ '<%= dirs.themes.src %>/base.scss', '<%= dirs.themes.src %>/classic.scss' ],
                    '<%= dirs.themes.dest %>/default.date.css': [ '<%= dirs.themes.src %>/base.date.scss', '<%= dirs.themes.src %>/default.date.scss' ],
                    '<%= dirs.themes.dest %>/default.time.css': [ '<%= dirs.themes.src %>/base.time.scss', '<%= dirs.themes.src %>/default.time.scss' ],
                    '<%= dirs.themes.dest %>/classic.date.css': [ '<%= dirs.themes.src %>/base.date.scss', '<%= dirs.themes.src %>/classic.date.scss' ],
                    '<%= dirs.themes.dest %>/classic.time.css': [ '<%= dirs.themes.src %>/base.time.scss', '<%= dirs.themes.src %>/classic.time.scss' ],
                    '<%= dirs.themes.dest %>/rtl.css': [ '<%= dirs.themes.src %>/rtl.scss' ]
                }
            }
        },


        // Lint the files.
        jshint: {
            options: {
                jshintrc: true
            },
            gruntfile: 'Gruntfile.js',
            demo: [ '<%= dirs.demo.scripts %>/demo.js' ],
            lib: [
                '<%= dirs.tests %>/units/*.js',
                '<%= dirs.lib.src %>/**/*.js',

                // Ignore the legacy and minified files.
                '!<%= dirs.lib.src %>/legacy.js',
                '!<%= dirs.lib.src %>/compressed/**/*.js'
            ]
        },


        // Minify all the things!
        uglify: {
            options: {
                preserveComments: 'some'
            },
            lib: {
                files: [
                    {
                        expand : true,
                        cwd : '<%= dirs.lib.src %>',
                        src   : [ '**/*.js', '!compressed/**/*.js' ],
                        dest : '<%= dirs.lib.min %>'
                    }
                ]
            }
        },
        cssmin: {
            lib: {
                expand: true,
                cwd: '<%= dirs.themes.dest %>',
                src: [ '**/*.css', '!compressed/**/*.css' ],
                dest: '<%= dirs.themes.min %>'
            }
        },


        // Prefix the styles.
        autoprefixer: {
            options: {
                browsers: [ '> 5%', 'last 2 versions', 'ie 8', 'ie 9' ]
            },
            themes: {
                src: '<%= dirs.themes.dest %>/**/*.css'
            },
            demo: {
                src: '<%= dirs.demo.styles.dest %>/**/*.css'
            }
        },


        // Unit test the files.
        qunit: {
            lib: [ '<%= dirs.tests %>/units/all.htm' ]
        },


        // Watch the project files.
        watch: {
            quick: {
                files: [
                    '<%= dirs.docs.src %>/**/*.htm',
                    '<%= dirs.docs.src %>/**/*.md',
                    '<%= dirs.demo.styles.src %>/**/*.scss',
                    '<%= dirs.themes.src %>/**/*.scss'
                ],
                tasks: [ 'quick' ]
            },
            demo: {
                files: [
                    '<%= dirs.demo.styles.src %>/**/*.scss'
                ],
                tasks: [ 'demo' ]
            },
            docs: {
                files: [
                    '<%= dirs.docs.src %>/**/*.htm',
                    '<%= dirs.docs.src %>/**/*.md'
                ],
                tasks: [ 'docs' ]
            },
            themes: {
                files: [
                    '<%= dirs.themes.src %>/**/*.scss'
                ],
                tasks: [ 'themes' ]
            },
            autoprefix: {
                files: [
                    '<%= dirs.demo.styles.src %>/**/*.scss',
                    '<%= dirs.themes.dest %>/**/*.css',
                    '<%= dirs.themes.min %>/**/*.css'
                ],
                tasks: [ 'autoprefixer' ]
            }
        },


        // Any extra data needed in rendering static files.
        meta: {

            // The sanitized github repo url.
            gitrepo_url: packageJSON.repository.url.replace( /.git$/, '' ),

            // Get the min & gzip size of a text file.
            fileSize: function( content ) {
                return {
                    min: content.length || 0,
                    gzip: content ? require( 'zlib-browserify' ).gzipSync( content ).length : 0
                }
            }
        }
    }) //grunt.initConfig


    // Register the tasks.
    // * `htmlify` and `copy:pkg` should come after `uglify` because some package files measure `.min` file sizes.
    grunt.registerTask( 'default', [ 'sass', 'cssmin', 'autoprefixer', 'jshint', 'qunit', 'uglify', 'htmlify', 'copy:pkg' ] )
    grunt.registerTask( 'quick', [ 'sass', 'cssmin', 'autoprefixer', 'uglify', 'htmlify', 'copy:pkg' ] )
    grunt.registerTask( 'themes', [ 'sass:themes', 'autoprefixer:themes' ] )
    grunt.registerTask( 'demo', [ 'sass:demo', 'autoprefixer:demo', 'jshint:demo' ] )
    grunt.registerTask( 'docs', [ 'copy:pkg', 'htmlify:docs' ] )
    grunt.registerTask( 'travis', [ 'jshint:lib', 'qunit:lib' ] )



    // Create and register the task to build out the static HTML files.
    grunt.registerMultiTask( 'htmlify', 'Recursively build static HTML files', function() {

        var task = this,
            // options = task.options(),

            // Process the base file using the source file content.
            processFile = function( fileSource ) {

                var processedContent = ''/*,
                    fileNameMatch = fileSource.match( /([\w-]+)(\.htm)$/ )*/

                // Recursively process the base template using the file source content.
                grunt.verbose.writeln( 'Processing ' + fileSource )
                processedContent = grunt.template.process( grunt.file.read( task.data.cwd + task.data.base ), {
                    delimiters: 'curly',
                    data: {
                        pkg: packageJSON,
                        page: fileSource.match( /[\w-]+(?=\.htm$)/ )[ 0 ],
                        content: grunt.file.read( fileSource ),
                        meta: grunt.config.data.meta,
                        dirs: grunt.config.data.dirs
                    }
                })

                // Write the destination file by cleaning the file name.
                grunt.log.writeln( 'Writing ' + fileSource.cyan )
                grunt.file.write( task.data.dest + fileSource.match( /[\w-]+\.htm$/ )[ 0 ], processedContent )
            }


        // Map through the task directory and process the HTML files.
        grunt.log.writeln( 'Expanding ' + task.data.cwd.cyan )
        grunt.file.expand( task.data.cwd + task.data.src ).map( processFile )
    })

} //module.exports


