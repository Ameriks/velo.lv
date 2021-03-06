@Participant_inline_class_added = (row) ->
  update_line_participant row

@CompanyParticipant_inline_class_added = (row) ->
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
  insurance = $("select[name$='-insurance']", row)
  city = $("select[name$='-city']", row)
  country = $("select[name$='-country']", row)
  bike_brand = $("select[name$='-bike_brand']", row)
  bike_brand2 = $("input[name$='-bike_brand2']", row)

  $("input[name$='-first_name']", row).autocomplete
      serviceUrl: row.parents("form").data("autocomplete"),
      onSelect: (suggestion) ->
          $("select[name$='country']", row).val(suggestion.country).change()
          $("select[name$='gender']", row).val(suggestion.gender).change()

          $("input[name$='last_name']", row).val(suggestion.last_name).change().focus()
          $("input[name$='bike_brand2']", row).val(suggestion.bike_brand2).change().focus()

          birthday = suggestion.birthday.split('-')
          console.log birthday
          $("select[name$='birthday_year']", row).val(parseInt(birthday[0])).change()
          $("select[name$='birthday_month']", row).val(parseInt(birthday[1])).change()
          $("select[name$='birthday_day']", row).val(parseInt(birthday[2])).change()

          $("input[name$='team_name']", row).val(suggestion.team_name).change().focus()
          $("input[name$='phone_number']", row).val(suggestion.phone_number).change().focus()
          $("input[name$='email']", row).val(suggestion.email).change().focus().blur()

      formatResult: (suggestion, currentValue) ->
          return "#{suggestion.first_name} #{suggestion.last_name} #{suggestion.birthday} "

  if row.parents(".formset_container").data("can-delete") == 'False'
    $('.delete_button', row).remove()
    $('.price', row).remove()

  $(".participant__number", row).html(row.index())


  if not bike_brand.val() or bike_brand.val() != "216"
    $(bike_brand2).parents(".input-wrap").hide()

  bike_brand.on "change", (e) ->
    el = $(bike_brand2).parents(".input-wrap")

    if $(this).val() == '216'
      el.show()
    else
      el.hide()

  if not insurance.val()
    $(ssn).parents(".input-wrap").hide()

  insurance.on "change", (e) ->
    el = $(ssn).parents(".input-wrap")

    if $(this).val()
      el.show()
    else
      $(ssn).val("")
      el.hide()

  if not country.val() == 'LV'
    $(city).parents(".input-wrap").hide()

  country.on "change", (e) ->
    el = $(city).parents(".input-wrap")

    if $(this).val() == 'LV'
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

$ ->
  if $(".CompanyParticipant_inline_class")[0]

    for container in $('.item:not(.template)')
      update_line_participant($(container))
