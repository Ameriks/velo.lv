(function(){
    var onTransitionEnd = 'transitionend webkitTransitionEnd oTransitionEnd MSTransitionEnd';
    var lightboxLink;
    var articleLightbox;
    var lightboxAnimatingFlag = false;
    var html = $('html');
    var galleryInitialized = false;
    
    var initializeGallery = function($this){
        var sync1    = $('#sync1'),
            sync2    = $('#sync2'),
            duration = 300,
            thumbs   = 10,
            navSlider = $this.attr('data-nav') == 'true' ? true : false,
            gallerySlideReached = 0,
            gallerySliderItem;

        var syncCarousels = function(itemIndex){
            sync2.trigger('to.owl.carousel', [itemIndex, duration, true]);
            sync1.trigger('to.owl.carousel', [itemIndex, duration, true]);
            
            gallerySliderItem = itemIndex + 2;
            for(var i = gallerySlideReached; i < gallerySliderItem; i++) {
                var thisImage = sync1.find('.gallery-slider__slide img:eq('+i+')');
                thisImage.attr('src', thisImage.attr('data-slider-src'));
                gallerySlideReached ++;
            }
        }
        
        sync1.on('initialized.owl.carousel', function(e) {

            for(var i = gallerySlideReached; i < 3; i++) {
                var thisImage = sync1.find('.gallery-slider__slide img:eq('+i+')');
                thisImage.attr('src', thisImage.attr('data-slider-src'));
                gallerySlideReached ++;
            }
            gallerySliderItem = e.item.index + 1;
            sync1   
                .trigger('next.owl.carousel')
                .trigger('prev.owl.carousel');
        });
        
        // Start Carousel
        sync1.owlCarousel({
            rtl: false,
            center: true,
            loop: false,
            items: 1,
            margin: 0,
            nav: navSlider,
            navText:['<svg class="icon"><use xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="/img/icons.svg#arrow--left"></use></svg>',
                     '<svg class="icon"><use xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="/img/icons.svg#arrow--right"></use></svg>'],
            dots:false,
            mouseDrag:navSlider,
            lazyLoad:false
        });        
        sync2.owlCarousel({
            rtl: false,
            center: true,
            loop: false,
            items: thumbs,
            margin: 0,
            nav: false,
            dots:false,
            mouseDrag:navSlider
        });
        
        sync1.on('changed.owl.carousel', function (e) {
            syncCarousels(e.item.index);
        });
        sync2.on('click', '.owl-item', function (e) {
            syncCarousels($(this).index());
        });
        sync2.on('changed.owl.carousel', function (e) {
            syncCarousels(e.item.index);
        });
    }
    
    var openLightbox = function(lightboxTrigger){
        if(lightboxAnimatingFlag == false){
            lightboxAnimatingFlag = true;
            lightboxLink = lightboxTrigger.attr('data-lightbox');
            articleLightbox = $(lightboxLink);
            
            if (articleLightbox[0]!==void(0)) {
                articleLightbox.addClass('animate');
                articleLightbox.on(onTransitionEnd, function () {
                    lightboxAnimatingFlag = false;
                    articleLightbox.off(onTransitionEnd);
                });

                html.addClass('overflow--hidden');
                
                if(galleryInitialized == false){
                    galleryInitialized = true;
                    initializeGallery(lightboxTrigger);
                }
            }
        }
    }
    
    var closeLightbox = function(){
        if(lightboxAnimatingFlag == false){
            lightboxAnimatingFlag = true;
            articleLightbox.removeClass('animate');
            articleLightbox.on(onTransitionEnd, function(){

                html.removeClass('overflow--hidden');
                lightboxAnimatingFlag = false;
                articleLightbox.off(onTransitionEnd);
                articleLightbox = null;
                lightboxLink = null;
            });
        }
    }
    
    $('.js-open-gallery-lightbox').on('click', function(){
        var $this = $(this);
        openLightbox($this);
    });
    
    $(document).on('click', '.js-close-gallery-lightbox', function(){
        closeLightbox();
    });
})();