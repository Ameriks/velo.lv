(function () {
    var isFileSize = function(file, allowedSize){
        var fileLength = file.length;
        for (var i = 0; i < fileLength; i++) {
            if(file[i].size >= allowedSize){
                return false;
            }
        }
        return true;
    }
    
    $('.js-input-file').each(function () {
        var $input = $(this),
            $label = $input.next('.js-input-file__label'),
            labelVal = $label.html(),
            labelText = $label.find('.js-input-file__text'),
            allowedSize = $input.attr('data-filesize'),
            errorMessage = $input.parent().find('.js-input-file__error'),
            errorMessageFileSize = errorMessage.find('.js-allowed-size');
        
        errorMessageFileSize.html(Math.round(allowedSize/1024/1024));
        
        $input.on('change', function (e) {
            var files = this.files;
            var filesLength = files.length;
            var fileName = '';
            
            if(isFileSize(files, allowedSize)){
                errorMessage.addClass('hidden');
                
                if (files && filesLength > 1){
                    fileName = (this.getAttribute('data-multiple-caption') || '').replace('{count}', filesLength);
                }else if (e.target.value){
                    fileName = e.target.value.split('\\').pop();
                }
                
                if (fileName){
                    labelText.html(fileName);
                }else{
                    $label.html(labelVal);
                }
            }else{
                errorMessage.removeClass('hidden');
            }
        });

        // Firefox bug fix
        $input
            .on('focus', function () {
                $input.addClass('focus');
            })
            .on('blur', function () {
                $input.removeClass('focus');
            });
    });
})();