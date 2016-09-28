(function(){
    var languageNav = $('.js-profile-nav');
    languageNav.on('click', function(){
        languageNav.toggleClass('active');
    });
    
    //close opened stuff
    $(document).on('click', function(e) {
        if (!$(e.target).closest('.js-profile-nav').length) {
            languageNav.removeClass('active');
        }
    });
})();