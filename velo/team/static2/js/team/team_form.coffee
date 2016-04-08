@Member_inline_class_added = (row) ->
  update_every_line(row)

@Member_inline_class_removed = (row) ->
  console.log 'removed'

teams = null

parseDate = (input) ->
  parts = input.split('-')
  return new Date(parts[0], parts[1]-1, parts[2])

show_hide_ssn = (parent_item, hide) ->
  if hide
    $("input[name$='ssn']", parent_item).parents('.form-group').hide()
  else
    $("input[name$='ssn']", parent_item).parents('.form-group').show()

show_hide_birthday = (parent_item, hide) ->
  if hide
    $("input[name$='birthday']", parent_item).parents('.form-group').hide()
  else
    $("input[name$='birthday']", parent_item).parents('.form-group').show()


update_every_line = (row) ->
  $('.dateinput', row).datepicker
    format: 'yyyy-mm-dd'
    autoclose: true
    weekStart: 1

  if $("select[name$='country']", row).val() == 'LV'
    maskedSSN $("input[name$='ssn']", row)


  $("select[name$='country']", row).on 'change', (e) ->
    element = if e.srcElement then e.srcElement else e.target
    element = $(element)
    value = element.val()
    if value == 'LV'
      maskedSSN $("input[name$='ssn']", element.parents('.item'))
    else
      field = $("input[name$='ssn']", element.parents('.item'))
      field.unmask()
      field.parents(".control-group").removeClass("error")

  if $("select[name$='country']", row).val() == 'LV'
    show_hide_ssn(row, false)
    show_hide_birthday(row, true)
  else
    show_hide_ssn(row, true)
    show_hide_birthday(row, false)

  $("select[name$='country']", row).on 'change', (e) ->
    element = if e.srcElement then e.srcElement else e.target
    if element.value == 'LV'
      show_hide_ssn(row, false)
      show_hide_birthday(row, true)
    else
      show_hide_ssn(row, true)
      show_hide_birthday(row, false)


  ""




$ ->

  for container in $('.item:not(.template)')
    update_every_line($(container))
