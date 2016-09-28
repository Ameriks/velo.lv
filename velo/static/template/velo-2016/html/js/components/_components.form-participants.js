(function(){
    var registrationForm = $('.js-form-participants');
    
    registrationForm.validate({
        ignore: [],
        errorElement: 'p',
        errorPlacement: function(error, element) {
            error.appendTo(element.closest('.input-wrap'));
        }
    });
})();