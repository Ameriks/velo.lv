show_hide_invoice_fields = (element) ->
  if element.data 'bill'
    $('.invoice_fields ').show()
  else
    $('.invoice_fields ').hide()



$ ->
  payment = $("input[name$='payment_type']:checked")
  show_hide_invoice_fields payment


  $("input[name$='payment_type']").on 'change', (e) ->
    element = if e.srcElement then e.srcElement else e.target
    element = $(element)
    show_hide_invoice_fields element
