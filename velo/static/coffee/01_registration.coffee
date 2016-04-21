@Participant_inline_class_added = (row) ->
  update_line_participant row
  jsSelect(row)





check_price = (row) ->
  distance = $("select[name$='distance']", row).val()
  birthday = $("input[name$='birthday']", row).val()
  insurance = $("select[name$='insurance']", row).val()
  csrf = document.getElementsByName('csrfmiddlewaretoken')[0].value

  url = $("select[name$='distance']", row).data('url')

  $.ajax
    url: url
    type: 'POST'
    data:
      csrfmiddlewaretoken: csrf
      distance: distance
      birthday: birthday
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

  $('.dateinput', row).datetimepicker
    format: 'YYYY-MM-DD'

  if not insurance.val()
    $(ssn).parents(".input-wrap").hide()

  insurance.on "selectmenuchange", (e) ->
    el = $(ssn).parents(".input-wrap")

    if $(this).val()
      el.show()
    else
      $(ssn).val("")
      el.hide()

  $("input[name$='-birthday']", row).on "dp.change", (e) ->
    check_price row
#    alert "Check price"
  $("select[name$='distance'], select[name$='insurance']", row).on "selectmenuchange", (e) ->
    check_price row
#    alert "Check price"

  check_price row



#  if !row.hasClass("noadd")
##    debugger
#    $("select[name$='distance'], input[name$='birthday'], select[name$='insurance']", row).change ->
#      check_price(row)
#      ""
#    check_price(row)




  undefined


$ ->
  if $(".Participant_inline_class")[0]

    for container in $('.item:not(.template)')
      update_line_participant($(container))
