window.ENV = window.ENV || {}

formset = (containers) ->
  ret_obj = {}
  for container in containers

    prefix = $(container).data "prefix"
    $container = $(container).find(".formset_container")
    $items = $container.find ".item:not(.template)"
    $items.formset
      prefix: prefix
      container: $container
      formTemplate: $(container).parent().find ".template"



$ ->
  $('input[type=reset]').on 'click', (event) ->
    elem = event.target
    form = $(elem).parents('form')
    $('input[type=text], input[type=password], input[type=textarea], input[type=number], select', form).val("")
    false

  window.ENV.formsets = formset $ '.django-inline-form'
