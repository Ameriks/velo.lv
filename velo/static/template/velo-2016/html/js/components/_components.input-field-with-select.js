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