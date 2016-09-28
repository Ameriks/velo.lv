(function(){   
    var inputAmount = $('.js-input-amount');
    
    var incrementAmount = function(inputValue){
        var amount = inputValue.val();
        
        amount ++
        
        inputValue.val(parseInt(amount));
    }
    
    var decrementAmount = function(inputValue){
        var amount = inputValue.val();
        
        if(amount <= 1){
            amount = 1
        }else{
            amount --
        }
        
        inputValue.val(parseInt(amount));
    }
    
    inputAmount.each(function(){
        var $this = $(this);
        var inputPlus = $this.find('.js-input-amount-plus');
        var inputMinus = $this.find('.js-input-amount-minus');
        var inputValue = $this.find('.js-input-amount-value');
        
        inputPlus.on('click', function(){
            incrementAmount(inputValue);
        });
        inputMinus.on('click', function(){
            decrementAmount(inputValue);
        });
    });
})();