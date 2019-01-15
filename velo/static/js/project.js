/**
*  Ajax Autocomplete for jQuery, version 1.2.24
*  (c) 2015 Tomas Kirda
*
*  Ajax Autocomplete for jQuery is freely distributable under the terms of an MIT-style license.
*  For details, see the web site: https://github.com/devbridge/jQuery-Autocomplete
*/

/*jslint  browser: true, white: true, plusplus: true, vars: true */
/*global define, window, document, jQuery, exports, require */

// Expose plugin as an AMD module if AMD loader is present:
(function (factory) {
    'use strict';
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery'], factory);
    } else if (typeof exports === 'object' && typeof require === 'function') {
        // Browserify
        factory(require('jquery'));
    } else {
        // Browser globals
        factory(jQuery);
    }
}(function ($) {
    'use strict';

    var
        utils = (function () {
            return {
                escapeRegExChars: function (value) {
                    return value.replace(/[\-\[\]\/\{\}\(\)\*\+\?\.\\\^\$\|]/g, "\\$&");
                },
                createNode: function (containerClass) {
                    var div = document.createElement('div');
                    div.className = containerClass;
                    div.style.position = 'absolute';
                    div.style.display = 'none';
                    return div;
                }
            };
        }()),

        keys = {
            ESC: 27,
            TAB: 9,
            RETURN: 13,
            LEFT: 37,
            UP: 38,
            RIGHT: 39,
            DOWN: 40
        };

    function Autocomplete(el, options) {
        var noop = function () { },
            that = this,
            defaults = {
                ajaxSettings: {},
                autoSelectFirst: false,
                appendTo: document.body,
                serviceUrl: null,
                lookup: null,
                onSelect: null,
                width: 'auto',
                minChars: 1,
                maxHeight: 300,
                deferRequestBy: 0,
                params: {},
                formatResult: Autocomplete.formatResult,
                delimiter: null,
                zIndex: 9999,
                type: 'GET',
                noCache: false,
                onSearchStart: noop,
                onSearchComplete: noop,
                onSearchError: noop,
                preserveInput: false,
                containerClass: 'autocomplete-suggestions',
                tabDisabled: false,
                dataType: 'text',
                currentRequest: null,
                triggerSelectOnValidInput: true,
                preventBadQueries: true,
                lookupFilter: function (suggestion, originalQuery, queryLowerCase) {
                    return suggestion.value.toLowerCase().indexOf(queryLowerCase) !== -1;
                },
                paramName: 'query',
                transformResult: function (response) {
                    return typeof response === 'string' ? $.parseJSON(response) : response;
                },
                showNoSuggestionNotice: false,
                noSuggestionNotice: 'No results',
                orientation: 'bottom',
                forceFixPosition: false
            };

        // Shared variables:
        that.element = el;
        that.el = $(el);
        that.suggestions = [];
        that.badQueries = [];
        that.selectedIndex = -1;
        that.currentValue = that.element.value;
        that.intervalId = 0;
        that.cachedResponse = {};
        that.onChangeInterval = null;
        that.onChange = null;
        that.isLocal = false;
        that.suggestionsContainer = null;
        that.noSuggestionsContainer = null;
        that.options = $.extend({}, defaults, options);
        that.classes = {
            selected: 'autocomplete-selected',
            suggestion: 'autocomplete-suggestion'
        };
        that.hint = null;
        that.hintValue = '';
        that.selection = null;

        // Initialize and set options:
        that.initialize();
        that.setOptions(options);
    }

    Autocomplete.utils = utils;

    $.Autocomplete = Autocomplete;

    Autocomplete.formatResult = function (suggestion, currentValue) {
        var pattern = '(' + utils.escapeRegExChars(currentValue) + ')';
        
        return suggestion.value
            .replace(new RegExp(pattern, 'gi'), '<strong>$1<\/strong>')
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/&lt;(\/?strong)&gt;/g, '<$1>');
    };

    Autocomplete.prototype = {

        killerFn: null,

        initialize: function () {
            var that = this,
                suggestionSelector = '.' + that.classes.suggestion,
                selected = that.classes.selected,
                options = that.options,
                container;

            // Remove autocomplete attribute to prevent native suggestions:
            that.element.setAttribute('autocomplete', 'off');

            that.killerFn = function (e) {
                if ($(e.target).closest('.' + that.options.containerClass).length === 0) {
                    that.killSuggestions();
                    that.disableKillerFn();
                }
            };

            // html() deals with many types: htmlString or Element or Array or jQuery
            that.noSuggestionsContainer = $('<div class="autocomplete-no-suggestion"></div>')
                                          .html(this.options.noSuggestionNotice).get(0);

            that.suggestionsContainer = Autocomplete.utils.createNode(options.containerClass);

            container = $(that.suggestionsContainer);

            container.appendTo(options.appendTo);

            // Only set width if it was provided:
            if (options.width !== 'auto') {
                container.width(options.width);
            }

            // Listen for mouse over event on suggestions list:
            container.on('mouseover.autocomplete', suggestionSelector, function () {
                that.activate($(this).data('index'));
            });

            // Deselect active element when mouse leaves suggestions container:
            container.on('mouseout.autocomplete', function () {
                that.selectedIndex = -1;
                container.children('.' + selected).removeClass(selected);
            });

            // Listen for click event on suggestions list:
            container.on('click.autocomplete', suggestionSelector, function () {
                that.select($(this).data('index'));
            });

            that.fixPositionCapture = function () {
                if (that.visible) {
                    that.fixPosition();
                }
            };

            $(window).on('resize.autocomplete', that.fixPositionCapture);

            that.el.on('keydown.autocomplete', function (e) { that.onKeyPress(e); });
            that.el.on('keyup.autocomplete', function (e) { that.onKeyUp(e); });
            that.el.on('blur.autocomplete', function () { that.onBlur(); });
            that.el.on('focus.autocomplete', function () { that.onFocus(); });
            that.el.on('change.autocomplete', function (e) { that.onKeyUp(e); });
            that.el.on('input.autocomplete', function (e) { that.onKeyUp(e); });
        },

        onFocus: function () {
            var that = this;
            that.fixPosition();
            if (that.options.minChars === 0 && that.el.val().length === 0) {
                that.onValueChange();
            }
        },

        onBlur: function () {
            this.enableKillerFn();
        },
        
        abortAjax: function () {
            var that = this;
            if (that.currentRequest) {
                that.currentRequest.abort();
                that.currentRequest = null;
            }
        },

        setOptions: function (suppliedOptions) {
            var that = this,
                options = that.options;

            $.extend(options, suppliedOptions);

            that.isLocal = $.isArray(options.lookup);

            if (that.isLocal) {
                options.lookup = that.verifySuggestionsFormat(options.lookup);
            }

            options.orientation = that.validateOrientation(options.orientation, 'bottom');

            // Adjust height, width and z-index:
            $(that.suggestionsContainer).css({
                'max-height': options.maxHeight + 'px',
                'width': options.width + 'px',
                'z-index': options.zIndex
            });
        },


        clearCache: function () {
            this.cachedResponse = {};
            this.badQueries = [];
        },

        clear: function () {
            this.clearCache();
            this.currentValue = '';
            this.suggestions = [];
        },

        disable: function () {
            var that = this;
            that.disabled = true;
            clearInterval(that.onChangeInterval);
            that.abortAjax();
        },

        enable: function () {
            this.disabled = false;
        },

        fixPosition: function () {
            // Use only when container has already its content

            var that = this,
                $container = $(that.suggestionsContainer),
                containerParent = $container.parent().get(0);
            // Fix position automatically when appended to body.
            // In other cases force parameter must be given.
            if (containerParent !== document.body && !that.options.forceFixPosition) {
                return;
            }

            // Choose orientation
            var orientation = that.options.orientation,
                containerHeight = $container.outerHeight(),
                height = that.el.outerHeight(),
                offset = that.el.offset(),
                styles = { 'top': offset.top, 'left': offset.left };

            if (orientation === 'auto') {
                var viewPortHeight = $(window).height(),
                    scrollTop = $(window).scrollTop(),
                    topOverflow = -scrollTop + offset.top - containerHeight,
                    bottomOverflow = scrollTop + viewPortHeight - (offset.top + height + containerHeight);

                orientation = (Math.max(topOverflow, bottomOverflow) === topOverflow) ? 'top' : 'bottom';
            }

            if (orientation === 'top') {
                styles.top += -containerHeight;
            } else {
                styles.top += height;
            }

            // If container is not positioned to body,
            // correct its position using offset parent offset
            if(containerParent !== document.body) {
                var opacity = $container.css('opacity'),
                    parentOffsetDiff;

                    if (!that.visible){
                        $container.css('opacity', 0).show();
                    }

                parentOffsetDiff = $container.offsetParent().offset();
                styles.top -= parentOffsetDiff.top;
                styles.left -= parentOffsetDiff.left;

                if (!that.visible){
                    $container.css('opacity', opacity).hide();
                }
            }

            // -2px to account for suggestions border.
            if (that.options.width === 'auto') {
                styles.width = (that.el.outerWidth() - 2) + 'px';
            }

            $container.css(styles);
        },

        enableKillerFn: function () {
            var that = this;
            $(document).on('click.autocomplete', that.killerFn);
        },

        disableKillerFn: function () {
            var that = this;
            $(document).off('click.autocomplete', that.killerFn);
        },

        killSuggestions: function () {
            var that = this;
            that.stopKillSuggestions();
            that.intervalId = window.setInterval(function () {
                if (that.visible) {
                    that.el.val(that.currentValue);
                    that.hide();
                }
                
                that.stopKillSuggestions();
            }, 50);
        },

        stopKillSuggestions: function () {
            window.clearInterval(this.intervalId);
        },

        isCursorAtEnd: function () {
            var that = this,
                valLength = that.el.val().length,
                selectionStart = that.element.selectionStart,
                range;

            if (typeof selectionStart === 'number') {
                return selectionStart === valLength;
            }
            if (document.selection) {
                range = document.selection.createRange();
                range.moveStart('character', -valLength);
                return valLength === range.text.length;
            }
            return true;
        },

        onKeyPress: function (e) {
            var that = this;

            // If suggestions are hidden and user presses arrow down, display suggestions:
            if (!that.disabled && !that.visible && e.which === keys.DOWN && that.currentValue) {
                that.suggest();
                return;
            }

            if (that.disabled || !that.visible) {
                return;
            }

            switch (e.which) {
                case keys.ESC:
                    that.el.val(that.currentValue);
                    that.hide();
                    break;
                case keys.RIGHT:
                    if (that.hint && that.options.onHint && that.isCursorAtEnd()) {
                        that.selectHint();
                        break;
                    }
                    return;
                case keys.TAB:
                    if (that.hint && that.options.onHint) {
                        that.selectHint();
                        return;
                    }
                    if (that.selectedIndex === -1) {
                        that.hide();
                        return;
                    }
                    that.select(that.selectedIndex);
                    if (that.options.tabDisabled === false) {
                        return;
                    }
                    break;
                case keys.RETURN:
                    if (that.selectedIndex === -1) {
                        that.hide();
                        return;
                    }
                    that.select(that.selectedIndex);
                    break;
                case keys.UP:
                    that.moveUp();
                    break;
                case keys.DOWN:
                    that.moveDown();
                    break;
                default:
                    return;
            }

            // Cancel event if function did not return:
            e.stopImmediatePropagation();
            e.preventDefault();
        },

        onKeyUp: function (e) {
            var that = this;

            if (that.disabled) {
                return;
            }

            switch (e.which) {
                case keys.UP:
                case keys.DOWN:
                    return;
            }

            clearInterval(that.onChangeInterval);

            if (that.currentValue !== that.el.val()) {
                that.findBestHint();
                if (that.options.deferRequestBy > 0) {
                    // Defer lookup in case when value changes very quickly:
                    that.onChangeInterval = setInterval(function () {
                        that.onValueChange();
                    }, that.options.deferRequestBy);
                } else {
                    that.onValueChange();
                }
            }
        },

        onValueChange: function () {
            var that = this,
                options = that.options,
                value = that.el.val(),
                query = that.getQuery(value);

            if (that.selection && that.currentValue !== query) {
                that.selection = null;
                (options.onInvalidateSelection || $.noop).call(that.element);
            }

            clearInterval(that.onChangeInterval);
            that.currentValue = value;
            that.selectedIndex = -1;

            // Check existing suggestion for the match before proceeding:
            if (options.triggerSelectOnValidInput && that.isExactMatch(query)) {
                that.select(0);
                return;
            }

            if (query.length < options.minChars) {
                that.hide();
            } else {
                that.getSuggestions(query);
            }
        },

        isExactMatch: function (query) {
            var suggestions = this.suggestions;

            return (suggestions.length === 1 && suggestions[0].value.toLowerCase() === query.toLowerCase());
        },

        getQuery: function (value) {
            var delimiter = this.options.delimiter,
                parts;

            if (!delimiter) {
                return value;
            }
            parts = value.split(delimiter);
            return $.trim(parts[parts.length - 1]);
        },

        getSuggestionsLocal: function (query) {
            var that = this,
                options = that.options,
                queryLowerCase = query.toLowerCase(),
                filter = options.lookupFilter,
                limit = parseInt(options.lookupLimit, 10),
                data;

            data = {
                suggestions: $.grep(options.lookup, function (suggestion) {
                    return filter(suggestion, query, queryLowerCase);
                })
            };

            if (limit && data.suggestions.length > limit) {
                data.suggestions = data.suggestions.slice(0, limit);
            }

            return data;
        },

        getSuggestions: function (q) {
            var response,
                that = this,
                options = that.options,
                serviceUrl = options.serviceUrl,
                params,
                cacheKey,
                ajaxSettings;

            options.params[options.paramName] = q;
            params = options.ignoreParams ? null : options.params;

            if (options.onSearchStart.call(that.element, options.params) === false) {
                return;
            }

            if ($.isFunction(options.lookup)){
                options.lookup(q, function (data) {
                    that.suggestions = data.suggestions;
                    that.suggest();
                    options.onSearchComplete.call(that.element, q, data.suggestions);
                });
                return;
            }

            if (that.isLocal) {
                response = that.getSuggestionsLocal(q);
            } else {
                if ($.isFunction(serviceUrl)) {
                    serviceUrl = serviceUrl.call(that.element, q);
                }
                cacheKey = serviceUrl + '?' + $.param(params || {});
                response = that.cachedResponse[cacheKey];
            }

            if (response && $.isArray(response.suggestions)) {
                that.suggestions = response.suggestions;
                that.suggest();
                options.onSearchComplete.call(that.element, q, response.suggestions);
            } else if (!that.isBadQuery(q)) {
                that.abortAjax();

                ajaxSettings = {
                    url: serviceUrl,
                    data: params,
                    type: options.type,
                    dataType: options.dataType
                };

                $.extend(ajaxSettings, options.ajaxSettings);

                that.currentRequest = $.ajax(ajaxSettings).done(function (data) {
                    var result;
                    that.currentRequest = null;
                    result = options.transformResult(data, q);
                    that.processResponse(result, q, cacheKey);
                    options.onSearchComplete.call(that.element, q, result.suggestions);
                }).fail(function (jqXHR, textStatus, errorThrown) {
                    options.onSearchError.call(that.element, q, jqXHR, textStatus, errorThrown);
                });
            } else {
                options.onSearchComplete.call(that.element, q, []);
            }
        },

        isBadQuery: function (q) {
            if (!this.options.preventBadQueries){
                return false;
            }

            var badQueries = this.badQueries,
                i = badQueries.length;

            while (i--) {
                if (q.indexOf(badQueries[i]) === 0) {
                    return true;
                }
            }

            return false;
        },

        hide: function () {
            var that = this,
                container = $(that.suggestionsContainer);

            if ($.isFunction(that.options.onHide) && that.visible) {
                that.options.onHide.call(that.element, container);
            }

            that.visible = false;
            that.selectedIndex = -1;
            clearInterval(that.onChangeInterval);
            $(that.suggestionsContainer).hide();
            that.signalHint(null);
        },

        suggest: function () {
            if (this.suggestions.length === 0) {
                if (this.options.showNoSuggestionNotice) {
                    this.noSuggestions();
                } else {
                    this.hide();
                }
                return;
            }

            var that = this,
                options = that.options,
                groupBy = options.groupBy,
                formatResult = options.formatResult,
                value = that.getQuery(that.currentValue),
                className = that.classes.suggestion,
                classSelected = that.classes.selected,
                container = $(that.suggestionsContainer),
                noSuggestionsContainer = $(that.noSuggestionsContainer),
                beforeRender = options.beforeRender,
                html = '',
                category,
                formatGroup = function (suggestion, index) {
                        var currentCategory = suggestion.data[groupBy];

                        if (category === currentCategory){
                            return '';
                        }

                        category = currentCategory;

                        return '<div class="autocomplete-group"><strong>' + category + '</strong></div>';
                    };

            if (options.triggerSelectOnValidInput && that.isExactMatch(value)) {
                that.select(0);
                return;
            }

            // Build suggestions inner HTML:
            $.each(that.suggestions, function (i, suggestion) {
                if (groupBy){
                    html += formatGroup(suggestion, value, i);
                }

                html += '<div class="' + className + '" data-index="' + i + '">' + formatResult(suggestion, value) + '</div>';
            });

            this.adjustContainerWidth();

            noSuggestionsContainer.detach();
            container.html(html);

            if ($.isFunction(beforeRender)) {
                beforeRender.call(that.element, container);
            }

            that.fixPosition();
            container.show();

            // Select first value by default:
            if (options.autoSelectFirst) {
                that.selectedIndex = 0;
                container.scrollTop(0);
                container.children('.' + className).first().addClass(classSelected);
            }

            that.visible = true;
            that.findBestHint();
        },

        noSuggestions: function() {
             var that = this,
                 container = $(that.suggestionsContainer),
                 noSuggestionsContainer = $(that.noSuggestionsContainer);

            this.adjustContainerWidth();

            // Some explicit steps. Be careful here as it easy to get
            // noSuggestionsContainer removed from DOM if not detached properly.
            noSuggestionsContainer.detach();
            container.empty(); // clean suggestions if any
            container.append(noSuggestionsContainer);

            that.fixPosition();

            container.show();
            that.visible = true;
        },

        adjustContainerWidth: function() {
            var that = this,
                options = that.options,
                width,
                container = $(that.suggestionsContainer);

            // If width is auto, adjust width before displaying suggestions,
            // because if instance was created before input had width, it will be zero.
            // Also it adjusts if input width has changed.
            // -2px to account for suggestions border.
            if (options.width === 'auto') {
                width = that.el.outerWidth() - 2;
                container.width(width > 0 ? width : 300);
            }
        },

        findBestHint: function () {
            var that = this,
                value = that.el.val().toLowerCase(),
                bestMatch = null;

            if (!value) {
                return;
            }

            $.each(that.suggestions, function (i, suggestion) {
                var foundMatch = suggestion.value.toLowerCase().indexOf(value) === 0;
                if (foundMatch) {
                    bestMatch = suggestion;
                }
                return !foundMatch;
            });

            that.signalHint(bestMatch);
        },

        signalHint: function (suggestion) {
            var hintValue = '',
                that = this;
            if (suggestion) {
                hintValue = that.currentValue + suggestion.value.substr(that.currentValue.length);
            }
            if (that.hintValue !== hintValue) {
                that.hintValue = hintValue;
                that.hint = suggestion;
                (this.options.onHint || $.noop)(hintValue);
            }
        },

        verifySuggestionsFormat: function (suggestions) {
            // If suggestions is string array, convert them to supported format:
            if (suggestions.length && typeof suggestions[0] === 'string') {
                return $.map(suggestions, function (value) {
                    return { value: value, data: null };
                });
            }

            return suggestions;
        },

        validateOrientation: function(orientation, fallback) {
            orientation = $.trim(orientation || '').toLowerCase();

            if($.inArray(orientation, ['auto', 'bottom', 'top']) === -1){
                orientation = fallback;
            }

            return orientation;
        },

        processResponse: function (result, originalQuery, cacheKey) {
            var that = this,
                options = that.options;

            result.suggestions = that.verifySuggestionsFormat(result.suggestions);

            // Cache results if cache is not disabled:
            if (!options.noCache) {
                that.cachedResponse[cacheKey] = result;
                if (options.preventBadQueries && result.suggestions.length === 0) {
                    that.badQueries.push(originalQuery);
                }
            }

            // Return if originalQuery is not matching current query:
            if (originalQuery !== that.getQuery(that.currentValue)) {
                return;
            }

            that.suggestions = result.suggestions;
            that.suggest();
        },

        activate: function (index) {
            var that = this,
                activeItem,
                selected = that.classes.selected,
                container = $(that.suggestionsContainer),
                children = container.find('.' + that.classes.suggestion);

            container.find('.' + selected).removeClass(selected);

            that.selectedIndex = index;

            if (that.selectedIndex !== -1 && children.length > that.selectedIndex) {
                activeItem = children.get(that.selectedIndex);
                $(activeItem).addClass(selected);
                return activeItem;
            }

            return null;
        },

        selectHint: function () {
            var that = this,
                i = $.inArray(that.hint, that.suggestions);

            that.select(i);
        },

        select: function (i) {
            var that = this;
            that.hide();
            that.onSelect(i);
        },

        moveUp: function () {
            var that = this;

            if (that.selectedIndex === -1) {
                return;
            }

            if (that.selectedIndex === 0) {
                $(that.suggestionsContainer).children().first().removeClass(that.classes.selected);
                that.selectedIndex = -1;
                that.el.val(that.currentValue);
                that.findBestHint();
                return;
            }

            that.adjustScroll(that.selectedIndex - 1);
        },

        moveDown: function () {
            var that = this;

            if (that.selectedIndex === (that.suggestions.length - 1)) {
                return;
            }

            that.adjustScroll(that.selectedIndex + 1);
        },

        adjustScroll: function (index) {
            var that = this,
                activeItem = that.activate(index);

            if (!activeItem) {
                return;
            }

            var offsetTop,
                upperBound,
                lowerBound,
                heightDelta = $(activeItem).outerHeight();

            offsetTop = activeItem.offsetTop;
            upperBound = $(that.suggestionsContainer).scrollTop();
            lowerBound = upperBound + that.options.maxHeight - heightDelta;

            if (offsetTop < upperBound) {
                $(that.suggestionsContainer).scrollTop(offsetTop);
            } else if (offsetTop > lowerBound) {
                $(that.suggestionsContainer).scrollTop(offsetTop - that.options.maxHeight + heightDelta);
            }

            if (!that.options.preserveInput) {
                that.el.val(that.getValue(that.suggestions[index].value));
            }
            that.signalHint(null);
        },

        onSelect: function (index) {
            var that = this,
                onSelectCallback = that.options.onSelect,
                suggestion = that.suggestions[index];

            that.currentValue = that.getValue(suggestion.value);

            if (that.currentValue !== that.el.val() && !that.options.preserveInput) {
                that.el.val(that.currentValue);
            }

            that.signalHint(null);
            that.suggestions = [];
            that.selection = suggestion;

            if ($.isFunction(onSelectCallback)) {
                onSelectCallback.call(that.element, suggestion);
            }
        },

        getValue: function (value) {
            var that = this,
                delimiter = that.options.delimiter,
                currentValue,
                parts;

            if (!delimiter) {
                return value;
            }

            currentValue = that.currentValue;
            parts = currentValue.split(delimiter);

            if (parts.length === 1) {
                return value;
            }

            return currentValue.substr(0, currentValue.length - parts[parts.length - 1].length) + value;
        },

        dispose: function () {
            var that = this;
            that.el.off('.autocomplete').removeData('autocomplete');
            that.disableKillerFn();
            $(window).off('resize.autocomplete', that.fixPositionCapture);
            $(that.suggestionsContainer).remove();
        }
    };

    // Create chainable jQuery plugin:
    $.fn.autocomplete = $.fn.devbridgeAutocomplete = function (options, args) {
        var dataKey = 'autocomplete';
        // If function invoked without argument return
        // instance of the first matched element:
        if (arguments.length === 0) {
            return this.first().data(dataKey);
        }

        return this.each(function () {
            var inputElement = $(this),
                instance = inputElement.data(dataKey);

            if (typeof options === 'string') {
                if (instance && typeof instance[options] === 'function') {
                    instance[options](args);
                }
            } else {
                // If instance already exists, destroy it:
                if (instance && instance.dispose) {
                    instance.dispose();
                }
                instance = new Autocomplete(this, options);
                inputElement.data(dataKey, instance);
            }
        });
    };
}));

