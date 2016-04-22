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

  $('#id_donation').on('change', (evt) ->
    total = Math.round((parseFloat($(this).val() or 0) + parseFloat($('#final_price').data('amount') or 0)) * 100) / 100
    $('#final_price').html(total)
  ).change()
