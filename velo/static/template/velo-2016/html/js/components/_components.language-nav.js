(function(){
    var languageNav = $('.js-language-nav');
    languageNav.on('click', function(){
        languageNav.toggleClass('active');
    });
    
    //close opened stuff
    $(document).on('click', function(e) {
        if (!$(e.target).closest('.js-language-nav').length) {
            languageNav.removeClass('active');
        }
    });
})();