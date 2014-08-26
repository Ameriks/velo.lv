/**
 * jQuery Formset 1.2
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
            $$ = $(this),

            applyExtraClasses = function(row, ndx) {
                if (options.extraClasses) {
                    row.removeClass(flatExtraClasses);
                    row.addClass(options.extraClasses[ndx % options.extraClasses.length]);
                }
            },

            updateElementIndex = function(elem, prefix, ndx) {
                var idRegex = new RegExp('' + prefix + '-(?:\\d+|(?:__prefix__))-'),
                    replacement = prefix + '-' + ndx + '-';
                if (elem.attr("for")) elem.attr("for", elem.attr("for").replace(idRegex, replacement));
                if (elem.attr('id')) elem.attr('id', elem.attr('id').replace(idRegex, replacement));
                if (elem.attr('name')) elem.attr('name', elem.attr('name').replace(idRegex, replacement));
            },

            hasChildElements = function(row) {
                return row.find('input,select,textarea,label').length > 0;
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
                var $del_link = $('<button type="button">');
                $del_link.addClass(options.deleteCssClass);
                $del_link.html(options.deleteText);
                if (row.is('TR')) {
                    // If the forms are laid out in table rows, insert
                    // the remove button into the last table cell:
                    row.children('td:last').append($del_link);
                } else if (row.is('UL') || row.is('OL')) {
                    // If they're laid out as an ordered/unordered list,
                    // insert an <li> after the last list item:
                    row.append($('li').append($del_link));
                } else {
                    // Otherwise, just insert the remove button as the
                    // last child element of the form's container:
                    row.append($del_link);
                }
                $del_link.click(function() {
                    var row = $(this).parents('.' + options.formCssClass),
                        del = row.find('input:hidden[id $= "-DELETE"]'),
                        parent = row.parent();

                    if (del.length) {
                        // We're dealing with an inline formset; rather than remove
                        // this form from the DOM, we'll mark it as deleted and hide
                        // it, then let Django handle the deleting:
                        del.val('on');
                        row.insertBefore(parent.children().eq(0))
                        row.hide();
                    } else {
                        row.remove();
                        // Update the TOTAL_FORMS form count.
                        // Also update names and IDs for all remaining form controls so they remain in sequence:
                        var forms = $('.' + options.formCssClass).not('.formset-custom-template');
                        $('#id_' + options.prefix + '-TOTAL_FORMS').val(forms.length);
                        for (var i=0, formCount=forms.length; i<formCount; i++) {
                            applyExtraClasses(forms.eq(i), i);
                            forms.eq(i).find('input,select,textarea,label').each(function() {
                                updateElementIndex($(this), options.prefix, i);
                            });
                        }
                    }
                    // If a post-delete callback was provided, call it with the deleted form:
                    if (options.removed) options.removed(row);
                    return false;
                });
            },

            replaceDeleteLink = function(row) {
                var del = row.find('input:checkbox[id $= "-DELETE"]');
                if (del.length) {
                    // If you specify "can_delete = True" when creating an inline formset,
                    // Django adds a checkbox to each form in the formset.
                    // Replace the default checkbox with a hidden field:
                    del.before('<input type="hidden" name="' + del.attr('name') + '" id="' + del.attr('id') + '" />');
                    del.remove();
                }
            };
        if (!options.container) {
            options.container = $$.parent()
        }
        $$.each(function(i) {
            var row = $(this);
            replaceDeleteLink(row);
            if (hasChildElements(row)) {
                if (options.container.data('can-delete') == 'True')
                    insertDeleteLink(row);
                insertOrderingButtons(row);
                row.addClass(options.formCssClass);
                applyExtraClasses(row, i);
            }
        });

        var addButton, template, insertPoint;

        if (options.formTemplate) {
            // If a form template was specified, we'll clone it to generate new form instances:
            template = (options.formTemplate instanceof $) ? options.formTemplate : $(options.formTemplate);
            template.removeAttr('id').addClass(options.formCssClass).addClass('formset-custom-template');
            template.find('input,select,textarea,label').each(function() {
                updateElementIndex($(this), options.prefix, '__prefix__');
            });
            replaceDeleteLink(template);
            if (options.container.data('can-delete') == 'True')
                insertDeleteLink(template);
            insertOrderingButtons(template);
            template.detach();
        } else {
            // Otherwise, use the last form in the formset; this works much better if you've got
            // extra (>= 1) forms (thnaks to justhamade for pointing this out):
            template = $('.' + options.formCssClass + ':last').clone(true).removeAttr('id');
            template.find('input:hidden[id $= "-DELETE"]').remove();
            template.find('input,select,textarea,label').each(function() {
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

        addButton = $('<button type="button">')
            .addClass(options.addCssClass)
            .html(options.addText);

        if ($$.prop('tagName') == 'TR' || ['TBODY', 'TABLE'].indexOf(options.container.attr('tagName')) !== -1) {
            // If forms are laid out as table rows, insert the
            // "add" button in a new table row:
            var numCols = options.formTemplate.eq(0).children().length;
            insertPoint = $('<tr>').addClass(options.formCssClass + '-add').append(
                $('<td>').attr('colspan', numCols).append(addButton));
            options.container.append(insertPoint);
        } else {
            // Otherwise, insert it immediately after the last form:
            addButtonDiv = $('<div class="addline">').append(addButton)
            options.container.append(addButtonDiv);
            insertPoint = addButton;
        }
        var $totalForms = $('#id_' + options.prefix + '-TOTAL_FORMS');
        addButton.click(function() {
            var max_num = parseInt($('#id_' + options.prefix + '-MAX_NUM_FORMS').val());
            var formCount = parseInt($totalForms.val());

            if (formCount >= max_num) {
                alert('Reached maximum row count.');
                return false;
            }

            var row = options.formTemplate.clone(true).removeClass('formset-custom-template'),
                ordering = row.find('input[id $= "-ORDER"]');



            applyExtraClasses(row, formCount);
            row.insertBefore(insertPoint).show();
            row.find('input,select,textarea,label').each(function() {
                updateElementIndex($(this), options.prefix, formCount);
            });
            if (ordering.length)
                ordering.val(formCount + 1);
            $totalForms.val(formCount + 1);
            // If a post-add callback was supplied, call it with the added form:
            if (options.added) options.added(row);
            return false;
        });

        return $$;
    }

    /* Setup plugin defaults */
    $.fn.formset.defaults = {
        prefix: 'form',                  // The form prefix for your django formset
        formTemplate: null,              // The jQuery selection cloned to generate new form instances
        addText: 'add another',          // Text for the add link
        deleteText: 'remove',            // Text for the delete link
        upCssClass: 'icon-arrow-up',
        downCssClass: 'icon-arrow-down',
        addCssClass: 'add-row',          // CSS class applied to the add link
        deleteCssClass: 'delete-row',    // CSS class applied to the delete link
        formCssClass: 'dynamic-form',    // CSS class applied to each form in a formset
        extraClasses: [],                // Additional CSS classes, which will be applied to each form in turn
        added: null,                     // Function called each time a new form is added
        removed: null,                   // Function called each time a form is deleted
        container: null                  // Container of formsets. Used when no formsets defined
    };
})(jQuery)
