$ ->
    $('input[type=reset]').on 'click', (event) ->
        elem = event.target
        form = $(elem).parents('form')
        $('input[type=text], input[type=password], input[type=textarea], input[type=number], select', form).val("")
        false
