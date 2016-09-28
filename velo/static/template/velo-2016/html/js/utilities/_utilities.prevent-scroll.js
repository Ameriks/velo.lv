$('.js-prevent-scroll').bind('mousewheel DOMMouseScroll', function (e) {
    if ($(this)[0].scrollHeight !== $(this).outerHeight()) {
        var e0 = e.originalEvent,
            delta = e0.wheelDelta || -e0.detail;

        this.scrollTop += (delta < 0 ? 1 : -1) * 30;
        e.preventDefault();
    }
});