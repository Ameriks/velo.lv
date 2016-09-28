(function(){
    var playVideo = function(triggerElement){
        var videoIframe = triggerElement.find('.js-video-iframe');
        var videoIframeSrc = videoIframe.attr('data-src');
        
        triggerElement.off('click');
        triggerElement.addClass('brief--video-playing');
        videoIframe.attr('src', videoIframeSrc);
    }
    
    $('.js-play-video').on('click', function(){
        playVideo($(this));
    });
})();