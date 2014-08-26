window.ENV = window.ENV || {}

@replaceemail = (self) ->
  $(self).parents(".form-group").removeClass("has-error")
  $(self).parents(".form-group").find('input').val($(self).html())
  $(self).parent().remove()

@getCookie = (name) ->
  for cookie in document.cookie.split ';' when cookie and name is (cookie.split '=')[0].trim()
    return decodeURIComponent cookie[(1 + (cookie.split '=')[0].length)...]
  null

@validateSSN = (value) ->
    value = $.trim(value.replace("-",""))
    if not value or value.length != 11
        false
    checksum = 1
    checksum = checksum - (parseInt(value[i], 10) * parseInt("01060307091005080402".substr(i * 2,2), 10)) for i in [0..9]
    if  checksum - (Math.floor(checksum / 11) * 11) != parseInt(value[10], 10)
        return false
    value

@maskedSSN = (field) ->
    field.mask("999999-99999",{
        completed: ->
            value = validateSSN this.val()
            if not value
                this.parents(".form-group").addClass("has-error")
            else
                this.parents(".form-group").removeClass("has-error")
                year = if value[6] == "1" then "19" else "20"
                $("input[name$='birthday']", this.parents('form')).val("#{year}#{value.substr(4,2)}-#{value.substr(2,2)}-#{value.substr(0,2)}").change()
    })
    false


pad = (val, length, padChar = '0') ->
  val += ''
  numPads = length - val.length
  if (numPads > 0) then new Array(numPads + 1).join(padChar) + val else val

call_formset_function = (row, container, type) ->
  function_name = field for field in $(container).prop("class").split(' ') when field.indexOf('_inline_class') != -1
  if typeof window[function_name+'_'+type] == 'function'
    window[function_name+'_'+type](row)

formset = (containers) ->
  ret_obj = {}
  for container in containers

    prefix = $(container).data "prefix"
    $container = $(container).find(".formset_container")
    $items = $container.find ".item:not(.template)"
    $items.formset
      prefix: prefix
      container: $container
      addText: ''
      addCssClass: 'btn btn-default glyphicon glyphicon-plus'
      deleteText: ''
      deleteCssClass: 'btn btn-danger glyphicon glyphicon-remove delete'
      upCssClass: 'btn btn-minier icon-arrow-up'
      downCssClass: 'btn btn-minier icon-arrow-down'
      formTemplate: $(container).find ".template"
      added: (row) -> call_formset_function(row, container, 'added')
      removed: (row) -> call_formset_function(row, container, 'removed')

$ ->
  window.ENV.formsets = formset $ '.django-inline-form'

  $('table th input:checkbox').on 'click', ->
    for checkbox in $(@).closest('table').find('tr > td:first-child input:checkbox')
      checkbox.checked = @.checked
      $(checkbox).closest('tr').toggleClass('selected')
      ""
  $('.calculate_time_field_btn').on 'click', ->
    field = $(@).parents('.input-group').find('input')

    calc_milliseconds = (time) ->
      time_array = time.split(':')
      mills = 0
      mills = parseInt(time_array[0]) * 60 * 60 * 1000
      mills += parseInt(time_array[1]) * 60 * 1000
      time_array2 = time_array[2].split('.')
      mills += parseInt(time_array2[0]) * 1000
      if time_array2[1] != undefined
        mills += parseInt(time_array2[1])
      return mills

    zero_m = calc_milliseconds(field.attr('zero_time'))
    input_m = calc_milliseconds(field.val())
    final_m = input_m - zero_m
    # Calc back to normal
    millisecs = final_m % 1000
    final_m_tmp = (final_m - millisecs) / 1000
    seconds = final_m_tmp % 60
    final_m_tmp = (final_m_tmp - seconds) / 60
    minutes = final_m_tmp % 60
    hours = (final_m_tmp - minutes) / 60

    field.val("#{pad(hours, 2)}:#{pad(minutes, 2)}:#{pad(seconds, 2)}.#{millisecs}")
    ""