@Participant_inline_class_added = (row) ->
  update_line_participant row





check_price = (row) ->
  distance = $("select[name$='distance']", row).val()
  birthday = $("select[name$='birthday_year']", row).val()
  insurance = $("[name$='insurance']", row).val()
  csrf = document.getElementsByName('csrfmiddlewaretoken')[0].value

  url = $(row).parents("form").data('check-price')

  $.ajax
    url: url
    type: 'POST'
    data:
      csrfmiddlewaretoken: csrf
      distance: distance
      birthday_year: birthday
      insurance: insurance
    dataType: 'json'
    success: (data) ->
      $('.price', row).html(data.message)
    error: ->
      $('.price', row).html('Please enter all details')


update_line_participant = (row) ->
  ssn = $("input[name$='-ssn']", row)
  birthday = $("input[name$='-birthday']", row).val()
  insurance = $("select[name$='-insurance']", row)

  $(".participant__number", row).html(row.index())

  if not insurance.val()
    $(ssn).parents(".input-wrap").hide()

  insurance.on "selectmenuchange", (e) ->
    el = $(ssn).parents(".input-wrap")

    if $(this).val()
      el.show()
    else
      $(ssn).val("")
      el.hide()

  if !row.hasClass("noadd")
    $("select[name$='-birthday_year'], select[name$='distance'], select[name$='insurance']", row).on "change", (e) ->
      check_price row
      undefined

    check_price row


  undefined


$ ->
  if $(".Participant_inline_class")[0]

    for container in $('.item:not(.template)')
      update_line_participant($(container))
