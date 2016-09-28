(function(){
    //defer background image loading
    var deferBackgroundImageLoading = function() {
        var imgBackgroundDefer = $('.js-background-image');
        var windowWidth = window.innerWidth;
        
        imgBackgroundDefer.each(function(){
            var $this = $(this);
            var imgBackgroundSrc = $this.attr('data-background-image');
            var imgDeferScreenSize = Number($this.attr('data-load-on'));
            
            var loadImage = function(){
                $('<img/>').attr('src', imgBackgroundSrc).load(function() {
                    $(this).remove();
                    $this
                    .css({'background-image': 'url('+imgBackgroundSrc+')'})
                    .addClass('image-loaded');
                });                
            }
            
            if (!isNaN(imgDeferScreenSize)){
                if(imgDeferScreenSize < windowWidth){
                    loadImage();
                }
            }else{
                loadImage();
            }
        });
    };
    
    $(window).on('load orientationchange', deferBackgroundImageLoading);
    
    var resizeTimer;
    $(window).on('resize', function (e) {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function () {
            deferBackgroundImageLoading();
        }, 250);
    });
})();