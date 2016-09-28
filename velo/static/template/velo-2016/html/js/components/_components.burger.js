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