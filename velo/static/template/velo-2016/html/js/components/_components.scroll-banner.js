(function(){
    var scrollBanner = document.querySelector('.js-scroll-banner');
    
    if($(scrollBanner).length){
        $('html').addClass('overflow--hidden');
        
        $(scrollBanner).on('mousewheel DOMMouseScroll', function(e){
            if ($(this)[0].scrollHeight !== $(this).outerHeight()) {
                var e0 = e.originalEvent,
                    delta = e0.wheelDelta || -e0.detail;

                this.scrollTop += (delta < 0 ? 1 : -1) * 30;
                e.preventDefault();
            }
        });

        $(scrollBanner).on('scroll', function(e){
            if (scrollBanner.offsetHeight + scrollBanner.scrollTop >= scrollBanner.scrollHeight) {
                setTimeout(function(){
                    $('html').removeClass('overflow--hidden');
                    $(scrollBanner).off('mousewheel DOMMouseScroll');
                    $(scrollBanner).remove();
                }, 100);
            }
        });

        $('.js-scroll-banner-scroll-end').on('click', function(e){
            e.preventDefault();

            $(scrollBanner).stop().animate({
                scrollTop: scrollBanner.scrollHeight
            }, 1600);
        });
    }
})();