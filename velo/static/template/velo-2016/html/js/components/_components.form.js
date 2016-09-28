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
