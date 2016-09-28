(function () {
    var cursorXStartPosition;
    var cursorXCurrentPosition;
    var currentScrollPosition;
    var mouseDown = false;
    var touchFlag = false;
    var secondaryNavScroll = $('.js-secondary-nav-scroll');

    secondaryNavScroll.on('touchstart', function(){
        touchFlag = true;
    });
    
    secondaryNavScroll.on('touchend', function(){
        touchFlag = false;
    });
    
    secondaryNavScroll.on('mousedown', function (e) {
        if(touchFlag == false){
            mouseDown = true;
            cursorXStartPosition = e.clientX;
            currentScrollPosition = secondaryNavScroll.scrollLeft();
        }
    });

    $(window).on('mousemove', function (e) {
        if(touchFlag == false && mouseDown == true){
            secondaryNavScroll.scrollLeft(currentScrollPosition + (cursorXStartPosition - e.clientX));
        }
    });

    $(window).on('mouseup', function (e) {
        mouseDown = false;
    });
    
    $('.secondary-nav__link').on('click', function(e){
        if(Math.abs(cursorXStartPosition - e.clientX) > 20){
            e.preventDefault();
        }
    });
})();