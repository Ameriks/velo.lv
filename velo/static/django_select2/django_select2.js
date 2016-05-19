(function ($) {

    var init = function ($element, options) {
        $element.select2(options);
    };


    var initHeavyNumber = function ($element, options) {
        var settings = $.extend({
            ajax: {
                data: function (params) {
                    return {
                        term: params.term,
                        page: params.page,
                        field_id: $element.data('field_id'),
                        context: function() {
                            var competition = $("#id_competition").val();
                            var distance = $("#id_distance").val();
                            var gender = $("#id_gender").val();
                            var birthday = $("#id_birthday").val();
                            var context = [competition, distance, gender, birthday];
                            return context.join('~~~')
                        }
                    };
                },
                processResults: function (data, page) {
                    return {
                        results: data.results,
                        pagination: {
                            more: data.more
                        }
                    };
                }
            }
        }, options);

        $element.select2(settings);
    };


    var initHeavy = function ($element, options) {
        var settings = $.extend({
            ajax: {
                data: function (params) {
                    return {
                        term: params.term,
                        page: params.page,
                        field_id: $element.data('field_id')
                    };
                },
                processResults: function (data, page) {
                    return {
                        results: data.results,
                        pagination: {
                            more: data.more
                        }
                    };
                }
            }
        }, options);

        $element.select2(settings);
    };

    $.fn.djangoSelect2 = function (options) {
        var settings = $.extend({}, options);
        $.each(this, function (i, element) {
            var $element = $(element);
            if ($element.hasClass('django-select2-heavy')) {
                initHeavy($element, settings);
            } else if ($element.hasClass('django-select2-heavy-number')) {
                initHeavyNumber($element, settings);
            } else {
                init($element, settings);
            }
        });
        return this;
    };

    $(function () {
        $('.django-select2').djangoSelect2();
    });

}(this.jQuery));

