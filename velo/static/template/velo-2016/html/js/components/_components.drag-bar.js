(function () {
    var dragBar = $('.js-drag-bar'); 
    var dragHandle = $('.js-drag-handle');
    var dragContainer = $('.js-drag-container');
    var dragContent = $('.js-drag-content');
    
    var dragFlag = false;
    var contentDragFlag = false;
    var handleLastPosition = 0;
    var scrollLastPosition = 0;
    var handleDifference;
    
    var pointerStartPosition;
    var scrollStartPosition;
    
    var pointerPosition = function(e){
        var clientX;
        if((e.originalEvent.clientX)){
            clientX = e.originalEvent.clientX;
        }else if(e.originalEvent.targetTouches){
            clientX = e.originalEvent.targetTouches[0].clientX;
        }
        return clientX;
    };
    
    var relativeTo = function(numberOne, numberTow){
        return numberTow * 100 / numberOne; 
    }
    var absoluteTo = function(precentage, numberOne){
        return precentage * numberOne / 100; 
    }
    
    var setDragHandleWidth = function(){
        var dragContentWidth = dragContent.width();
        var dragContainerWidth = dragContainer.width();
        if(dragContentWidth > dragContainerWidth){
            dragHandle.css({width:relativeTo(dragContentWidth, dragContainerWidth)+'%'});
        }else{
            dragHandle.css({width:'100%'});
        }
        
    }
    
    var updateHandlePosition = function(e, pointerStartPosition){
        var handlePosition;
        var handleDifference = dragBar.width() - dragHandle.width();
        var pointerDelta = pointerPosition(e) - pointerStartPosition;
        
        if(pointerDelta <= -handleLastPosition){
            handlePosition = 0;
        }else if(pointerDelta >= handleDifference - handleLastPosition){
            handlePosition = handleDifference;
        }else{
            handlePosition = handleLastPosition + pointerDelta;
        }
        
        return relativeTo(dragBar.width(), handlePosition);
    }
    
    var updateScrollPosition = function(e, scrollStartPosition){
        var scrollPosition;
        var contentDifference = dragContent.width() - dragContainer.width();
        var scrollDelta = scrollStartPosition - pointerPosition(e);
        
        if(scrollDelta <= -scrollLastPosition || contentDifference < 0){
            scrollPosition = 0;
        }else if(scrollDelta >= contentDifference - scrollLastPosition){
            scrollPosition = contentDifference;
        }else{
            scrollPosition = scrollLastPosition + scrollDelta;
        }
        return scrollPosition;
    }
        
    dragContainer.on('mousedown touchstart', function (e) {
        contentDragFlag = true;
        scrollStartPosition = pointerPosition(e);
    });
    
    dragHandle.on('mousedown touchstart', function(e){
        dragFlag = true;
        pointerStartPosition = pointerPosition(e);
        
    });
    
    $(window).on('mousemove touchmove', function(e){
        //dragContainer move
        if(contentDragFlag == true){

            var setScrollPosition = updateScrollPosition(e, scrollStartPosition);
            
            dragContainer.scrollLeft(setScrollPosition);
            dragHandle.css({left:relativeTo(dragContent.width(), setScrollPosition)+'%'});
        }
        
        //dragBar move
        if(dragFlag == true){

            var setHandlePosition = updateHandlePosition(e, pointerStartPosition);
            
            dragHandle.css({left:setHandlePosition+'%'});
            dragContainer.scrollLeft(absoluteTo(setHandlePosition, dragContent.width()));
        }
    });
    
    $(window).on('mouseup touchend', function(e){
        dragFlag = false;
        contentDragFlag = false;
        if(dragHandle.length){
            handleLastPosition = dragHandle.position().left;
            scrollLastPosition = dragContainer.scrollLeft();
        }
    });
    
    $(window).on('load orientationchange resize', setDragHandleWidth);
    
})();