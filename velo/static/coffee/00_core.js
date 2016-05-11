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
    return $(".filter-form select").on("change", function(evt) {
      return $(this).parents("form").submit();
    });
  });

}).call(this);

//# sourceMappingURL=00_core.js.map
