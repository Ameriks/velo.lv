$ ->
  # maskedSSN $('#id_ssn')
  $('#id_email').mailgun_validator
    api_key: 'pubkey-7049tobos-x721ipc8b3dp68qzxo3ri5'
    success: (data) ->
      $('#id_email').parents(".controls").find('span').remove()
      if not data.is_valid
        $('#id_email').parents(".form-group").addClass("has-error")
        button = if data.did_you_mean then "<button onclick='replaceemail(this);return false;'>#{data.did_you_mean}</button> ?" else ""
        $('#id_email').after("<span class='help-block'><strong>Invalid. #{button}</strong></span>");
      else
        $('#id_email').parents(".form-group").removeClass("has-error")
  $('#id_first_name').on 'change', (e) ->
    element = if e.srcElement then e.srcElement else e.target
    last_char = element.value.slice(-1).toLowerCase()
    if last_char == 'a' or last_char == 'e'
      $('#id_gender').val('F')
    else
      $('#id_gender').val('M')
  true
