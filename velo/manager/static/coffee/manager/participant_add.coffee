participants = null

$ ->
  participants = new Bloodhound
    datumTokenizer: Bloodhound.tokenizers.obj.whitespace('birthday')
    queryTokenizer: Bloodhound.tokenizers.whitespace
    remote: participant_search

  participants.initialize()

  tmpl = Handlebars.compile('<p><strong>{{full_name}}</strong><br />{{birthday}}<br />{{ssn}}<br />{{competition__name}}</p>')

  $('#id_birthday').typeahead(null, {
    name: 'birthday',
    displayKey: 'birthday',
    source: participants.ttAdapter(),
    templates:
      suggestion: tmpl
  })

  $('#id_last_name').typeahead(null, {
    name: 'last_name',
    displayKey: 'last_name',
    source: participants.ttAdapter(),
    templates:
      suggestion: tmpl
  })

  $('#id_ssn').typeahead(null, {
    name: 'ssn',
    displayKey: 'ssn',
    source: participants.ttAdapter(),
    templates:
      suggestion: tmpl
  })

  $("#id_birthday, #id_last_name, #id_ssn").bind 'typeahead:selected', (obj, datum) ->
    for key, value of datum
      if key == 'birthday' or key == 'ssn' or key == 'last_name'
        typeaheadInput = $("#id_#{key}").data('ttTypeahead').input
        typeaheadInput.setQuery(value)
        typeaheadInput.resetInputValue()
      else
        $("#id_#{key}").val(value)
      ""
  $('#id_ssn').bind 'change', (obj) ->
    value = obj.target.value.replace('-', '')
    year = if value[6] == "1" then "19" else "20"
    input = $("input[name$='birthday']", $(this).parents('form'))
    new_val = "#{year}#{value.substr(4,2)}-#{value.substr(2,2)}-#{value.substr(0,2)}"
    if input.hasClass('tt-input')
      input = input.data('ttTypeahead').input
      input.setQuery(new_val)
      input.resetInputValue()
    else
      input.val(new_val)


  $('.datetimeinput').datetimepicker({
    useSeconds: false,
    minuteStepping: 5,
    pick12HourFormat: false,
    format: 'YYYY-MM-DD HH:mm'
  })