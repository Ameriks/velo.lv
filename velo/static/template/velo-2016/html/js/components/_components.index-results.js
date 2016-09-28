(function(){
    var showResults = $('.js-show-results');
    var indexResults = $('.js-index-results');
    var showWinner = $('.js-show-winner');
    var winner = $('.js-winner');
    
    var loadWinnerImage = function(winnerObject){
        var winnerImage = winnerObject.find('.js-winner-image');
        var winnerImageSrc = winnerImage.attr('data-background-image');
        
        $('<img/>').attr('src', winnerImageSrc).load(function() {
            $(this).remove();
            winnerImage
            .css({'background-image': 'url('+winnerImageSrc+')'})
            .addClass('image-loaded');
        });
    }
    
    
    showResults.on('click', function(){
        var $this = $(this);
        var dataShow = $this.attr('data-show');
        showResults.removeClass('active');
        $this.addClass('active');
        indexResults.addClass('hidden');
        $(dataShow).removeClass('hidden');
    });
    
    showWinner.on('click', function(){
        var $this = $(this);
        var dataShow = $this.attr('data-show');
        
        winner.addClass('hidden');
        $(dataShow).removeClass('hidden');
        
        loadWinnerImage($(dataShow));
    });
    
    $(window).on('load', function(){
        loadWinnerImage(winner.eq(0));
    });
})();