/*
 v.1.2 by Aivis Lisovskis (c)

 changelog:
 1.2 - @11.11.2015
 repaired small bugs
 added test() - just creates some test cases
 added getBase() - gets current base url
 1.1 - @09.11.2015
 changed api name to StdHistory
 changed base singleton name to HistoryApi
 changed 'status' function to 'location'
 added 'search' to event listeners
 removed test function
 */

var StdHistory = function (d) {
    if(parent===void(0)){parent=false;};var p=this,settings={},elements={},body=false,config={body:document.body,'baseUrl':''},data={badBrowser:false,forceHash:false,state:false,'links':{},'listeners':{}, 'filters':{}},accessible={},objects={'albums':[]},publish=function(nameMe,resource,changable){if(changable===void(0)){canChange=false;}else{canChange=changable;};if(accessible[nameMe]!==void(0)){if(changable!==void(0)){accessible[nameMe]['changable']=canChange;}}else{accessible[nameMe]={'changable':canChange}};accessible[nameMe]['value']=resource;},
        create = function () {
            badBrowser();
            data.state = location.hash.substr(1);
            window.onhashchange = checkIfHashChanges;
            window.onpopstate = checkIfChanges;
            publish('base', config.baseUrl,false);
            checkIfChanges();
        },
        add = function (params) {
            data.links[params.address] = params;
        },
        navigate = function (setData) {
            data.state = setData;
            var stateObj = {};
            history.pushState(stateObj, null, config.baseUrl + setData);
            analytics(config.baseUrl + setData);
        },
        navigateReplace = function (setData) {
            data.state = setData;
            var stateObj = {};
            history.replaceState(stateObj, null, config.baseUrl + setData);
        },
        navigateHash = function (setData) {
            data.state = setData;
            data.forceHash = true;
            parts = document.location.href.split('#');
            document.location.href = parts[0] + '#' + setData;
        },
        checkIfHashChanges = function () {
            var hash = document.location.hash;
            if (hash!='#' + data.state && hash!='#') {
                var hash = hash.substr(1);
                data.state = hash;
                goto(data.state);
            }
        },
        checkIfChanges = function () {
            var myLocation = document.location.href.substr(config.baseUrl.length-1);
            if (myLocation!='/' + data.state && !data.forceHash) {
                var hash = myLocation.substr(1);
                data.state = hash;
                goto(data.state);
            } else {
                data.forceHash = false;
            }
        },
        goto = function (address) {
            if (data.links[address] !==void(0) && data.links[address].call !== void(0) && data.links[address].call!='') {
                data.links[address].call(data.links['params']);
                return true;
            } else {
                for (var a in data.listeners) {
                    var valid = false;
                    if (data.filters[a]) {
                        if (address.search(data.filters[a])) {
                            valid = true;
                        }
                    } else {
                        valid = true;
                    }

                    if (valid) {
                        if (data.listeners[a](address)) {
                            return true;
                        }
                    }
                }
            }

            return false;
        },
        analytics = function (link) {
            if (typeof (_gaq)!='undefined' && typeof(_gaq.push)!='undefined') {
                _gaq.push(['_trackPageview', link]);
            }
        },
        badBrowser = function () {
            if(navigator.appName.indexOf("Internet Explorer")!=-1){     //yeah, he's using IE
                var badBrowser=(
                    navigator.appVersion.indexOf("MSIE 1")==-1  //v10, 11, 12, etc. is fine too
                );

                if(badBrowser){
                    data.badBrowser = true;
                }
            }
        }
        ;

    p.getBase = function () {
        return config;
    }

    p.setBase = function (url) {
        config.baseUrl = url;
        publish('base', config.baseUrl,false);
    };

    p.location = function () {
        if (data.state == '') {
            return document.location;
        } else {
            return data.state;
        }
    };

    p.navigate = function (params) {
        if (data.badBrowser) {
            return false;
        }
        add(params);

        if (params.address === void(0)) {
            params.address = '/';
        }

        if (params['hash']!==void(0)) {
            navigateHash(params.address);
        } else if (params['replace']!==void(0)) {
            navigateReplace(params.address);
        } else {
            navigate(params.address);
        }

        if (params.callNow !== void(0)) {
            params.callNow(document.location.href);
        }
    };

    p.call = function (address) {
        goto(address);
    };

    p.list = function (addressList) {
        for (var a = 0; a<addressList.length; a++) {
            add(addressList[a])
        }

    };

    p.addListener = function (listener, call, filter) {
        if (data.listeners[listener]===void(0)) {
            data.listeners[listener] = call;
            if (filter!==void(0)) {
                data.filters[listener] = filter;
            } else {
                data.filters[listener] = false;
            }
        }
    };

    p.addAnalytics = function (link) {
        analytics(link['address']);
    };

    p.test = function () {
        historyApi.navigate({'address':'addr1'});
        historyApi.navigate({'address':'/addr/2'});
        historyApi.navigate({'address': 'addr/3/4/5'});
        historyApi.addListener('testListener', function (add) {console.info(add)});
    };

    p.get=function(nameMe){if(accessible[nameMe]!==void(0)){return accessible[nameMe]['value'];}else{return false;}};p.set=function(nameMe,value){if(accessible[nameMe]!==void(0) && accessible[nameMe]['changable']){accessible[nameMe]['value']=value;return true;}else{return false;}};p.parent=parent;if(typeof(d)!='undefined'){_.sval(config,d);};create();
};

var historyApi = new StdHistory();
/**
 * jQuery Unveil
 * A very lightweight jQuery plugin to lazy load images
 * http://luis-almeida.github.com/unveil
 *
 * Licensed under the MIT license.
 * Copyright 2013 Luís Almeida
 * https://github.com/luis-almeida
 */

;(function($) {

  $.fn.unveil = function(threshold, callback) {

    var $w = $(window),
        th = threshold || 0,
        retina = window.devicePixelRatio > 1,
        attrib = retina? "data-src-retina" : "data-src",
        images = this,
        loaded;

    this.one("unveil", function() {
      var source = this.getAttribute(attrib);
      source = source || this.getAttribute("data-src");
      if (source) {
        this.setAttribute("src", source);
        if (typeof callback === "function") callback.call(this);
      }
    });

    function unveil() {
      var inview = images.filter(function() {
        var $e = $(this);
        if ($e.is(":hidden")) return;

        var wt = $w.scrollTop(),
            wb = wt + $w.height(),
            et = $e.offset().top,
            eb = et + $e.height();

        return eb >= wt - th && et <= wb + th;
      });

      loaded = inview.trigger("unveil");
      images = images.not(loaded);
    }

    $w.on("scroll.unveil resize.unveil lookup.unveil", unveil);

    unveil();

    return this;

  };

})(window.jQuery || window.Zepto);

/*! jQuery Validation Plugin - v1.15.0 - 2/24/2016
 * http://jqueryvalidation.org/
 * Copyright (c) 2016 Jörn Zaefferer; Licensed MIT */
