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
