(function(){
    var slider = $('.js-calendar-slider');
    var slideTo = slider.attr('data-slide-to');

    slider.owlCarousel({
        items:1,
        navText:[$("#slider-button-left").html(),$("#slider-button-right").html()],
        mouseDrag:false,
        responsive : {
            0 : {
                nav:false
            },
            480 : {
                nav:true
            }
        }
    });
    
    slider.trigger('to.owl.carousel', [slideTo]);

    var loadSliderImages = function(containingObject){
        var sliderImage = containingObject.find('.js-calendar-slider-image');
        var sliderImageSrc = sliderImage.attr('data-calendar-slider-img');
        var sliderImageLoadOn = Number(sliderImage.attr('data-load-on'));
        var windowWidth = window.innerWidth;

        if(sliderImageLoadOn < windowWidth){
            sliderImage.attr('src', sliderImageSrc);
            sliderImage.removeAttr('data-calendar-slider-img');
        }
    }

    var openCloseAccordeon = function(accordeonHead){
        var accordeonBody = accordeonHead.next();

        if(!accordeonHead.hasClass('active')){
            $('.owl-item.active .js-accordeon-head').removeClass('active');
            $('.owl-item.active .accordeon-body').removeClass('active');
            accordeonHead.addClass('active');
            accordeonBody.addClass('active');
            loadSliderImages(accordeonBody);
        }
    }

    $(document).on('click', '.js-open-accordeon', function(e){
        var $this = $(this);

        if($this.hasClass('js-accordeon-head')){
            openCloseAccordeon($this);
        }else{
            openCloseAccordeon($this.closest('.js-accordeon-head'));
        }

    });

    var eventLink = $('.js-calendar-slider-link');
    var setEventLink = function(){
        var windowWidth = window.innerWidth;

        if(windowWidth >= 880){
            eventLink.removeAttr('href');
        }else{
            eventLink.each(function(){
                var $this = $(this);
                $this.attr('href', $this.attr('data-href'));
            });
        }
    }


    $(window).on('load orientationchange', setEventLink);
    $(window).on('load', function(){
        loadSliderImages($('.calendar-slider__slide').find('.calendar-slider__body:eq(0)'));
    });

    var resizeTimer;
    $(window).on('resize', function (e) {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function () {
            setEventLink();
            loadSliderImages($('.calendar-slider__slide').find('.calendar-slider__body:eq(0)'));
        }, 250);
    });
})();
