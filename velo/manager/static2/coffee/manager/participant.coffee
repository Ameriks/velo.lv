$ ->
  $('#id_ssn').on 'change', (e) ->
    element = if e.srcElement then e.srcElement else e.target
    value = validateSSN element.value
    if not value
        this.parents(".form-group").addClass("has-error")
    else
        this.parents(".form-group").removeClass("has-error")
        year = if value[6] == "1" then "19" else "20"
        $("input[name$='birthday']", this.parents('form')).val("#{year}#{value.substr(4,2)}-#{value.substr(2,2)}-#{value.substr(0,2)}").change()
    false

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
