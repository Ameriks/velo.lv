(function(){
    var scrollElement = $('.js-scroll-along');
    var scrollBlock = $('.js-scroll-along-block');
    
    if(scrollElement.length){
        var initialOffsetTop;
        var scrollBlockHeight;
        var scrollBlockOffset;
        var tableHeadHeight;
        var tableThead = scrollBlock.find('thead');
        var clonedThead = tableThead.clone();
        
        var createSecondHead = function(){
            clonedThead.addClass('scroll-along__thead');
            $('.js-scroll-append').append(clonedThead);
        }
        createSecondHead();
        
        var seteDimensions = function(){
            tableThead.find('th').each(function(){
                var $this = $(this);
                var cellWidth = $this.width();
                var cellIndex = $this.index();
                clonedThead.find('th:eq('+cellIndex+')').width(cellWidth);
            });
            tableThead.find('tr').each(function(){
                var $this = $(this);
                var cellWidth = $this.width();
                var cellIndex = $this.index();
                clonedThead.find('tr:eq('+cellIndex+')').width(cellWidth);
            });
            
            scrollBlockHeight = scrollBlock.height();
            scrollBlockOffset = scrollBlock.offset().top;
            tableHeadHeight = tableThead.height();
        }
        
        var toggleScrollClass = function($this){
            var thisScroll = $this.scrollTop();
            
            if (thisScroll > initialOffsetTop) {
                scrollElement.addClass('scroll-along');
            }
            if (thisScroll < initialOffsetTop || thisScroll > (scrollBlockHeight + scrollBlockOffset - tableHeadHeight - 120)) {
                scrollElement.removeClass('scroll-along');
            }
        }
        
        $(window).scroll(function () {
            toggleScrollClass($(this));
        });
        
        $(window).on('load resize orientationchange', function(){
            initialOffsetTop = scrollElement.offset().top;
            seteDimensions();
        });
    }    
})();