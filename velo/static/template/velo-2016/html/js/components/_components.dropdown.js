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