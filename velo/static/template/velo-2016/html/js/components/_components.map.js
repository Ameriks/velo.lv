(function(){    
    var deparmentMap = $('#js-map');
    
    function initialize() {
        var longitude = Number(deparmentMap.attr('data-lng'));
        var lattitude = Number(deparmentMap.attr('data-lat'));
        var mapCanvas = document.getElementById('js-map');
        
        var myLatLng = {lat: lattitude, lng: longitude};
        var mapOptions = {
            center: {lat: lattitude, lng: longitude-0.005},
            zoom: 16,
            mapTypeId: google.maps.MapTypeId.ROADMAP,
            scrollwheel: false
        }

        var map = new google.maps.Map(mapCanvas, mapOptions);

        var marker = new google.maps.Marker({
            position: myLatLng,
            map: map,
            icon: '/img/map-pin.png'
        });
    }
    if(deparmentMap.length){
        $.getScript("https://maps.googleapis.com/maps/api/js").done(function() {
            google.maps.event.addDomListener(window, 'load', initialize);
        });
    }
})();