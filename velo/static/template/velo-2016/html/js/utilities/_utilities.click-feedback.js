(function(){
    var onAnimationEnd = 'animationend webkitAnimationEnd oAnimationEnd MSAnimationEnd';

    window.onunload = function(){
        $('.click-circle').remove();
    }; 
  
    $('body').on('click', 'a, button, input, select, textarea, label, .js-click-feedback', function(e){
        var clickX = e.clientX - 10;
        var clickY = e.clientY - 10;
        var clickCircle = '<div class="click-circle" style="top:'+clickY+'px; left:'+clickX+'px;"></div>'
        $('body').append(clickCircle);
        $('.click-circle').addClass('scale');
        $('.click-circle').on(onAnimationEnd, function (e) {
            $(this).remove();
            $(this).off(e);
        });
    });
})();