!function(a){"function"==typeof define&&define.amd?define(["jquery"],a):"object"==typeof module&&module.exports?module.exports=a(require("jquery")):a(jQuery)}(function(a){a.extend(a.fn,{validate:function(b){if(!this.length)return void(b&&b.debug&&window.console&&console.warn("Nothing selected, can't validate, returning nothing."));var c=a.data(this[0],"validator");return c?c:(this.attr("novalidate","novalidate"),c=new a.validator(b,this[0]),a.data(this[0],"validator",c),c.settings.onsubmit&&(this.on("click.validate",":submit",function(b){c.settings.submitHandler&&(c.submitButton=b.target),a(this).hasClass("cancel")&&(c.cancelSubmit=!0),void 0!==a(this).attr("formnovalidate")&&(c.cancelSubmit=!0)}),this.on("submit.validate",function(b){function d(){var d,e;return c.settings.submitHandler?(c.submitButton&&(d=a("<input type='hidden'/>").attr("name",c.submitButton.name).val(a(c.submitButton).val()).appendTo(c.currentForm)),e=c.settings.submitHandler.call(c,c.currentForm,b),c.submitButton&&d.remove(),void 0!==e?e:!1):!0}return c.settings.debug&&b.preventDefault(),c.cancelSubmit?(c.cancelSubmit=!1,d()):c.form()?c.pendingRequest?(c.formSubmitted=!0,!1):d():(c.focusInvalid(),!1)})),c)},valid:function(){var b,c,d;return a(this[0]).is("form")?b=this.validate().form():(d=[],b=!0,c=a(this[0].form).validate(),this.each(function(){b=c.element(this)&&b,b||(d=d.concat(c.errorList))}),c.errorList=d),b},rules:function(b,c){if(this.length){var d,e,f,g,h,i,j=this[0];if(b)switch(d=a.data(j.form,"validator").settings,e=d.rules,f=a.validator.staticRules(j),b){case"add":a.extend(f,a.validator.normalizeRule(c)),delete f.messages,e[j.name]=f,c.messages&&(d.messages[j.name]=a.extend(d.messages[j.name],c.messages));break;case"remove":return c?(i={},a.each(c.split(/\s/),function(b,c){i[c]=f[c],delete f[c],"required"===c&&a(j).removeAttr("aria-required")}),i):(delete e[j.name],f)}return g=a.validator.normalizeRules(a.extend({},a.validator.classRules(j),a.validator.attributeRules(j),a.validator.dataRules(j),a.validator.staticRules(j)),j),g.required&&(h=g.required,delete g.required,g=a.extend({required:h},g),a(j).attr("aria-required","true")),g.remote&&(h=g.remote,delete g.remote,g=a.extend(g,{remote:h})),g}}}),a.extend(a.expr[":"],{blank:function(b){return!a.trim(""+a(b).val())},filled:function(b){var c=a(b).val();return null!==c&&!!a.trim(""+c)},unchecked:function(b){return!a(b).prop("checked")}}),a.validator=function(b,c){this.settings=a.extend(!0,{},a.validator.defaults,b),this.currentForm=c,this.init()},a.validator.format=function(b,c){return 1===arguments.length?function(){var c=a.makeArray(arguments);return c.unshift(b),a.validator.format.apply(this,c)}:void 0===c?b:(arguments.length>2&&c.constructor!==Array&&(c=a.makeArray(arguments).slice(1)),c.constructor!==Array&&(c=[c]),a.each(c,function(a,c){b=b.replace(new RegExp("\\{"+a+"\\}","g"),function(){return c})}),b)},a.extend(a.validator,{defaults:{messages:{},groups:{},rules:{},errorClass:"error",pendingClass:"pending",validClass:"valid",errorElement:"label",focusCleanup:!1,focusInvalid:!0,errorContainer:a([]),errorLabelContainer:a([]),onsubmit:!0,ignore:":hidden",ignoreTitle:!1,onfocusin:function(a){this.lastActive=a,this.settings.focusCleanup&&(this.settings.unhighlight&&this.settings.unhighlight.call(this,a,this.settings.errorClass,this.settings.validClass),this.hideThese(this.errorsFor(a)))},onfocusout:function(a){this.checkable(a)||!(a.name in this.submitted)&&this.optional(a)||this.element(a)},onkeyup:function(b,c){var d=[16,17,18,20,35,36,37,38,39,40,45,144,225];9===c.which&&""===this.elementValue(b)||-1!==a.inArray(c.keyCode,d)||(b.name in this.submitted||b.name in this.invalid)&&this.element(b)},onclick:function(a){a.name in this.submitted?this.element(a):a.parentNode.name in this.submitted&&this.element(a.parentNode)},highlight:function(b,c,d){"radio"===b.type?this.findByName(b.name).addClass(c).removeClass(d):a(b).addClass(c).removeClass(d)},unhighlight:function(b,c,d){"radio"===b.type?this.findByName(b.name).removeClass(c).addClass(d):a(b).removeClass(c).addClass(d)}},setDefaults:function(b){a.extend(a.validator.defaults,b)},messages:{required:"This field is required.",remote:"Please fix this field.",email:"Please enter a valid email address.",url:"Please enter a valid URL.",date:"Please enter a valid date.",dateISO:"Please enter a valid date ( ISO ).",number:"Please enter a valid number.",digits:"Please enter only digits.",equalTo:"Please enter the same value again.",maxlength:a.validator.format("Please enter no more than {0} characters."),minlength:a.validator.format("Please enter at least {0} characters."),rangelength:a.validator.format("Please enter a value between {0} and {1} characters long."),range:a.validator.format("Please enter a value between {0} and {1}."),max:a.validator.format("Please enter a value less than or equal to {0}."),min:a.validator.format("Please enter a value greater than or equal to {0}."),step:a.validator.format("Please enter a multiple of {0}.")},autoCreateRanges:!1,prototype:{init:function(){function b(b){var c=a.data(this.form,"validator"),d="on"+b.type.replace(/^validate/,""),e=c.settings;e[d]&&!a(this).is(e.ignore)&&e[d].call(c,this,b)}this.labelContainer=a(this.settings.errorLabelContainer),this.errorContext=this.labelContainer.length&&this.labelContainer||a(this.currentForm),this.containers=a(this.settings.errorContainer).add(this.settings.errorLabelContainer),this.submitted={},this.valueCache={},this.pendingRequest=0,this.pending={},this.invalid={},this.reset();var c,d=this.groups={};a.each(this.settings.groups,function(b,c){"string"==typeof c&&(c=c.split(/\s/)),a.each(c,function(a,c){d[c]=b})}),c=this.settings.rules,a.each(c,function(b,d){c[b]=a.validator.normalizeRule(d)}),a(this.currentForm).on("focusin.validate focusout.validate keyup.validate",":text, [type='password'], [type='file'], select, textarea, [type='number'], [type='search'], [type='tel'], [type='url'], [type='email'], [type='datetime'], [type='date'], [type='month'], [type='week'], [type='time'], [type='datetime-local'], [type='range'], [type='color'], [type='radio'], [type='checkbox'], [contenteditable]",b).on("click.validate","select, option, [type='radio'], [type='checkbox']",b),this.settings.invalidHandler&&a(this.currentForm).on("invalid-form.validate",this.settings.invalidHandler),a(this.currentForm).find("[required], [data-rule-required], .required").attr("aria-required","true")},form:function(){return this.checkForm(),a.extend(this.submitted,this.errorMap),this.invalid=a.extend({},this.errorMap),this.valid()||a(this.currentForm).triggerHandler("invalid-form",[this]),this.showErrors(),this.valid()},checkForm:function(){this.prepareForm();for(var a=0,b=this.currentElements=this.elements();b[a];a++)this.check(b[a]);return this.valid()},element:function(b){var c,d,e=this.clean(b),f=this.validationTargetFor(e),g=this,h=!0;return void 0===f?delete this.invalid[e.name]:(this.prepareElement(f),this.currentElements=a(f),d=this.groups[f.name],d&&a.each(this.groups,function(a,b){b===d&&a!==f.name&&(e=g.validationTargetFor(g.clean(g.findByName(a))),e&&e.name in g.invalid&&(g.currentElements.push(e),h=h&&g.check(e)))}),c=this.check(f)!==!1,h=h&&c,c?this.invalid[f.name]=!1:this.invalid[f.name]=!0,this.numberOfInvalids()||(this.toHide=this.toHide.add(this.containers)),this.showErrors(),a(b).attr("aria-invalid",!c)),h},showErrors:function(b){if(b){var c=this;a.extend(this.errorMap,b),this.errorList=a.map(this.errorMap,function(a,b){return{message:a,element:c.findByName(b)[0]}}),this.successList=a.grep(this.successList,function(a){return!(a.name in b)})}this.settings.showErrors?this.settings.showErrors.call(this,this.errorMap,this.errorList):this.defaultShowErrors()},resetForm:function(){a.fn.resetForm&&a(this.currentForm).resetForm(),this.invalid={},this.submitted={},this.prepareForm(),this.hideErrors();var b=this.elements().removeData("previousValue").removeAttr("aria-invalid");this.resetElements(b)},resetElements:function(a){var b;if(this.settings.unhighlight)for(b=0;a[b];b++)this.settings.unhighlight.call(this,a[b],this.settings.errorClass,""),this.findByName(a[b].name).removeClass(this.settings.validClass);else a.removeClass(this.settings.errorClass).removeClass(this.settings.validClass)},numberOfInvalids:function(){return this.objectLength(this.invalid)},objectLength:function(a){var b,c=0;for(b in a)a[b]&&c++;return c},hideErrors:function(){this.hideThese(this.toHide)},hideThese:function(a){a.not(this.containers).text(""),this.addWrapper(a).hide()},valid:function(){return 0===this.size()},size:function(){return this.errorList.length},focusInvalid:function(){if(this.settings.focusInvalid)try{a(this.findLastActive()||this.errorList.length&&this.errorList[0].element||[]).filter(":visible").focus().trigger("focusin")}catch(b){}},findLastActive:function(){var b=this.lastActive;return b&&1===a.grep(this.errorList,function(a){return a.element.name===b.name}).length&&b},elements:function(){var b=this,c={};return a(this.currentForm).find("input, select, textarea, [contenteditable]").not(":submit, :reset, :image, :disabled").not(this.settings.ignore).filter(function(){var d=this.name||a(this).attr("name");return!d&&b.settings.debug&&window.console&&console.error("%o has no name assigned",this),this.hasAttribute("contenteditable")&&(this.form=a(this).closest("form")[0]),d in c||!b.objectLength(a(this).rules())?!1:(c[d]=!0,!0)})},clean:function(b){return a(b)[0]},errors:function(){var b=this.settings.errorClass.split(" ").join(".");return a(this.settings.errorElement+"."+b,this.errorContext)},resetInternals:function(){this.successList=[],this.errorList=[],this.errorMap={},this.toShow=a([]),this.toHide=a([])},reset:function(){this.resetInternals(),this.currentElements=a([])},prepareForm:function(){this.reset(),this.toHide=this.errors().add(this.containers)},prepareElement:function(a){this.reset(),this.toHide=this.errorsFor(a)},elementValue:function(b){var c,d,e=a(b),f=b.type;return"radio"===f||"checkbox"===f?this.findByName(b.name).filter(":checked").val():"number"===f&&"undefined"!=typeof b.validity?b.validity.badInput?"NaN":e.val():(c=b.hasAttribute("contenteditable")?e.text():e.val(),"file"===f?"C:\\fakepath\\"===c.substr(0,12)?c.substr(12):(d=c.lastIndexOf("/"),d>=0?c.substr(d+1):(d=c.lastIndexOf("\\"),d>=0?c.substr(d+1):c)):"string"==typeof c?c.replace(/\r/g,""):c)},check:function(b){b=this.validationTargetFor(this.clean(b));var c,d,e,f=a(b).rules(),g=a.map(f,function(a,b){return b}).length,h=!1,i=this.elementValue(b);if("function"==typeof f.normalizer){if(i=f.normalizer.call(b,i),"string"!=typeof i)throw new TypeError("The normalizer should return a string value.");delete f.normalizer}for(d in f){e={method:d,parameters:f[d]};try{if(c=a.validator.methods[d].call(this,i,b,e.parameters),"dependency-mismatch"===c&&1===g){h=!0;continue}if(h=!1,"pending"===c)return void(this.toHide=this.toHide.not(this.errorsFor(b)));if(!c)return this.formatAndAdd(b,e),!1}catch(j){throw this.settings.debug&&window.console&&console.log("Exception occurred when checking element "+b.id+", check the '"+e.method+"' method.",j),j instanceof TypeError&&(j.message+=".  Exception occurred when checking element "+b.id+", check the '"+e.method+"' method."),j}}if(!h)return this.objectLength(f)&&this.successList.push(b),!0},customDataMessage:function(b,c){return a(b).data("msg"+c.charAt(0).toUpperCase()+c.substring(1).toLowerCase())||a(b).data("msg")},customMessage:function(a,b){var c=this.settings.messages[a];return c&&(c.constructor===String?c:c[b])},findDefined:function(){for(var a=0;a<arguments.length;a++)if(void 0!==arguments[a])return arguments[a]},defaultMessage:function(b,c){var d=this.findDefined(this.customMessage(b.name,c.method),this.customDataMessage(b,c.method),!this.settings.ignoreTitle&&b.title||void 0,a.validator.messages[c.method],"<strong>Warning: No message defined for "+b.name+"</strong>"),e=/\$?\{(\d+)\}/g;return"function"==typeof d?d=d.call(this,c.parameters,b):e.test(d)&&(d=a.validator.format(d.replace(e,"{$1}"),c.parameters)),d},formatAndAdd:function(a,b){var c=this.defaultMessage(a,b);this.errorList.push({message:c,element:a,method:b.method}),this.errorMap[a.name]=c,this.submitted[a.name]=c},addWrapper:function(a){return this.settings.wrapper&&(a=a.add(a.parent(this.settings.wrapper))),a},defaultShowErrors:function(){var a,b,c;for(a=0;this.errorList[a];a++)c=this.errorList[a],this.settings.highlight&&this.settings.highlight.call(this,c.element,this.settings.errorClass,this.settings.validClass),this.showLabel(c.element,c.message);if(this.errorList.length&&(this.toShow=this.toShow.add(this.containers)),this.settings.success)for(a=0;this.successList[a];a++)this.showLabel(this.successList[a]);if(this.settings.unhighlight)for(a=0,b=this.validElements();b[a];a++)this.settings.unhighlight.call(this,b[a],this.settings.errorClass,this.settings.validClass);this.toHide=this.toHide.not(this.toShow),this.hideErrors(),this.addWrapper(this.toShow).show()},validElements:function(){return this.currentElements.not(this.invalidElements())},invalidElements:function(){return a(this.errorList).map(function(){return this.element})},showLabel:function(b,c){var d,e,f,g,h=this.errorsFor(b),i=this.idOrName(b),j=a(b).attr("aria-describedby");h.length?(h.removeClass(this.settings.validClass).addClass(this.settings.errorClass),h.html(c)):(h=a("<"+this.settings.errorElement+">").attr("id",i+"-error").addClass(this.settings.errorClass).html(c||""),d=h,this.settings.wrapper&&(d=h.hide().show().wrap("<"+this.settings.wrapper+"/>").parent()),this.labelContainer.length?this.labelContainer.append(d):this.settings.errorPlacement?this.settings.errorPlacement(d,a(b)):d.insertAfter(b),h.is("label")?h.attr("for",i):0===h.parents("label[for='"+this.escapeCssMeta(i)+"']").length&&(f=h.attr("id"),j?j.match(new RegExp("\\b"+this.escapeCssMeta(f)+"\\b"))||(j+=" "+f):j=f,a(b).attr("aria-describedby",j),e=this.groups[b.name],e&&(g=this,a.each(g.groups,function(b,c){c===e&&a("[name='"+g.escapeCssMeta(b)+"']",g.currentForm).attr("aria-describedby",h.attr("id"))})))),!c&&this.settings.success&&(h.text(""),"string"==typeof this.settings.success?h.addClass(this.settings.success):this.settings.success(h,b)),this.toShow=this.toShow.add(h)},errorsFor:function(b){var c=this.escapeCssMeta(this.idOrName(b)),d=a(b).attr("aria-describedby"),e="label[for='"+c+"'], label[for='"+c+"'] *";return d&&(e=e+", #"+this.escapeCssMeta(d).replace(/\s+/g,", #")),this.errors().filter(e)},escapeCssMeta:function(a){return a.replace(/([\\!"#$%&'()*+,./:;<=>?@\[\]^`{|}~])/g,"\\$1")},idOrName:function(a){return this.groups[a.name]||(this.checkable(a)?a.name:a.id||a.name)},validationTargetFor:function(b){return this.checkable(b)&&(b=this.findByName(b.name)),a(b).not(this.settings.ignore)[0]},checkable:function(a){return/radio|checkbox/i.test(a.type)},findByName:function(b){return a(this.currentForm).find("[name='"+this.escapeCssMeta(b)+"']")},getLength:function(b,c){switch(c.nodeName.toLowerCase()){case"select":return a("option:selected",c).length;case"input":if(this.checkable(c))return this.findByName(c.name).filter(":checked").length}return b.length},depend:function(a,b){return this.dependTypes[typeof a]?this.dependTypes[typeof a](a,b):!0},dependTypes:{"boolean":function(a){return a},string:function(b,c){return!!a(b,c.form).length},"function":function(a,b){return a(b)}},optional:function(b){var c=this.elementValue(b);return!a.validator.methods.required.call(this,c,b)&&"dependency-mismatch"},startRequest:function(b){this.pending[b.name]||(this.pendingRequest++,a(b).addClass(this.settings.pendingClass),this.pending[b.name]=!0)},stopRequest:function(b,c){this.pendingRequest--,this.pendingRequest<0&&(this.pendingRequest=0),delete this.pending[b.name],a(b).removeClass(this.settings.pendingClass),c&&0===this.pendingRequest&&this.formSubmitted&&this.form()?(a(this.currentForm).submit(),this.formSubmitted=!1):!c&&0===this.pendingRequest&&this.formSubmitted&&(a(this.currentForm).triggerHandler("invalid-form",[this]),this.formSubmitted=!1)},previousValue:function(b,c){return a.data(b,"previousValue")||a.data(b,"previousValue",{old:null,valid:!0,message:this.defaultMessage(b,{method:c})})},destroy:function(){this.resetForm(),a(this.currentForm).off(".validate").removeData("validator").find(".validate-equalTo-blur").off(".validate-equalTo").removeClass("validate-equalTo-blur")}},classRuleSettings:{required:{required:!0},email:{email:!0},url:{url:!0},date:{date:!0},dateISO:{dateISO:!0},number:{number:!0},digits:{digits:!0},creditcard:{creditcard:!0}},addClassRules:function(b,c){b.constructor===String?this.classRuleSettings[b]=c:a.extend(this.classRuleSettings,b)},classRules:function(b){var c={},d=a(b).attr("class");return d&&a.each(d.split(" "),function(){this in a.validator.classRuleSettings&&a.extend(c,a.validator.classRuleSettings[this])}),c},normalizeAttributeRule:function(a,b,c,d){/min|max|step/.test(c)&&(null===b||/number|range|text/.test(b))&&(d=Number(d),isNaN(d)&&(d=void 0)),d||0===d?a[c]=d:b===c&&"range"!==b&&(a[c]=!0)},attributeRules:function(b){var c,d,e={},f=a(b),g=b.getAttribute("type");for(c in a.validator.methods)"required"===c?(d=b.getAttribute(c),""===d&&(d=!0),d=!!d):d=f.attr(c),this.normalizeAttributeRule(e,g,c,d);return e.maxlength&&/-1|2147483647|524288/.test(e.maxlength)&&delete e.maxlength,e},dataRules:function(b){var c,d,e={},f=a(b),g=b.getAttribute("type");for(c in a.validator.methods)d=f.data("rule"+c.charAt(0).toUpperCase()+c.substring(1).toLowerCase()),this.normalizeAttributeRule(e,g,c,d);return e},staticRules:function(b){var c={},d=a.data(b.form,"validator");return d.settings.rules&&(c=a.validator.normalizeRule(d.settings.rules[b.name])||{}),c},normalizeRules:function(b,c){return a.each(b,function(d,e){if(e===!1)return void delete b[d];if(e.param||e.depends){var f=!0;switch(typeof e.depends){case"string":f=!!a(e.depends,c.form).length;break;case"function":f=e.depends.call(c,c)}f?b[d]=void 0!==e.param?e.param:!0:(a.data(c.form,"validator").resetElements(a(c)),delete b[d])}}),a.each(b,function(d,e){b[d]=a.isFunction(e)&&"normalizer"!==d?e(c):e}),a.each(["minlength","maxlength"],function(){b[this]&&(b[this]=Number(b[this]))}),a.each(["rangelength","range"],function(){var c;b[this]&&(a.isArray(b[this])?b[this]=[Number(b[this][0]),Number(b[this][1])]:"string"==typeof b[this]&&(c=b[this].replace(/[\[\]]/g,"").split(/[\s,]+/),b[this]=[Number(c[0]),Number(c[1])]))}),a.validator.autoCreateRanges&&(null!=b.min&&null!=b.max&&(b.range=[b.min,b.max],delete b.min,delete b.max),null!=b.minlength&&null!=b.maxlength&&(b.rangelength=[b.minlength,b.maxlength],delete b.minlength,delete b.maxlength)),b},normalizeRule:function(b){if("string"==typeof b){var c={};a.each(b.split(/\s/),function(){c[this]=!0}),b=c}return b},addMethod:function(b,c,d){a.validator.methods[b]=c,a.validator.messages[b]=void 0!==d?d:a.validator.messages[b],c.length<3&&a.validator.addClassRules(b,a.validator.normalizeRule(b))},methods:{required:function(b,c,d){if(!this.depend(d,c))return"dependency-mismatch";if("select"===c.nodeName.toLowerCase()){var e=a(c).val();return e&&e.length>0}return this.checkable(c)?this.getLength(b,c)>0:b.length>0},email:function(a,b){return this.optional(b)||/^[a-zA-Z0-9.!#$%&'*+\/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/.test(a)},url:function(a,b){return this.optional(b)||/^(?:(?:(?:https?|ftp):)?\/\/)(?:\S+(?::\S*)?@)?(?:(?!(?:10|127)(?:\.\d{1,3}){3})(?!(?:169\.254|192\.168)(?:\.\d{1,3}){2})(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))|(?:(?:[a-z\u00a1-\uffff0-9]-*)*[a-z\u00a1-\uffff0-9]+)(?:\.(?:[a-z\u00a1-\uffff0-9]-*)*[a-z\u00a1-\uffff0-9]+)*(?:\.(?:[a-z\u00a1-\uffff]{2,})).?)(?::\d{2,5})?(?:[/?#]\S*)?$/i.test(a)},date:function(a,b){return this.optional(b)||!/Invalid|NaN/.test(new Date(a).toString())},dateISO:function(a,b){return this.optional(b)||/^\d{4}[\/\-](0?[1-9]|1[012])[\/\-](0?[1-9]|[12][0-9]|3[01])$/.test(a)},number:function(a,b){return this.optional(b)||/^(?:-?\d+|-?\d{1,3}(?:,\d{3})+)?(?:\.\d+)?$/.test(a)},digits:function(a,b){return this.optional(b)||/^\d+$/.test(a)},minlength:function(b,c,d){var e=a.isArray(b)?b.length:this.getLength(b,c);return this.optional(c)||e>=d},maxlength:function(b,c,d){var e=a.isArray(b)?b.length:this.getLength(b,c);return this.optional(c)||d>=e},rangelength:function(b,c,d){var e=a.isArray(b)?b.length:this.getLength(b,c);return this.optional(c)||e>=d[0]&&e<=d[1]},min:function(a,b,c){return this.optional(b)||a>=c},max:function(a,b,c){return this.optional(b)||c>=a},range:function(a,b,c){return this.optional(b)||a>=c[0]&&a<=c[1]},step:function(b,c,d){var e=a(c).attr("type"),f="Step attribute on input type "+e+" is not supported.",g=["text","number","range"],h=new RegExp("\\b"+e+"\\b"),i=e&&!h.test(g.join());if(i)throw new Error(f);return this.optional(c)||b%d===0},equalTo:function(b,c,d){var e=a(d);return this.settings.onfocusout&&e.not(".validate-equalTo-blur").length&&e.addClass("validate-equalTo-blur").on("blur.validate-equalTo",function(){a(c).valid()}),b===e.val()},remote:function(b,c,d,e){if(this.optional(c))return"dependency-mismatch";e="string"==typeof e&&e||"remote";var f,g,h,i=this.previousValue(c,e);return this.settings.messages[c.name]||(this.settings.messages[c.name]={}),i.originalMessage=i.originalMessage||this.settings.messages[c.name][e],this.settings.messages[c.name][e]=i.message,d="string"==typeof d&&{url:d}||d,h=a.param(a.extend({data:b},d.data)),i.old===h?i.valid:(i.old=h,f=this,this.startRequest(c),g={},g[c.name]=b,a.ajax(a.extend(!0,{mode:"abort",port:"validate"+c.name,dataType:"json",data:g,context:f.currentForm,success:function(a){var d,g,h,j=a===!0||"true"===a;f.settings.messages[c.name][e]=i.originalMessage,j?(h=f.formSubmitted,f.resetInternals(),f.toHide=f.errorsFor(c),f.formSubmitted=h,f.successList.push(c),f.invalid[c.name]=!1,f.showErrors()):(d={},g=a||f.defaultMessage(c,{method:e,parameters:b}),d[c.name]=i.message=g,f.invalid[c.name]=!0,f.showErrors(d)),i.valid=j,f.stopRequest(c,j)}},d)),"pending")}}});var b,c={};a.ajaxPrefilter?a.ajaxPrefilter(function(a,b,d){var e=a.port;"abort"===a.mode&&(c[e]&&c[e].abort(),c[e]=d)}):(b=a.ajax,a.ajax=function(d){var e=("mode"in d?d:a.ajaxSettings).mode,f=("port"in d?d:a.ajaxSettings).port;return"abort"===e?(c[f]&&c[f].abort(),c[f]=b.apply(this,arguments),c[f]):b.apply(this,arguments)})});


!function(a,b,c,d){function e(b,c){this.settings=null,this.options=a.extend({},e.Defaults,c),this.$element=a(b),this.drag=a.extend({},m),this.state=a.extend({},n),this.e=a.extend({},o),this._plugins={},this._supress={},this._current=null,this._speed=null,this._coordinates=[],this._breakpoint=null,this._width=null,this._items=[],this._clones=[],this._mergers=[],this._invalidated={},this._pipe=[],a.each(e.Plugins,a.proxy(function(a,b){this._plugins[a[0].toLowerCase()+a.slice(1)]=new b(this)},this)),a.each(e.Pipe,a.proxy(function(b,c){this._pipe.push({filter:c.filter,run:a.proxy(c.run,this)})},this)),this.setup(),this.initialize()}function f(a){if(a.touches!==d)return{x:a.touches[0].pageX,y:a.touches[0].pageY};if(a.touches===d){if(a.pageX!==d)return{x:a.pageX,y:a.pageY};if(a.pageX===d)return{x:a.clientX,y:a.clientY}}}function g(a){var b,d,e=c.createElement("div"),f=a;for(b in f)if(d=f[b],"undefined"!=typeof e.style[d])return e=null,[d,b];return[!1]}function h(){return g(["transition","WebkitTransition","MozTransition","OTransition"])[1]}function i(){return g(["transform","WebkitTransform","MozTransform","OTransform","msTransform"])[0]}function j(){return g(["perspective","webkitPerspective","MozPerspective","OPerspective","MsPerspective"])[0]}function k(){return"ontouchstart"in b||!!navigator.msMaxTouchPoints}function l(){return b.navigator.msPointerEnabled}var m,n,o;m={start:0,startX:0,startY:0,current:0,currentX:0,currentY:0,offsetX:0,offsetY:0,distance:null,startTime:0,endTime:0,updatedX:0,targetEl:null},n={isTouch:!1,isScrolling:!1,isSwiping:!1,direction:!1,inMotion:!1},o={_onDragStart:null,_onDragMove:null,_onDragEnd:null,_transitionEnd:null,_resizer:null,_responsiveCall:null,_goToLoop:null,_checkVisibile:null},e.Defaults={items:3,loop:!1,center:!1,mouseDrag:!0,touchDrag:!0,pullDrag:!0,freeDrag:!1,margin:0,stagePadding:0,merge:!1,mergeFit:!0,autoWidth:!1,startPosition:0,rtl:!1,smartSpeed:250,fluidSpeed:!1,dragEndSpeed:!1,responsive:{},responsiveRefreshRate:200,responsiveBaseElement:b,responsiveClass:!1,fallbackEasing:"swing",info:!1,nestedItemSelector:!1,itemElement:"div",stageElement:"div",themeClass:"owl-theme",baseClass:"owl-carousel",itemClass:"owl-item",centerClass:"center",activeClass:"active"},e.Width={Default:"default",Inner:"inner",Outer:"outer"},e.Plugins={},e.Pipe=[{filter:["width","items","settings"],run:function(a){a.current=this._items&&this._items[this.relative(this._current)]}},{filter:["items","settings"],run:function(){var a=this._clones,b=this.$stage.children(".cloned");(b.length!==a.length||!this.settings.loop&&a.length>0)&&(this.$stage.children(".cloned").remove(),this._clones=[])}},{filter:["items","settings"],run:function(){var a,b,c=this._clones,d=this._items,e=this.settings.loop?c.length-Math.max(2*this.settings.items,4):0;for(a=0,b=Math.abs(e/2);b>a;a++)e>0?(this.$stage.children().eq(d.length+c.length-1).remove(),c.pop(),this.$stage.children().eq(0).remove(),c.pop()):(c.push(c.length/2),this.$stage.append(d[c[c.length-1]].clone().addClass("cloned")),c.push(d.length-1-(c.length-1)/2),this.$stage.prepend(d[c[c.length-1]].clone().addClass("cloned")))}},{filter:["width","items","settings"],run:function(){var a,b,c,d=this.settings.rtl?1:-1,e=(this.width()/this.settings.items).toFixed(3),f=0;for(this._coordinates=[],b=0,c=this._clones.length+this._items.length;c>b;b++)a=this._mergers[this.relative(b)],a=this.settings.mergeFit&&Math.min(a,this.settings.items)||a,f+=(this.settings.autoWidth?this._items[this.relative(b)].width()+this.settings.margin:e*a)*d,this._coordinates.push(f)}},{filter:["width","items","settings"],run:function(){var b,c,d=(this.width()/this.settings.items).toFixed(3),e={width:Math.abs(this._coordinates[this._coordinates.length-1])+2*this.settings.stagePadding,"padding-left":this.settings.stagePadding||"","padding-right":this.settings.stagePadding||""};if(this.$stage.css(e),e={width:this.settings.autoWidth?"auto":d-this.settings.margin},e[this.settings.rtl?"margin-left":"margin-right"]=this.settings.margin,!this.settings.autoWidth&&a.grep(this._mergers,function(a){return a>1}).length>0)for(b=0,c=this._coordinates.length;c>b;b++)e.width=Math.abs(this._coordinates[b])-Math.abs(this._coordinates[b-1]||0)-this.settings.margin,this.$stage.children().eq(b).css(e);else this.$stage.children().css(e)}},{filter:["width","items","settings"],run:function(a){a.current&&this.reset(this.$stage.children().index(a.current))}},{filter:["position"],run:function(){this.animate(this.coordinates(this._current))}},{filter:["width","position","items","settings"],run:function(){var a,b,c,d,e=this.settings.rtl?1:-1,f=2*this.settings.stagePadding,g=this.coordinates(this.current())+f,h=g+this.width()*e,i=[];for(c=0,d=this._coordinates.length;d>c;c++)a=this._coordinates[c-1]||0,b=Math.abs(this._coordinates[c])+f*e,(this.op(a,"<=",g)&&this.op(a,">",h)||this.op(b,"<",g)&&this.op(b,">",h))&&i.push(c);this.$stage.children("."+this.settings.activeClass).removeClass(this.settings.activeClass),this.$stage.children(":eq("+i.join("), :eq(")+")").addClass(this.settings.activeClass),this.settings.center&&(this.$stage.children("."+this.settings.centerClass).removeClass(this.settings.centerClass),this.$stage.children().eq(this.current()).addClass(this.settings.centerClass))}}],e.prototype.initialize=function(){if(this.trigger("initialize"),this.$element.addClass(this.settings.baseClass).addClass(this.settings.themeClass).toggleClass("owl-rtl",this.settings.rtl),this.browserSupport(),this.settings.autoWidth&&this.state.imagesLoaded!==!0){var b,c,e;if(b=this.$element.find("img"),c=this.settings.nestedItemSelector?"."+this.settings.nestedItemSelector:d,e=this.$element.children(c).width(),b.length&&0>=e)return this.preloadAutoWidthImages(b),!1}this.$element.addClass("owl-loading"),this.$stage=a("<"+this.settings.stageElement+' class="owl-stage"/>').wrap('<div class="owl-stage-outer">'),this.$element.append(this.$stage.parent()),this.replace(this.$element.children().not(this.$stage.parent())),this._width=this.$element.width(),this.refresh(),this.$element.removeClass("owl-loading").addClass("owl-loaded"),this.eventsCall(),this.internalEvents(),this.addTriggerableEvents(),this.trigger("initialized")},e.prototype.setup=function(){var b=this.viewport(),c=this.options.responsive,d=-1,e=null;c?(a.each(c,function(a){b>=a&&a>d&&(d=Number(a))}),e=a.extend({},this.options,c[d]),delete e.responsive,e.responsiveClass&&this.$element.attr("class",function(a,b){return b.replace(/\b owl-responsive-\S+/g,"")}).addClass("owl-responsive-"+d)):e=a.extend({},this.options),(null===this.settings||this._breakpoint!==d)&&(this.trigger("change",{property:{name:"settings",value:e}}),this._breakpoint=d,this.settings=e,this.invalidate("settings"),this.trigger("changed",{property:{name:"settings",value:this.settings}}))},e.prototype.optionsLogic=function(){this.$element.toggleClass("owl-center",this.settings.center),this.settings.loop&&this._items.length<this.settings.items&&(this.settings.loop=!1),this.settings.autoWidth&&(this.settings.stagePadding=!1,this.settings.merge=!1)},e.prototype.prepare=function(b){var c=this.trigger("prepare",{content:b});return c.data||(c.data=a("<"+this.settings.itemElement+"/>").addClass(this.settings.itemClass).append(b)),this.trigger("prepared",{content:c.data}),c.data},e.prototype.update=function(){for(var b=0,c=this._pipe.length,d=a.proxy(function(a){return this[a]},this._invalidated),e={};c>b;)(this._invalidated.all||a.grep(this._pipe[b].filter,d).length>0)&&this._pipe[b].run(e),b++;this._invalidated={}},e.prototype.width=function(a){switch(a=a||e.Width.Default){case e.Width.Inner:case e.Width.Outer:return this._width;default:return this._width-2*this.settings.stagePadding+this.settings.margin}},e.prototype.refresh=function(){if(0===this._items.length)return!1;(new Date).getTime();this.trigger("refresh"),this.setup(),this.optionsLogic(),this.$stage.addClass("owl-refresh"),this.update(),this.$stage.removeClass("owl-refresh"),this.state.orientation=b.orientation,this.watchVisibility(),this.trigger("refreshed")},e.prototype.eventsCall=function(){this.e._onDragStart=a.proxy(function(a){this.onDragStart(a)},this),this.e._onDragMove=a.proxy(function(a){this.onDragMove(a)},this),this.e._onDragEnd=a.proxy(function(a){this.onDragEnd(a)},this),this.e._onResize=a.proxy(function(a){this.onResize(a)},this),this.e._transitionEnd=a.proxy(function(a){this.transitionEnd(a)},this),this.e._preventClick=a.proxy(function(a){this.preventClick(a)},this)},e.prototype.onThrottledResize=function(){b.clearTimeout(this.resizeTimer),this.resizeTimer=b.setTimeout(this.e._onResize,this.settings.responsiveRefreshRate)},e.prototype.onResize=function(){return this._items.length?this._width===this.$element.width()?!1:this.trigger("resize").isDefaultPrevented()?!1:(this._width=this.$element.width(),this.invalidate("width"),this.refresh(),void this.trigger("resized")):!1},e.prototype.eventsRouter=function(a){var b=a.type;"mousedown"===b||"touchstart"===b?this.onDragStart(a):"mousemove"===b||"touchmove"===b?this.onDragMove(a):"mouseup"===b||"touchend"===b?this.onDragEnd(a):"touchcancel"===b&&this.onDragEnd(a)},e.prototype.internalEvents=function(){var c=(k(),l());this.settings.mouseDrag?(this.$stage.on("mousedown",a.proxy(function(a){this.eventsRouter(a)},this)),this.$stage.on("dragstart",function(){return!1}),this.$stage.get(0).onselectstart=function(){return!1}):this.$element.addClass("owl-text-select-on"),this.settings.touchDrag&&!c&&this.$stage.on("touchstart touchcancel",a.proxy(function(a){this.eventsRouter(a)},this)),this.transitionEndVendor&&this.on(this.$stage.get(0),this.transitionEndVendor,this.e._transitionEnd,!1),this.settings.responsive!==!1&&this.on(b,"resize",a.proxy(this.onThrottledResize,this))},e.prototype.onDragStart=function(d){var e,g,h,i;if(e=d.originalEvent||d||b.event,3===e.which||this.state.isTouch)return!1;if("mousedown"===e.type&&this.$stage.addClass("owl-grab"),this.trigger("drag"),this.drag.startTime=(new Date).getTime(),this.speed(0),this.state.isTouch=!0,this.state.isScrolling=!1,this.state.isSwiping=!1,this.drag.distance=0,g=f(e).x,h=f(e).y,this.drag.offsetX=this.$stage.position().left,this.drag.offsetY=this.$stage.position().top,this.settings.rtl&&(this.drag.offsetX=this.$stage.position().left+this.$stage.width()-this.width()+this.settings.margin),this.state.inMotion&&this.support3d)i=this.getTransformProperty(),this.drag.offsetX=i,this.animate(i),this.state.inMotion=!0;else if(this.state.inMotion&&!this.support3d)return this.state.inMotion=!1,!1;this.drag.startX=g-this.drag.offsetX,this.drag.startY=h-this.drag.offsetY,this.drag.start=g-this.drag.startX,this.drag.targetEl=e.target||e.srcElement,this.drag.updatedX=this.drag.start,("IMG"===this.drag.targetEl.tagName||"A"===this.drag.targetEl.tagName)&&(this.drag.targetEl.draggable=!1),a(c).on("mousemove.owl.dragEvents mouseup.owl.dragEvents touchmove.owl.dragEvents touchend.owl.dragEvents",a.proxy(function(a){this.eventsRouter(a)},this))},e.prototype.onDragMove=function(a){var c,e,g,h,i,j;this.state.isTouch&&(this.state.isScrolling||(c=a.originalEvent||a||b.event,e=f(c).x,g=f(c).y,this.drag.currentX=e-this.drag.startX,this.drag.currentY=g-this.drag.startY,this.drag.distance=this.drag.currentX-this.drag.offsetX,this.drag.distance<0?this.state.direction=this.settings.rtl?"right":"left":this.drag.distance>0&&(this.state.direction=this.settings.rtl?"left":"right"),this.settings.loop?this.op(this.drag.currentX,">",this.coordinates(this.minimum()))&&"right"===this.state.direction?this.drag.currentX-=(this.settings.center&&this.coordinates(0))-this.coordinates(this._items.length):this.op(this.drag.currentX,"<",this.coordinates(this.maximum()))&&"left"===this.state.direction&&(this.drag.currentX+=(this.settings.center&&this.coordinates(0))-this.coordinates(this._items.length)):(h=this.coordinates(this.settings.rtl?this.maximum():this.minimum()),i=this.coordinates(this.settings.rtl?this.minimum():this.maximum()),j=this.settings.pullDrag?this.drag.distance/5:0,this.drag.currentX=Math.max(Math.min(this.drag.currentX,h+j),i+j)),(this.drag.distance>8||this.drag.distance<-8)&&(c.preventDefault!==d?c.preventDefault():c.returnValue=!1,this.state.isSwiping=!0),this.drag.updatedX=this.drag.currentX,(this.drag.currentY>16||this.drag.currentY<-16)&&this.state.isSwiping===!1&&(this.state.isScrolling=!0,this.drag.updatedX=this.drag.start),this.animate(this.drag.updatedX)))},e.prototype.onDragEnd=function(b){var d,e,f;if(this.state.isTouch){if("mouseup"===b.type&&this.$stage.removeClass("owl-grab"),this.trigger("dragged"),this.drag.targetEl.removeAttribute("draggable"),this.state.isTouch=!1,this.state.isScrolling=!1,this.state.isSwiping=!1,0===this.drag.distance&&this.state.inMotion!==!0)return this.state.inMotion=!1,!1;this.drag.endTime=(new Date).getTime(),d=this.drag.endTime-this.drag.startTime,e=Math.abs(this.drag.distance),(e>3||d>300)&&this.removeClick(this.drag.targetEl),f=this.closest(this.drag.updatedX),this.speed(this.settings.dragEndSpeed||this.settings.smartSpeed),this.current(f),this.invalidate("position"),this.update(),this.settings.pullDrag||this.drag.updatedX!==this.coordinates(f)||this.transitionEnd(),this.drag.distance=0,a(c).off(".owl.dragEvents")}},e.prototype.removeClick=function(c){this.drag.targetEl=c,a(c).on("click.preventClick",this.e._preventClick),b.setTimeout(function(){a(c).off("click.preventClick")},300)},e.prototype.preventClick=function(b){b.preventDefault?b.preventDefault():b.returnValue=!1,b.stopPropagation&&b.stopPropagation(),a(b.target).off("click.preventClick")},e.prototype.getTransformProperty=function(){var a,c;return a=b.getComputedStyle(this.$stage.get(0),null).getPropertyValue(this.vendorName+"transform"),a=a.replace(/matrix(3d)?\(|\)/g,"").split(","),c=16===a.length,c!==!0?a[4]:a[12]},e.prototype.closest=function(b){var c=-1,d=30,e=this.width(),f=this.coordinates();return this.settings.freeDrag||a.each(f,a.proxy(function(a,g){return b>g-d&&g+d>b?c=a:this.op(b,"<",g)&&this.op(b,">",f[a+1]||g-e)&&(c="left"===this.state.direction?a+1:a),-1===c},this)),this.settings.loop||(this.op(b,">",f[this.minimum()])?c=b=this.minimum():this.op(b,"<",f[this.maximum()])&&(c=b=this.maximum())),c},e.prototype.animate=function(b){this.trigger("translate"),this.state.inMotion=this.speed()>0,this.support3d?this.$stage.css({transform:"translate3d("+b+"px,0px, 0px)",transition:this.speed()/1e3+"s"}):this.state.isTouch?this.$stage.css({left:b+"px"}):this.$stage.animate({left:b},this.speed()/1e3,this.settings.fallbackEasing,a.proxy(function(){this.state.inMotion&&this.transitionEnd()},this))},e.prototype.current=function(a){if(a===d)return this._current;if(0===this._items.length)return d;if(a=this.normalize(a),this._current!==a){var b=this.trigger("change",{property:{name:"position",value:a}});b.data!==d&&(a=this.normalize(b.data)),this._current=a,this.invalidate("position"),this.trigger("changed",{property:{name:"position",value:this._current}})}return this._current},e.prototype.invalidate=function(a){this._invalidated[a]=!0},e.prototype.reset=function(a){a=this.normalize(a),a!==d&&(this._speed=0,this._current=a,this.suppress(["translate","translated"]),this.animate(this.coordinates(a)),this.release(["translate","translated"]))},e.prototype.normalize=function(b,c){var e=c?this._items.length:this._items.length+this._clones.length;return!a.isNumeric(b)||1>e?d:b=this._clones.length?(b%e+e)%e:Math.max(this.minimum(c),Math.min(this.maximum(c),b))},e.prototype.relative=function(a){return a=this.normalize(a),a-=this._clones.length/2,this.normalize(a,!0)},e.prototype.maximum=function(a){var b,c,d,e=0,f=this.settings;if(a)return this._items.length-1;if(!f.loop&&f.center)b=this._items.length-1;else if(f.loop||f.center)if(f.loop||f.center)b=this._items.length+f.items;else{if(!f.autoWidth&&!f.merge)throw"Can not detect maximum absolute position.";for(revert=f.rtl?1:-1,c=this.$stage.width()-this.$element.width();(d=this.coordinates(e))&&!(d*revert>=c);)b=++e}else b=this._items.length-f.items;return b},e.prototype.minimum=function(a){return a?0:this._clones.length/2},e.prototype.items=function(a){return a===d?this._items.slice():(a=this.normalize(a,!0),this._items[a])},e.prototype.mergers=function(a){return a===d?this._mergers.slice():(a=this.normalize(a,!0),this._mergers[a])},e.prototype.clones=function(b){var c=this._clones.length/2,e=c+this._items.length,f=function(a){return a%2===0?e+a/2:c-(a+1)/2};return b===d?a.map(this._clones,function(a,b){return f(b)}):a.map(this._clones,function(a,c){return a===b?f(c):null})},e.prototype.speed=function(a){return a!==d&&(this._speed=a),this._speed},e.prototype.coordinates=function(b){var c=null;return b===d?a.map(this._coordinates,a.proxy(function(a,b){return this.coordinates(b)},this)):(this.settings.center?(c=this._coordinates[b],c+=(this.width()-c+(this._coordinates[b-1]||0))/2*(this.settings.rtl?-1:1)):c=this._coordinates[b-1]||0,c)},e.prototype.duration=function(a,b,c){return Math.min(Math.max(Math.abs(b-a),1),6)*Math.abs(c||this.settings.smartSpeed)},e.prototype.to=function(c,d){if(this.settings.loop){var e=c-this.relative(this.current()),f=this.current(),g=this.current(),h=this.current()+e,i=0>g-h?!0:!1,j=this._clones.length+this._items.length;h<this.settings.items&&i===!1?(f=g+this._items.length,this.reset(f)):h>=j-this.settings.items&&i===!0&&(f=g-this._items.length,this.reset(f)),b.clearTimeout(this.e._goToLoop),this.e._goToLoop=b.setTimeout(a.proxy(function(){this.speed(this.duration(this.current(),f+e,d)),this.current(f+e),this.update()},this),30)}else this.speed(this.duration(this.current(),c,d)),this.current(c),this.update()},e.prototype.next=function(a){a=a||!1,this.to(this.relative(this.current())+1,a)},e.prototype.prev=function(a){a=a||!1,this.to(this.relative(this.current())-1,a)},e.prototype.transitionEnd=function(a){return a!==d&&(a.stopPropagation(),(a.target||a.srcElement||a.originalTarget)!==this.$stage.get(0))?!1:(this.state.inMotion=!1,void this.trigger("translated"))},e.prototype.viewport=function(){var d;if(this.options.responsiveBaseElement!==b)d=a(this.options.responsiveBaseElement).width();else if(b.innerWidth)d=b.innerWidth;else{if(!c.documentElement||!c.documentElement.clientWidth)throw"Can not detect viewport width.";d=c.documentElement.clientWidth}return d},e.prototype.replace=function(b){this.$stage.empty(),this._items=[],b&&(b=b instanceof jQuery?b:a(b)),this.settings.nestedItemSelector&&(b=b.find("."+this.settings.nestedItemSelector)),b.filter(function(){return 1===this.nodeType}).each(a.proxy(function(a,b){b=this.prepare(b),this.$stage.append(b),this._items.push(b),this._mergers.push(1*b.find("[data-merge]").andSelf("[data-merge]").attr("data-merge")||1)},this)),this.reset(a.isNumeric(this.settings.startPosition)?this.settings.startPosition:0),this.invalidate("items")},e.prototype.add=function(a,b){b=b===d?this._items.length:this.normalize(b,!0),this.trigger("add",{content:a,position:b}),0===this._items.length||b===this._items.length?(this.$stage.append(a),this._items.push(a),this._mergers.push(1*a.find("[data-merge]").andSelf("[data-merge]").attr("data-merge")||1)):(this._items[b].before(a),this._items.splice(b,0,a),this._mergers.splice(b,0,1*a.find("[data-merge]").andSelf("[data-merge]").attr("data-merge")||1)),this.invalidate("items"),this.trigger("added",{content:a,position:b})},e.prototype.remove=function(a){a=this.normalize(a,!0),a!==d&&(this.trigger("remove",{content:this._items[a],position:a}),this._items[a].remove(),this._items.splice(a,1),this._mergers.splice(a,1),this.invalidate("items"),this.trigger("removed",{content:null,position:a}))},e.prototype.addTriggerableEvents=function(){var b=a.proxy(function(b,c){return a.proxy(function(a){a.relatedTarget!==this&&(this.suppress([c]),b.apply(this,[].slice.call(arguments,1)),this.release([c]))},this)},this);a.each({next:this.next,prev:this.prev,to:this.to,destroy:this.destroy,refresh:this.refresh,replace:this.replace,add:this.add,remove:this.remove},a.proxy(function(a,c){this.$element.on(a+".owl.carousel",b(c,a+".owl.carousel"))},this))},e.prototype.watchVisibility=function(){function c(a){return a.offsetWidth>0&&a.offsetHeight>0}function d(){c(this.$element.get(0))&&(this.$element.removeClass("owl-hidden"),this.refresh(),b.clearInterval(this.e._checkVisibile))}c(this.$element.get(0))||(this.$element.addClass("owl-hidden"),b.clearInterval(this.e._checkVisibile),this.e._checkVisibile=b.setInterval(a.proxy(d,this),500))},e.prototype.preloadAutoWidthImages=function(b){var c,d,e,f;c=0,d=this,b.each(function(g,h){e=a(h),f=new Image,f.onload=function(){c++,e.attr("src",f.src),e.css("opacity",1),c>=b.length&&(d.state.imagesLoaded=!0,d.initialize())},f.src=e.attr("src")||e.attr("data-src")||e.attr("data-src-retina")})},e.prototype.destroy=function(){this.$element.hasClass(this.settings.themeClass)&&this.$element.removeClass(this.settings.themeClass),this.settings.responsive!==!1&&a(b).off("resize.owl.carousel"),this.transitionEndVendor&&this.off(this.$stage.get(0),this.transitionEndVendor,this.e._transitionEnd);for(var d in this._plugins)this._plugins[d].destroy();(this.settings.mouseDrag||this.settings.touchDrag)&&(this.$stage.off("mousedown touchstart touchcancel"),a(c).off(".owl.dragEvents"),this.$stage.get(0).onselectstart=function(){},this.$stage.off("dragstart",function(){return!1})),this.$element.off(".owl"),this.$stage.children(".cloned").remove(),this.e=null,this.$element.removeData("owlCarousel"),this.$stage.children().contents().unwrap(),this.$stage.children().unwrap(),this.$stage.unwrap()},e.prototype.op=function(a,b,c){var d=this.settings.rtl;switch(b){case"<":return d?a>c:c>a;case">":return d?c>a:a>c;case">=":return d?c>=a:a>=c;case"<=":return d?a>=c:c>=a}},e.prototype.on=function(a,b,c,d){a.addEventListener?a.addEventListener(b,c,d):a.attachEvent&&a.attachEvent("on"+b,c)},e.prototype.off=function(a,b,c,d){a.removeEventListener?a.removeEventListener(b,c,d):a.detachEvent&&a.detachEvent("on"+b,c)},e.prototype.trigger=function(b,c,d){var e={item:{count:this._items.length,index:this.current()}},f=a.camelCase(a.grep(["on",b,d],function(a){return a}).join("-").toLowerCase()),g=a.Event([b,"owl",d||"carousel"].join(".").toLowerCase(),a.extend({relatedTarget:this},e,c));return this._supress[b]||(a.each(this._plugins,function(a,b){b.onTrigger&&b.onTrigger(g)}),this.$element.trigger(g),this.settings&&"function"==typeof this.settings[f]&&this.settings[f].apply(this,g)),g},e.prototype.suppress=function(b){a.each(b,a.proxy(function(a,b){this._supress[b]=!0},this))},e.prototype.release=function(b){a.each(b,a.proxy(function(a,b){delete this._supress[b]},this))},e.prototype.browserSupport=function(){if(this.support3d=j(),this.support3d){this.transformVendor=i();var a=["transitionend","webkitTransitionEnd","transitionend","oTransitionEnd"];this.transitionEndVendor=a[h()],this.vendorName=this.transformVendor.replace(/Transform/i,""),this.vendorName=""!==this.vendorName?"-"+this.vendorName.toLowerCase()+"-":""}this.state.orientation=b.orientation},a.fn.owlCarousel=function(b){return this.each(function(){a(this).data("owlCarousel")||a(this).data("owlCarousel",new e(this,b))})},a.fn.owlCarousel.Constructor=e}(window.Zepto||window.jQuery,window,document),function(a,b){var c=function(b){this._core=b,this._loaded=[],this._handlers={"initialized.owl.carousel change.owl.carousel":a.proxy(function(b){if(b.namespace&&this._core.settings&&this._core.settings.lazyLoad&&(b.property&&"position"==b.property.name||"initialized"==b.type))for(var c=this._core.settings,d=c.center&&Math.ceil(c.items/2)||c.items,e=c.center&&-1*d||0,f=(b.property&&b.property.value||this._core.current())+e,g=this._core.clones().length,h=a.proxy(function(a,b){this.load(b)},this);e++<d;)this.load(g/2+this._core.relative(f)),g&&a.each(this._core.clones(this._core.relative(f++)),h)},this)},this._core.options=a.extend({},c.Defaults,this._core.options),this._core.$element.on(this._handlers)};c.Defaults={lazyLoad:!1},c.prototype.load=function(c){var d=this._core.$stage.children().eq(c),e=d&&d.find(".owl-lazy");!e||a.inArray(d.get(0),this._loaded)>-1||(e.each(a.proxy(function(c,d){var e,f=a(d),g=b.devicePixelRatio>1&&f.attr("data-src-retina")||f.attr("data-src");this._core.trigger("load",{element:f,url:g},"lazy"),f.is("img")?f.one("load.owl.lazy",a.proxy(function(){f.css("opacity",1),this._core.trigger("loaded",{element:f,url:g},"lazy")},this)).attr("src",g):(e=new Image,e.onload=a.proxy(function(){f.css({"background-image":"url("+g+")",opacity:"1"}),this._core.trigger("loaded",{element:f,url:g},"lazy")},this),e.src=g)},this)),this._loaded.push(d.get(0)))},c.prototype.destroy=function(){var a,b;for(a in this.handlers)this._core.$element.off(a,this.handlers[a]);for(b in Object.getOwnPropertyNames(this))"function"!=typeof this[b]&&(this[b]=null)},a.fn.owlCarousel.Constructor.Plugins.Lazy=c}(window.Zepto||window.jQuery,window,document),function(a){var b=function(c){this._core=c,this._handlers={"initialized.owl.carousel":a.proxy(function(){this._core.settings.autoHeight&&this.update()},this),"changed.owl.carousel":a.proxy(function(a){this._core.settings.autoHeight&&"position"==a.property.name&&this.update()},this),"loaded.owl.lazy":a.proxy(function(a){this._core.settings.autoHeight&&a.element.closest("."+this._core.settings.itemClass)===this._core.$stage.children().eq(this._core.current())&&this.update()},this)},this._core.options=a.extend({},b.Defaults,this._core.options),this._core.$element.on(this._handlers)};b.Defaults={autoHeight:!1,autoHeightClass:"owl-height"},b.prototype.update=function(){this._core.$stage.parent().height(this._core.$stage.children().eq(this._core.current()).height()).addClass(this._core.settings.autoHeightClass)},b.prototype.destroy=function(){var a,b;for(a in this._handlers)this._core.$element.off(a,this._handlers[a]);for(b in Object.getOwnPropertyNames(this))"function"!=typeof this[b]&&(this[b]=null)},a.fn.owlCarousel.Constructor.Plugins.AutoHeight=b}(window.Zepto||window.jQuery,window,document),function(a,b,c){var d=function(b){this._core=b,this._videos={},this._playing=null,this._fullscreen=!1,this._handlers={"resize.owl.carousel":a.proxy(function(a){this._core.settings.video&&!this.isInFullScreen()&&a.preventDefault()},this),"refresh.owl.carousel changed.owl.carousel":a.proxy(function(){this._playing&&this.stop()},this),"prepared.owl.carousel":a.proxy(function(b){var c=a(b.content).find(".owl-video");c.length&&(c.css("display","none"),this.fetch(c,a(b.content)))},this)},this._core.options=a.extend({},d.Defaults,this._core.options),this._core.$element.on(this._handlers),this._core.$element.on("click.owl.video",".owl-video-play-icon",a.proxy(function(a){this.play(a)},this))};d.Defaults={video:!1,videoHeight:!1,videoWidth:!1},d.prototype.fetch=function(a,b){var c=a.attr("data-vimeo-id")?"vimeo":"youtube",d=a.attr("data-vimeo-id")||a.attr("data-youtube-id"),e=a.attr("data-width")||this._core.settings.videoWidth,f=a.attr("data-height")||this._core.settings.videoHeight,g=a.attr("href");if(!g)throw new Error("Missing video URL.");if(d=g.match(/(http:|https:|)\/\/(player.|www.)?(vimeo\.com|youtu(be\.com|\.be|be\.googleapis\.com))\/(video\/|embed\/|watch\?v=|v\/)?([A-Za-z0-9._%-]*)(\&\S+)?/),d[3].indexOf("youtu")>-1)c="youtube";else{if(!(d[3].indexOf("vimeo")>-1))throw new Error("Video URL not supported.");c="vimeo"}d=d[6],this._videos[g]={type:c,id:d,width:e,height:f},b.attr("data-video",g),this.thumbnail(a,this._videos[g])},d.prototype.thumbnail=function(b,c){var d,e,f,g=c.width&&c.height?'style="width:'+c.width+"px;height:"+c.height+'px;"':"",h=b.find("img"),i="src",j="",k=this._core.settings,l=function(a){e='<div class="owl-video-play-icon"></div>',d=k.lazyLoad?'<div class="owl-video-tn '+j+'" '+i+'="'+a+'"></div>':'<div class="owl-video-tn" style="opacity:1;background-image:url('+a+')"></div>',b.after(d),b.after(e)};return b.wrap('<div class="owl-video-wrapper"'+g+"></div>"),this._core.settings.lazyLoad&&(i="data-src",j="owl-lazy"),h.length?(l(h.attr(i)),h.remove(),!1):void("youtube"===c.type?(f="http://img.youtube.com/vi/"+c.id+"/hqdefault.jpg",l(f)):"vimeo"===c.type&&a.ajax({type:"GET",url:"http://vimeo.com/api/v2/video/"+c.id+".json",jsonp:"callback",dataType:"jsonp",success:function(a){f=a[0].thumbnail_large,l(f)}}))},d.prototype.stop=function(){this._core.trigger("stop",null,"video"),this._playing.find(".owl-video-frame").remove(),this._playing.removeClass("owl-video-playing"),this._playing=null},d.prototype.play=function(b){this._core.trigger("play",null,"video"),this._playing&&this.stop();var c,d,e=a(b.target||b.srcElement),f=e.closest("."+this._core.settings.itemClass),g=this._videos[f.attr("data-video")],h=g.width||"100%",i=g.height||this._core.$stage.height();"youtube"===g.type?c='<iframe width="'+h+'" height="'+i+'" src="http://www.youtube.com/embed/'+g.id+"?autoplay=1&v="+g.id+'" frameborder="0" allowfullscreen></iframe>':"vimeo"===g.type&&(c='<iframe src="http://player.vimeo.com/video/'+g.id+'?autoplay=1" width="'+h+'" height="'+i+'" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe>'),f.addClass("owl-video-playing"),this._playing=f,d=a('<div style="height:'+i+"px; width:"+h+'px" class="owl-video-frame">'+c+"</div>"),e.after(d)},d.prototype.isInFullScreen=function(){var d=c.fullscreenElement||c.mozFullScreenElement||c.webkitFullscreenElement;return d&&a(d).parent().hasClass("owl-video-frame")&&(this._core.speed(0),this._fullscreen=!0),d&&this._fullscreen&&this._playing?!1:this._fullscreen?(this._fullscreen=!1,!1):this._playing&&this._core.state.orientation!==b.orientation?(this._core.state.orientation=b.orientation,!1):!0},d.prototype.destroy=function(){var a,b;this._core.$element.off("click.owl.video");for(a in this._handlers)this._core.$element.off(a,this._handlers[a]);for(b in Object.getOwnPropertyNames(this))"function"!=typeof this[b]&&(this[b]=null)},a.fn.owlCarousel.Constructor.Plugins.Video=d}(window.Zepto||window.jQuery,window,document),function(a,b,c,d){var e=function(b){this.core=b,this.core.options=a.extend({},e.Defaults,this.core.options),this.swapping=!0,this.previous=d,this.next=d,this.handlers={"change.owl.carousel":a.proxy(function(a){"position"==a.property.name&&(this.previous=this.core.current(),this.next=a.property.value)},this),"drag.owl.carousel dragged.owl.carousel translated.owl.carousel":a.proxy(function(a){this.swapping="translated"==a.type},this),"translate.owl.carousel":a.proxy(function(){this.swapping&&(this.core.options.animateOut||this.core.options.animateIn)&&this.swap()},this)},this.core.$element.on(this.handlers)};e.Defaults={animateOut:!1,animateIn:!1},e.prototype.swap=function(){if(1===this.core.settings.items&&this.core.support3d){this.core.speed(0);var b,c=a.proxy(this.clear,this),d=this.core.$stage.children().eq(this.previous),e=this.core.$stage.children().eq(this.next),f=this.core.settings.animateIn,g=this.core.settings.animateOut;this.core.current()!==this.previous&&(g&&(b=this.core.coordinates(this.previous)-this.core.coordinates(this.next),d.css({left:b+"px"}).addClass("animated owl-animated-out").addClass(g).one("webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend",c)),f&&e.addClass("animated owl-animated-in").addClass(f).one("webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend",c))}},e.prototype.clear=function(b){a(b.target).css({left:""}).removeClass("animated owl-animated-out owl-animated-in").removeClass(this.core.settings.animateIn).removeClass(this.core.settings.animateOut),this.core.transitionEnd()},e.prototype.destroy=function(){var a,b;for(a in this.handlers)this.core.$element.off(a,this.handlers[a]);for(b in Object.getOwnPropertyNames(this))"function"!=typeof this[b]&&(this[b]=null)},a.fn.owlCarousel.Constructor.Plugins.Animate=e}(window.Zepto||window.jQuery,window,document),function(a,b,c){var d=function(b){this.core=b,this.core.options=a.extend({},d.Defaults,this.core.options),this.handlers={"translated.owl.carousel refreshed.owl.carousel":a.proxy(function(){this.autoplay()
},this),"play.owl.autoplay":a.proxy(function(a,b,c){this.play(b,c)},this),"stop.owl.autoplay":a.proxy(function(){this.stop()},this),"mouseover.owl.autoplay":a.proxy(function(){this.core.settings.autoplayHoverPause&&this.pause()},this),"mouseleave.owl.autoplay":a.proxy(function(){this.core.settings.autoplayHoverPause&&this.autoplay()},this)},this.core.$element.on(this.handlers)};d.Defaults={autoplay:!1,autoplayTimeout:5e3,autoplayHoverPause:!1,autoplaySpeed:!1},d.prototype.autoplay=function(){this.core.settings.autoplay&&!this.core.state.videoPlay?(b.clearInterval(this.interval),this.interval=b.setInterval(a.proxy(function(){this.play()},this),this.core.settings.autoplayTimeout)):b.clearInterval(this.interval)},d.prototype.play=function(){return c.hidden===!0||this.core.state.isTouch||this.core.state.isScrolling||this.core.state.isSwiping||this.core.state.inMotion?void 0:this.core.settings.autoplay===!1?void b.clearInterval(this.interval):void this.core.next(this.core.settings.autoplaySpeed)},d.prototype.stop=function(){b.clearInterval(this.interval)},d.prototype.pause=function(){b.clearInterval(this.interval)},d.prototype.destroy=function(){var a,c;b.clearInterval(this.interval);for(a in this.handlers)this.core.$element.off(a,this.handlers[a]);for(c in Object.getOwnPropertyNames(this))"function"!=typeof this[c]&&(this[c]=null)},a.fn.owlCarousel.Constructor.Plugins.autoplay=d}(window.Zepto||window.jQuery,window,document),function(a){"use strict";var b=function(c){this._core=c,this._initialized=!1,this._pages=[],this._controls={},this._templates=[],this.$element=this._core.$element,this._overrides={next:this._core.next,prev:this._core.prev,to:this._core.to},this._handlers={"prepared.owl.carousel":a.proxy(function(b){this._core.settings.dotsData&&this._templates.push(a(b.content).find("[data-dot]").andSelf("[data-dot]").attr("data-dot"))},this),"add.owl.carousel":a.proxy(function(b){this._core.settings.dotsData&&this._templates.splice(b.position,0,a(b.content).find("[data-dot]").andSelf("[data-dot]").attr("data-dot"))},this),"remove.owl.carousel prepared.owl.carousel":a.proxy(function(a){this._core.settings.dotsData&&this._templates.splice(a.position,1)},this),"change.owl.carousel":a.proxy(function(a){if("position"==a.property.name&&!this._core.state.revert&&!this._core.settings.loop&&this._core.settings.navRewind){var b=this._core.current(),c=this._core.maximum(),d=this._core.minimum();a.data=a.property.value>c?b>=c?d:c:a.property.value<d?c:a.property.value}},this),"changed.owl.carousel":a.proxy(function(a){"position"==a.property.name&&this.draw()},this),"refreshed.owl.carousel":a.proxy(function(){this._initialized||(this.initialize(),this._initialized=!0),this._core.trigger("refresh",null,"navigation"),this.update(),this.draw(),this._core.trigger("refreshed",null,"navigation")},this)},this._core.options=a.extend({},b.Defaults,this._core.options),this.$element.on(this._handlers)};b.Defaults={nav:!1,navRewind:!0,navText:["prev","next"],navSpeed:!1,navElement:"div",navContainer:!1,navContainerClass:"owl-nav",navClass:["owl-prev","owl-next"],slideBy:1,dotClass:"owl-dot",dotsClass:"owl-dots",dots:!0,dotsEach:!1,dotData:!1,dotsSpeed:!1,dotsContainer:!1,controlsClass:"owl-controls"},b.prototype.initialize=function(){var b,c,d=this._core.settings;d.dotsData||(this._templates=[a("<div>").addClass(d.dotClass).append(a("<span>")).prop("outerHTML")]),d.navContainer&&d.dotsContainer||(this._controls.$container=a("<div>").addClass(d.controlsClass).appendTo(this.$element)),this._controls.$indicators=d.dotsContainer?a(d.dotsContainer):a("<div>").hide().addClass(d.dotsClass).appendTo(this._controls.$container),this._controls.$indicators.on("click","div",a.proxy(function(b){var c=a(b.target).parent().is(this._controls.$indicators)?a(b.target).index():a(b.target).parent().index();b.preventDefault(),this.to(c,d.dotsSpeed)},this)),b=d.navContainer?a(d.navContainer):a("<div>").addClass(d.navContainerClass).prependTo(this._controls.$container),this._controls.$next=a("<"+d.navElement+">"),this._controls.$previous=this._controls.$next.clone(),this._controls.$previous.addClass(d.navClass[0]).html(d.navText[0]).hide().prependTo(b).on("click",a.proxy(function(){this.prev(d.navSpeed)},this)),this._controls.$next.addClass(d.navClass[1]).html(d.navText[1]).hide().appendTo(b).on("click",a.proxy(function(){this.next(d.navSpeed)},this));for(c in this._overrides)this._core[c]=a.proxy(this[c],this)},b.prototype.destroy=function(){var a,b,c,d;for(a in this._handlers)this.$element.off(a,this._handlers[a]);for(b in this._controls)this._controls[b].remove();for(d in this.overides)this._core[d]=this._overrides[d];for(c in Object.getOwnPropertyNames(this))"function"!=typeof this[c]&&(this[c]=null)},b.prototype.update=function(){var a,b,c,d=this._core.settings,e=this._core.clones().length/2,f=e+this._core.items().length,g=d.center||d.autoWidth||d.dotData?1:d.dotsEach||d.items;if("page"!==d.slideBy&&(d.slideBy=Math.min(d.slideBy,d.items)),d.dots||"page"==d.slideBy)for(this._pages=[],a=e,b=0,c=0;f>a;a++)(b>=g||0===b)&&(this._pages.push({start:a-e,end:a-e+g-1}),b=0,++c),b+=this._core.mergers(this._core.relative(a))},b.prototype.draw=function(){var b,c,d="",e=this._core.settings,f=(this._core.$stage.children(),this._core.relative(this._core.current()));if(!e.nav||e.loop||e.navRewind||(this._controls.$previous.toggleClass("disabled",0>=f),this._controls.$next.toggleClass("disabled",f>=this._core.maximum())),this._controls.$previous.toggle(e.nav),this._controls.$next.toggle(e.nav),e.dots){if(b=this._pages.length-this._controls.$indicators.children().length,e.dotData&&0!==b){for(c=0;c<this._controls.$indicators.children().length;c++)d+=this._templates[this._core.relative(c)];this._controls.$indicators.html(d)}else b>0?(d=new Array(b+1).join(this._templates[0]),this._controls.$indicators.append(d)):0>b&&this._controls.$indicators.children().slice(b).remove();this._controls.$indicators.find(".active").removeClass("active"),this._controls.$indicators.children().eq(a.inArray(this.current(),this._pages)).addClass("active")}this._controls.$indicators.toggle(e.dots)},b.prototype.onTrigger=function(b){var c=this._core.settings;b.page={index:a.inArray(this.current(),this._pages),count:this._pages.length,size:c&&(c.center||c.autoWidth||c.dotData?1:c.dotsEach||c.items)}},b.prototype.current=function(){var b=this._core.relative(this._core.current());return a.grep(this._pages,function(a){return a.start<=b&&a.end>=b}).pop()},b.prototype.getPosition=function(b){var c,d,e=this._core.settings;return"page"==e.slideBy?(c=a.inArray(this.current(),this._pages),d=this._pages.length,b?++c:--c,c=this._pages[(c%d+d)%d].start):(c=this._core.relative(this._core.current()),d=this._core.items().length,b?c+=e.slideBy:c-=e.slideBy),c},b.prototype.next=function(b){a.proxy(this._overrides.to,this._core)(this.getPosition(!0),b)},b.prototype.prev=function(b){a.proxy(this._overrides.to,this._core)(this.getPosition(!1),b)},b.prototype.to=function(b,c,d){var e;d?a.proxy(this._overrides.to,this._core)(b,c):(e=this._pages.length,a.proxy(this._overrides.to,this._core)(this._pages[(b%e+e)%e].start,c))},a.fn.owlCarousel.Constructor.Plugins.Navigation=b}(window.Zepto||window.jQuery,window,document),function(a,b){"use strict";var c=function(d){this._core=d,this._hashes={},this.$element=this._core.$element,this._handlers={"initialized.owl.carousel":a.proxy(function(){"URLHash"==this._core.settings.startPosition&&a(b).trigger("hashchange.owl.navigation")},this),"prepared.owl.carousel":a.proxy(function(b){var c=a(b.content).find("[data-hash]").andSelf("[data-hash]").attr("data-hash");this._hashes[c]=b.content},this)},this._core.options=a.extend({},c.Defaults,this._core.options),this.$element.on(this._handlers),a(b).on("hashchange.owl.navigation",a.proxy(function(){var a=b.location.hash.substring(1),c=this._core.$stage.children(),d=this._hashes[a]&&c.index(this._hashes[a])||0;return a?void this._core.to(d,!1,!0):!1},this))};c.Defaults={URLhashListener:!1},c.prototype.destroy=function(){var c,d;a(b).off("hashchange.owl.navigation");for(c in this._handlers)this._core.$element.off(c,this._handlers[c]);for(d in Object.getOwnPropertyNames(this))"function"!=typeof this[d]&&(this[d]=null)},a.fn.owlCarousel.Constructor.Plugins.Hash=c}(window.Zepto||window.jQuery,window,document);
!function(a,b){"function"==typeof define&&define.amd?
// AMD. Register as an anonymous module unless amdModuleId is set
define([],function(){return a.svg4everybody=b()}):"object"==typeof exports?module.exports=b():a.svg4everybody=b()}(this,function(){/*! svg4everybody v2.0.3 | github.com/jonathantneal/svg4everybody */
function a(a,b){
// if the target exists
if(b){
// create a document fragment to hold the contents of the target
var c=document.createDocumentFragment(),d=!a.getAttribute("viewBox")&&b.getAttribute("viewBox");
// conditionally set the viewBox on the svg
d&&a.setAttribute("viewBox",d);
// copy the contents of the clone into the fragment
for(
// clone the target
var e=b.cloneNode(!0);e.childNodes.length;)c.appendChild(e.firstChild);
// append the fragment into the svg
a.appendChild(c)}}function b(b){
// listen to changes in the request
b.onreadystatechange=function(){
// if the request is ready
if(4===b.readyState){
// get the cached html document
var c=b._cachedDocument;
// ensure the cached html document based on the xhr response
c||(c=b._cachedDocument=document.implementation.createHTMLDocument(""),c.body.innerHTML=b.responseText,b._cachedTarget={}),
// clear the xhr embeds list and embed each item
b._embeds.splice(0).map(function(d){
// get the cached target
var e=b._cachedTarget[d.id];
// ensure the cached target
e||(e=b._cachedTarget[d.id]=c.getElementById(d.id)),
// embed the target into the svg
a(d.svg,e)})}},
// test the ready state change immediately
b.onreadystatechange()}function c(c){function d(){
// while the index exists in the live <use> collection
for(
// get the cached <use> index
var c=0;c<l.length;){
// get the current <use>
var g=l[c],h=g.parentNode;if(h&&/svg/i.test(h.nodeName)){var i=g.getAttribute("xlink:href");if(e&&(!f.validate||f.validate(i,h,g))){
// remove the <use> element
h.removeChild(g);
// parse the src and get the url and id
var m=i.split("#"),n=m.shift(),o=m.join("#");
// if the link is external
if(n.length){
// get the cached xhr request
var p=j[n];
// ensure the xhr request exists
p||(p=j[n]=new XMLHttpRequest,p.open("GET",n),p.send(),p._embeds=[]),
// add the svg and id as an item to the xhr embeds list
p._embeds.push({svg:h,id:o}),
// prepare the xhr ready state change event
b(p)}else
// embed the local id into the svg
a(h,document.getElementById(o))}}else
// increase the index when the previous value was not "valid"
++c}
// continue the interval
k(d,67)}var e,f=Object(c),g=/\bTrident\/[567]\b|\bMSIE (?:9|10)\.0\b/,h=/\bAppleWebKit\/(\d+)\b/,i=/\bEdge\/12\.(\d+)\b/;e="polyfill"in f?f.polyfill:g.test(navigator.userAgent)||(navigator.userAgent.match(i)||[])[1]<10547||(navigator.userAgent.match(h)||[])[1]<537;
// create xhr requests object
var j={},k=window.requestAnimationFrame||setTimeout,l=document.getElementsByTagName("use");
// conditionally start the interval if the polyfill is active
e&&d()}return c});
(function(){
    var onAnimationEnd = 'animationend webkitAnimationEnd oAnimationEnd MSAnimationEnd';

    window.onunload = function(){
        $('.click-circle').remove();
    }; 
  
    $('body').on('click', 'a, button, input, select, textarea, label, .js-click-feedback', function(e){
        var clickX = e.clientX - 10;
        var clickY = e.clientY - 10;
        var clickCircle = '<div class="click-circle" style="top:'+clickY+'px; left:'+clickX+'px;"></div>'
        $('body').append(clickCircle);
        $('.click-circle').addClass('scale');
        $('.click-circle').on(onAnimationEnd, function (e) {
            $(this).remove();
            $(this).off(e);
        });
    });
})();
(function(){
    //defer background image loading
    var deferBackgroundImageLoading = function() {
        var imgBackgroundDefer = $('.js-background-image');
        var windowWidth = window.innerWidth;
        
        imgBackgroundDefer.each(function(){
            var $this = $(this);
            var imgBackgroundSrc = $this.attr('data-background-image');
            var imgDeferScreenSize = Number($this.attr('data-load-on'));
            
            var loadImage = function(){
                $('<img/>').attr('src', imgBackgroundSrc).load(function() {
                    $(this).remove();
                    $this
                    .css({'background-image': 'url('+imgBackgroundSrc+')'})
                    .addClass('image-loaded');
                });                
            }
            
            if (!isNaN(imgDeferScreenSize)){
                if(imgDeferScreenSize < windowWidth){
                    loadImage();
                }
            }else{
                loadImage();
            }
        });
    };
    
    $(window).on('load orientationchange', deferBackgroundImageLoading);
    
    var resizeTimer;
    $(window).on('resize', function (e) {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function () {
            deferBackgroundImageLoading();
        }, 250);
    });
})();
(function(){
    var textInput = $(".js-placeholder-up");

    textInput.each(function() {
        var $this = $(this);
        if($this.val().length > 0){
            $this.parent().find('.js-placeholder').addClass('focus');
        };
    });

    textInput.on('focus', function(){
        $(this).parent().find('.js-placeholder').addClass('focus');
    });
    textInput.on('blur', function(){
        textInput.each(function(){
            var $this = $(this);
            var textInputPlaceholder = $this.parent().find('.js-placeholder');
            if($this.val().length === 0){
                textInputPlaceholder.removeClass('focus');
            }else{
                textInputPlaceholder.addClass('focus');
            }
        });
    });
})();
$('.js-prevent-scroll').bind('mousewheel DOMMouseScroll', function (e) {
    if ($(this)[0].scrollHeight !== $(this).outerHeight()) {
        var e0 = e.originalEvent,
            delta = e0.wheelDelta || -e0.detail;

        this.scrollTop += (delta < 0 ? 1 : -1) * 30;
        e.preventDefault();
    }
});
(function(){
    //menu
    $('body').on('click', '.js-burger', function() {        
        $('.mobile-nav').toggleClass('active');
        $(this).toggleClass('active');
    });

    $('body').on('click', '.main-nav__item', function() {
        $('.mobile-nav').removeClass('active');
        $('.js-burger').removeClass('active');
    });
    
    //close opened stuff
    $(document).on('click', function(e) {
        //close mobile-nav
        if (!$(e.target).closest('.mobile-nav, .js-burger').length) {
            $('.mobile-nav').removeClass('active');
            $('.js-burger').removeClass('active');
        }
    });
})();
(function(){
    var slider = $('.js-calendar-slider');
    var slideTo = slider.attr('data-slide-to');

    slider.owlCarousel({
        items:1,
        navText:[$("#slider-button-left").html(),$("#slider-button-right").html()],
        mouseDrag:false,
        responsive : {
            0 : {
                nav:false
            },
            480 : {
                nav:true
            }
        }
    });
    
    slider.trigger('to.owl.carousel', [slideTo]);

    var loadSliderImages = function(containingObject){
        var sliderImage = containingObject.find('.js-calendar-slider-image');
        var sliderImageSrc = sliderImage.attr('data-calendar-slider-img');
        var sliderImageLoadOn = Number(sliderImage.attr('data-load-on'));
        var windowWidth = window.innerWidth;

        if(sliderImageLoadOn < windowWidth){
            sliderImage.attr('src', sliderImageSrc);
            sliderImage.removeAttr('data-calendar-slider-img');
        }
    }

    var openCloseAccordeon = function(accordeonHead){
        var accordeonBody = accordeonHead.next();

        if(!accordeonHead.hasClass('active')){
            $('.owl-item.active .js-accordeon-head').removeClass('active');
            $('.owl-item.active .accordeon-body').removeClass('active');
            accordeonHead.addClass('active');
            accordeonBody.addClass('active');
            loadSliderImages(accordeonBody);
        }
    }

    $(document).on('click', '.js-open-accordeon', function(e){
        var $this = $(this);

        if($this.hasClass('js-accordeon-head')){
            openCloseAccordeon($this);
        }else{
            openCloseAccordeon($this.closest('.js-accordeon-head'));
        }

    });

    var eventLink = $('.js-calendar-slider-link');
    var setEventLink = function(){
        var windowWidth = window.innerWidth;

        if(windowWidth >= 880){
            eventLink.removeAttr('href');
        }else{
            eventLink.each(function(){
                var $this = $(this);
                $this.attr('href', $this.attr('data-href'));
            });
        }
    }


    $(window).on('load orientationchange', setEventLink);
    $(window).on('load', function(){
        loadSliderImages($('.calendar-slider__slide').find('.calendar-slider__body:eq(0)'));
    });

    var resizeTimer;
    $(window).on('resize', function (e) {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function () {
            setEventLink();
            loadSliderImages($('.calendar-slider__slide').find('.calendar-slider__body:eq(0)'));
        }, 250);
    });
})();

(function () {
    var dragBar = $('.js-drag-bar'); 
    var dragHandle = $('.js-drag-handle');
    var dragContainer = $('.js-drag-container');
    var dragContent = $('.js-drag-content');
    
    var dragFlag = false;
    var contentDragFlag = false;
    var handleLastPosition = 0;
    var scrollLastPosition = 0;
    var handleDifference;
    
    var pointerStartPosition;
    var scrollStartPosition;
    
    var pointerPosition = function(e){
        var clientX;
        if((e.originalEvent.clientX)){
            clientX = e.originalEvent.clientX;
        }else if(e.originalEvent.targetTouches){
            clientX = e.originalEvent.targetTouches[0].clientX;
        }
        return clientX;
    };
    
    var relativeTo = function(numberOne, numberTow){
        return numberTow * 100 / numberOne; 
    }
    var absoluteTo = function(precentage, numberOne){
        return precentage * numberOne / 100; 
    }
    
    var setDragHandleWidth = function(){
        var dragContentWidth = dragContent.width();
        var dragContainerWidth = dragContainer.width();
        if(dragContentWidth > dragContainerWidth){
            dragHandle.css({width:relativeTo(dragContentWidth, dragContainerWidth)+'%'});
        }else{
            dragHandle.css({width:'100%'});
        }
        
    }
    
    var updateHandlePosition = function(e, pointerStartPosition){
        var handlePosition;
        var handleDifference = dragBar.width() - dragHandle.width();
        var pointerDelta = pointerPosition(e) - pointerStartPosition;
        
        if(pointerDelta <= -handleLastPosition){
            handlePosition = 0;
        }else if(pointerDelta >= handleDifference - handleLastPosition){
            handlePosition = handleDifference;
        }else{
            handlePosition = handleLastPosition + pointerDelta;
        }
        
        return relativeTo(dragBar.width(), handlePosition);
    }
    
    var updateScrollPosition = function(e, scrollStartPosition){
        var scrollPosition;
        var contentDifference = dragContent.width() - dragContainer.width();
        var scrollDelta = scrollStartPosition - pointerPosition(e);
        
        if(scrollDelta <= -scrollLastPosition || contentDifference < 0){
            scrollPosition = 0;
        }else if(scrollDelta >= contentDifference - scrollLastPosition){
            scrollPosition = contentDifference;
        }else{
            scrollPosition = scrollLastPosition + scrollDelta;
        }
        return scrollPosition;
    }
        
    dragContainer.on('mousedown touchstart', function (e) {
        contentDragFlag = true;
        scrollStartPosition = pointerPosition(e);
    });
    
    dragHandle.on('mousedown touchstart', function(e){
        dragFlag = true;
        pointerStartPosition = pointerPosition(e);
        
    });
    
    $(window).on('mousemove touchmove', function(e){
        //dragContainer move
        if(contentDragFlag == true){

            var setScrollPosition = updateScrollPosition(e, scrollStartPosition);
            
            dragContainer.scrollLeft(setScrollPosition);
            dragHandle.css({left:relativeTo(dragContent.width(), setScrollPosition)+'%'});
        }
        
        //dragBar move
        if(dragFlag == true){

            var setHandlePosition = updateHandlePosition(e, pointerStartPosition);
            
            dragHandle.css({left:setHandlePosition+'%'});
            dragContainer.scrollLeft(absoluteTo(setHandlePosition, dragContent.width()));
        }
    });
    
    $(window).on('mouseup touchend', function(e){
        dragFlag = false;
        contentDragFlag = false;
        if(dragHandle.length){
            handleLastPosition = dragHandle.position().left;
            scrollLastPosition = dragContainer.scrollLeft();
        }
    });
    
    $(window).on('load orientationchange resize', setDragHandleWidth);
    
})();
(function(){
    $('.dropdown').on('click', function(){
        var $this = $(this);
        if(!$this.hasClass('active')){
            $('.dropdown').removeClass('active');
            $this.addClass('active');
        }else{
            $('.dropdown').removeClass('active');
        }
    });

    $('.dropdown__link').on('click', function(e){
        $('.dropdown').removeClass('active');
    });

    //close opened stuff
    $(document).on('click', function(e) {
        //close dropdown
        if(!$(e.target).closest('.dropdown__selected').length) {
            $('.dropdown').removeClass('active');
        }
    });
})();
(function(){
    // var registrationForm = $('.js-form-participants');

    // registrationForm.validate({
    //     ignore: [],
    //     errorElement: 'p',
    //     errorPlacement: function(error, element) {
    //         error.appendTo(element.closest('.input-wrap'));
    //     }
    // });
})();

(function(){
    var resultsForm = $('.js-form-results');
    var resultsFormInput = $('.js-form-results-input');
    var resultsFormLoadSource = $('.js-form-results-source option');
    var resultsFormLoadArea = $('.js-form-results-load-area');
    var resultsFormButton = $('.js-form-results-btn');

    resultsFormInput.on('change', function(){
        var year = resultsFormInput.val()

        if ($("option", resultsFormLoadArea).length > 0)
          $("option", resultsFormLoadArea).remove();
        resultsFormLoadSource.each(function () {
            var self = $(this);
            if (self.hasClass(year) || self.hasClass("top")) {
              resultsFormLoadArea.append(self);
            }
        });
        resultsFormLoadArea.parent().show();

        resultsFormButton
            .removeAttr('disabled')
            .removeClass('btn--disabled')
            .addClass('btn--blue btn--blue-hover btn--blue-active');
    });
})();

(function(){
    var registrationForm = $('.js-form');
    
    registrationForm.validate({
        ignore: [],
        errorElement: 'p',
        errorPlacement: function(error, element) {
            error.appendTo(element.closest('.input-wrap'));
        }
    });
})();

(function(){
    var onTransitionEnd = 'transitionend webkitTransitionEnd oTransitionEnd MSTransitionEnd';
    var lightboxLink;
    var articleLightbox;
    var lightboxAnimatingFlag = false;
    var html = $('html');
    var galleryInitialized = false;
    
    var initializeGallery = function($this){
        var sync1    = $('#sync1'),
            sync2    = $('#sync2'),
            duration = 300,
            thumbs   = 10,
            navSlider = $this.attr('data-nav') == 'true' ? true : false,
            gallerySlideReached = 0,
            gallerySliderItem;

        var syncCarousels = function(itemIndex){
            sync2.trigger('to.owl.carousel', [itemIndex, duration, true]);
            sync1.trigger('to.owl.carousel', [itemIndex, duration, true]);
            
            gallerySliderItem = itemIndex + 2;
            for(var i = gallerySlideReached; i < gallerySliderItem; i++) {
                var thisImage = sync1.find('.gallery-slider__slide img:eq('+i+')');
                thisImage.attr('src', thisImage.attr('data-slider-src'));
                gallerySlideReached ++;
            }
        }
        
        sync1.on('initialized.owl.carousel', function(e) {

            for(var i = gallerySlideReached; i < 3; i++) {
                var thisImage = sync1.find('.gallery-slider__slide img:eq('+i+')');
                thisImage.attr('src', thisImage.attr('data-slider-src'));
                gallerySlideReached ++;
            }
            gallerySliderItem = e.item.index + 1;
            sync1   
                .trigger('next.owl.carousel')
                .trigger('prev.owl.carousel');
        });
        
        // Start Carousel
        sync1.owlCarousel({
            rtl: false,
            center: true,
            loop: false,
            items: 1,
            margin: 0,
            nav: navSlider,
            navText:['<svg class="icon"><use xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="/img/icons.svg#arrow--left"></use></svg>',
                     '<svg class="icon"><use xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="/img/icons.svg#arrow--right"></use></svg>'],
            dots:false,
            mouseDrag:navSlider,
            lazyLoad:false
        });        
        sync2.owlCarousel({
            rtl: false,
            center: true,
            loop: false,
            items: thumbs,
            margin: 0,
            nav: false,
            dots:false,
            mouseDrag:navSlider
        });
        
        sync1.on('changed.owl.carousel', function (e) {
            syncCarousels(e.item.index);
        });
        sync2.on('click', '.owl-item', function (e) {
            syncCarousels($(this).index());
        });
        sync2.on('changed.owl.carousel', function (e) {
            syncCarousels(e.item.index);
        });
    }
    
    var openLightbox = function(lightboxTrigger){
        if(lightboxAnimatingFlag == false){
            lightboxAnimatingFlag = true;
            lightboxLink = lightboxTrigger.attr('data-lightbox');
            articleLightbox = $(lightboxLink);
            
            if (articleLightbox[0]!==void(0)) {
                articleLightbox.addClass('animate');
                articleLightbox.on(onTransitionEnd, function () {
                    lightboxAnimatingFlag = false;
                    articleLightbox.off(onTransitionEnd);
                });

                html.addClass('overflow--hidden');
                
                if(galleryInitialized == false){
                    galleryInitialized = true;
                    initializeGallery(lightboxTrigger);
                }
            }
        }
    }
    
    var closeLightbox = function(){
        if(lightboxAnimatingFlag == false){
            lightboxAnimatingFlag = true;
            articleLightbox.removeClass('animate');
            articleLightbox.on(onTransitionEnd, function(){

                html.removeClass('overflow--hidden');
                lightboxAnimatingFlag = false;
                articleLightbox.off(onTransitionEnd);
                articleLightbox = null;
                lightboxLink = null;
            });
        }
    }
    
    $('.js-open-gallery-lightbox').on('click', function(){
        var $this = $(this);
        openLightbox($this);
    });
    
    $(document).on('click', '.js-close-gallery-lightbox', function(){
        closeLightbox();
    });
})();
(function(){
    var showResults = $('.js-show-results');
    var indexResults = $('.js-index-results');
    var showWinner = $('.js-show-winner');
    var winner = $('.js-winner');
    
    var loadWinnerImage = function(winnerObject){
        var winnerImage = winnerObject.find('.js-winner-image');
        var winnerImageSrc = winnerImage.attr('data-background-image');
        
        $('<img/>').attr('src', winnerImageSrc).load(function() {
            $(this).remove();
            winnerImage
            .css({'background-image': 'url('+winnerImageSrc+')'})
            .addClass('image-loaded');
        });
    }
    
    
    showResults.on('click', function(){
        var $this = $(this);
        var dataShow = $this.attr('data-show');
        showResults.removeClass('active');
        $this.addClass('active');
        indexResults.addClass('hidden');
        $(dataShow).removeClass('hidden');
    });
    
    showWinner.on('click', function(){
        var $this = $(this);
        var dataShow = $this.attr('data-show');
        
        winner.addClass('hidden');
        $(dataShow).removeClass('hidden');
        
        loadWinnerImage($(dataShow));
    });
    
    $(window).on('load', function(){
        loadWinnerImage(winner.eq(0));
    });
})();
(function(){   
    var inputAmount = $('.js-input-amount');
    
    var incrementAmount = function(inputValue){
        var amount = inputValue.val();
        
        amount ++
        
        inputValue.val(parseInt(amount));
    }
    
    var decrementAmount = function(inputValue){
        var amount = inputValue.val();
        
        if(amount <= 1){
            amount = 1
        }else{
            amount --
        }
        
        inputValue.val(parseInt(amount));
    }
    
    inputAmount.each(function(){
        var $this = $(this);
        var inputPlus = $this.find('.js-input-amount-plus');
        var inputMinus = $this.find('.js-input-amount-minus');
        var inputValue = $this.find('.js-input-amount-value');
        
        inputPlus.on('click', function(){
            incrementAmount(inputValue);
        });
        inputMinus.on('click', function(){
            decrementAmount(inputValue);
        });
    });
})();
(function(){
    var fieldSelectGroupSelect = $('.js-input-field-with-select__select');
    
    var updateFieldValue = function(triggerElement){
        var fieldSelectGroup = triggerElement.closest('.js-input-field-with-select');
        var fieldSelectGroupField = fieldSelectGroup.find('.js-input-field-with-select__field');
        var selectVal = triggerElement.val();
        fieldSelectGroupField.val('€ '+ selectVal);
    }
    
    fieldSelectGroupSelect.on('change', function(){
        updateFieldValue($(this));
    });
})();
(function () {
    var isFileSize = function(file, allowedSize){
        var fileLength = file.length;
        for (var i = 0; i < fileLength; i++) {
            if(file[i].size >= allowedSize){
                return false;
            }
        }
        return true;
    }
    
    $('.js-input-file').each(function () {
        var $input = $(this),
            $label = $input.next('.js-input-file__label'),
            labelVal = $label.html(),
            labelText = $label.find('.js-input-file__text'),
            allowedSize = $input.attr('data-filesize'),
            errorMessage = $input.parent().find('.js-input-file__error'),
            errorMessageFileSize = errorMessage.find('.js-allowed-size');
        
        errorMessageFileSize.html(Math.round(allowedSize/1024/1024));
        
        $input.on('change', function (e) {
            var files = this.files;
            var filesLength = files.length;
            var fileName = '';
            
            if(isFileSize(files, allowedSize)){
                errorMessage.addClass('hidden');
                
                if (files && filesLength > 1){
                    fileName = (this.getAttribute('data-multiple-caption') || '').replace('{count}', filesLength);
                }else if (e.target.value){
                    fileName = e.target.value.split('\\').pop();
                }
                
                if (fileName){
                    labelText.html(fileName);
                }else{
                    $label.html(labelVal);
                }
            }else{
                errorMessage.removeClass('hidden');
            }
        });

        // Firefox bug fix
        $input
            .on('focus', function () {
                $input.addClass('focus');
            })
            .on('blur', function () {
                $input.removeClass('focus');
            });
    });
})();
(function(){
    var languageNav = $('.js-language-nav');
    languageNav.on('click', function(){
        languageNav.toggleClass('active');
    });
    
    //close opened stuff
    $(document).on('click', function(e) {
        if (!$(e.target).closest('.js-language-nav').length) {
            languageNav.removeClass('active');
        }
    });
})();
(function(){    
    var deparmentMap = $('#js-map');
    
    function initialize() {
        var longitude = Number(deparmentMap.attr('data-lng'));
        var lattitude = Number(deparmentMap.attr('data-lat'));
        var mapCanvas = document.getElementById('js-map');
        
        var myLatLng = {lat: lattitude, lng: longitude};
        var mapOptions = {
            center: {lat: lattitude, lng: longitude-0.005},
            zoom: 16,
            mapTypeId: google.maps.MapTypeId.ROADMAP,
            scrollwheel: false
        }

        var map = new google.maps.Map(mapCanvas, mapOptions);

        var marker = new google.maps.Marker({
            position: myLatLng,
            map: map,
            icon: '/img/map-pin.png'
        });
    }
    if(deparmentMap.length){
        $.getScript("https://maps.googleapis.com/maps/api/js").done(function() {
            google.maps.event.addDomListener(window, 'load', initialize);
        });
    }
})();
(function(){
    var playVideo = function(triggerElement){
        var videoIframe = triggerElement.find('.js-video-iframe');
        var videoIframeSrc = videoIframe.attr('data-src');
        
        triggerElement.off('click');
        triggerElement.addClass('brief--video-playing');
        videoIframe.attr('src', videoIframeSrc);
    }
    
    $('.js-play-video').on('click', function(){
        playVideo($(this));
    });
})();
(function(){
    var languageNav = $('.js-profile-nav');
    languageNav.on('click', function(){
        languageNav.toggleClass('active');
    });
    
    //close opened stuff
    $(document).on('click', function(e) {
        if (!$(e.target).closest('.js-profile-nav').length) {
            languageNav.removeClass('active');
        }
    });
})();
(function(){
    var scrollElement = $('.js-scroll-along');
    var scrollBlock = $('.js-scroll-along-block');
    
    if(scrollElement.length){
        var initialOffsetTop;
        var scrollBlockHeight;
        var scrollBlockOffset;
        var tableHeadHeight;
        var tableThead = scrollBlock.find('thead');
        var clonedThead = tableThead.clone();
        
        var createSecondHead = function(){
            clonedThead.addClass('scroll-along__thead');
            $('.js-scroll-append').append(clonedThead);
        }
        createSecondHead();
        
        var seteDimensions = function(){
            tableThead.find('th').each(function(){
                var $this = $(this);
                var cellWidth = $this.width();
                var cellIndex = $this.index();
                clonedThead.find('th:eq('+cellIndex+')').width(cellWidth);
            });
            tableThead.find('tr').each(function(){
                var $this = $(this);
                var cellWidth = $this.width();
                var cellIndex = $this.index();
                clonedThead.find('tr:eq('+cellIndex+')').width(cellWidth);
            });
            
            scrollBlockHeight = scrollBlock.height();
            scrollBlockOffset = scrollBlock.offset().top;
            tableHeadHeight = tableThead.height();
        }
        
        var toggleScrollClass = function($this){
            var thisScroll = $this.scrollTop();
            
            if (thisScroll > initialOffsetTop) {
                scrollElement.addClass('scroll-along');
            }
            if (thisScroll < initialOffsetTop || thisScroll > (scrollBlockHeight + scrollBlockOffset - tableHeadHeight - 120)) {
                scrollElement.removeClass('scroll-along');
            }
        }
        
        $(window).scroll(function () {
            toggleScrollClass($(this));
        });
        
        $(window).on('load resize orientationchange', function(){
            initialOffsetTop = scrollElement.offset().top;
            seteDimensions();
        });
    }    
})();
(function(){
    var scrollBanner = document.querySelector('.js-scroll-banner');
    
    if($(scrollBanner).length){
        $('html').addClass('overflow--hidden');
        
        $(scrollBanner).on('mousewheel DOMMouseScroll', function(e){
            if ($(this)[0].scrollHeight !== $(this).outerHeight()) {
                var e0 = e.originalEvent,
                    delta = e0.wheelDelta || -e0.detail;

                this.scrollTop += (delta < 0 ? 1 : -1) * 30;
                e.preventDefault();
            }
        });

        $(scrollBanner).on('scroll', function(e){
            if (scrollBanner.offsetHeight + scrollBanner.scrollTop >= scrollBanner.scrollHeight) {
                setTimeout(function(){
                    $('html').removeClass('overflow--hidden');
                    $(scrollBanner).off('mousewheel DOMMouseScroll');
                    $(scrollBanner).remove();
                }, 100);
            }
        });

        $('.js-scroll-banner-scroll-end').on('click', function(e){
            e.preventDefault();

            $(scrollBanner).stop().animate({
                scrollTop: scrollBanner.scrollHeight
            }, 1600);
        });
    }
})();
(function () {
    var cursorXStartPosition;
    var cursorXCurrentPosition;
    var currentScrollPosition;
    var mouseDown = false;
    var touchFlag = false;
    var secondaryNavScroll = $('.js-secondary-nav-scroll');

    secondaryNavScroll.on('touchstart', function(){
        touchFlag = true;
    });
    
    secondaryNavScroll.on('touchend', function(){
        touchFlag = false;
    });
    
    secondaryNavScroll.on('mousedown', function (e) {
        if(touchFlag == false){
            mouseDown = true;
            cursorXStartPosition = e.clientX;
            currentScrollPosition = secondaryNavScroll.scrollLeft();
        }
    });

    $(window).on('mousemove', function (e) {
        if(touchFlag == false && mouseDown == true){
            secondaryNavScroll.scrollLeft(currentScrollPosition + (cursorXStartPosition - e.clientX));
        }
    });

    $(window).on('mouseup', function (e) {
        mouseDown = false;
    });
    
    $('.secondary-nav__link').on('click', function(e){
        if(Math.abs(cursorXStartPosition - e.clientX) > 20){
            e.preventDefault();
        }
    });
})();
svg4everybody();
(function(){
    $('.video__iframe').unveil();
    $('img').unveil(200);
})();
/**
 * jQuery Formset 1.3-pre
 * @author Stanislaus Madueke (stan DOT madueke AT gmail DOT com)
 * @requires jQuery 1.2.6 or later
 *
 * Copyright (c) 2009, Stanislaus Madueke
 * All rights reserved.
 *
 * Licensed under the New BSD License
 * See: http://www.opensource.org/licenses/bsd-license.php
 */
;(function($) {
    $.fn.formset = function(opts)
    {
        var options = $.extend({}, $.fn.formset.defaults, opts),
            flatExtraClasses = options.extraClasses.join(' '),
            totalForms = $('#id_' + options.prefix + '-TOTAL_FORMS'),
            maxForms = $('#id_' + options.prefix + '-MAX_NUM_FORMS'),
            minForms = $('#id_' + options.prefix + '-MIN_NUM_FORMS'),
            childElementSelector = 'input,select,textarea,label,div',
            $$ = $(this),

            applyExtraClasses = function(row, ndx) {
                if ($('.counter', row)) {
                    $('.counter', row).html((ndx+1)+".");
                }

                if (options.extraClasses) {
                    row.removeClass(flatExtraClasses);
                    row.addClass(options.extraClasses[ndx % options.extraClasses.length]);
                }
            },

            updateElementIndex = function(elem, prefix, ndx) {
                var idRegex = new RegExp(prefix + '-(\\d+|__prefix__)-'),
                    replacement = prefix + '-' + ndx + '-';
                if (elem.attr("for")) elem.attr("for", elem.attr("for").replace(idRegex, replacement));
                if (elem.attr('id')) elem.attr('id', elem.attr('id').replace(idRegex, replacement));
                if (elem.attr('name')) elem.attr('name', elem.attr('name').replace(idRegex, replacement));
            },

            hasChildElements = function(row) {
                return row.find(childElementSelector).length > 0;
            },

            showAddButton = function() {
                return (maxForms.val() == '' || (maxForms.val() - totalForms.val() > 0)) && (options.container.data('can-add-new') == 'True');
            },

            /**
            * Indicates whether delete link(s) can be displayed - when total forms > min forms
            */
            showDeleteLinks = function() {
                return (minForms.val() == '' || (totalForms.val() - minForms.val() > 0)) && (options.container.data('can-delete') == 'True');
            },
            insertOrderingButtons = function(row) {
                var order_input = row.find('input[id $= "-ORDER"]');
                if (order_input.length) {
                    order_input.attr("type", "hidden");
                    var $up_button = $("<button type='button'>").addClass(options.upCssClass);
                    var $down_button = $("<button type='button'>").addClass(options.downCssClass);
                    order_input.before($up_button);
                    order_input.before($down_button);
                    $up_button.click(
                        function() {
                            var row = $(this).parents('.' + options.formCssClass),
                                other_row = row.prev();
                            if (other_row.is(':visible') && other_row.length && !other_row.hasClass('dynamic-form-add')) {
                                var row_order = row.find('input[id $= "-ORDER"]'),
                                    other_row_order = other_row.find('input[id $= "-ORDER"]'),
                                    row_order_val = row_order.val(),
                                    other_row_order_val = other_row_order.val();
                                row_order.val(other_row_order_val);
                                other_row_order.val(row_order_val);
                                row.insertBefore(other_row);
                            }
                            return false;
                        }
                    );

                    $down_button.click(
                        function() {
                            var row = $(this).parents('.' + options.formCssClass),
                                other_row = row.next();
                            if (other_row.is(':visible') && other_row.length && !other_row.hasClass('dynamic-form-add')) {
                                var row_order = row.find('input[id $= "-ORDER"]'),
                                    other_row_order = other_row.find('input[id $= "-ORDER"]'),
                                    row_order_val = row_order.val(),
                                    other_row_order_val = other_row_order.val();
                                row_order.val(other_row_order_val);
                                other_row_order.val(row_order_val);
                                row.insertAfter(other_row);
                            }
                            return false;
                        }
                    );
                }
            },
            insertDeleteLink = function(row) {
                var addCssSelector = options.addCssClass.trim().replace(/\s+/g, '.'),
                    delete_button = undefined;

                if (options.deleteButtonSelector) {
                    delete_button = row.find(options.deleteButtonSelector)
                } else if (row.is('TR')) {
                    // If the forms are laid out in table rows, insert
                    // the remove button into the last table cell:
                    delete_button = $('<a class="' + options.deleteCssClass +'" href="javascript:void(0)">' + options.deleteText + '</a>');
                    row.children(':last').append(delete_button);

                    // AA ADDED
                    row.children(':last').removeClass('checkbox')
                    // END AA ADDED

                } else if (row.is('UL') || row.is('OL')) {
                    // If they're laid out as an ordered/unordered list,
                    // insert an <li> after the last list item:
                    delete_button =  $('<a class="' + options.deleteCssClass + '" href="javascript:void(0)">' + options.deleteText +'</a>');
                    row.append($("<li>").append(delete_button));
                } else {
                    // Otherwise, just insert the remove button as the
                    // last child element of the form's container:
                    delete_button = $('<a class="' + options.deleteCssClass + '" href="javascript:void(0)">' + options.deleteText +'</a>');
                    if (options.container.data('delete-prepend') == 'True')
                        row.prepend(delete_button);
                    else
                        row.append(delete_button);
                }
                // Check if we're under the minimum number of forms - not to display delete link at rendering
                if (!showDeleteLinks()){
                    delete_button.hide();
                }

                delete_button.click(function() {
                    var row = $(this).parents('.' + options.formCssClass),
                        del = row.find('input:hidden[id $= "-DELETE"]'),
                        buttonRow = row.siblings("a." + addCssSelector + ', .' + options.formCssClass + '-add'),
                        forms;
                    if (del.length) {
                        // We're dealing with an inline formset.
                        // Rather than remove this form from the DOM, we'll mark it as deleted
                        // and hide it, then let Django handle the deleting:
                        del.val('on');
                        row.hide();
                        forms = $('.' + options.formCssClass).not(':hidden');
                    } else {
                        row.remove();
                        // Update the TOTAL_FORMS count:
                        forms = $('.' + options.formCssClass).not('.template');
                        totalForms.val(forms.length);
                    }
                    for (var i=0, formCount=forms.length; i<formCount; i++) {
                        // Apply `extraClasses` to form rows so they're nicely alternating:
                        applyExtraClasses(forms.eq(i), i);
                        if (!del.length) {
                            // Also update names and IDs for all child controls (if this isn't
                            // a delete-able inline formset) so they remain in sequence:
                            forms.eq(i).find(childElementSelector).each(function() {
                                updateElementIndex($(this), options.prefix, i);
                            });
                        }
                    }
                    // Check if we've reached the minimum number of forms - hide all delete link(s)
                    if (!showDeleteLinks()){
                        delete_button.each(function(){$(this).hide();});
                    }
                    // Check if we need to show the add button:
                    if (buttonRow.is(':hidden') && showAddButton()) buttonRow.show();
                    // If a post-delete callback was provided, call it with the deleted form:
                    if (options.removed) options.removed(row);
                    return false;
                });
            },
            // AA ADDED FUNCTION
            replaceDeleteLink = function(row) {
                var del = row.find('input:checkbox[id $= "-DELETE"]');
                if (del.length) {
                    // If you specify "can_delete = True" when creating an inline formset,
                    // Django adds a checkbox to each form in the formset.
                    // Replace the default checkbox with a hidden field:
                    if (del.is(':checked')) {
                        // If an inline formset containing deleted forms fails validation, make sure
                        // we keep the forms hidden (thanks for the bug report and suggested fix Mike)
                        del.before('<input type="hidden" name="' + del.attr('name') +'" id="' + del.attr('id') +'" value="on" />');
                        row.hide();
                    } else {
                        del.before('<input type="hidden" name="' + del.attr('name') +'" id="' + del.attr('id') +'" />');
                    }
                    // Hide any labels associated with the DELETE checkbox:
                    $('label[for="' + del.attr('id') + '"]').hide();
                    del.remove();
                }
            };
        if (!options.container) {
            options.container = $$.parent()
        }
        // END AA ADDED FUNCTION
        $$.each(function(i) {
            // AA UPDATED
            var row = $(this);
            replaceDeleteLink(row);
            // END AA UPDATED
            if (hasChildElements(row)) {
                row.addClass(options.formCssClass);
                if (row.is(':visible')) {
                    // AA ADDED IF
                    if (options.container.data('can-delete') == 'True')
                        insertDeleteLink(row);
                    insertOrderingButtons(row);
                    applyExtraClasses(row, i);
                }
            }
        });


        var hideAddButton = !showAddButton(),
            addButton, template;
        if (options.formTemplate) {
            // If a form template was specified, we'll clone it to generate new form instances:
            template = (options.formTemplate instanceof $) ? options.formTemplate : $(options.formTemplate);
            template.removeAttr('id').addClass(options.formCssClass + ' template');
            template.find(childElementSelector).each(function() {
                updateElementIndex($(this), options.prefix, '__prefix__');
            });
            // AA ADDED
            replaceDeleteLink(template);
            insertOrderingButtons(template);
            if (options.container.data('can-delete') == 'True')
                insertDeleteLink(template);
            // END AA ADDED
        } else {
            // Otherwise, use the last form in the formset; this works much better if you've got
            // extra (>= 1) forms (thnaks to justhamade for pointing this out):
            template = $('.' + options.formCssClass + ':last').clone(true).removeAttr('id');
            template.find('input:hidden[id $= "-DELETE"]').remove();
            // Clear all cloned fields, except those the user wants to keep (thanks to brunogola for the suggestion):
            template.find(childElementSelector).not(options.keepFieldValues).each(function() {
                var elem = $(this);
                // If this is a checkbox or radiobutton, uncheck it.
                // This fixes Issue 1, reported by Wilson.Andrew.J:
                if (elem.is('input:checkbox') || elem.is('input:radio')) {
                    elem.attr('checked', false);
                } else {
                    elem.val('');
                }
            });
        }
        // FIXME: Perhaps using $.data would be a better idea?
        options.formTemplate = template;

        if ($$.is('TR') || options.container.is("TBODY") || options.container.is("TABLE")) {
            // If forms are laid out as table rows, insert the
            // "add" button in a new table row:
            var numCols = $$.eq(0).children().length,   // This is a bit of an assumption :|
                buttonRow = $('<tr><td colspan="' + numCols + '"><a class="' + options.addCssClass + '" href="javascript:void(0)">' + options.addText + '</a></tr>')
                            .addClass(options.formCssClass + '-add');

            // AA ADDED
            var tfoot = options.container.parents("table").find("tfoot");
            if (tfoot[0]) {
                tfoot.prepend(buttonRow);
            } else {
                options.container.append(buttonRow);
            }
            //$$.parent().append(buttonRow);
            // END AA ADDED

            if (hideAddButton) buttonRow.hide();
            addButton = buttonRow.find('a');
        } else {
            // AA Added CSS Selector
            if (options.addCssSelector) {
                addButton = options.container.parents("form").find(options.addCssSelector);
                if (hideAddButton) addButton.hide();
            }
            if (!addButton) {
                // Otherwise, insert it immediately after the last form:
                addButton = $('<div class="button-add"><a class="' + options.addCssClass + '" href="javascript:void(0)">' + options.addText + '</a></div>');
                options.container.parent().append(addButton);
                if (hideAddButton) addButton.hide();
                addButton = addButton.find('a');
            }
        }

        addButton.click(function() {
            var formCount = parseInt(totalForms.val()),
                row = options.formTemplate.clone(true).removeClass('template'),
                buttonRow = $($(this).parents('tr.' + options.formCssClass + '-add').get(0) || this),
                delCssSelector = options.deleteCssClass.trim().replace(/\s+/g, '.');

            // AA ADDED
            var max_num = parseInt($('#id_' + options.prefix + '-MAX_NUM_FORMS').val());
            if (formCount >= max_num) {
                alert('Reached maximum row count.');
                return false;
            }

            applyExtraClasses(row, formCount);
            if (options.container) {
                row.appendTo(options.container).show();
            } else
                row.insertBefore(buttonRow).show();

            // END AA ADDED

            row.find(childElementSelector).each(function() {
                updateElementIndex($(this), options.prefix, formCount);
            });
            totalForms.val(formCount + 1);
            // Check if we're above the minimum allowed number of forms -> show all delete link(s)
            if (showDeleteLinks()){
                if (options.deleteButtonSelector)
                    $(options.deleteButtonSelector, row).each(function(){$(this).show();});
                else
                    $('a.' + delCssSelector).each(function(){$(this).show();});
            }
            // Check if we've exceeded the maximum allowed number of forms:
            if (!showAddButton()) buttonRow.hide();
            // If a post-add callback was supplied, call it with the added form:
            if (options.added) options.added(row);
            return false;
        });


        return $$;
    };

    /* Setup plugin defaults */
    $.fn.formset.defaults = {
        prefix: 'form',                  // The form prefix for your django formset
        container: null,                 // Container of formsets. AA ADDED
        formTemplate: null,              // The jQuery selection cloned to generate new form instances
        addText: 'add another',          // Text for the add link
        deleteText: 'remove',            // Text for the delete link
        addCssClass: 'add-row',          // CSS class applied to the add link
        addButtonSelector: null,        // AA ADDED if this is set, no new add buttons are added.
        deleteCssClass: 'delete-row',    // CSS class applied to the delete link
        deleteButtonSelector: null,        // AA ADDED if this is set, no new add buttons are added.
        formCssClass: 'dynamic-form',    // CSS class applied to each form in a formset
        upCssClass: 'icon-arrow-up',
        downCssClass: 'icon-arrow-down',
        extraClasses: [],                // Additional CSS classes, which will be applied to each form in turn
        keepFieldValues: '',             // jQuery selector for fields whose values should be kept when the form is cloned
        added: null,                     // Function called each time a new form is added
        removed: null                    // Function called each time a form is deleted
    };
})(jQuery);

// Generated by CoffeeScript 1.10.0
(function() {
  var call_formset_function, formset;

  window.ENV = window.ENV || {};

  this.format_date = function(dt) {
    var date, hours, minutes, month;
    month = dt.getUTCMonth() > 8 ? "" + (dt.getUTCMonth() + 1) : "0" + (dt.getUTCMonth() + 1);
    date = dt.getUTCDate() > 9 ? "" + (dt.getUTCDate()) : "0" + (dt.getUTCDate());
    hours = dt.getUTCHours() > 9 ? "" + (dt.getUTCHours()) : "0" + (dt.getUTCHours());
    minutes = dt.getUTCMinutes() > 9 ? "" + (dt.getUTCMinutes()) : "0" + (dt.getUTCMinutes());
    return (dt.getUTCFullYear()) + "-" + month + "-" + date + " " + hours + ":" + minutes;
  };

  call_formset_function = function(row, container, type) {
    var field, function_name, i, len, ref;
    ref = $(container).prop("class").split(' ');
    for (i = 0, len = ref.length; i < len; i++) {
      field = ref[i];
      if (field.indexOf('_inline_class') !== -1) {
        function_name = field;
      }
    }
    if (window.console) {
      console.log(function_name + '_' + type);
    }
    if (typeof window[function_name + '_' + type] === 'function') {
      return window[function_name + '_' + type](row);
    }
  };

  formset = function(containers) {
    var $container, $items, container, i, len, prefix, results, ret_obj;
    ret_obj = {};
    results = [];
    for (i = 0, len = containers.length; i < len; i++) {
      container = containers[i];
      prefix = $(container).data("prefix");
      $container = $(container).find(".formset_container");
      $items = $container.find(".item:not(.template)");
      results.push($items.formset({
        prefix: prefix,
        container: $container,
        addText: '',
        addCssClass: 'add-new-row',
        addCssSelector: '.add-new-row',
        deleteButtonSelector: '.delete_button',
        deleteText: '',
        deleteCssClass: '',
        upCssClass: 'btn btn-sm icon-arrow-up',
        downCssClass: 'btn btn-sm icon-arrow-down',
        formTemplate: $(container).parent().find(".template"),
        added: function(row) {
          return call_formset_function(row, container, 'added');
        },
        removed: function(row) {
          return call_formset_function(row, container, 'removed');
        }
      }));
    }
    return results;
  };

  $(function() {
    window.ENV.formsets = formset($('.django-inline-form'));
    $(".filter-form select").on("change", function(evt) {
      return $(this).parents("form").submit();
    });
    $('th.selection input[type=checkbox]').on('change', function() {
      return $('tr td:nth-child(1) input[type=checkbox]', $(this).parents('table')).prop("checked", $(this).prop("checked"));
    });
    $('.gallery_album').on('click', function(evt) {
      var template;
      template = $('#hb-video-tmpl').html();
      template = template.replace('{{ video_link }}', $(this).data('url'));
      $("#video-modal .modal-inner").html(template);
      $("#video-modal").addClass("is-active");
      return false;
    });
    return $('#video-modal .modal-close').on('click', function(evt) {
      return $("#video-modal").removeClass("is-active");
    });
  });

}).call(this);

//# sourceMappingURL=00_core.js.map

// Generated by CoffeeScript 2.3.2
(function() {
  var check_price, update_line_participant;

  this.Participant_inline_class_added = function(row) {
    return update_line_participant(row);
  };

  this.CompanyParticipant_inline_class_added = function(row) {
    return update_line_participant(row);
  };

  check_price = function(row) {
    var birthday, csrf, distance, insurance, url;
    distance = $("select[name$='distance']", row).val();
    birthday = $("select[name$='birthday_year']", row).val();
    insurance = $("[name$='insurance']", row).val();
    csrf = document.getElementsByName('csrfmiddlewaretoken')[0].value;
    url = $(row).parents("form").data('check-price');
    return $.ajax({
      url: url,
      type: 'POST',
      data: {
        csrfmiddlewaretoken: csrf,
        distance: distance,
        birthday_year: birthday,
        insurance: insurance
      },
      dataType: 'json',
      success: function(data) {
        return $('.price', row).html(data.message);
      },
      error: function() {
        return $('.price', row).html('Please enter all details');
      }
    });
  };

  update_line_participant = function(row) {
    var bike_brand, bike_brand2, city, country, insurance, ssn;
    ssn = $("input[name$='-ssn']", row);
    insurance = $("select[name$='-insurance']", row);
    city = $("select[name$='-city']", row);
    country = $("select[name$='-country']", row);
    bike_brand = $("select[name$='-bike_brand']", row);
    bike_brand2 = $("input[name$='-bike_brand2']", row);
    $("input[name$='-first_name']", row).autocomplete({
      serviceUrl: row.parents("form").data("autocomplete"),
      onSelect: function(suggestion) {
        var birthday;
        $("select[name$='country']", row).val(suggestion.country).change();
        $("select[name$='gender']", row).val(suggestion.gender).change();
        $("input[name$='last_name']", row).val(suggestion.last_name).change().focus();
        $("input[name$='bike_brand2']", row).val(suggestion.bike_brand2).change().focus();
        birthday = suggestion.birthday.split('-');
        console.log(birthday);
        $("select[name$='birthday_year']", row).val(parseInt(birthday[0])).change();
        $("select[name$='birthday_month']", row).val(parseInt(birthday[1])).change();
        $("select[name$='birthday_day']", row).val(parseInt(birthday[2])).change();
        $("input[name$='team_name']", row).val(suggestion.team_name).change().focus();
        $("input[name$='phone_number']", row).val(suggestion.phone_number).change().focus();
        return $("input[name$='email']", row).val(suggestion.email).change().focus().blur();
      },
      formatResult: function(suggestion, currentValue) {
        return `${suggestion.first_name} ${suggestion.last_name} ${suggestion.birthday} `;
      }
    });
    if (row.parents(".formset_container").data("can-delete") === 'False') {
      $('.delete_button', row).remove();
      $('.price', row).remove();
    }
    $(".participant__number", row).html(row.index());
    if (!bike_brand.val() || bike_brand.val() !== "216") {
      $(bike_brand2).parents(".input-wrap").hide();
    }
    bike_brand.on("change", function(e) {
      var el;
      el = $(bike_brand2).parents(".input-wrap");
      if ($(this).val() === '216') {
        return el.show();
      } else {
        return el.hide();
      }
    });
    if (!insurance.val()) {
      $(ssn).parents(".input-wrap").hide();
    }
    insurance.on("change", function(e) {
      var el;
      el = $(ssn).parents(".input-wrap");
      if ($(this).val()) {
        return el.show();
      } else {
        $(ssn).val("");
        return el.hide();
      }
    });
    if (!country.val() === 'LV') {
      $(city).parents(".input-wrap").hide();
    }
    country.on("change", function(e) {
      var el;
      el = $(city).parents(".input-wrap");
      if ($(this).val() === 'LV') {
        return el.show();
      } else {
        $(ssn).val("");
        return el.hide();
      }
    });
    if (!row.hasClass("noadd")) {
      $("select[name$='-birthday_year'], select[name$='distance'], select[name$='insurance']", row).on("change", function(e) {
        check_price(row);
        return void 0;
      });
      check_price(row);
    }
    return void 0;
  };

  $(function() {
    var container, i, len, ref, results;
    if ($(".Participant_inline_class")[0]) {
      ref = $('.item:not(.template)');
      results = [];
      for (i = 0, len = ref.length; i < len; i++) {
        container = ref[i];
        results.push(update_line_participant($(container)));
      }
      return results;
    }
  });

  $(function() {
    var container, i, len, ref, results;
    if ($(".CompanyParticipant_inline_class")[0]) {
      ref = $('.item:not(.template)');
      results = [];
      for (i = 0, len = ref.length; i < len; i++) {
        container = ref[i];
        results.push(update_line_participant($(container)));
      }
      return results;
    }
  });

}).call(this);

//# sourceMappingURL=01_registration.js.map

// Generated by CoffeeScript 1.10.0
(function() {
  var show_hide_invoice_fields;

  show_hide_invoice_fields = function(element) {
    if (element.data('bill')) {
      return $('.invoice_fields ').show();
    } else {
      return $('.invoice_fields ').hide();
    }
  };

  $(function() {
    var payment;
    payment = $("input[name$='payment_type']:checked");
    show_hide_invoice_fields(payment);
    $("input[name$='payment_type']").on('change', function(e) {
      var element;
      element = e.srcElement ? e.srcElement : e.target;
      element = $(element);
      return show_hide_invoice_fields(element);
    });
    return $('#id_donation').on('change', function(evt) {
      var total;
      total = Math.round((parseFloat($(this).val() || 0) + parseFloat($('#final_price').data('amount') || 0)) * 100) / 100;
      return $('#final_price').html(total);
    }).change();
  });

}).call(this);

//# sourceMappingURL=02_payment_application.js.map

// Generated by CoffeeScript 1.10.0
(function() {
  var formset;

  window.ENV = window.ENV || {};

  formset = function(containers) {
    var $container, $items, container, i, len, prefix, results, ret_obj;
    ret_obj = {};
    results = [];
    for (i = 0, len = containers.length; i < len; i++) {
      container = containers[i];
      prefix = $(container).data("prefix");
      $container = $(container).find(".formset_container");
      $items = $container.find(".item:not(.template)");
      results.push($items.formset({
        prefix: prefix,
        container: $container,
        formTemplate: $(container).parent().find(".template")
      }));
    }
    return results;
  };

  $(function() {
    $('input[type=reset]').on('click', function(event) {
      var elem, form;
      elem = event.target;
      form = $(elem).parents('form');
      $('input[type=text], input[type=password], input[type=textarea], input[type=number], select', form).val("");
      return false;
    });
    return window.ENV.formsets = formset($('.django-inline-form'));
  });

}).call(this);

//# sourceMappingURL=manager.js.map
