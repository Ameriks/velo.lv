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